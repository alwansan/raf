"""Synthetic, no-device-data regression tests for T2 JSONL evidence gate."""
import json
import unittest
from scripts.t2_gles_device_jsonl_gate import verify


def records(case="CASE02"):
    detail = ("OK 2-pass RGBA8 FBO; sourceLeft=[32, 96, 159, 255] "
              "sourceRight=[223, 32, 64, 255] finalBaseline=[32, 96, 159, 255] "
              "finalContrast=[223, 32, 64, 255] tolerance=2")
    out = []
    for i, event in enumerate(("startup", "gl_context", "surface", "case_start",
                               "gl_observed", "shared_auto_result", "export")):
        out.append(dict(unix_ms=10000+i, elapsed_ms=500+i, worker="T2",
                        package="com.example.lab", version="0.1.1",
                        session="20261108-230235-466525434",
                        case=case if i >= 3 else None, event=event,
                        detail=detail if event in ("gl_observed", "shared_auto_result") else "ok"))
    return out


def encoded(rows):
    return [json.dumps(row) for row in rows]


class TestEvidenceGate(unittest.TestCase):
    def test_consistent_synthetic_case(self):
        self.assertTrue(verify(encoded(records()), "CASE02")["synthetic_gles_log_consistent"])
        self.assertFalse(verify(encoded(records()), "CASE02")["original_raft_water_verified"])

    def test_missing_or_duplicate_event(self):
        for rows in (records()[:-2] + [records()[-1]],
                     records()[:5] + [records()[4]] + records()[5:]):
            with self.assertRaises(ValueError):
                verify(encoded(rows), "CASE02")

    def test_wrong_case_or_session(self):
        for field, value in (("case", "CASE01"), ("session", "20261108-230235-123456")):
            rows = records()
            rows[4][field] = value
            with self.assertRaises(ValueError):
                verify(encoded(rows), "CASE02")

    def test_disagreement_and_fake_ok(self):
        for detail in ("OK success", "FAIL FBO", "OK 2-pass RGBA8 FBO"):
            rows = records()
            rows[4]["detail"] = detail
            with self.assertRaises(ValueError):
                verify(encoded(rows), "CASE02")

    def test_order_and_elapsed(self):
        rows = records()
        rows[4]["elapsed_ms"] = 0
        with self.assertRaises(ValueError):
            verify(encoded(rows), "CASE02")

    def test_duplicate_keys_and_nonfinite(self):
        rows = encoded(records())
        rows[0] = rows[0][:-1] + ', "worker": "T2"}'
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            verify(rows, "CASE02")
        rows = encoded(records())
        rows[0] = rows[0].replace('"unix_ms": 10000', '"unix_ms": NaN')
        with self.assertRaises(ValueError):
            verify(rows, "CASE02")

    def test_reject_unknown_events(self):
        rows = records()
        rows[2]["event"] = "private_dump"
        with self.assertRaises(ValueError):
            verify(encoded(rows), "CASE02")


    def test_reject_negative_or_backwards_clock(self):
        for field, value in (("unix_ms", -1), ("elapsed_ms", -1),
                             ("unix_ms", 9999), ("elapsed_ms", 0)):
            rows = records()
            rows[4][field] = value
            with self.subTest(field=field, value=value):
                with self.assertRaises(ValueError):
                    verify(encoded(rows), "CASE02")

    def test_reject_mixed_apk_version(self):
        rows = records()
        rows[4]["version"] = "0.1.2"
        with self.assertRaisesRegex(ValueError, "mixed_sessions"):
            verify(encoded(rows), "CASE02")

    def test_case02_rejects_inconsistent_numeric_pixels(self):
        changes = (
            ("finalBaseline=[32, 96, 159, 255]", "finalBaseline=[99, 96, 159, 255]"),
            ("finalContrast=[223, 32, 64, 255]", "finalContrast=[32, 96, 159, 255]"),
            ("sourceLeft=[32, 96, 159, 255]", "sourceLeft=[256, 96, 159, 255]"),
            ("sourceRight=[223, 32, 64, 255]", "sourceRight=[223, 32, 64]"),
        )
        for original, replacement in changes:
            rows = records()
            for row in rows:
                if row["event"] in ("gl_observed", "shared_auto_result"):
                    row["detail"] = row["detail"].replace(original, replacement)
            with self.subTest(replacement=replacement):
                with self.assertRaises(ValueError):
                    verify(encoded(rows), "CASE02")

    def test_case02_allows_tolerance_two(self):
        rows = records()
        for row in rows:
            if row["event"] in ("gl_observed", "shared_auto_result"):
                row["detail"] = row["detail"].replace(
                    "finalBaseline=[32, 96, 159, 255]",
                    "finalBaseline=[34, 94, 160, 255]")
        self.assertTrue(verify(encoded(rows), "CASE02")["synthetic_gles_log_consistent"])

    def test_allow_equal_timestamps(self):
        rows = records()
        rows[4]["unix_ms"] = rows[3]["unix_ms"]
        rows[4]["elapsed_ms"] = rows[3]["elapsed_ms"]
        self.assertTrue(verify(encoded(rows), "CASE02")["synthetic_gles_log_consistent"])

if __name__ == "__main__":
    unittest.main()
