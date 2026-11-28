import unittest
from tools.gt_light_exact_editor import audit as a
from tools.gt_light_same_export.audit import Rejected

def stage():
    return dict(scene_sha256=a.SCENE_SHA,scene_meta_sha256=a.META_SHA,source_scene_sha256=a.SOURCE_SHA,
                selected_objects=42,same_export_scene_copy_exact=True,other_original_assets_staged=0,
                scene_dependency_closure_claimed=False,import_executed=False)

def editor():
    return dict(status="PASS_ISOLATED_IMPORT",editor_step_outcome="success",Unity_import_verified=True,
                scene_and_meta_unchanged_after_import=True,player_built=False,XAPK=False,
                editor_report=dict(matchedObjects=42,checks=154,mismatches=0,sceneOpened=True,
                                   sceneGuidMatched=True,mismatchCategories=[]))

class ExactEditorControls(unittest.TestCase):
    def test_stage(self): self.assertTrue(a.validate_stage(stage()))
    def test_scene_drift(self):
        x=stage();x["scene_sha256"]="0"*64
        with self.assertRaises(Rejected):a.validate_stage(x)
    def test_meta_drift(self):
        x=stage();x["scene_meta_sha256"]="0"*64
        with self.assertRaises(Rejected):a.validate_stage(x)
    def test_extra_asset(self):
        x=stage();x["other_original_assets_staged"]=1
        with self.assertRaises(Rejected):a.validate_stage(x)
    def test_source_export_proof(self):
        x=dict(status="PASS_SAME_EXPORT",source_export_mapping_proven=True,private_trace_mapping_matched=True,
               same_export_hierarchy_parity=True,mismatches={},scene_sha256=a.SOURCE_SHA,
               mapped_objects=42,selected_source_objects=42,checks={"authored":108})
        self.assertTrue(a.validate_same_export(x))
        x["checks"]["authored"]=107
        with self.assertRaises(Rejected):a.validate_same_export(x)
    def test_editor(self): self.assertTrue(a.validate_editor(editor()))
    def test_fewer_editor_checks(self):
        x=editor();x["editor_report"]["checks"]=153
        self.assertFalse(a.validate_editor(x))
    def test_wrong_guid(self):
        x=editor();x["editor_report"]["sceneGuidMatched"]=False
        self.assertFalse(a.validate_editor(x))
    def test_missing_object(self):
        x=editor();x["editor_report"]["matchedObjects"]=41
        self.assertFalse(a.validate_editor(x))
    def test_mismatch(self):
        x=editor();x["editor_report"]["mismatches"]=1
        self.assertFalse(a.validate_editor(x))
    def test_skipped_editor(self):
        x=editor();x["editor_step_outcome"]="skipped"
        self.assertFalse(a.validate_editor(x))
    def test_player(self):
        x=editor();x["player_built"]=True
        self.assertFalse(a.validate_editor(x))

if __name__=="__main__": unittest.main()
