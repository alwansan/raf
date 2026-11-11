"""GFX108 original-free bone-index-preserving CPU LBS tests."""
import math
import unittest
from types import SimpleNamespace
from gfxlab.tools.gfx108_indexed_skinning_cpu import (
    positions_from_parsed_mesh,decoded_skin_weights,
    skin_positions_cpu,safe_displacement_stats,transform_point,
    handler_skin_safe_shapes)
from gfxlab.tools.gfx107_source_bindpose_math import identity,mul

def translate(x):
    v=list(identity());v[3]=x;return tuple(v)

def skin(weights,indices):
    return {"weight":weights,"boneIndex":indices}

class OriginalIndexedCPUSkin(unittest.TestCase):
    def test_decode_original_mesh_index_order_not_obj_weld(self):
        s=SimpleNamespace(m_Vertices=[SimpleNamespace(x=0.,y=0.,z=0.),
              SimpleNamespace(x=0.,y=0.,z=0.),SimpleNamespace(x=1.,y=0.,z=0.)])
        points=positions_from_parsed_mesh(s,3)
        self.assertEqual(len(points),3)
        self.assertEqual(points[0],points[1])
    def test_dict_and_flat_vertex_shapes(self):
        self.assertEqual(positions_from_parsed_mesh(SimpleNamespace(
            m_Vertices=[{"x":2.,"y":3.,"z":4.}]),1),[(2.,3.,4.)])
        self.assertEqual(positions_from_parsed_mesh(SimpleNamespace(
            m_Vertices=[1.,2.,3.]),1),[(1.,2.,3.)])
    def test_reject_missing_or_misordered_source_positions(self):
        with self.assertRaisesRegex(ValueError,"GFX108_DIRECT_VERTEX_COUNT_MISMATCH"):
            positions_from_parsed_mesh(SimpleNamespace(m_Vertices=[1.]),2)
        with self.assertRaisesRegex(ValueError,"GFX108_DIRECT_VERTEX_POSITIONS_UNAVAILABLE"):
            positions_from_parsed_mesh(SimpleNamespace(),2)
    def test_exact_weight_array_and_indices_verified(self):
        mesh={"m_Skin":[skin([.5,.5,0.,0.],[0,1,0,0]),
                        skin([1.,0.,0.,0.],[1,0,0,0])]}
        result=decoded_skin_weights(mesh,2,2)
        self.assertEqual(result,[[(.5,0),(.5,1)],[(1.,1)]])
    def test_bad_bone_index_with_positive_weight_fails(self):
        mesh={"m_Skin":[skin([1.,0.,0.,0.],[2,0,0,0])]}
        with self.assertRaisesRegex(ValueError,"GFX108_BONE_INDEX_OUT_OF_RANGE"):
            decoded_skin_weights(mesh,1,2)
    def test_weight_sum_and_nonfinite_fails(self):
        mesh={"m_Skin":[skin([.5,0.,0.,0.],[0,0,0,0])]}
        with self.assertRaisesRegex(ValueError,"GFX108_BONE_WEIGHT_SUM_NOT_NORMALIZED"):
            decoded_skin_weights(mesh,1,1)
        mesh={"m_Skin":[skin([float("nan"),0,0,0],[0,0,0,0])]}
        with self.assertRaisesRegex(ValueError,"GFX108_BAD_FINITE_SCALAR"):
            decoded_skin_weights(mesh,1,1)
    def test_two_bone_linear_blend_vertex_deformed(self):
        points=[(1.,0.,0.)]
        weights=[[(.25,0),(.75,1)]]
        result=skin_positions_cpu(points,weights,
             [translate(0.),translate(4.)],[identity(),identity()])
        self.assertEqual(result,[(4.,0.,0.)])
        report=safe_displacement_stats(result,points,identity())
        self.assertEqual(report["cpu_vertices_different_from_first_bone_reference_at_1e4"],1)
        self.assertEqual(report["cpu_vertex_max_distance_from_first_bone_reference"],3.)
        self.assertFalse(report["android_gpu_skinning_verified"])
    def test_bindpose_cancels_bone_in_stable_mesh_pose(self):
        points=[(1.,2.,3.)]
        result=skin_positions_cpu(points,[[(.5,0),(.5,1)]],
             [translate(4.),translate(9.)],
             [translate(-4.),translate(-9.)])
        self.assertEqual(result,points)
    def test_reference_mat_affine_homogeneous_guard(self):
        matrix=list(identity());matrix[15]=0.
        with self.assertRaisesRegex(ValueError,"GFX108_AFFINE_HOMOGENEOUS_W_INVALID"):
            transform_point(tuple(matrix),(1.,2.,3.))
    def test_only_shape_histograms_exported_for_unknown_mesh_skin(self):
        m=SimpleNamespace(m_BoneWeights=[(.5,.5),(.2,.8,0.,0.)],
                          m_BoneIndices=[(0,1),(0,1,0,0)])
        report=handler_skin_safe_shapes(m)
        self.assertEqual(report["weight_row_width_histogram"],{"2":1,"4":1})
        self.assertEqual(report["index_row_width_histogram"],{"2":1,"4":1})
        self.assertNotIn("weights",report)
        self.assertNotIn("bone_indices",report)
    def test_repeated_identical_vertices_distinct_skinning(self):
        # Two duplicate positions must NOT be welded: weights and poses differ.
        result=skin_positions_cpu([(0.,0.,0.),(0.,0.,0.)],
             [[(1.,0)],[(1.,1)]],
             [translate(0.),translate(10.)],[identity(),identity()])
        self.assertEqual(result,[(0.,0.,0.),(10.,0.,0.)])

if __name__=="__main__":unittest.main()
