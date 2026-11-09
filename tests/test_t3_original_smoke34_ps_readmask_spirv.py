"""T3 source-free guards for authentic smoke34 original DXBC PS ReadMask lanes.

Synthetic names/code intentionally never escape the public aggregate report.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_smoke34_ps_readmask_spirv as t3

SECRET = "SECRET_ORIGINAL_PRIVATE_DXBC_SEMANTIC_NEVER_LEAK"
CODE = b"SECRET_PRIVATE_SYNTHETIC_DXBC_NEVER_PUBLISH"


def source_row(index, *, mask=15, used=3, semantic=None):
    return {
        "semantic": semantic or (SECRET + str(index)), "index": 0,
        "system_value": 0, "type": 3, "register": index,
        "mask": mask, "used_mask": used, "stream": 0,
    }


def parser(code):
    stage, pair_no = code.rsplit(b"_", 2)[-2:]
    n = 3 if pair_no == b"0" else 4
    if stage not in (b"VS", b"FS") or pair_no not in (b"0", b"1"):
        raise ValueError("invalid_private_synthetic_stage")
    rows = [source_row(i) for i in range(n)]
    if stage == b"VS":
        return {"input_tag": "ISGN", "output_tag": "OSGN",
                "input": [], "output": rows}
    return {"input_tag": "ISGN", "output_tag": "OSGN",
            "input": rows, "output": []}


def pairs():
    return [
        (CODE + b"_VS_0", CODE + b"_FS_0"),
        (CODE + b"_VS_1", CODE + b"_FS_1"),
    ]


def translator(_code, stage, root):
    assert stage == 0 and root.is_dir()
    return {"stage": stage, "vulkan11_valid": True,
            "hlsl_recovered": True, "roundtrip_vulkan11_valid": True,
            "SECRET_DEBUG": SECRET}


def reflect(path):
    source_index = int(path.parent.name.split("-")[2])
    vecs = ["vec4", "vec2"] if source_index == 0 else ["vec4", "vec4"]
    return {"inputs": [{"location": i, "type": typ}
                       for i, typ in enumerate(vecs)],
            "outputs": [], "resource_slots": {}}


class Smoke34RealStageReadMaskControls(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="t3-smoke34-sourcefree-private-")
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)

    def evaluate(self, **kwargs):
        return t3.evaluate(kwargs.get("pairs", pairs()), self.root,
                           translator=kwargs.get("translator", translator),
                           reflector=kwargs.get("reflector", reflect),
                           parser=kwargs.get("parser", parser),
                           checker=kwargs.get("checker", t3.dxbc.compare_original_vf),
                           mask_reader=kwargs.get(
                               "mask_reader", t3.inherited.private_fragment_readmask),
                           spv_counter=kwargs.get(
                               "spv_counter", t3.checked_private_reflection))

    def test_both_exact_source_pairs_match_spirv_lane_cardinality(self):
        result = self.evaluate()
        c = result["counts"]
        self.assertEqual(result["status"], t3.STATUS)
        self.assertEqual(c["passes_examined"], 2)
        self.assertEqual(c["source_ps_user_semantic_records"], 7)
        self.assertEqual(c["source_ps_declared_component_lanes"], 28)
        self.assertEqual(c["source_ps_read_component_lanes"], 14)
        self.assertEqual(c["source_ps_declared_but_unread_component_lanes"], 14)
        self.assertEqual(c["source_spirv_fragment_input_records"], 4)
        self.assertEqual(c["source_spirv_fragment_input_component_lanes"], 14)
        self.assertEqual(c["roundtrip_spirv_fragment_input_component_lanes"], 14)
        self.assertEqual(c["passes_readmask_equals_source_spirv_input_lane_count"], 2)
        self.assertEqual(c["passes_readmask_equals_roundtrip_spirv_input_lane_count"], 2)
        self.assertFalse(result["DXBC_semantic_to_SPIRV_Location_Component_mapping_verified"])
        self.assertFalse(result["Unity_Android_Adreno_device_smoke_verified"])

    def test_unequal_roundtrip_lane_count_reports_delta_not_faked_success(self):
        def altered(path):
            row = reflect(path)
            if path.name == "roundtrip.spv":
                row["inputs"].append({"location": 5, "type": "vec2"})
            return row
        c = self.evaluate(reflector=altered)["counts"]
        self.assertEqual(c["passes_readmask_equals_source_spirv_input_lane_count"], 2)
        self.assertEqual(c["passes_readmask_equals_roundtrip_spirv_input_lane_count"], 0)
        self.assertEqual(c["passes_source_spirv_equals_roundtrip_spirv_input_lane_count"], 0)
        self.assertEqual(c["roundtrip_to_spirv_absolute_component_lane_count_difference"], 4)

    def test_source_incorrect_lane_count_records_gap(self):
        def changed(path):
            row = reflect(path)
            if path.name == "original.spv":
                row["inputs"] = row["inputs"][:1]
            return row
        c = self.evaluate(reflector=changed)["counts"]
        self.assertEqual(c["passes_readmask_equals_source_spirv_input_lane_count"], 1)
        self.assertEqual(c["passes_readmask_equals_roundtrip_spirv_input_lane_count"], 2)
        self.assertEqual(c["source_to_spirv_absolute_component_lane_count_difference"], 2)

    def test_reject_wrong_original_two_pair_scope_and_fake_stage(self):
        for invalid in ([pairs()[0]], pairs() + [pairs()[0]],
                        [(CODE + b"_VS_0", b""), pairs()[1]],
                        [[*pairs()[0]], pairs()[1]]):
            with self.subTest(invalid=str(type(invalid))), self.assertRaisesRegex(
                    ValueError, "invalid_original_two_pair_readmask_scope"):
                self.evaluate(pairs=invalid)

    def test_missing_or_untrusted_original_semantics_fail_closed(self):
        def bad_parser(code):
            data = parser(code)
            if code.endswith(b"FS_0"):
                data["input"][0]["semantic"] = "OTHER_PRIVATE_NAME"
            return data
        with self.assertRaisesRegex(ValueError, "original_DXBC_VS_FS_semantic_baseline_changed"):
            self.evaluate(parser=bad_parser)

    def test_original_stage_code_must_not_be_swapped_for_vertex(self):
        with self.assertRaisesRegex(ValueError, "nonoriginal_DXBC_signature_tags"):
            def wrong_tag(code):
                data = parser(code)
                if code.endswith(b"FS_0"):
                    data["input_tag"] = "OSGN"
                return data
            self.evaluate(parser=wrong_tag)

    def test_translator_flags_must_be_real_all_three(self):
        def partial(code, stage, root):
            row = translator(code, stage, root)
            row["hlsl_recovered"] = False
            return row
        with self.assertRaisesRegex(ValueError, "incomplete_private_DXBC_PS_SPV_roundtrip"):
            self.evaluate(translator=partial)

    def test_duplicate_private_spirv_location_refused(self):
        def duplicate(path):
            row = reflect(path)
            row["inputs"].append(dict(row["inputs"][0]))
            return row
        with self.assertRaisesRegex(ValueError, "duplicate_SPIRV_input_location"):
            self.evaluate(reflector=duplicate)

    def test_unsupported_private_spirv_input_type_refused(self):
        def unsupported(path):
            row = reflect(path)
            row["inputs"][0]["type"] = "mat4"
            return row
        with self.assertRaisesRegex(ValueError, "unsupported_SPIRV_fragment_input_type"):
            self.evaluate(reflector=unsupported)

    def test_untrusted_named_reflection_record_refused(self):
        def named(path):
            row = reflect(path)
            row["inputs"][0]["secret"] = SECRET
            return row
        with self.assertRaisesRegex(ValueError, "invalid_or_duplicate_SPIRV_input_location"):
            self.evaluate(reflector=named)

    def test_readmask_counter_schema_secrets_and_boolean_refused(self):
        def leaking(_records):
            row = t3.inherited.private_fragment_readmask(parser(CODE + b"_FS_0")["input"])
            row[SECRET] = "PRIVATE_LEAK"
            return row
        with self.assertRaisesRegex(ValueError, "private_DXBC_readmask_disagrees"):
            self.evaluate(mask_reader=leaking)
        def bool_count(records):
            row = t3.inherited.private_fragment_readmask(records)
            row["source_ps_read_component_lanes"] = True
            return row
        with self.assertRaisesRegex(ValueError, "private_DXBC_readmask_disagrees"):
            self.evaluate(mask_reader=bool_count)

    def test_untrusted_spv_lane_report_rejected(self):
        def fake_counter(_raw):
            return {"records": 2, "lanes": True}
        with self.assertRaisesRegex(ValueError, "untrusted_private_SPIRV_input_lane_counts"):
            self.evaluate(spv_counter=fake_counter)

    def test_readmask_with_unread_channels_only_counts_used(self):
        def no_reads(_rows):
            row = t3.inherited.private_fragment_readmask(parser(CODE + b"_FS_0")["input"])
            row["source_ps_read_component_lanes"] = 0
            row["source_ps_declared_but_unread_component_lanes"] = 12
            return row
        # Source pair count 3 vs 4 still checked; this synthetic mismatch
        # requires retaining only correct 7 record source baseline.
        with self.assertRaisesRegex(ValueError, "private_DXBC_readmask_disagrees"):
            def invalid(_rows):
                row = no_reads(_rows)
                row["source_ps_read_component_lanes"] = 24
                return row
            self.evaluate(mask_reader=invalid)

    def test_private_names_dxbc_and_locations_never_escape_report(self):
        output = json.dumps(self.evaluate(), sort_keys=True)
        for private in (SECRET, CODE.decode(), "PRIVATE_DEBUG",
                        '"location":', '"semantic":', '"register":'):
            self.assertNotIn(private, output)
        self.assertTrue(all(type(v) is int for v in
                            self.evaluate_isolated()["counts"].values()))

    def evaluate_isolated(self):
        # A new temporary directory prevents reusing private-stage filenames.
        with tempfile.TemporaryDirectory() as td:
            return t3.evaluate(pairs(), Path(td), translator=translator,
                               reflector=reflect, parser=parser)


if __name__ == "__main__":
    unittest.main()
