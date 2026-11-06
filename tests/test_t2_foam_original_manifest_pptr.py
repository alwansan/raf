"""Synthetic only; no original game assets or private paths."""
import csv
import tempfile
import unittest
from pathlib import Path

from scripts.t2_foam_original_manifest_pptr import (
    _MANIFEST_BYTES, _MANIFEST_ROWS, parse_original_manifest,
    resolve_unmapped_external_materials,
)
from scripts.w1_stage_zip2_owners import PINS

H = "a" * 64


def entry(path, size=1, sha=H, kind="plain"):
    return {"path": path, "sha256": sha, "bytes": size, "kind": kind}


class OriginalManifestPPtrTests(unittest.TestCase):
    def check(self, externals, pointers, rows):
        return resolve_unmapped_external_materials(externals, pointers, rows)

    def test_unique_target_candidate_and_known_classification(self):
        counts, targets = self.check(
            ["archive:/source/resources.assets", "archive:/external/other.assets"],
            [(1, 22), (2, 45), (0, 1), (2, 0)],
            [entry("Raft_Data/extras/other.assets")],
        )
        self.assertEqual((counts["total_external"], counts["known_four_owner"],
                          counts["unmapped"], counts["unique_manifest_candidate"]),
                         (2, 1, 1, 1))
        self.assertEqual(targets, [("Raft_Data/extras/other.assets", H, 45)])

    def test_absent_candidate(self):
        counts, targets = self.check(["a/missing.assets"], [(1, 10)],
                                     [entry("Raft_Data/extras/other.assets")])
        self.assertEqual(counts["no_manifest_candidate"], 1)
        self.assertFalse(targets)

    def test_collision_never_arbitrarily_resolved(self):
        counts, targets = self.check(
            ["a/other.assets"], [(1, 10)],
            [entry("a/other.assets"), entry("b/other.assets")],
        )
        self.assertEqual(counts["ambiguous_manifest_candidate"], 1)
        self.assertEqual(targets, [])

    def test_malformed_unrelated_manifest_is_fail_closed(self):
        counts, targets = self.check(
            ["a/other.assets"], [(1, 10)],
            [entry("a/other.assets"), entry("b/bad.assets", sha="bad")],
        )
        self.assertEqual(counts["unique_manifest_candidate"], 0)
        self.assertFalse(targets)

    def test_out_of_range_external_fileid(self):
        with self.assertRaisesRegex(ValueError, "out_of_bounds"):
            self.check(["a/other.assets"], [(2, 10)],
                       [entry("a/other.assets")])

    def test_malformed_private_external_path(self):
        with self.assertRaisesRegex(ValueError, "untrusted_path"):
            self.check(["bad\x00path"], [(1, 10)], [entry("badpath")])

    def test_bad_material_pointer(self):
        for bad in [(True, 1), (-1, 12), ("1", 10), None, (1,)]:
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValueError, "pointer_invalid"):
                    self.check(["a/other.assets"], [bad], [entry("a/other.assets")])

    def fixture(self):
        rows = []
        for name, (size, sha) in PINS.items():
            rows.append(("plain", str(size), sha, "-", name))
        remaining = _MANIFEST_BYTES - sum(x[0] for x in PINS.values())
        fillers = _MANIFEST_ROWS - len(rows)
        self.assertGreater(remaining, fillers)
        for n in range(fillers):
            size = 1 if n < fillers - 1 else remaining - fillers + 1
            rows.append(("plain", str(size), H, "-",
                         "Raft_Data/fixture/data-%03d.assets" % n))
        return rows

    def write_manifest(self, rows, location):
        with location.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, delimiter="\t")
            writer.writerow(["kind", "bytes", "sha256", "mode",
                             "relative_path_under_Raft"])
            writer.writerows(rows)

    def test_original_manifest_schema_and_total_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            loc = Path(tmp) / "manifest.tsv"
            self.write_manifest(self.fixture(), loc)
            result = parse_original_manifest(loc)
            self.assertEqual(len(result), 366)
            self.assertEqual(sum(x["bytes"] for x in result), _MANIFEST_BYTES)

    def test_original_manifest_invalid_unrelated_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            loc = Path(tmp) / "manifest.tsv"
            rows = self.fixture()
            rows[-1] = (rows[-1][0], rows[-1][1], "not-sha",
                        rows[-1][3], rows[-1][4])
            self.write_manifest(rows, loc)
            with self.assertRaisesRegex(ValueError, "entry_invalid"):
                parse_original_manifest(loc)

    def test_original_manifest_duplicate_path_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            loc = Path(tmp) / "manifest.tsv"
            rows = self.fixture()
            last = list(rows[-1])
            last[-1] = rows[-2][-1]
            rows[-1] = tuple(last)
            self.write_manifest(rows, loc)
            with self.assertRaisesRegex(ValueError, "entry_invalid"):
                parse_original_manifest(loc)

    def test_original_manifest_independent_pin_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            loc = Path(tmp) / "manifest.tsv"
            rows = self.fixture()
            first = list(rows[0])
            first[2] = "b" * 64
            rows[0] = tuple(first)
            self.write_manifest(rows, loc)
            with self.assertRaisesRegex(ValueError, "pins_drift"):
                parse_original_manifest(loc)


if __name__ == "__main__":
    unittest.main()
