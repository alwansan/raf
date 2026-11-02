"""Prove local PPtr parser distinguishes byte patterns from typed references."""
import struct
import unittest
from scripts.probe_original_fft_serialized_refs import candidate_offsets, typed_reference_paths, raw_tail_array_shape


class OriginalFftPptrTests(unittest.TestCase):
    def test_candidate_and_field_match(self):
        target = 2456
        buf = b"padding" + struct.pack("<iq", 0, target) + b"extra"
        self.assertEqual(candidate_offsets(buf, target), [7])
        tree = {"Settings": [{"real": {"m_FileID": 0, "m_PathID": target}},
                             {"nope": {"m_FileID": 1, "m_PathID": target}}]}
        self.assertEqual(typed_reference_paths(tree, target), ["$/Settings[]/real"])

    def test_raw_pattern_not_evidence_and_nonlocal_link_rejected(self):
        buf = b"A" + struct.pack("<iq", 0, 905)
        self.assertEqual(len(candidate_offsets(buf, 905)), 1)
        self.assertEqual(typed_reference_paths({"other_bytes": [0, 905]}, 905), [])
        self.assertEqual(typed_reference_paths({"m_FileID": 2, "m_PathID": 905}, 905), [])
        self.assertEqual(candidate_offsets(struct.pack("<iq", 1, 905), 905), [])


    def test_serialized_one_item_tail_is_structural_hypothesis_only(self):
        raw = b"private fields" + struct.pack("<i", 1) + struct.pack("<iq", 0, 2456)
        offset = len(raw) - 12
        evidence = raw_tail_array_shape(raw, [offset])[0]
        self.assertEqual(evidence["preceding_four_bytes_as_int32"], 1)
        self.assertTrue(evidence["pointer_at_end_of_object"])
        self.assertTrue(evidence["one_item_array_tail_shape_only"])
        self.assertFalse(evidence["typed_array_field_verified"])
        opposite = raw_tail_array_shape(raw[:-16] + struct.pack("<i", 99) + raw[-12:], [offset])[0]
        self.assertFalse(opposite["one_item_array_tail_shape_only"])
        with self.assertRaisesRegex(ValueError, "Out-of-range"):
            raw_tail_array_shape(raw, [1])

    def test_bounds_and_types(self):
        with self.assertRaisesRegex(ValueError, "bounded"):
            candidate_offsets(b"x" * (4 * 1024 * 1024 + 1), 1)
        with self.assertRaisesRegex(ValueError, "list exceeds"):
            typed_reference_paths({"x": [None] * 40001}, 1)
        self.assertEqual(typed_reference_paths({"m_FileID": True, "m_PathID": 905}, 905), [])


if __name__ == "__main__":
    unittest.main()
