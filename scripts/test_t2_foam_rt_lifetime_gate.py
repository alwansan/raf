import copy
import json
import unittest
from scripts.t2_foam_rt_lifetime_gate import check

BASE = {"schema": "t2-foam-rt-lifetime-v1", "capture_id": "capture_0001",
        "source_commit": "a" * 40, "frame": 42,
        "events": [{"seq": i + 1, "kind": kind, "token": "buffer_0001"}
                   for i, kind in enumerate(("allocate", "pass0_write", "pass1_read", "release"))]}

def encoded(doc):
    return json.dumps(doc).encode()

class LifetimeTest(unittest.TestCase):
    def test_valid_is_not_authenticated(self):
        result = check(encoded(BASE))
        self.assertEqual(result["lifetime_order_evidence"], "CAPTURE_ORDER_CONSISTENT")
        self.assertFalse(result["original_foam_runtime_provenance_verified"])
        self.assertFalse(result["android_pixels_verified"])

    def test_bad_order_and_alias(self):
        for order in ((0, 2, 1, 3), (0, 1, 3, 2), (1, 0, 2, 3)):
            doc = copy.deepcopy(BASE)
            doc["events"] = [doc["events"][i] for i in order]
            for i, event in enumerate(doc["events"]):
                event["seq"] = i + 1
            with self.subTest(order=order), self.assertRaises(ValueError):
                check(encoded(doc))
        for index in (2, 3):
            doc = copy.deepcopy(BASE)
            doc["events"][index]["token"] = "buffer_0002"
            with self.subTest(index=index), self.assertRaises(ValueError):
                check(encoded(doc))

    def test_reuse_and_double_read(self):
        for kind in ("allocate", "pass1_read"):
            doc = copy.deepcopy(BASE)
            doc["events"].insert(3, {"seq": 4, "kind": kind, "token": "buffer_0001"})
            doc["events"][-1]["seq"] = 5
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                check(encoded(doc))

    def test_invalid_json_and_sequence(self):
        for raw in (b'{"schema":1,"schema":2}', b'NaN', bytes([255]), b" " * 65537):
            with self.assertRaises(ValueError):
                check(raw)
        for seq in (True, 1.5, -1, 2**31):
            doc = copy.deepcopy(BASE)
            doc["events"][2]["seq"] = seq
            with self.subTest(seq=seq), self.assertRaises(ValueError):
                check(encoded(doc))

    def test_unreleased_extra_resource_rejected(self):
        doc = copy.deepcopy(BASE)
        doc["events"].insert(1, {"seq": 2, "kind": "allocate", "token": "extra_0001"})
        for i, event in enumerate(doc["events"]):
            event["seq"] = i + 1
        with self.assertRaisesRegex(ValueError, "unreleased_capture_resource"):
            check(encoded(doc))

    def test_released_extra_resource_accepted_without_authenticity(self):
        doc = copy.deepcopy(BASE)
        doc["events"].insert(1, {"seq": 2, "kind": "allocate", "token": "extra_0001"})
        doc["events"].insert(2, {"seq": 3, "kind": "release", "token": "extra_0001"})
        for i, event in enumerate(doc["events"]):
            event["seq"] = i + 1
        result = check(encoded(doc))
        self.assertEqual(result["lifetime_order_evidence"], "CAPTURE_ORDER_CONSISTENT")
        self.assertFalse(result["original_foam_runtime_provenance_verified"])

    def test_completed_pair_with_second_unreleased_write_rejected(self):
        doc = copy.deepcopy(BASE)
        doc["events"].insert(1, {"seq": 2, "kind": "allocate", "token": "extra_0001"})
        doc["events"].insert(2, {"seq": 3, "kind": "pass0_write", "token": "extra_0001"})
        for i, event in enumerate(doc["events"]):
            event["seq"] = i + 1
        with self.assertRaisesRegex(ValueError, "unreleased_capture_resource"):
            check(encoded(doc))

    def test_invalid_identity(self):
        for key, value in (("frame", True), ("frame", -1), ("source_commit", "A" * 40)):
            doc = copy.deepcopy(BASE)
            doc[key] = value
            with self.assertRaises(ValueError):
                check(encoded(doc))

if __name__ == "__main__":
    unittest.main()
