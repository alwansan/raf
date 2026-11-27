"""Authored full-size metadata fixtures, not original source or Unity receipts."""
import copy
import itertools
import json
import unittest

from scripts.gt_next23b_route_provenance import (
    COUNTS, bind_candidate_route_manifest, derive_source_contract,
    verify_candidate_route_manifest, verify_bundle_metadata,
)


def fixture():
    names, flags, passes, copies, pairs, routes = [], [], [], [], [], []
    modes = ("ForwardBase", "ForwardAdd", "Deferred", "ShadowCaster")
    for p, (n, count, mode) in enumerate(zip((9, 2, 7, 9), COUNTS, modes)):
        local_names = [f"AUTHORED_P{p}_K{k}" for k in range(n)]
        fixed = {0: "DIRECTIONAL", 3: "UNITY_PASS_SHADOWCASTER"}.get(p)
        offset = len(names)
        names.extend(local_names + ([fixed] if fixed else []))
        flags.extend([k % 2 for k in range(n)] + ([0] if fixed else []))
        state = {"m_Tags": {"tags": [["LightMode", mode]]}}
        original = {"m_Type": 0, "m_State": state}
        copied = dict(subshader=0, pass_=p, matched_pairs=count,
                      unmatched_vertex=0, unmatched_fragment=0, original_state=copy.deepcopy(state))
        copied["pass"] = copied.pop("pass_")
        stage_tables = {"vs": [], "fs": []}
        engine_routes = []
        for r, bits in enumerate(itertools.product((False, True), repeat=n)):
            indices = [offset + k for k, on in enumerate(bits) if on] + ([offset + n] if fixed else [])
            engine_routes.append({"keywords": [name for name, on in zip(local_names, bits) if on]})
            pair = {"subshader": 0, "pass": p}
            for stage, base in (("vs", 0), ("fs", 67)):
                meta = {"m_BlobIndex": base + r % 67, "m_ShaderHardwareTier": 0,
                        "m_KeywordIndices": indices[:], "m_GlobalKeywordIndices": [], "m_LocalKeywordIndices": []}
                stage_tables[stage].append(meta)
                pair[stage] = {"player_bucket": 0, "bucket_ordinal": r,
                               "original_variant_metadata": copy.deepcopy(meta),
                               "program_ref": f"program-{base + r % 67:03d}"}
            pairs.append(pair)
        for stage, field, copy_field in (("vs", "progVertex", "original_vertex_program"),
                                         ("fs", "progFragment", "original_fragment_program")):
            original[field] = {"m_SubPrograms": [], "m_PlayerSubPrograms": [stage_tables[stage]]}
            copied[copy_field] = copy.deepcopy(original[field])
        passes.append(original)
        copies.append(copied)
        routes.append({"passType": mode, "variants": engine_routes})
    source = {"original_shader_ParsedForm_full_private": {
        "m_KeywordNames": names, "m_KeywordFlags": flags, "m_SubShaders": [{"m_Passes": passes}]},
        "original_passes": copies, "paired": pairs, "unpaired": []}
    return source, {"passes": routes}


def encoded(source):
    return json.dumps(source, sort_keys=True).encode()


