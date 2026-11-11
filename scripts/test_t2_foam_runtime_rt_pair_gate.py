import json
import unittest
from scripts.t2_foam_runtime_rt_pair_gate import check

BASE = {"schema": "t2-foam-runtime-rt-v1", "capture_id": "capture_0001",
        "source_commit": "a" * 40, "frame": 42,
        "pass0": {"source": "input_0001", "destination": "buffer_0001"},
        "pass1": {"source": "buffer_0001", "destination": "output_001"}}


class RuntimeRTGateTest(unittest.TestCase):
    def test_same_token(self):
        result = check(json.dumps(BASE).encode())
        self.assertEqual(result["runtime_identity_evidence"], "CAPTURE_TOKEN_MATCH")
        self.assertFalse(result["original_foam_runtime_provenance_verified"])
        self.assertFalse(result["android_pixels_verified"])

    def test_different_token(self):
        doc = json.loads(json.dumps(BASE))
        doc["pass1"]["source"] = "buffer_0002"
        self.assertEqual(check(json.dumps(doc).encode())["runtime_identity_evidence"],
                         "CAPTURE_TOKEN_MISMATCH")

    def test_fail_closed(self):
        for bad in (b'{"schema":1,"schema":2}', b'NaN', b'\xff',
                    json.dumps({**BASE, "frame": True}).encode(),
                    json.dumps({**BASE, "capture_id": "../private"}).encode(),
                    json.dumps({**BASE, "pass0": {"source": "foo"}}).encode()):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    check(bad)


if __name__ == "__main__":
    unittest.main()
