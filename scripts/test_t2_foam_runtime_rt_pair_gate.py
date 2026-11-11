import copy
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
        doc = copy.deepcopy(BASE)
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

    def test_capture_boundary_rejections(self):
        mutations = [
            {"frame": -1}, {"frame": 2**31}, {"frame": 1.0},
            {"source_commit": "A" * 40}, {"source_commit": "g" * 40},
            {"capture_id": "capture/escape"}, {"capture_id": "é" * 8},
            {"schema": "t2-foam-runtime-rt-v2"},
        ]
        for change in mutations:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    check(json.dumps({**BASE, **change}).encode())

    def test_token_boundary_rejections(self):
        for token in ("short", "é" * 8, "bad/token", "a" * 65, "", 123, True):
            doc = copy.deepcopy(BASE)
            doc["pass1"]["source"] = token
            with self.subTest(token=token):
                with self.assertRaises(ValueError):
                    check(json.dumps(doc).encode())

    def test_duplicate_nested_keys_rejected(self):
        raw = json.dumps(BASE).replace('"source": "buffer_0001"', '"source": "buffer_0001", "source": "buffer_0001"')
        with self.assertRaises(ValueError):
            check(raw.encode())

    def test_oversize_and_non_bytes_rejected(self):
        for raw in (b" " * 8193, "not bytes", None, bytearray(b"{}")):
            with self.subTest(raw_type=type(raw).__name__):
                with self.assertRaises(ValueError):
                    check(raw)

    def test_valid_frame_boundaries_still_unverified(self):
        for frame in (0, 2**31 - 1):
            doc = {**BASE, "frame": frame}
            result = check(json.dumps(doc).encode())
            self.assertEqual(result["frame"], frame)
            self.assertFalse(result["original_foam_runtime_provenance_verified"])
            self.assertFalse(result["android_pixels_verified"])


if __name__ == "__main__":
    unittest.main()
