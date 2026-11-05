"""T3 high-use original Shader48 real V/F per-Pass translation bounded controls."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_top_shader_fourpass_translation as t3

SECRET = b"ORIGINAL_SECRET_DXBC_VERTEX_BLOCK_921"
VERT = b"ORIGINAL_SECRET_DXBC_VERTEX_BLOCK_921"
FRAG = b"ORIGINAL_SECRET_DXBC_FRAGMENT_BLOCK_921"


def metadata(blob, kws=None):
    return {"m_BlobIndex": blob, "m_ShaderHardwareTier": 0,
            "m_KeywordIndices": list(kws or [])}


def stage(rows):
    return {"m_SubPrograms": list(rows), "m_PlayerSubPrograms": []}


def normal_pass(vertex=None, fragment=None):
    return {"m_Type": 0,
            "progVertex": stage([metadata(0)] if vertex is None else vertex),
            "progFragment": stage([metadata(1)] if fragment is None else fragment)}


def four_pass_source():
    return {"m_SubShaders": [{"m_Passes": [normal_pass() for _ in range(4)]}]}


def fake_link(meta, _entries, stage_kind):
    if meta.get("m_BlobIndex") != (0 if stage_kind == 1 else 1):
        raise ValueError("actual original DXBC stage mismatch")
    return (VERT if stage_kind == 1 else FRAG), {"private": "do_not_emit"}


def fake_translate(code, stage_kind, destination):
    assert isinstance(code, bytes) and code in (VERT, FRAG)
    assert destination.is_dir()
    assert destination.parent.name.startswith("temp") or "tmp" in str(destination.parent)
    return {"vulkan11_valid": True, "hlsl_recovered": True,
            "roundtrip_vulkan11_valid": True,
            "hlsl_sha256": "ORIGINAL_PRIVATE_HASH_NEVER_PUBLISH",
            "untrusted_private_path": "ORIGINAL_SECRET_SHADER_NAME"}


def fake_reflect(spv: Path):
    vert = spv.parent.name.endswith("stage-1")
    return {"inputs": [] if vert else [{"location": 0, "type": "vec4"}],
            "outputs": [{"location": 0, "type": "vec4"}] if vert else [],
            "resource_slots": {"ubos": [[0, 0]], "textures": [[0, 1]]}}


class FourPassTranslation(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory(prefix="t3-source-921-test-temp-")
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)

    def pairs(self, source=None, link=fake_link):
        return t3.exact_pass_samples(source or four_pass_source(),
                                     [(0, b"synthetic")], source_link=link)

    def evaluate(self, pairs=None, translator=fake_translate, reflector=fake_reflect):
        return t3.evaluate_samples(self.pairs() if pairs is None else pairs,
                                   self.root, translator=translator,
                                   reflector=reflector)

    def test_four_original_Passes_produce_four_authentic_vf_pairs(self):
        pairs = self.pairs()
        self.assertEqual(len(pairs), 4)
        self.assertTrue(all(v == VERT and f == FRAG for v, f in pairs))

    def test_translate_one_pair_per_pass_preserves_original_variant_limits(self):
        result = self.evaluate()
        c = result["counts"]
        self.assertEqual(result["status"], t3.STATUS)
        self.assertEqual(c["original_passes_sampled"], 4)
        self.assertEqual(c["original_stage_translation_attempts"], 8)
        self.assertEqual(c["genuine_stage_spirv11_valid"], 8)
        self.assertEqual(c["genuine_stage_hlsl_recovered"], 8)
        self.assertEqual(c["genuine_stage_hlsl_roundtrip_spirv11_valid"], 8)
        self.assertEqual(c["passes_with_source_SPIRV_vertex_fragment_interface_matching"], 4)
        self.assertEqual(c["passes_with_roundtrip_SPIRV_vertex_fragment_interface_matching"], 4)
        self.assertEqual(c["stage_original_roundtrip_resource_binding_shape_equal"], 8)
        self.assertEqual(result["source_variant_pairs_from_prior_full_linkage"], 33)
        self.assertEqual(result["source_unpaired_original_vertex_variants_not_translated"], 8)
        self.assertFalse(result["full_original_variant_population_translated"])
        self.assertFalse(result["native_Unity_Android_Adreno_pixels_verified"])

    def test_differing_player_bucket_not_claimed_matching(self):
        p = normal_pass()
        p["progVertex"] = {"m_SubPrograms": [], "m_PlayerSubPrograms": [[metadata(0)]]}
        p["progFragment"] = {"m_SubPrograms": [], "m_PlayerSubPrograms": [[], [metadata(1)]]}
        source = four_pass_source()
        source["m_SubShaders"][0]["m_Passes"][2] = p
        with self.assertRaisesRegex(ValueError, "no_exact_player_bucket"):
            self.pairs(source)

    def test_source_keyword_mismatch_must_not_use_arbitrary_fragment(self):
        p = normal_pass(vertex=[metadata(0, [7])],
                        fragment=[metadata(1, [8])])
        source = four_pass_source()
        source["m_SubShaders"][0]["m_Passes"][0] = p
        with self.assertRaisesRegex(ValueError, "no_exact_player_bucket"):
            self.pairs(source)

    def test_duplicate_original_variant_permutation_rejected(self):
        p = normal_pass(vertex=[metadata(0), metadata(0)])
        source = four_pass_source()
        source["m_SubShaders"][0]["m_Passes"][0] = p
        with self.assertRaisesRegex(ValueError, "duplicated_original_stage"):
            self.pairs(source)

    def test_wrong_original_pass_kind_cannot_be_fabricated(self):
        source = four_pass_source()
        source["m_SubShaders"][0]["m_Passes"][3] = {"m_Type": 1}
        with self.assertRaisesRegex(ValueError, "non_normal_original_Pass"):
            self.pairs(source)

    def test_source_pass_count_or_missing_compiled_stage_rejected(self):
        source = four_pass_source()
        source["m_SubShaders"][0]["m_Passes"].pop()
        with self.assertRaisesRegex(ValueError, "four_pass"):
            self.pairs(source)
        source = four_pass_source()
        del source["m_SubShaders"][0]["m_Passes"][0]["progFragment"]
        with self.assertRaisesRegex(ValueError, "missing_original_Pass_stage"):
            self.pairs(source)

    def test_original_dxbc_stage_guard_failure_stops_probe(self):
        def wrong_link(_meta, _table, _stage):
            raise ValueError("not an original DXBC vertex stage")
        with self.assertRaisesRegex(ValueError, "DXBC"):
            self.pairs(link=wrong_link)

    def test_partial_translation_does_not_claim_full_roundtrip(self):
        def partial(code, stage_kind, destination):
            fake_translate(code, stage_kind, destination)
            return {"vulkan11_valid": stage_kind == 1,
                    "hlsl_recovered": False,
                    "roundtrip_vulkan11_valid": False}
        result = self.evaluate(translator=partial)
        c = result["counts"]
        self.assertEqual(c["original_stage_translation_attempts"], 8)
        self.assertEqual(c["genuine_stage_spirv11_valid"], 4)
        self.assertEqual(c["genuine_stage_hlsl_recovered"], 0)
        self.assertEqual(c["passes_with_both_genuine_spirv_stages_valid"], 0)
        self.assertEqual(c["passes_with_source_SPIRV_vertex_fragment_interface_compared"], 0)
        self.assertFalse(result["resource_samplers_uniform_matrices_or_render_state_verified"])

    def test_reflection_failure_remains_counted_not_paired(self):
        def broken_reflection(_path):
            raise ValueError("reflector_private_error_message")
        c = self.evaluate(reflector=broken_reflection)["counts"]
        self.assertEqual(c["original_SPIRV_stage_reflections_verified"], 0)
        self.assertEqual(c["original_SPIRV_stage_reflection_failures"], 8)
        self.assertEqual(c["passes_with_source_SPIRV_vertex_fragment_interface_compared"], 0)

    def test_untrusted_translator_report_missing_required_flags_rejected(self):
        def malformed(_code, _stage, _destination):
            return {"vulkan11_valid": True}
        with self.assertRaisesRegex(ValueError, "untrusted_DXBC"):
            self.evaluate(translator=malformed)

    def test_compiler_private_names_hashes_and_dxbc_never_leave_public_aggregate(self):
        r = self.evaluate()
        blob = json.dumps(r)
        for secret in ("ORIGINAL_SECRET_DXBC_VERTEX_BLOCK_921",
                       "ORIGINAL_SECRET_DXBC_FRAGMENT_BLOCK_921",
                       "ORIGINAL_PRIVATE_HASH_NEVER_PUBLISH",
                       "ORIGINAL_SECRET_SHADER_NAME",
                       str(self.root), "m_BlobIndex"):
            self.assertNotIn(secret, blob)
        self.assertFalse(r["original_shader_programs_bytes_or_hashes_published"])

    def test_invalid_four_pass_synthetic_scope_fails_before_compiler(self):
        with self.assertRaisesRegex(ValueError, "bad_private_four_pass"):
            self.evaluate(pairs=[(VERT, FRAG)] * 3)
        with self.assertRaisesRegex(ValueError, "not_source_verified"):
            self.evaluate(pairs=[(VERT, FRAG)] * 3 + [("text", FRAG)])

    def test_no_mismatch_pass_selection_from_nonempty_stage_with_empty_paired_key(self):
        source = four_pass_source()
        source["m_SubShaders"][0]["m_Passes"][0]["progFragment"] = stage([])
        with self.assertRaisesRegex(ValueError, "empty_or_unbounded"):
            self.pairs(source)

    def test_if_stage_interface_shape_differs_report_true_negative(self):
        def mismatch_reflect(spv):
            data = fake_reflect(spv)
            if spv.parent.name.endswith("stage-0"):
                data["inputs"] = [{"location": 5, "type": "int"}]
            return data
        c = self.evaluate(reflector=mismatch_reflect)["counts"]
        self.assertEqual(c["passes_with_source_SPIRV_vertex_fragment_interface_compared"], 4)
        self.assertEqual(c["passes_with_source_SPIRV_vertex_fragment_interface_matching"], 0)

    def test_opt_in_scheduled_stage_io_classifier_asymmetric_drift(self):
        from scripts.t3_stage_io_drift import classify_stage_io
        def changed(spv):
            row = fake_reflect(spv)
            if spv.name == "roundtrip.spv":
                if spv.parent.name.endswith("stage-1"):
                    row["inputs"] = [{"location": 3, "type": "vec2"}]
                    row["outputs"] = [{"location": 4, "type": "vec4"}]
                else:
                    row["inputs"] = [{"location": 4, "type": "vec4"}]
                    row["outputs"] = [{"location": 5, "type": "vec2"}]
            return row
        out = t3.evaluate_samples(self.pairs(), self.root,
                                  translator=fake_translate, reflector=changed,
                                  io_classifier=classify_stage_io)
        c = out["counts"]
        self.assertEqual(out["status"], t3.IO_STATUS)
        self.assertTrue(out["source_to_roundtrip_io_drift_all_eight_stages_classified"])
        self.assertEqual(c["io_drift_stage_reflection_pairs_classified"], 8)
        self.assertEqual(c["stage_original_roundtrip_io_location_types_equal"], 0)
        # A relocated field contributes one removed AND one added location.
        # Each of four passes changes one Vertex and one Fragment side.
        self.assertEqual(c["io_drift_inputs_added_locations"], 8)
        self.assertEqual(c["io_drift_outputs_added_locations"], 8)
        self.assertEqual(c["io_drift_inputs_removed_locations"], 4)
        self.assertEqual(c["io_drift_outputs_removed_locations"], 4)
        self.assertEqual(c["io_drift_inputs_location_only_remap_candidate"], 4)
        self.assertEqual(c["io_drift_outputs_location_only_remap_candidate"], 4)
        self.assertEqual(c["io_drift_inputs_same_location_type_changes"], 0)
        self.assertEqual(c["io_drift_outputs_same_location_type_changes"], 0)

    def test_legacy_status_not_relabelled_or_invented_io_counts(self):
        r = self.evaluate()
        self.assertEqual(r["status"], t3.STATUS)
        self.assertFalse(r["source_to_roundtrip_io_drift_classification_opt_in"])
        self.assertFalse(any(k.startswith("io_drift_") for k in r["counts"]))

    def test_opt_in_partial_reflection_is_inconclusive_not_fake_zero(self):
        from scripts.t3_stage_io_drift import classify_stage_io
        def fail(spv):
            if spv.name == "roundtrip.spv" and spv.parent.name.endswith("stage-1"):
                raise ValueError("source_private_reflection_error")
            return fake_reflect(spv)
        with self.assertRaisesRegex(ValueError, "incomplete_real_original_roundtrip"):
            t3.evaluate_samples(self.pairs(), self.root,
                                translator=fake_translate, reflector=fail,
                                io_classifier=classify_stage_io)

    def test_reject_malicious_classifier_output_and_secret_leakage(self):
        def leak(_a, _b):
            return {"private_name": "PRIVATE_SHADER_SECRET"}
        with self.assertRaisesRegex(ValueError, "untrusted_private_stage_IO_classifier"):
            t3.evaluate_samples(self.pairs(), self.root,
                                translator=fake_translate, reflector=fake_reflect,
                                io_classifier=leak)
        from scripts.t3_stage_io_drift import classify_stage_io
        with tempfile.TemporaryDirectory(prefix="t3-private-io-") as tmp:
            result = t3.evaluate_samples(self.pairs(), Path(tmp),
                                         translator=fake_translate,
                                         reflector=fake_reflect,
                                         io_classifier=classify_stage_io)
        summary = json.dumps(result)
        for needle in ("ORIGINAL_SECRET_DXBC_VERTEX_BLOCK_921",
                       "ORIGINAL_PRIVATE_HASH_NEVER_PUBLISH",
                       "ORIGINAL_SECRET_SHADER_NAME", "m_BlobIndex"):
            self.assertNotIn(needle, summary)

    def test_reject_boolean_public_io_metric_value(self):
        from scripts.t3_stage_io_drift import classify_stage_io
        def corrupt(a, b):
            report = classify_stage_io(a, b)
            report["inputs_original_slots"] = True
            return report
        with self.assertRaisesRegex(ValueError, "invalid_public_stage_IO_classifier_counter"):
            t3.evaluate_samples(self.pairs(), self.root,
                                translator=fake_translate, reflector=fake_reflect,
                                io_classifier=corrupt)

if __name__ == "__main__":
    unittest.main()
