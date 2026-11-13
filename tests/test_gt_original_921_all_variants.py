"""GT 921 authentic source 33+8 full variant recovery, synthetic-only safety gates."""
import json
from pathlib import Path
import tempfile
import unittest
from scripts.gt_original_921_all_variants import (
    enumerate_all, stage_private, source_keyword_profile, _private_destination, PAIRED_COUNT,
    ORPHAN_VERTEX_COUNT, DISTINCT_DXBC_COUNT,
)

def fixture():
    n_by_pass=[9,9,8,7]
    passes=[]
    for p,n in enumerate(n_by_pass):
        offset=sum(n_by_pass[:p])
        def records(stage, count):
            return [{"bucket":0,"key":(p,i),"stage":stage,
                     "payload":("vs-" if stage==1 else "fs-")+str((offset+i)%29)}
                    for i in range(count)]
        passes.append({
            "m_Type":0,"m_State":{"original_pass":p},"m_NameIndices":[0],
            "progVertex":{"variants":records(1,n+2)},
            "progFragment":{"variants":records(0,n)},
        })
    return {"m_SubShaders":[{"m_Passes":passes}]}

def variants(program):
    return [(v["bucket"],i,v) for i,v in enumerate(program["variants"])]

def key(metadata):
    return metadata["key"]

def link(metadata,table,stage):
    if stage!=metadata["stage"]:raise ValueError("incorrect original stage")
    return metadata["payload"].encode(),{"source_original_record":42}

class Original921VariantTests(unittest.TestCase):
    def collect(self,tree=None):
        return enumerate_all(tree if tree is not None else fixture(),[object()],
                             variants=variants,permutation=key,linker=link)

    def test_complete_four_pass_33_pairs_eight_unmatched_58_unique(self):
        paired,orphans,passes,unique=self.collect()
        self.assertEqual(len(paired),PAIRED_COUNT)
        self.assertEqual(len(orphans),ORPHAN_VERTEX_COUNT)
        self.assertEqual(len(unique),DISTINCT_DXBC_COUNT)
        self.assertEqual([p["matched_pairs"] for p in passes],[9,9,8,7])
        self.assertEqual([p["unmatched_vertex"] for p in passes],[2,2,2,2])
        self.assertTrue(all(o["stage"]==1 for o in orphans))

    def test_original_keyword_index_census_is_safe_not_premature_pragma_proof(self):
        paired,orphans,passes,unique=self.collect()
        original=fixture()
        original["m_KeywordNames"]=["INTERNAL_0","INTERNAL_1"]
        original["m_KeywordFlags"]=[0,1]
        original["m_PropInfo"]={"m_Props":[{"m_Name":"PRIVATE_PROP"}]}
        paired[0]["vs"]["original_variant_metadata"]["m_KeywordIndices"]=[0]
        paired[0]["fs"]["original_variant_metadata"]["m_KeywordIndices"]=[0]
        result=source_keyword_profile(paired,orphans,original)
        self.assertEqual(result["original_keyword_names"],2)
        self.assertEqual(result["original_property_definitions"],1)
        self.assertEqual(result["all_source_variant_metadata_stages_censused"],74)
        self.assertEqual(result["source_original_unique_used_keyword_indices"],1)
        self.assertTrue(result["original_keyword_indices_within_name_table"])
        self.assertFalse(result["original_global_local_pragma_flags_and_compilation_selection_proven"])
        self.assertNotIn("INTERNAL_0",str(result))
        self.assertNotIn("PRIVATE_PROP",str(result))
        paired[0]["vs"]["original_variant_metadata"]["m_GlobalKeywordIndices"]=[50]
        self.assertFalse(source_keyword_profile(paired,orphans,original)["original_keyword_indices_within_name_table"])
        paired[0]["vs"]["original_variant_metadata"]["m_KeywordIndices"]=[-1]
        with self.assertRaisesRegex(ValueError,"unsupported_original_keyword"):
            source_keyword_profile(paired,orphans,original)


    def test_original_private_stage_all_programs_and_no_public_id_leak(self):
        paired,orphans,passes,unique=self.collect()
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"private"
            def translator(code,stage,target):
                (target/"private.hlsl").write_text("private-921-stage")
                return {"vulkan11_valid":True,"hlsl_recovered":True,
                        "roundtrip_vulkan11_valid":True}
            safe=stage_private(paired,orphans,passes,unique,root,translator=translator,source_parsed=fixture())
            packet=json.loads((root/"original-private-variant-manifest.json").read_text())
            self.assertEqual(len(packet["paired"]),33)
            self.assertEqual(len(packet["original_shader_ParsedForm_full_private"]["m_SubShaders"][0]["m_Passes"]),4)
            self.assertTrue(safe["source_original_Shader_ParsedForm_pass_states_keyword_property_tables_preserved_privately"])
            self.assertEqual(len(packet["unpaired"]),8)
            self.assertEqual(len(list(root.glob("program-*"))),58)
            self.assertEqual(safe["private_HLSL_roundtrip_vulkan11_valid_stages"],58)
            self.assertTrue(safe["all_distinct_original_D3D11_programs_translated"])
            self.assertFalse(safe["original_project_Shader_GUID_replaced"])
            self.assertNotIn("private-921-stage",str(safe))
            self.assertNotIn("vs-0",str(safe))

    def test_partial_stage_not_claimed_complete(self):
        p,o,s,u=self.collect()
        with tempfile.TemporaryDirectory() as d:
            def translator(code,stage,target):
                ok=code!=b"vs-0"
                return {"vulkan11_valid":ok,"hlsl_recovered":ok,
                        "roundtrip_vulkan11_valid":ok}
            safe=stage_private(p,o,s,u,Path(d)/"private",translator=translator,source_parsed=fixture())
            self.assertFalse(safe["all_distinct_original_D3D11_programs_translated"])
            self.assertLess(safe["private_HLSL_roundtrip_vulkan11_valid_stages"],58)

    def test_empty_entire_fragment_pass_is_rejected(self):
        tree=fixture()
        tree["m_SubShaders"][0]["m_Passes"][0]["progFragment"]["variants"]=[]
        with self.assertRaises(ValueError):self.collect(tree)

    def test_player_bucket_mismatch_does_not_fallback_to_ordinal(self):
        tree=fixture()
        tree["m_SubShaders"][0]["m_Passes"][0]["progFragment"]["variants"][0]["bucket"]=1
        with self.assertRaisesRegex(ValueError,"population_drift"):self.collect(tree)

    def test_duplicate_exact_keyword_variant_rejected(self):
        tree=fixture()
        v=tree["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["variants"]
        v[1]["key"]=v[0]["key"]
        with self.assertRaisesRegex(ValueError,"duplicate_original"):self.collect(tree)

    def test_private_destination_cannot_escape_via_symlink_or_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);src=root/"source";src.mkdir()
            public=root/"safe.json"
            with self.assertRaises(ValueError):
                _private_destination(src/"leak",src,public)
            (root/"alias").symlink_to(src,target_is_directory=True)
            with self.assertRaises(ValueError):
                _private_destination(root/"alias"/"leak",src,public)

if __name__=="__main__":
    unittest.main()
