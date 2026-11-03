"""A12 synthetic authenticated-layout tests; no original game resources or DXBC."""
from unittest import mock
import json
import unittest

from scripts import a12_probe_original_blur_passes as p


def stage(blob=1, *, keyword=(), parameter_index=0, params=True):
    metadata = {"m_BlobIndex": blob, "m_KeywordIndices": list(keyword),
                "m_ShaderHardwareTier": 0}
    return {"m_SubPrograms": [],
            "m_PlayerSubPrograms": [[metadata]],
            "m_ParameterBlobIndices": [[parameter_index]] if params else []}


def fixture(*, passes=2):
    row = {"m_Type": 0, "progVertex": stage(1), "progFragment": stage(2)}
    return {"m_Name": p.TARGET,
            "m_SubShaders": [{"m_Passes": [json.loads(json.dumps(row)) for _ in range(passes)]}]}


class BlurPassGraphTests(unittest.TestCase):
    def analyse(self, parsed=None, entries=None):
        with mock.patch.object(p, "linked_program", side_effect=lambda m, entries, s: (
            b"private-synthetic-dxbc-" + bytes([s, m["m_BlobIndex"]]), {"index": m["m_BlobIndex"]}
        )):
            return p.inspect_shader(parsed if parsed is not None else fixture(),
                                    entries if entries is not None else [object()] * 3)

    def test_two_real_pass_slots_with_paired_original_stage_permutation(self):
        d = self.analyse()
        self.assertEqual(d["original_pass_count"], 2)
        self.assertEqual(d["linked_stage_programs"], 4)
        self.assertEqual(d["paired_original_passes"], 2)
        self.assertEqual(d["single_variant_paired_passes"], 2)
        self.assertEqual(d["unpaired_original_passes"], 0)
        self.assertEqual(d["distinct_stage_programs"], 2)
        self.assertTrue(d["original_minimum_logged_passes_met"])
        self.assertFalse(d["shaderlab_wrapper_constructed"])
        self.assertFalse(d["water_or_fft_build_ready"])

    def test_rejects_unrelated_or_ambiguous_name(self):
        x = fixture()
        x["m_Name"] = "Synthetic/WrongWater"
        with self.assertRaisesRegex(ValueError, "identity"):
            self.analyse(x)

    def test_missing_original_subshaders_fail_closed(self):
        for x in ({}, {"m_Name": p.TARGET, "m_SubShaders": None},
                  {"m_Name": p.TARGET, "m_SubShaders": []}):
            with self.assertRaises(ValueError):
                self.analyse(x)

    def test_missing_or_bad_stage_metadata_fails(self):
        for field in ("progVertex", "progFragment"):
            x = fixture()
            del x["m_SubShaders"][0]["m_Passes"][0][field]
            with self.assertRaisesRegex(ValueError, "Missing original pass stage program"):
                self.analyse(x)

    def test_unpaired_original_permutations_cannot_be_counted_as_paired(self):
        x = fixture()
        x["m_SubShaders"][0]["m_Passes"][1]["progFragment"] = stage(2, keyword=("SYNTHETIC",))
        d = self.analyse(x)
        self.assertEqual(d["paired_original_passes"], 1)
        self.assertEqual(d["unpaired_original_passes"], 1)
        self.assertEqual(d["single_variant_paired_passes"], 1)
        self.assertEqual(d["stages_with_keyword_permutations"], 1)

    def test_invalid_parameter_layout_is_not_reported_as_recovered(self):
        x = fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["progVertex"] = stage(params=False)
        d = self.analyse(x)
        self.assertEqual(d["parameter_index_layout_unresolved"], 1)
        self.assertFalse(d["water_or_fft_build_ready"])

    def test_no_program_does_not_count_as_valid_pair(self):
        x = fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_PlayerSubPrograms"] = [[]]
        x["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_ParameterBlobIndices"] = [[]]
        d = self.analyse(x)
        self.assertEqual(d["unpaired_original_passes"], 1)
        self.assertEqual(d["paired_original_passes"], 1)

    def test_non_normal_original_pass_type_is_explicit_not_silent(self):
        x = fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["m_Type"] = 2
        d = self.analyse(x)
        self.assertEqual(d["non_normal_passes"], 1)

    def test_too_many_passes_rejected(self):
        x = fixture(passes=p.MAX_PASSES + 1)
        with self.assertRaisesRegex(ValueError, "budget"):
            self.analyse(x)

    def test_no_private_name_or_program_payload_in_public_aggregate(self):
        d = self.analyse()
        report = json.dumps(d, sort_keys=True)
        for token in (p.TARGET, "private-synthetic-dxbc", "m_Name", "progVertex"):
            self.assertNotIn(token, report)

    def test_malformed_original_pass_type_rejected(self):
        x = fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["m_Type"] = "0"
        with self.assertRaisesRegex(ValueError, "pass type"):
            self.analyse(x)


if __name__ == "__main__":
    unittest.main()
