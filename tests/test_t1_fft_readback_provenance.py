import unittest
from scripts.t1_fft_readback_provenance import validate_manifest


def manifest():
    return {"build_sha": "a" * 40, "session_id": "device-1",
            "passes": [{"name": "fft-stage-0", "vulkan_sha256": "b" * 64,
                        "unity_sha256": "c" * 64, "vulkan_bytes": 64, "unity_bytes": 64}]}


class ProvenanceTests(unittest.TestCase):
    def test_valid_metadata_does_not_prove_gpu(self):
        result = validate_manifest(manifest())
        self.assertTrue(result["metadata_valid"])
        self.assertFalse(result["gpu_execution_proven"])

    def test_reject_mismatched_sizes(self):
        m = manifest()
        m["passes"][0]["unity_bytes"] = 128
        with self.assertRaisesRegex(ValueError, "shape"):
            validate_manifest(m)

    def test_reject_duplicate_pass(self):
        m = manifest()
        m["passes"].append(dict(m["passes"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_manifest(m)

    def test_reject_invalid_digest(self):
        m = manifest()
        m["passes"][0]["unity_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(ValueError, "digest"):
            validate_manifest(m)


if __name__ == "__main__":
    unittest.main()
