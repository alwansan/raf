"""Source-free original smoke34 two-pair DXBC signature semantic contract tests.

All private synthetic names/registers and program bytes stay in test memory.
Never read or ship original Raft programs in unit tests.
"""
import json
import unittest

from scripts import t3_original_smoke34_dxbc_semantic_join as t3


PRIVATE = "PRIVATE_SYNTHETIC_SEMANTIC_NEVER_PUBLISH"


def row(semantic, reg=0, mask=15, system_value=0):
    return {
        "semantic": semantic, "index": 0, "system_value": system_value,
        "type": 3, "register": reg, "mask": mask, "used_mask": mask,
        "stream": 0,
    }


def reader(code):
    is_vertex = code.startswith(b"PRIVATE_VERTEX")
    if is_vertex:
        return {
            "input": [row("PRIVATE_SOURCE_POSITION", 0)],
            "output": [row(PRIVATE, 1)],
            "input_tag": "ISGN", "output_tag": "OSGN",
        }
    if code.startswith(b"PRIVATE_FRAGMENT"):
        return {
            "input": [row(PRIVATE, 1)],
            "output": [row("PRIVATE_TARGET", 0)],
            "input_tag": "ISGN", "output_tag": "OSGN",
        }
    raise ValueError("untrusted_synthetic_stage")


def pair():
    return [(b"PRIVATE_VERTEX_" + bytes((i,)),
             b"PRIVATE_FRAGMENT_" + bytes((i,))) for i in (0, 1)]


class Smoke34SourceDXBCSemanticJoin(unittest.TestCase):
    def run_safe(self, pairs=None, **kwargs):
        return t3.classify_two_pairs(pair() if pairs is None else pairs,
                                     reader=kwargs.get("reader", reader),
                                     comparer=kwargs.get("comparer",
                                                        t3.signatures.compare_original_vf))

    def test_private_original_two_pair_source_semantics_match(self):
        result = self.run_safe()
        self.assertEqual(result["status"], t3.STATUS)
        self.assertEqual(result["exact_original_keyword_vertex_fragment_pairs"], 2)
        self.assertEqual(result["counts"]["original_programs_read"], 4)
        self.assertEqual(result["counts"]["original_matched_semantic_records"], 2)
        self.assertEqual(result["counts"]["original_unmatched_fragment_semantic_records"], 0)
        self.assertEqual(result["counts"]["original_matched_semantic_missing_output_component_lanes"], 0)
        self.assertEqual(result["counts"]["original_matched_semantic_type_mismatches"], 0)
        self.assertFalse(result["source_original_DXBC_to_SPIRV_location_semantic_map_proven"])
        self.assertFalse(result["Android_Raft_device_pixel_fix_verified"])

    def test_private_semantic_names_and_code_do_not_escape(self):
        output = json.dumps(self.run_safe(), sort_keys=True)
        self.assertNotIn(PRIVATE, output)
        self.assertNotIn("PRIVATE_VERTEX", output)
        self.assertNotIn("PRIVATE_FRAGMENT", output)
        self.assertNotIn("PRIVATE_TARGET", output)
        self.assertNotIn("PRIVATE_SOURCE_POSITION", output)
        self.assertNotIn('"register":', output)

    def test_missing_extra_or_invalid_original_pairs_refused(self):
        for samples in (pair()[:1], pair() + [pair()[0]],
                        [pair()[0], (b"", b"PRIVATE_FRAGMENT_0")],
                        [pair()[0], (True, b"PRIVATE_FRAGMENT_0")],
                        [pair()[0], [b"PRIVATE_VERTEX_1", b"PRIVATE_FRAGMENT_1"]]):
            with self.subTest(samples=str(type(samples))), self.assertRaisesRegex(
                    ValueError, "changed_original_smoke34_two_keyword_pairs"):
                self.run_safe(samples)

    def test_unknown_original_private_stage_refused(self):
        with self.assertRaisesRegex(ValueError, "untrusted_synthetic_stage"):
            self.run_safe([(b"PRIVATE_VERTEX_0", b"NOT_A_FRAGMENT"),
                           (b"PRIVATE_VERTEX_1", b"PRIVATE_FRAGMENT_1")])

    def test_original_semantic_mismatch_is_measured_not_falsely_matched(self):
        def mismatch(code):
            data = reader(code)
            if code.startswith(b"PRIVATE_FRAGMENT"):
                data["input"][0]["semantic"] = "ORIGINAL_OTHER_SEMANTIC"
            return data
        result = self.run_safe(reader=mismatch)
        self.assertEqual(result["counts"]["original_unmatched_fragment_semantic_records"], 2)
        self.assertEqual(result["counts"]["original_matched_semantic_records"], 0)
        self.assertFalse(result["source_original_DXBC_to_SPIRV_location_semantic_map_proven"])

    def test_changed_component_mask_detected_without_semantic_leakage(self):
        def masked(code):
            data = reader(code)
            if code.startswith(b"PRIVATE_VERTEX"):
                data["output"][0]["mask"] = 3
            return data
        result = self.run_safe(reader=masked)
        self.assertEqual(result["counts"]["original_matched_semantic_missing_output_component_lanes"], 4)
        self.assertNotIn(PRIVATE, json.dumps(result))

    def test_untrusted_comparator_secret_key_is_refused(self):
        def leak(a, b):
            output = t3.signatures.compare_original_vf(a, b)
            output["PRIVATE_SEMANTIC"] = "LEAK"
            return output
        with self.assertRaisesRegex(ValueError, "untrusted_original_smoke34_semantic_aggregate_shape"):
            self.run_safe(comparer=leak)

    def test_boolean_negative_or_big_comparator_counter_refused(self):
        for invalid in (True, -1, 999999):
            def unsafe(a, b):
                result = t3.signatures.compare_original_vf(a, b)
                result["original_input_records"] = invalid
                return result
            with self.subTest(invalid=invalid), self.assertRaisesRegex(
                    ValueError, "untrusted_original_smoke34_semantic_aggregate_counter"):
                self.run_safe(comparer=unsafe)

    def test_incomplete_original_program_count_refused(self):
        def malicious(a, b):
            result = t3.signatures.compare_original_vf(a, b)
            result["original_programs_read"] = 1
            return result
        with self.assertRaisesRegex(ValueError, "smoke34_incomplete_original_signature_stage_pairs"):
            self.run_safe(comparer=malicious)

    def test_unsafe_source_signature_schema_not_downgraded(self):
        def bad_reader(code):
            data = reader(code)
            if code.startswith(b"PRIVATE_FRAGMENT"):
                data["input"][0]["mask"] = True
            return data
        with self.assertRaises((ValueError, TypeError)):
            self.run_safe(reader=bad_reader)


if __name__ == "__main__":
    unittest.main()
