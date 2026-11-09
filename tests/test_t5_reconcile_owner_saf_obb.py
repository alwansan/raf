"""Source-free negative and positive controls for real T5 SAF evidence."""
import json
import unittest
from scripts.t5_reconcile_owner_saf_obb import (
    EvidenceError, REFERENCE_OBB_BYTES, REFERENCE_SHA_PREFIX,
    parse_summary, reconcile,
)


def sample(observed=None, status="EVIDENCE_READY", session="shared-20261108-230157-466487336"):
    if observed is None:
        observed = "bytes=2301280507 sha256=" + "911a53bc1dd4" + "0" * 52
    return {
        "session": session,
        "results": [{"case_id": "T5-02", "worker": "T5",
                     "result": {"id": "T5-02", "worker": "T5",
                                "status": status, "observed": observed}}],
    }


class T5OwnerSafProvenanceTests(unittest.TestCase):
    def test_actual_owner_observation_is_different_not_corrupt(self):
        actual = sample("bytes=2301280507 sha256=911a53bc1dd48c7fa08e5982b3741af1f45fd76825f64a961e24dc00dfea0bcf")
        report = reconcile(actual)
        self.assertEqual(report["comparison"], "DIFFERENT_FROM_OLD_REFERENCE")
        self.assertEqual(report["byte_difference"], 24195)
        self.assertFalse(report["phone_corruption_proven"])
        self.assertFalse(report["installed_obb_mount_verified"])

    def test_same_size_same_safe_prefix_is_not_full_match(self):
        v = sample("bytes=" + str(REFERENCE_OBB_BYTES) + " sha256=" + REFERENCE_SHA_PREFIX + "0"*52)
        report = reconcile(v)
        self.assertEqual(report["comparison"], "SIZE_AND_PREFIX_CONSISTENT_ONLY")
        self.assertFalse(report["full_reference_sha256_equality_proven"])
        self.assertFalse(report["phone_selected_file_location_recorded"])

    def test_same_size_different_sha_prefix_is_different(self):
        v = sample("bytes=" + str(REFERENCE_OBB_BYTES) + " sha256=" + "a" * 64)
        self.assertEqual(reconcile(v)["comparison"], "DIFFERENT_FROM_OLD_REFERENCE")

    def test_pending_newer_summary_does_not_erase_older_evidence(self):
        v = sample("User action, mouse/file or judgment is required", "NEEDS_INPUT",
                   "shared-20261108-232759-468049775")
        report = reconcile(v)
        self.assertEqual(report["comparison"], "NO_COMPLETED_DIGEST")
        self.assertIsNone(report["selected_file_bytes"])

    def test_unsubstantiated_pass_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "completed_case_has_no_valid_digest"):
            reconcile(sample("No bytes", "PASS"))

    def test_duplicate_nested_json_keys_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "duplicate_summary_json_key"):
            parse_summary(b'{"session":"a","results":[{"case_id":"T5-02","case_id":"T5-02"}]}')

    def test_nonstandard_numeric_constant_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "nonstandard_json_constant"):
            parse_summary(b'{"session":"a","results":NaN}')

    def test_duplicate_t5_case_rejected(self):
        v = sample()
        v["results"].append(v["results"][0].copy())
        with self.assertRaisesRegex(EvidenceError, "missing_or_duplicate"):
            reconcile(v)

    def test_wrong_owner_case_identity_rejected(self):
        v = sample()
        v["results"][0]["worker"] = "T4"
        with self.assertRaisesRegex(EvidenceError, "missing_or_duplicate"):
            reconcile(v)

    def test_wrong_session_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "invalid_session"):
            reconcile(sample(), expected_session="other-session")

    def test_trailing_path_or_unstructured_digest_refused(self):
        with self.assertRaisesRegex(EvidenceError, "completed_case_has_no_valid_digest"):
            reconcile(sample("bytes=2301280507 sha256=" + "a"*64 + " /Android/obb/path"))

    def test_bad_hash_rejected(self):
        with self.assertRaisesRegex(EvidenceError, "completed_case_has_no_valid_digest"):
            reconcile(sample("bytes=3 sha256=deadbeef"))

    def test_zero_and_overlimit_hash_size_rejected(self):
        for size in ("0", str(16*1024**3+1)):
            with self.subTest(size=size), self.assertRaises(EvidenceError):
                reconcile(sample("bytes="+size+" sha256="+"0"*64))

    def test_no_full_observed_digest_ever_logged(self):
        raw = "b"*64
        report = reconcile(sample("bytes=1 sha256="+raw))
        self.assertNotIn(raw, json.dumps(report))
        self.assertNotIn("file://", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
