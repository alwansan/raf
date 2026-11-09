"""Original Dx11FFT direct numeric Dispatch contract: no inferred FindKernel."""
import copy
import unittest
from scripts.t1_fft_original_direct_dispatch_gate import validate, ORIGINAL_DLL_BLOB_SHA1, ORIGINAL_DX11FFT_CSHARP9_SHA256

def fixture():
    return {
        "schema_version": 1,
        "build_sha": "a" * 40,
        "device_session": "LogRaft-20261108-164850-270",
        "original_dll_blob_sha1": ORIGINAL_DLL_BLOB_SHA1,
        "original_dx11fft_source_sha256": ORIGINAL_DX11FFT_CSHARP9_SHA256,
        "reported_invalid_kernel_index": 6,
        "correlated_event_id": None,
        "dispatches": [{
            "event_id": "first-fft-call",
            "event_timestamp_ms": 1794145757581,
            "caller": "Dx11FFT",
            "dispatch_origin": "direct_numeric_argument",
            "fft_size": 256,
            "mathf_log2_truncated": 8,
            "bank_flag": False,
            "pass_offset": 0,
            "source_numeric_kernel_arg": 6,
            "dispatch_kernel_arg": 6,
            "compute_shader_present": True,
            "supports_compute": True,
            "groups": [8, 8, 1],
            "binding_names": ["Input", "Output"],
        }],
    }

