"""Provenance-aware dispatch pair regressions; synthetic trace only."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER


def row(event, suffix):
    return {"event": event, "message": "sequence=1;kernel=FFT_H;" + suffix}


class ProvenancePairTests(unittest.TestCase):
    def test_matching_session_build_and_guid(self):
        fields = "session_id=phone-A;build_sha=abc123;shader_guid=guid1;resource_guid=guid2"
        result = audit([row(BEFORE, fields), row(AFTER, fields)])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["missing_return_sequences"], [])
        self.assertFalse(result["gpu_execution_proven"])

    def test_different_session_cannot_pair(self):
        result = audit([row(BEFORE, "session_id=phone-A"), row(AFTER, "session_id=phone-B")])
        self.assertIn("identity_mismatch:1:session_id", result["errors"])
        self.assertEqual(result["missing_return_sequences"], [1])

    def test_different_build_cannot_pair(self):
        result = audit([row(BEFORE, "build_sha=aaa"), row(AFTER, "build_sha=bbb")])
        self.assertIn("identity_mismatch:1:build_sha", result["errors"])

    def test_missing_guid_cannot_pair(self):
        result = audit([row(BEFORE, "shader_guid=abc"), row(AFTER, "result=returned")])
        self.assertIn("identity_mismatch:1:shader_guid", result["errors"])

    def test_legacy_sequence_only_does_not_prove_gpu(self):
        result = audit([row(BEFORE, "x=1"), row(AFTER, "result=returned")])
        self.assertEqual(result["errors"], [])
        self.assertFalse(result["runtime_kernel_identity_proven"])
        self.assertFalse(result["gpu_execution_proven"])


if __name__ == "__main__":
    unittest.main()