class Next23bRouteProvenance(unittest.TestCase):
    def setUp(self):
        self.source, self.routes = fixture()
        self.shader = b"authored candidate bytes -- not compiled ShaderLab"

    def bind(self):
        return bind_candidate_route_manifest(encoded(self.source), self.shader, self.routes)

    def reject(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.bind()

    def test_full_source_slot_join_and_numeric_scope_boundary(self):
        packet, report = self.bind()
        self.assertEqual(report["source_routes_by_pass"], list(COUNTS))
        self.assertEqual(report["paired_source_stage_slots_checked"], 2312)
        self.assertEqual(report["used_flag_byte_counts_across_passes"], {"0": 17, "1": 12})
        self.assertFalse(report["original_keyword_scope_verified"])
        self.assertFalse(report["original_runtime_keyword_selection_verified"])
        self.assertEqual(verify_candidate_route_manifest(encoded(self.source), self.shader, packet), report)
        self.assertNotIn("AUTHORED_P", json.dumps(report))

    def test_route_order_is_not_source_slot_identity(self):
        self.source["paired"].reverse()
        for row in self.routes["passes"]:
            row["variants"].reverse()
        self.bind()

    def test_copied_pass_state_drift(self):
        self.source["original_passes"][0]["original_state"]["m_Tags"]["tags"][0][1] = "Deferred"
        self.reject("copied_pass_state_drift")

    def test_route_pass_type_drift_even_with_correct_counts(self):
        self.routes["passes"][0]["passType"] = "Deferred"
        self.reject("engine_manifest_source_mismatch")

    def test_duplicate_source_slot(self):
        self.source["paired"][1]["vs"] = copy.deepcopy(self.source["paired"][0]["vs"])
        self.reject("duplicate_or_missing_stage_slot")

    def test_copied_variant_metadata_drift(self):
        self.source["paired"][1]["vs"]["original_variant_metadata"]["m_KeywordIndices"] = []
        self.reject("copied_variant_metadata_drift")

    def test_vertex_fragment_pair_must_match_actual_permutation(self):
        self.source["paired"][0]["fs"], self.source["paired"][1]["fs"] = (
            self.source["paired"][1]["fs"], self.source["paired"][0]["fs"])
        self.reject("vertex_fragment_permutation_drift")

    def test_complete_but_renamed_keyword_lattice_does_not_match_source(self):
        for variant in self.routes["passes"][0]["variants"]:
            variant["keywords"] = ["DIFFERENT" if x == "AUTHORED_P0_K0" else x for x in variant["keywords"]]
        self.reject("engine_manifest_source_mismatch")

    def test_flag_type_drift(self):
        self.source["original_shader_ParsedForm_full_private"]["m_KeywordFlags"][0] = True
        self.reject("invalid_keyword_flags")

    def test_scope_lane_not_silently_ignored(self):
        parsed = self.source["original_shader_ParsedForm_full_private"]
        meta = parsed["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_PlayerSubPrograms"][0][0]
        meta["m_LocalKeywordIndices"] = [0]
        self.source["original_passes"][0]["original_vertex_program"]["m_PlayerSubPrograms"][0][0] = copy.deepcopy(meta)
        self.source["paired"][0]["vs"]["original_variant_metadata"] = copy.deepcopy(meta)
        self.reject("separate_scope_unproved")

    def test_ambiguous_lightmode_in_original(self):
        parsed = self.source["original_shader_ParsedForm_full_private"]
        parsed["m_SubShaders"][0]["m_Passes"][0]["m_State"]["m_Tags"]["tags"].append(["LIGHTMODE", "ForwardBase"])
        self.reject("ambiguous_or_unknown_lightmode")

    def test_stale_candidate_and_source_bytes_fail(self):
        packet, _ = self.bind()
        for source, shader in ((encoded(self.source), self.shader + b"!"),
                               (encoded(self.source) + b"\n", self.shader)):
            with self.subTest(shader=shader), self.assertRaisesRegex(ValueError, "commitment_mismatch"):
                verify_candidate_route_manifest(source, shader, packet)

    def test_unsealed_manifest_cannot_be_accepted(self):
        with self.assertRaisesRegex(ValueError, "commitment_mismatch"):
            verify_candidate_route_manifest(encoded(self.source), self.shader, self.routes)

    def test_bundle_metadata_matches_raw_flags_by_name_not_index(self):
        packet, _ = self.bind()
        parsed = copy.deepcopy(self.source["original_shader_ParsedForm_full_private"])
        parsed["m_KeywordNames"].reverse()
        parsed["m_KeywordFlags"].reverse()
        result = verify_bundle_metadata(encoded(self.source), parsed, packet)
        self.assertEqual(result["bundle_serialized_pass_tags_matched"], 4)
        self.assertEqual(result["bundle_used_keyword_flag_bytes_matched"], 27)
        self.assertFalse(result["original_keyword_scope_verified"])
        parsed["m_KeywordFlags"] = bytes(parsed["m_KeywordFlags"])
        self.assertEqual(verify_bundle_metadata(encoded(self.source), parsed, packet), result)

    def test_bundle_flag_byte_mismatch_is_rejected_even_with_exact_routes(self):
        packet, _ = self.bind()
        parsed = copy.deepcopy(self.source["original_shader_ParsedForm_full_private"])
        parsed["m_KeywordFlags"][0] = 1 - parsed["m_KeywordFlags"][0]
        with self.assertRaisesRegex(ValueError, "bundle_keyword_flag_byte_mismatch"):
            verify_bundle_metadata(encoded(self.source), parsed, packet)

    def test_bundle_pass_tag_mismatch_is_rejected_even_with_exact_routes(self):
        packet, _ = self.bind()
        parsed = copy.deepcopy(self.source["original_shader_ParsedForm_full_private"])
        parsed["m_SubShaders"][0]["m_Passes"][0]["m_State"]["m_Tags"]["tags"] = [["LightMode", "Deferred"]]
        with self.assertRaisesRegex(ValueError, "bundle_pass_lightmode_mismatch"):
            verify_bundle_metadata(encoded(self.source), parsed, packet)


if __name__ == "__main__":
    unittest.main()
