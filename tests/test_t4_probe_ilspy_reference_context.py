"""T4 source-free controls for same-DLL ILSpy dependency-context comparison."""
import unittest
from scripts.t4_probe_ilspy_reference_context import OLD_PAIR, NEW_PAIR, summarize

def profile(pair, mask="a" * 64):
    return {
        "class_sha256": pair[0], "coroutine_body_sha256": pair[1],
        "masked_coroutine_sha256": mask,
        "iterator_return": "IEnumerator",
        "original_completion_writes": 1,
        "original_scene_broadcast_calls": 1,
    }

class ReferenceContextControls(unittest.TestCase):
    def test_authentic_context_fingerprint_delta_is_detected(self):
        x = summarize(profile(NEW_PAIR), profile(NEW_PAIR),
                      profile(OLD_PAIR, "b" * 64), 151)
        self.assertTrue(x["isolated_control_matches"])
        self.assertTrue(x["old_B07_source_pair_reproduced_with_siblings"])
        self.assertTrue(x["T4_isolated_source_pair_reproduced"])
        self.assertTrue(x["different_masked_executable_body_hash_with_siblings"])
        self.assertFalse(x["production_source_pins_changed"])
        self.assertFalse(x["device_tested"])

    def test_no_delta_is_valid_inconclusive_result(self):
        x = summarize(profile(NEW_PAIR), profile(NEW_PAIR), profile(NEW_PAIR), 151)
        self.assertFalse(x["old_B07_source_pair_reproduced_with_siblings"])
        self.assertFalse(x["different_class_hash_with_siblings"])
        self.assertFalse(x["different_masked_executable_body_hash_with_siblings"])

    def test_original_b07_alone_not_mislabelled_t4(self):
        x = summarize(profile(OLD_PAIR), profile(OLD_PAIR), profile(NEW_PAIR), 151)
        self.assertFalse(x["old_B07_source_pair_reproduced_with_siblings"])
        self.assertFalse(x["T4_isolated_source_pair_reproduced"])

    def test_unknown_pair_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unknown original"):
            summarize(profile(NEW_PAIR), profile(NEW_PAIR), profile(("0"*64, "1"*64)), 151)

    def test_mismatched_isolated_control_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Isolated same-DLL"):
            summarize(profile(NEW_PAIR), profile(OLD_PAIR), profile(OLD_PAIR), 151)

    def test_incomplete_reference_context_rejected(self):
        for count in (0, -1, None, 1.5):
            with self.subTest(count=count):
                with self.assertRaisesRegex(ValueError, "Reference context"):
                    summarize(profile(NEW_PAIR), profile(NEW_PAIR), profile(OLD_PAIR), count)

    def test_wrong_iterator_contract_rejected(self):
        p = profile(OLD_PAIR)
        p["iterator_return"] = "void"
        with self.assertRaisesRegex(ValueError, "coroutine contract"):
            summarize(profile(NEW_PAIR), profile(NEW_PAIR), p, 151)

    def test_duplicate_original_completion_rejected(self):
        p = profile(OLD_PAIR)
        p["original_completion_writes"] = 2
        with self.assertRaisesRegex(ValueError, "coroutine contract"):
            summarize(profile(NEW_PAIR), profile(NEW_PAIR), p, 151)

    def test_missing_original_broadcast_rejected(self):
        p = profile(OLD_PAIR)
        p["original_scene_broadcast_calls"] = 0
        with self.assertRaisesRegex(ValueError, "coroutine contract"):
            summarize(profile(NEW_PAIR), profile(NEW_PAIR), p, 151)

    def test_no_false_device_proof(self):
        v = summarize(profile(NEW_PAIR), profile(NEW_PAIR), profile(OLD_PAIR), 151)
        self.assertTrue(v["same_original_dll_sha_verified"])
        self.assertFalse(v["unity_compiled"])
        self.assertFalse(v["world_playable_or_rgd_roundtrip"])
        self.assertFalse(v["private_source_published"])

if __name__ == "__main__":
    unittest.main()
