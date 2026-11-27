"""Source-free row coverage regression; decoder and SPIR-V validator injected.

This exercises the real gate's topology and row/module join, not GPU or
original game byte equivalence.
"""
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import gt_fft_bundle_gate as gate


def row(index):
    return {"m_KeywordIndices": [], "m_BlobIndex": index}


def player(*buckets):
    return {"m_PlayerSubPrograms": [[row(i) for i in b] for b in buckets]}


def legacy(*indices):
    return {"m_SubPrograms": [row(i) for i in indices]}


def stage_variants(program):
    legacy_rows = program.get("m_SubPrograms", [])
    player_rows = program.get("m_PlayerSubPrograms", [])
    if legacy_rows and any(player_rows):
        raise ValueError("Both editor and player program tables populated; explicit choice required")
    if legacy_rows:
        return [(None, i, v) for i, v in enumerate(legacy_rows)]
    return [(b, i, v) for b, values in enumerate(player_rows) for i, v in enumerate(values)]


def blob(*modules):
    # Authored two-byte model/id tokens, NOT actual SPIR-V or Unity blobs.
    return (0, bytes(32) + b"".join(bytes(m) for m in modules))


def injected_decoder(data):
    return [data[i:i + 2] for i in range(32, len(data), 2)]


def injected_validator(data, workdir, models, sample_ops):
    return dict(gate.fingerprint(data), models=[data[0]], image_ops=[], validator_exit=0), ""


def parsed(vertex, fragment):
    p = {"m_Type": 0, "progVertex": vertex, "progFragment": fragment}
    return {"m_KeywordNames": [], "m_KeywordFlags": [],
            "m_SubShaders": [{"m_Passes": [deepcopy(p) for _ in range(7)]}]}


class FftRowCoverage(unittest.TestCase):
    def setUp(self):
        self.entries = [blob((0, 1), (4, 1)), blob((0, 2)), blob((4, 2)),
                        blob((0, 3), (4, 3)), blob((0, 4), (4, 4), (4, 5)),
                        blob((0, 6), (0, 7), (4, 6)), blob((0, 8), (4, 8), (4, 8))]

    def verify(self, tree):
        with tempfile.TemporaryDirectory() as directory, patch.object(
                gate, "validate_module", side_effect=injected_validator):
            proof, _ = gate.verify_modules(tree, self.entries, "unused", Path(directory),
                                          stage_variants, injected_decoder, None, None,
                                          authored_coordinate_profile=False)
        return proof

    def reject(self, tree, message):
        with self.assertRaisesRegex(ValueError, message):
            self.verify(tree)

    def test_complete_combined_player_rows(self):
        p = self.verify(parsed(player([0], [3], [], [0]), {}))
        self.assertEqual(p["pass_count"], 7)
        for entry in p["passes"]:
            self.assertTrue(entry["fragment_table_fallback"])
            for stage in ("progVertex", "progFragment"):
                refs = entry["stages"][stage]["rows"]
                self.assertEqual([r["bucket"] for r in refs], [0, 1, 3])
                self.assertTrue(all(len(r["module_sha256"]) == 1 for r in refs))
        self.assertEqual(p["validated_unique_modules"], 4)

    def test_complete_separate_player_rows(self):
        p = self.verify(parsed(player([1], [], [1]), player([2], [], [2])))
        for entry in p["passes"]:
            self.assertFalse(entry["fragment_table_fallback"])
            for stage in ("progVertex", "progFragment"):
                self.assertEqual([r["bucket"] for r in entry["stages"][stage]["rows"]], [0, 2])

    def test_complete_legacy_combined_and_separate(self):
        for vertex, fragment in ((legacy(0), {}), (legacy(1), legacy(2))):
            with self.subTest(vertex=vertex, fragment=fragment):
                p = self.verify(parsed(vertex, fragment))
                self.assertEqual(p["passes"][0]["stages"]["progVertex"]["rows"][0]["bucket"], None)

    def test_combined_partial_fragment_missing(self):
        self.reject(parsed(player([0], [1]), {}), "missing_execution_stage:0:progFragment")

    def test_combined_partial_vertex_missing(self):
        self.reject(parsed(player([0], [2]), {}), "missing_execution_stage:0:progVertex")

    def test_separate_partial_vertex_missing(self):
        self.reject(parsed(player([1], [2]), player([2], [2])), "missing_execution_stage:0:progVertex")

    def test_separate_partial_fragment_missing(self):
        self.reject(parsed(player([1], [1]), player([2], [1])), "missing_execution_stage:0:progFragment")

    def test_separate_bucket_sets_must_match(self):
        self.reject(parsed(player([1], [], [1]), player([2], [2], [])), "stage_bucket_mismatch:0")

    def test_separate_legacy_player_bucket_mismatch(self):
        self.reject(parsed(legacy(1), player([2])), "stage_bucket_mismatch:0")

    def test_duplicate_empty_route_in_player_bucket(self):
        self.reject(parsed(player([0, 3]), {}), "duplicate_empty_route_bucket:0:progVertex")

    def test_duplicate_empty_route_in_legacy_fragment(self):
        self.reject(parsed(legacy(1), legacy(2, 2)), "duplicate_empty_route_bucket:0:progFragment")

    def test_multiple_fragment_modules_in_row(self):
        self.reject(parsed(player([0], [4]), {}), "ambiguous_execution_stage:0:progFragment")

    def test_multiple_vertex_modules_in_row(self):
        self.reject(parsed(player([0], [5]), {}), "ambiguous_execution_stage:0:progVertex")

    def test_duplicate_identical_module_in_row(self):
        self.reject(parsed(player([0], [6]), {}), "ambiguous_execution_stage:0:progFragment")

    def test_last_pass_not_covered_by_prior_success(self):
        p = parsed(player([0], [3]), {})
        p["m_SubShaders"][0]["m_Passes"][6]["progVertex"] = player([0], [1])
        self.reject(p, "missing_execution_stage:6:progFragment")


if __name__ == "__main__":
    unittest.main()
