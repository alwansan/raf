"""GFX107 source-free CPU bindpose matrix and private original rig audit tests."""
import math
import unittest
from types import SimpleNamespace
from gfxlab.tools.gfx107_source_bindpose_math import (
    identity,mul,max_delta,source_matrix4,source_transform_trs,
    source_world_matrix,compute_bindpose_consistency)
from gfxlab.tools.gfx107_original_bindpose_matrix_audit import inspect_source_pose

OWNER="resources.assets"
def mk_entry(x):return {"e%d%d"%(r,c):x[4*r+c] for r in range(4) for c in range(4)}
def trans(x=0.,y=0.,z=0.):
    d=list(identity());d[3]=x;d[7]=y;d[11]=z;return tuple(d)
def transform(parent=0,x=0.,y=0.,z=0.):
    return {"m_LocalPosition":{"x":x,"y":y,"z":z},
        "m_LocalRotation":{"x":0.,"y":0.,"z":0.,"w":1.},
        "m_LocalScale":{"x":1.,"y":1.,"z":1.},
        "m_Father":{"m_FileID":0,"m_PathID":parent}}
def obj(kind,data):
    return SimpleNamespace(type=SimpleNamespace(name=kind),
        read_typetree=lambda check_read=False:data)
def ptr(index):return {"m_FileID":0,"m_PathID":index}

class TestGFX107BindposeMathematics(unittest.TestCase):
    def test_decodes_only_explicit_indexed_matrix(self):
        self.assertEqual(source_matrix4(mk_entry(identity())),identity())
        with self.assertRaisesRegex(ValueError,"GFX107_BINDPOSE_MATRIX_LAYOUT_UNRECOGNIZED"):
            source_matrix4({"matrix":[1.]*16})
        with self.assertRaisesRegex(ValueError,"GFX107_BINDPOSE_MATRIX_SHAPE"):
            source_matrix4(list(identity()))
    def test_trs_root_translation_and_child_ancestry(self):
        tr={11:transform(x=2.),12:transform(parent=11,x=3.)}
        def lookup(k):return tr[k]
        def parent(k,v):return v["m_Father"]["m_PathID"] or None
        world=source_world_matrix(12,lookup,parent)
        self.assertAlmostEqual(world[3],5.)
        self.assertEqual(world,trans(5.))
    def test_identity_source_bindpose_state(self):
        data=compute_bindpose_consistency(
            [mk_entry(trans(-5.)),mk_entry(trans(-10.))],
            [trans(5.),trans(10.)])
        self.assertEqual(data["source_pose_products_coherent_at_1e4"],2)
        self.assertTrue(data["source_pose_products_all_coherent_at_1e4"])
        self.assertFalse(data["source_pose_snapshot_is_confirmed_bind_pose"])
    def test_snapshot_disagreement_does_not_claim_bind_pose(self):
        data=compute_bindpose_consistency(
            [mk_entry(trans(-5.)),mk_entry(trans(-10.))],
            [trans(5.),trans(11.)])
        self.assertEqual(data["source_pose_products_coherent_at_1e4"],1)
        self.assertGreater(data["source_pose_products_max_abs_disagreement"],.9)
        self.assertFalse(data["source_pose_snapshot_is_confirmed_bind_pose"])
    def test_quaternion_rotation_columns_and_translation(self):
        p=transform(x=3.)
        p["m_LocalRotation"]={"x":0.,"y":0.,"z":math.sqrt(.5),"w":math.sqrt(.5)}
        m=source_transform_trs(p)
        self.assertAlmostEqual(m[0],0.,places=9)
        self.assertAlmostEqual(m[4],1.,places=9)
        self.assertAlmostEqual(m[1],-1.,places=9)
        self.assertAlmostEqual(m[3],3.,places=9)
    def test_nonunit_rotation_and_singular_scale_rejected(self):
        p=transform()
        p["m_LocalRotation"]["w"]=0.
        with self.assertRaisesRegex(ValueError,"GFX107_TRANSFORM_QUATERNION_NOT_UNIT"):
            source_transform_trs(p)
        p["m_LocalRotation"]["w"]=1.
        p["m_LocalScale"]["x"]=0.
        with self.assertRaisesRegex(ValueError,"GFX107_NONINVERTIBLE_TRANSFORM_SCALE"):
            source_transform_trs(p)
    def test_nan_and_missing_matrix_fail_closed(self):
        m=mk_entry(identity());m["e02"]=float("nan")
        with self.assertRaisesRegex(ValueError,"GFX107_BAD_MATRIX"):
            source_matrix4(m)
        with self.assertRaisesRegex(ValueError,"GFX107_TRANSFORM_COMPONENT_MISSING"):
            source_transform_trs({"m_LocalPosition":{}})
    def test_parent_loop_rejected(self):
        tr={11:transform(parent=12),12:transform(parent=11)}
        with self.assertRaisesRegex(ValueError,"GFX107_TRANSFORM_PARENT_CYCLE"):
            source_world_matrix(11,lambda k:tr[k],
                lambda k,x:x["m_Father"]["m_PathID"])
    def test_bone_bindpose_count_mismatch(self):
        with self.assertRaisesRegex(ValueError,"GFX107_BINDPOSE_BONE_COUNT_MISMATCH"):
            compute_bindpose_consistency([mk_entry(identity())],[])
    def test_exact_source_renderer_and_bone_matrix_snapshot(self):
        entry={"id":"M01","owner":OWNER,"mesh_pid":100,
               "game_object_pid":300,"source_bones":2}
        mesh={"m_BindPose":[mk_entry(identity()),mk_entry(trans(-5.))]}
        renderer={"m_Mesh":ptr(100),"m_GameObject":ptr(300),
                  "m_Bones":[ptr(11),ptr(12)]}
        wrong={"m_Mesh":ptr(100),"m_GameObject":ptr(301),
                  "m_Bones":[ptr(11),ptr(99)]}
        types={OWNER:{
            100:obj("Mesh",mesh),200:obj("SkinnedMeshRenderer",renderer),
            201:obj("SkinnedMeshRenderer",wrong),11:obj("Transform",transform()),
            12:obj("Transform",transform(parent=11,x=5.))}}
        result=inspect_source_pose(entry,types,{OWNER:[]})
        self.assertEqual(result["status"],"SOURCE_MATRIX_COMPUTED")
        self.assertEqual(result["source_bone_matrix_count"],2)
        self.assertEqual(result["source_pose_products_coherent_at_1e4"],2)
        self.assertFalse(result["original_rest_pose_restored"])
    def test_missing_unstaged_bone_does_not_claim_restoration(self):
        entry={"id":"M01","owner":OWNER,"mesh_pid":100,
               "game_object_pid":300,"source_bones":1}
        types={OWNER:{100:obj("Mesh",{"m_BindPose":[mk_entry(identity())]}),
            200:obj("SkinnedMeshRenderer",{"m_Mesh":ptr(100),
                "m_GameObject":ptr(300),"m_Bones":[ptr(99)]})}}
        out=inspect_source_pose(entry,types,{OWNER:[]})
        self.assertEqual(out["status"],"GFX107_SOURCE_TYPED_TRANSFORM_MISSING")
        self.assertFalse(out["original_rest_pose_restored"])
    def test_mesh_without_skin_is_not_restored(self):
        out=inspect_source_pose(
            {"id":"M03","owner":OWNER,"mesh_pid":100,"source_bones":0},
            {OWNER:{100:obj("Mesh",{})}},{OWNER:[]})
        self.assertEqual(out["status"],"NOT_APPLICABLE")

if __name__=="__main__":unittest.main()