class OriginalDirectNumericGateTests(unittest.TestCase):
    def test_numeric6_matches_only_source_hypothesis_unattributed(self):
        result = validate(fixture())
        self.assertEqual(result["source_selector_mismatch_count"], 0)
        self.assertEqual(result["reported_error_correlation"], "unattributed")
        self.assertFalse(result["named_unity_kernel_mapping_proven"])
        self.assertFalse(result["actual_runtime_trace_independently_attested"])

    def test_original_next_pass_numeric7(self):
        d = fixture()
        r = d["dispatches"][0]
        r.update(pass_offset=1, source_numeric_kernel_arg=7, dispatch_kernel_arg=7)
        self.assertEqual(validate(d)["source_selector_mismatch_count"], 0)

    def test_original_bank1_size256_numeric16(self):
        d = fixture()
        r = d["dispatches"][0]
        r.update(bank_flag=True, source_numeric_kernel_arg=16, dispatch_kernel_arg=16)
        self.assertEqual(validate(d)["source_selector_mismatch_count"], 0)

    def test_original_two_dispatch_calls_stay_distinct(self):
        d = fixture()
        r = copy.deepcopy(d["dispatches"][0])
        r.update(event_id="second-call", event_timestamp_ms=1794145757582,
                 pass_offset=1, source_numeric_kernel_arg=7, dispatch_kernel_arg=7)
        d["dispatches"].append(r)
        self.assertEqual(validate(d)["dispatch_observations"], 2)

    def test_original_source_selector_mismatch_is_reported_not_hidden(self):
        d = fixture()
        d["dispatches"][0]["source_numeric_kernel_arg"] = 5
        self.assertEqual(validate(d)["source_selector_mismatch_count"], 1)

    def test_real_dispatch_argument_mismatch_is_reported(self):
        d = fixture()
        d["dispatches"][0]["dispatch_kernel_arg"] = 7
        self.assertEqual(validate(d)["source_to_dispatch_mismatch_count"], 1)

    def test_size_exponent_disagreement_not_silently_replaced(self):
        d = fixture()
        d["dispatches"][0]["fft_size"] = 128
        self.assertEqual(validate(d)["fft_size_observed_exponent_disagreement_count"], 1)

    def test_out_of_original_twenty_domain_may_explain_invalid_kernel(self):
        d = fixture()
        r = d["dispatches"][0]
        r.update(fft_size=16, mathf_log2_truncated=4,
                 source_numeric_kernel_arg=-2, dispatch_kernel_arg=-2)
        self.assertEqual(validate(d)["outside_original_twenty_candidate_domain_count"], 1)

    def test_device_error_index_alone_does_not_attrib_to_dx11fft(self):
        d = fixture()
        d["reported_invalid_kernel_index"] = 6
        self.assertEqual(validate(d)["reported_error_correlation"], "unattributed")

    def test_explicit_event_correlation_does_not_prove_unity_kernel_name(self):
        d = fixture()
        d["correlated_event_id"] = "first-fft-call"
        r = validate(d)
        self.assertEqual(r["reported_error_correlation"], "same_event_numeric_argument_match_only")
        self.assertFalse(r["named_unity_kernel_mapping_proven"])

    def test_correlated_event_with_other_numeric_index_is_not_match(self):
        d = fixture()
        d["correlated_event_id"] = "first-fft-call"
        d["dispatches"][0]["dispatch_kernel_arg"] = 7
        self.assertEqual(validate(d)["reported_error_correlation"], "same_event_index_disagreement")

    def test_fake_unobserved_event_correlation_rejected(self):
        d = fixture()
        d["correlated_event_id"] = "event-never-observed"
        with self.assertRaisesRegex(ValueError, "not captured"):
            validate(d)

    def test_findkernel_claim_field_not_in_original_direct_schema(self):
        d = fixture()
        d["dispatches"][0]["find_kernel_result"] = 6
        with self.assertRaisesRegex(ValueError, "extra fields"):
            validate(d)

    def test_bool_numeric_index_rejected(self):
        d = fixture()
        d["dispatches"][0]["dispatch_kernel_arg"] = True
        with self.assertRaises(ValueError):
            validate(d)

    def test_string_bank_flag_rejected(self):
        d = fixture()
        d["dispatches"][0]["bank_flag"] = "false"
        with self.assertRaises(ValueError):
            validate(d)

    def test_duplicate_event_ids_rejected(self):
        d = fixture()
        d["dispatches"].append(copy.deepcopy(d["dispatches"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate(d)

    def test_out_of_order_timestamps_rejected(self):
        d = fixture()
        d["dispatches"].append(copy.deepcopy(d["dispatches"][0]))
        d["dispatches"][1].update(event_id="second", event_timestamp_ms=1794145757500)
        with self.assertRaisesRegex(ValueError, "ordering"):
            validate(d)

    def test_wrong_authentic_original_source_sha_rejected(self):
        d = fixture()
        d["original_dx11fft_source_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            validate(d)

    def test_private_gpu_label_control_character_rejected(self):
        d = fixture()
        d["dispatches"][0]["binding_names"][0] = "Input" + chr(0x85)
        with self.assertRaisesRegex(ValueError, "binding names"):
            validate(d)

    def test_missing_bound_bindings_flagged_not_success(self):
        d = fixture()
        d["dispatches"][0]["binding_names"] = []
        self.assertEqual(validate(d)["observations_without_binding_names"], 1)

    def test_foreign_caller_or_named_lookup_rejected(self):
        for key, value in (("caller", "OtherWaterShader"),
                           ("dispatch_origin", "find_kernel")):
            d = fixture()
            d["dispatches"][0][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "non-original"):
                validate(d)

    def test_correlated_index_six_with_wrong_source_argument_is_not_consistent(self):
        d = fixture()
        d["correlated_event_id"] = "first-fft-call"
        d["dispatches"][0]["source_numeric_kernel_arg"] = 5
        r = validate(d)
        self.assertEqual(r["reported_error_correlation"],
                         "same_event_number_matches_but_source_selector_mismatch")
        self.assertEqual(r["source_selector_mismatch_count"], 1)
        self.assertEqual(r["source_to_dispatch_mismatch_count"], 1)
        self.assertFalse(r["correlated_event_source_selector_consistent"])

    def test_correlated_index_six_with_wrong_exponent_formula_rejected_as_match(self):
        d = fixture()
        d["correlated_event_id"] = "first-fft-call"
        d["dispatches"][0].update(fft_size=512, mathf_log2_truncated=9)
        r = validate(d)
        self.assertEqual(r["reported_error_correlation"],
                         "same_event_number_matches_but_source_selector_mismatch")
        self.assertFalse(r["correlated_event_source_selector_consistent"])

    def test_correlated_index_six_with_wrong_bank_selector_not_matched(self):
        d = fixture()
        d["correlated_event_id"] = "first-fft-call"
        d["dispatches"][0]["bank_flag"] = True
        self.assertEqual(validate(d)["reported_error_correlation"],
                         "same_event_number_matches_but_source_selector_mismatch")

    def test_correlated_exponent_and_fft_size_disagreement_is_not_consistent(self):
        d = fixture()
        d["correlated_event_id"] = "first-fft-call"
        d["dispatches"][0]["fft_size"] = 128
        r = validate(d)
        self.assertEqual(r["reported_error_correlation"],
                         "same_event_number_matches_but_source_context_unverified")
        self.assertFalse(r["correlated_event_source_selector_consistent"])

    def test_correlated_compute_not_supported_does_not_prove_dispatch_preconditions(self):
        for key in ("compute_shader_present", "supports_compute"):
            d = fixture()
            d["correlated_event_id"] = "first-fft-call"
            d["dispatches"][0][key] = False
            with self.subTest(key=key):
                r = validate(d)
                self.assertEqual(r["reported_error_correlation"],
                                 "same_event_number_matches_but_dispatch_preconditions_unverified")
                self.assertTrue(r["correlated_event_source_selector_consistent"])
                self.assertFalse(r["correlated_event_numerical_match_is_runtime_identity_proof"])

    def test_correlated_missing_binding_or_zero_groups_not_full_numeric_match(self):
        for key, value in (("binding_names", []), ("groups", [0, 8, 1])):
            d = fixture()
            d["correlated_event_id"] = "first-fft-call"
            d["dispatches"][0][key] = value
            with self.subTest(key=key):
                r = validate(d)
                self.assertEqual(r["reported_error_correlation"],
                                 "same_event_number_matches_but_dispatch_preconditions_unverified")

    def test_correlated_clean_numeric_argument_remains_weak_evidence_only(self):
        d = fixture()
        d["correlated_event_id"] = "first-fft-call"
        r = validate(d)
        self.assertEqual(r["reported_error_correlation"],
                         "same_event_numeric_argument_match_only")
        self.assertTrue(r["correlated_event_source_selector_consistent"])
        self.assertFalse(r["correlated_event_numerical_match_is_runtime_identity_proof"])
        self.assertFalse(r["actual_runtime_trace_independently_attested"])

if __name__ == "__main__":
    unittest.main()
