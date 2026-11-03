"""Strict synthetic base header + scaler value tests; no proprietary source."""
import math
import struct
import unittest

from scripts.probe_a2_scaler_value_decode import (
    BASE_BYTES, CUSTOM, EXPECTED_ORDER, decode_record, verified_field_order,
)


def generated_record(*, go=5, script=123, ui=1, width=1280.0, height=720.0,
                     match=0.5, enabled=1, mode=0):
    ptr = lambda fid, pid: {"m_FileID": fid, "m_PathID": pid}
    typed = {"m_GameObject": ptr(0, go),
             "m_Enabled": enabled, "m_EditorHideFlags": 0,
             "m_Script": ptr(1, script), "m_Name": "", "m_EditorClassIdentifier": ""}
    raw = (struct.pack("<iq", 0, go) +
           struct.pack("<BB2x", enabled, 0) +
           struct.pack("<iq", 1, script) +
           struct.pack("<i", 0) +
           CUSTOM.pack(ui, 100, 1, width, height, mode, match, 2, 96, 96, 1) +
           struct.pack("<f", 1))
    assert len(raw) == BASE_BYTES + CUSTOM.size == 80
    return raw, typed


class A2StrictScalerValuesTests(unittest.TestCase):
    def test_verified_order_is_exact_and_not_hint_only(self):
        self.assertTrue(verified_field_order({
            "fields_matched": list(EXPECTED_ORDER), "field_types_match_expected": True}))
        with self.assertRaisesRegex(ValueError, "drift"):
            verified_field_order({"fields_matched": list(reversed(EXPECTED_ORDER)),
                                  "field_types_match_expected": True})

    def test_decodes_full_record_with_independently_verified_base_fields(self):
        raw, typed = generated_record()
        decoded = decode_record(raw, typed)
        self.assertEqual(decoded["reference_resolution"], [1280., 720.])
        self.assertEqual(decoded["unexplained_trailing_bytes"], 4)
        self.assertTrue(decoded["trailer_is_finite_float"])
        self.assertEqual(decoded["ui_scale_mode"], 1)
        self.assertEqual(decoded["match_width_or_height"], 0.5)
        self.assertEqual(decoded["screen_match_mode"], 0)
        self.assertEqual(decoded["physical_unit"], 2)
        self.assertNotIn("m_GameObject", decoded)

    def test_rejects_fake_short_or_long_data(self):
        raw, tree = generated_record()
        for bad in (raw[:-1], raw + b"\0"):
            with self.assertRaisesRegex(ValueError, "length"):
                decode_record(bad, tree)

    def test_rejects_header_pptr_and_scripts_drift(self):
        raw, tree = generated_record()
        bad = dict(tree)
        bad["m_GameObject"] = {"m_FileID": 0, "m_PathID": 6}
        with self.assertRaisesRegex(ValueError, "PPtr"):
            decode_record(raw, bad)
        bad = dict(tree)
        bad["m_Script"] = {"m_FileID": 2, "m_PathID": 123}
        with self.assertRaisesRegex(ValueError, "PPtr"):
            decode_record(raw, bad)

    def test_rejects_nonzero_padding_or_invalid_name(self):
        raw, typed = generated_record()
        changed = bytearray(raw)
        changed[15] = 1
        with self.assertRaisesRegex(ValueError, "alignment"):
            decode_record(bytes(changed), typed)
        bad = dict(typed);bad["m_Name"] = "bad"
        with self.assertRaisesRegex(ValueError, "name"):
            decode_record(raw, bad)

    def test_rejects_out_of_bounds_match_mode_and_nan(self):
        for args in ({"match": -0.1}, {"match": 1.1},
                     {"match": float("nan")}, {"width": math.inf},
                     {"ui": 5}, {"mode": 8}):
            raw, typed = generated_record(**args)
            with self.assertRaisesRegex(ValueError, "(range|bounded|non-finite|implausible)"):
                decode_record(raw, typed)

    def test_rejects_spoofed_base_field_types(self):
        raw, typed = generated_record()
        bad = dict(typed);bad["m_EditorHideFlags"] = "0"
        with self.assertRaisesRegex(ValueError, "flags"):
            decode_record(raw, bad)
        bad = dict(typed);bad["m_Enabled"] = 3
        with self.assertRaisesRegex(ValueError, "enabled"):
            decode_record(raw, bad)


if __name__ == "__main__":
    unittest.main()
