"""Synthetic source identity and GUID integrity tests for full-export dummy ranking."""
from collections import Counter
import unittest

from scripts.gt_rank_full_export_dummy_shader_sources import (
    STATUS, compare_exact_sources, select_dummy_export_sources,
)


def fixture():
    guids=["a"*32,"b"*32,"c"*32]
    profiles={
        guids[0]:{"dummy":True,"identity":"Original/ShaderA"},
        guids[1]:{"dummy":True,"identity":"Original/ShaderB"},
        guids[2]:{"dummy":False,"identity":"Original/Other"},
    }
    rows=[]
    names={}
    for i,guid in enumerate(guids,1):
        key=("resources.assets",i)
        rows.append({"class_id":48,
                     "source":{"owner":"Raft_Data/resources.assets","path_id":i},
                     "export":{"file_id":4800000,"guid":guid,"type":3}})
        names[key]=profiles[guid]["identity"]
    refs=Counter({
        (4800000,guids[0],"3"):10,
        (4800000,guids[1],"3"):5,
        (4800000,guids[2],"3"):2,
    })
    return {"schema_version":1,"export_instance":"f"*32,"objects":rows}, profiles, refs, names


class FullOriginalShaderSourceGuidsTests(unittest.TestCase):
    def test_verified_guid_and_name_join_ranks_true_originals(self):
        trace,profiles,refs,names=fixture()
        wanted,mapping=select_dummy_export_sources(trace,profiles,refs)
        self.assertEqual(len(wanted),2)
        self.assertEqual(len(mapping),2)
        private,safe=compare_exact_sources(
            profiles,refs,mapping,names,
            expected_material_documents=15,
            original_scene_weights={("resources.assets",1):921,("resources.assets",2):34})
        self.assertEqual(safe["status"],STATUS)
        self.assertEqual(safe["original_source_to_same_export_GUID_matched_dummy_Material_documents"],15)
        self.assertEqual(safe["actual_source_verified_Shader48_dummy_targets_ranked_by_Material_links"],[10,5])
        self.assertEqual(safe["actual_source_verified_Shader48_dummy_targets_corresponding_scene_renderer_slots"],[921,34])
        self.assertEqual(len(private),2)
        self.assertNotIn("resources.assets",str(safe))
        self.assertNotIn("Original/Shader",str(safe))
        self.assertNotIn("aaaa",str(safe))
        self.assertFalse(safe["APK_OBB_XAPK_created"])

    def test_original_mismatched_name_never_accepted_as_exact_guid(self):
        trace,profiles,refs,names=fixture()
        names[("resources.assets",2)]="WrongOriginalShader"
        _,mapping=select_dummy_export_sources(trace,profiles,refs)
        _,safe=compare_exact_sources(profiles,refs,mapping,names,expected_material_documents=15)
        self.assertEqual(safe["original_source_to_same_export_GUID_matched_dummy_Material_documents"],10)
        self.assertEqual(safe["remaining_dummy_Material_documents_without_complete_original_Shader48_GUID_join"],5)
        self.assertEqual(safe["remaining_original_export_Shader_identity_mismatch_targets"],1)

    def test_duplicate_source_trace_and_material_population_drift_blocked(self):
        trace,profiles,refs,names=fixture()
        trace["objects"].append(trace["objects"][0])
        with self.assertRaisesRegex(ValueError,"duplicate_original_Shader48"):
            select_dummy_export_sources(trace,profiles,refs)
        trace["objects"].pop()
        _,mapping=select_dummy_export_sources(trace,profiles,refs)
        with self.assertRaisesRegex(ValueError,"wrong_same_export_remaining_Dummy_Material_population"):
            compare_exact_sources(profiles,refs,mapping,names,expected_material_documents=16)


if __name__=="__main__":
    unittest.main()
