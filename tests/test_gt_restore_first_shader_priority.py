"""GT restore-first high-impact original source Shader queue; synthetic no game data."""
from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_renderer_shader_impact as original
from scripts import t3_source_renderer_shader_to_postvendor_export as joined
from scripts.gt_restore_first_shader_priority import (
    STATUS, _strict_destination, rank_original_shader_queue
)


def synthetic():
    counts=[921]+[28]*15+[32]+[219,34,3]+[4]
    assert len(counts)==21 and sum(counts)==1633
    source_use={}
    rows=[]
    profiles={}
    builtins=sorted(joined.VALID_BUILTIN_GUIDS)
    assert builtins
    for i,count in enumerate(counts,1):
        key=("resources.assets",i)
        source_use[key]=count
        if i in (18,19,20):
            guid=builtins[0]
            fid=4800000
            kind=0
        else:
            guid=f"{i:032x}"
            fid=4800000
            kind=3
            profiles[guid]={
                "dummy":i!=21,"unbalanced":False,"programmed":0 if i!=21 else 4,
                "partial_subshader_coverage":False,
            }
        rows.append({
            "class_id":48,
            "source":{"owner":"Raft_Data/resources.assets","path_id":i},
            "export":{"file_id":fid,"guid":guid,"type":kind},
        })
    return source_use, {
        "export_instance":"f"*32, "objects":rows
    }, profiles, {
        "status":original.STATUS,
        "six_original_scenes_sha_verified":True,
        "counts":{"original_slots_to_verified_Shader48":1633},
        "original_nonnull_renderer_material_slots":1635,
    }


class RestoreFirstShaderQueueTests(unittest.TestCase):
    def test_rank_source_original_921_and_dummies_before_non_dummy(self):
        use,trace,profiles,source=synthetic()
        private,safe=rank_original_shader_queue(use,trace,profiles,source)
        self.assertEqual(len(private),21)
        self.assertEqual(len([r for r in private if r["program_status"]=="dummy"]),17)
        self.assertEqual(safe["status"],STATUS)
        self.assertEqual(safe["highest_priority_dummy_original_renderer_slots"],921)
        self.assertEqual(safe["still_dummy_original_renderer_material_slots"],1373)
        self.assertEqual(safe["still_dummy_distinct_original_Shader48_targets"],17)
        self.assertEqual(safe["same_instance_original_source_count"],21)
        self.assertEqual(safe["original_typed_renderer_material_slots"],1633)
        self.assertEqual(private[0]["program_status"],"dummy")
        self.assertEqual(private[0]["original_scene_renderer_material_slots"],921)
        self.assertTrue(safe["source_original_6_scene_sha_authenticated"])
        self.assertTrue(safe["source_original_DXBC_to_complete_ShaderLab_restored_by_queue"] is False)
        self.assertFalse(safe["Unity_Editor_Android_or_Adreno_pixels_verified"])
        for private_only in (
            "original_owner","original_shader_path_id","exported_Shader_GUID",
            "private_exported_relative_shader_path"):
            self.assertNotIn(private_only,safe)
        self.assertNotIn("resources.assets",str(safe))
        self.assertNotIn("00000000000000000000000000000001",str(safe))

    def test_original_trace_identity_collision_rejected(self):
        use,trace,profiles,source=synthetic()
        trace["objects"][1]["export"]["guid"] = trace["objects"][0]["export"]["guid"]
        with self.assertRaisesRegex(ValueError,"collide_export_GUID"):
            rank_original_shader_queue(use,trace,profiles,source)

    def test_original_trace_missing_source_object_rejected(self):
        use,trace,profiles,source=synthetic()
        trace["objects"].pop()
        with self.assertRaisesRegex(ValueError,"missing_original_to_actual_Shader48"):
            rank_original_shader_queue(use,trace,profiles,source)

    def test_original_slot_fanout_drift_rejected(self):
        use,trace,profiles,source=synthetic()
        use[("resources.assets",1)]=920
        with self.assertRaises(ValueError):
            rank_original_shader_queue(use,trace,profiles,source)

    def test_source_sha_omitted_cannot_pass_even_for_matching_counts(self):
        use,trace,profiles,source=synthetic()
        source["six_original_scenes_sha_verified"]=False
        with self.assertRaisesRegex(ValueError,"source_SHA_not_verified"):
            rank_original_shader_queue(use,trace,profiles,source)

    def test_private_queue_cannot_be_written_under_source_or_project_or_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"zip2"/"Raft_Data";source.mkdir(parents=True)
            project=root/"project";project.mkdir()
            with self.assertRaisesRegex(ValueError,"unsafe_GT_priority_report_destination"):
                _strict_destination(source/"leak.json",root/"zip2",project)
            with self.assertRaisesRegex(ValueError,"unsafe_GT_priority_report_destination"):
                _strict_destination(project/"leak.json",root/"zip2",project)
            outside=root/"private.json"
            self.assertEqual(_strict_destination(outside,root/"zip2",project),outside)
            outside.write_text("already-created")
            with self.assertRaisesRegex(ValueError,"unsafe_GT_priority_report_destination"):
                _strict_destination(outside,root/"zip2",project)
            unsafe=root/"link"
            unsafe.symlink_to(project, target_is_directory=True)
            with self.assertRaisesRegex(ValueError,"unsafe_GT_priority_report_destination"):
                _strict_destination(unsafe/"leak.json",root/"zip2",project)


if __name__=="__main__":
    unittest.main()
