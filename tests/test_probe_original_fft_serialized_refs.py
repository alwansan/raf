"""Prove local PPtr parser distinguishes byte patterns from typed references."""
import struct
import unittest
from scripts.probe_original_fft_serialized_refs import candidate_offsets, typed_reference_paths


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

    def test_bounds_and_types(self):
        with self.assertRaisesRegex(ValueError, "bounded"):
            candidate_offsets(b"x" * (4 * 1024 * 1024 + 1), 1)
        with self.assertRaisesRegex(ValueError, "list exceeds"):
            typed_reference_paths({"x": [None] * 40001}, 1)
        self.assertEqual(typed_reference_paths({"m_FileID": True, "m_PathID": 905}, 905), [])


if __name__ == "__main__":
    unittest.main()
