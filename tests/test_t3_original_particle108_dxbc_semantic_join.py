"""Synthetic guards for genuine Particle108 authored DXBC semantic joins.

All semantic strings here are synthetic; real signature registers and names
stay private in CI and are never published.
"""
import json
import unittest

from scripts import t3_original_particle108_dxbc_semantic_join as t3
from scripts.t3_original_921_dxbc_semantic_join import compare_original_vf


PAIRS=[(b"synthetic-original-vs-"+bytes([i]),
        b"synthetic-original-fs-"+bytes([i])) for i in range(4)]


def row(name,register=0,mask=15,component=3,system=0):
    return {"semantic":name,"index":0,"system_value":system,
            "type":component,"register":register,"mask":mask,
            "used_mask":mask,"stream":0}


def source_signatures(code):
    if code.startswith(b"synthetic-original-vs-"):
        return {
            "input":[row("PRIVATE_VERTEX_POSITION",0)],
            "output":[row("PRIVATE_ORIGINAL_TEXCOORD",0,15),
                      row("PRIVATE_SYSTEM_POSITION",0xffffffff,15,3,1)],
            "input_tag":"ISGN","output_tag":"OSGN"
        }
    if code.startswith(b"synthetic-original-fs-"):
        return {
            "input":[row("PRIVATE_ORIGINAL_TEXCOORD",1,15)],
            "output":[row("PRIVATE_COLOR_TARGET",0,15,3,1)],
            "input_tag":"ISGN","output_tag":"OSGN"
        }
    raise ValueError("not_synthetic_source_stage")


class Particle108AuthenticSemantics(unittest.TestCase):
    def test_four_original_compiled_pairs_semantic_masks_match_without_leaking_names(self):
        result=t3.classify_pairs(PAIRS,reader=source_signatures)
        counts=result["counts"]
        self.assertEqual(result["status"],t3.STATUS)
        self.assertEqual(result["original_exact_VSFS_keyword_pairs"],4)
        self.assertEqual(counts["original_programs_read"],8)
        self.assertEqual(counts["original_matched_semantic_records"],4)
        self.assertEqual(counts["original_unmatched_fragment_semantic_records"],0)
        self.assertEqual(counts["original_matched_semantic_missing_output_component_lanes"],0)
        self.assertEqual(counts["original_matched_semantic_type_mismatches"],0)
        self.assertEqual(counts["source_pairs_with_complete_user_VSFS_semantic_mask_type_link"],4)
        self.assertFalse(result["original_semantic_to_SPIRV_Location_or_HLSL_mapping_verified"])
        self.assertFalse(result["native_Unity_Android_Adreno_pixels_verified"])
        payload=json.dumps(result,sort_keys=True)
        for secret in ("PRIVATE_ORIGINAL_TEXCOORD","PRIVATE_SYSTEM_POSITION","synthetic-original"):
            self.assertNotIn(secret,payload)

    def test_missing_original_fragment_semantic_record_is_counted_not_matched(self):
        def missing(code):
            p=source_signatures(code)
            if code.startswith(b"synthetic-original-fs-"):
                p["input"][0]["semantic"]="PRIVATE_UNRELATED_FS_INPUT"
            return p
        result=t3.classify_pairs(PAIRS,reader=missing)
        counts=result["counts"]
        self.assertEqual(counts["original_unmatched_fragment_semantic_records"],4)
        self.assertEqual(counts["source_pairs_with_complete_user_VSFS_semantic_mask_type_link"],0)
        self.assertEqual(counts["source_pairs_with_unmatched_fragment_semantics"],4)

    def test_mask_and_component_type_shortfall_are_not_silently_accepted(self):
        def drift(code):
            p=source_signatures(code)
            if code.startswith(b"synthetic-original-fs-"):
                p["input"][0]["mask"]=15
                p["input"][0]["type"]=1
            else:
                p["output"][0]["mask"]=3
            return p
        result=t3.classify_pairs(PAIRS,reader=drift)
        c=result["counts"]
        self.assertEqual(c["original_matched_semantic_missing_output_component_lanes"],8)
        self.assertEqual(c["original_matched_semantic_type_mismatches"],4)
        self.assertEqual(c["source_pairs_with_complete_user_VSFS_semantic_mask_type_link"],0)
        self.assertEqual(c["source_pairs_with_component_mask_shortfalls"],4)
        self.assertEqual(c["source_pairs_with_component_type_mismatch"],4)

    def test_private_comparison_cannot_inject_source_semantics_or_unknown_counts(self):
        def bad_join(v,f):
            d=compare_original_vf(v,f)
            d["PRIVATE_SOURCE_SHADER_SEMANTIC"]="never_publish"
            return d
        with self.assertRaisesRegex(ValueError,"semantic_join_aggregate"):
            t3.classify_pairs(PAIRS,reader=source_signatures,join=bad_join)
        def bad_bool(v,f):
            d=compare_original_vf(v,f)
            d["original_matched_semantic_records"]=True
            return d
        with self.assertRaisesRegex(ValueError,"semantic_counter"):
            t3.classify_pairs(PAIRS,reader=source_signatures,join=bad_bool)

    def test_ambiguous_or_unsupported_original_DXBC_signature_fails_closed(self):
        def unsupported(_):
            raise ValueError("unsupported_original_signature_stream_or_precision")
        with self.assertRaisesRegex(ValueError,"unsupported_original_signature"):
            t3.classify_pairs(PAIRS,reader=unsupported)
        def duplicate_semantic(code):
            out=source_signatures(code)
            if code.startswith(b"synthetic-original-vs-"):
                out["output"].append(row("PRIVATE_ORIGINAL_TEXCOORD",0,15))
            return out
        with self.assertRaisesRegex(ValueError,"overlapping register components"):
            t3.classify_pairs(PAIRS,reader=duplicate_semantic)

    def test_four_pair_and_private_byte_scope_guards(self):
        with self.assertRaisesRegex(ValueError,"four_original_DXBC_pair_scope"):
            t3.classify_pairs(PAIRS[:3],reader=source_signatures)
        with self.assertRaisesRegex(ValueError,"four_original_DXBC_pair_scope"):
            t3.classify_pairs([PAIRS[0]]*3+[("notbytes",b"fs")],reader=source_signatures)
        with self.assertRaisesRegex(ValueError,"four_original_DXBC_pair_scope"):
            t3.classify_pairs([PAIRS[0]]*3+[(b"a"*(4*1024*1024+1),b"fs")],
                              reader=source_signatures)


if __name__=="__main__":
    unittest.main()
