"""GFX106 rig hierarchy source-free exact renderer + transform ancestry tests."""
import unittest
from types import SimpleNamespace
from gfxlab.tools.gfx106_original_rig_hierarchy import inspect_rig_source,finite_transform

OWNER="resources.assets"
def ptr(n):return {"m_FileID":0,"m_PathID":n}
def obj(kind,data):
    return SimpleNamespace(type=SimpleNamespace(name=kind),
        read_typetree=lambda check_read=False:data)
def tr(parent):
    return {"m_LocalPosition":{"x":0.0,"y":1.0,"z":2.0},
            "m_LocalRotation":{"x":0.0,"y":0.0,"z":0.0,"w":1.0},
            "m_LocalScale":{"x":1.0,"y":1.0,"z":1.0},
            "m_Father":ptr(parent)}
def fixtures(*,cycle=False,missing=False,duplicate=False,bad_root=False,bindposes=2):
    r={"m_Mesh":ptr(100),"m_Bones":[ptr(11),ptr(99 if missing else 12)],
       "m_RootBone":ptr(77 if bad_root else 11)}
    t12=tr(12 if cycle else 11)
    allobjects={100:obj("Mesh",{"m_BindPose":[{} for _ in range(bindposes)]}),
                200:obj("SkinnedMeshRenderer",r),
                11:obj("Transform",tr(0)),
                12:obj("Transform",t12)}
    if duplicate:allobjects[201]=obj("SkinnedMeshRenderer",dict(r))
    e={"id":"M01","owner":OWNER,"mesh_pid":100,"source_bones":2}
    return e,{OWNER:allobjects},{OWNER:[]}

class OriginalSourceRigSyntheticTests(unittest.TestCase):
    def test_two_bones_reach_root_and_bindpose_counts(self):
        e,objs,ext=fixtures()
        r=inspect_rig_source(e,objs,ext)["counts"]
        self.assertEqual(r["renderer_bone_refs"],2)
        self.assertEqual(r["source_rig_hierarchy_coverage_complete"],1)
        self.assertEqual(r["bone_ancestor_reaches_root"],2)
        self.assertEqual(r["mesh_bindpose_count"],2)
        self.assertEqual(r["bone_pointer_resolved"],2)
    def test_cycle_rejected_without_fake_root(self):
        e,objs,ext=fixtures(cycle=True)
        r=inspect_rig_source(e,objs,ext)["counts"]
        self.assertGreater(r["bone_parent_chain_cycle"],0)
        self.assertEqual(r["source_rig_hierarchy_coverage_complete"],0)
    def test_missing_bone_reference_is_not_guessed(self):
        e,objs,ext=fixtures(missing=True)
        r=inspect_rig_source(e,objs,ext)["counts"]
        self.assertLess(r["bone_pointer_resolved"],2)
        self.assertEqual(r["source_rig_hierarchy_coverage_complete"],0)
    def test_missing_root_reference_blocks_complete_coverage(self):
        e,objs,ext=fixtures(bad_root=True)
        r=inspect_rig_source(e,objs,ext)["counts"]
        self.assertEqual(r["source_rootbone_pointer_resolved"],0)
        self.assertEqual(r["source_rig_hierarchy_coverage_complete"],0)
    def test_ambiguous_skinned_renderer_fails_closed(self):
        e,objs,ext=fixtures(duplicate=True)
        r=inspect_rig_source(e,objs,ext)["counts"]
        self.assertEqual(r["candidate_original_renderers"],2)
        self.assertEqual(r["source_renderer_identity_ambiguous_or_absent"],1)
    def test_bindpose_mismatch_blocks_coverage(self):
        e,objs,ext=fixtures(bindposes=1)
        r=inspect_rig_source(e,objs,ext)["counts"]
        self.assertEqual(r["renderer_bones_match_mesh_bindposes"],0)
        self.assertEqual(r["source_rig_hierarchy_coverage_complete"],0)
    def test_nonfinite_local_transform_rejected(self):
        d=tr(0)
        d["m_LocalPosition"]["x"]=float("nan")
        self.assertFalse(finite_transform(d))
        e,objs,ext=fixtures()
        objs[OWNER][12]=obj("Transform",d)
        r=inspect_rig_source(e,objs,ext)["counts"]
        self.assertEqual(r["bone_local_transform_invalid"],1)
        self.assertEqual(r["source_rig_hierarchy_coverage_complete"],0)
    def test_non_skinned_model_never_declared_restored(self):
        e,objs,ext=fixtures()
        e["source_bones"]=0
        r=inspect_rig_source(e,objs,ext)
        self.assertEqual(r["kind"],"NON_SKINNED")
        self.assertFalse(r["original_rig_restored"])
    def test_no_original_animation_or_identity_claimed(self):
        e,objs,ext=fixtures()
        r=inspect_rig_source(e,objs,ext)
        self.assertFalse(r["original_rig_restored"])
        self.assertNotIn("bone_names",r)
        self.assertNotIn("bone_transform_paths",r)

if __name__=="__main__":unittest.main()
