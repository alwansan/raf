"""GT 82-owner ZIP2 staging: synthetic authenticity and traversal controls."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.gt_stage_serialized_owners import (
    OWNERS, InventoryError, read_expected, stage,
)


def checksum(data):
    return hashlib.sha256(data).hexdigest()


def manifest_for(replace=None):
    replace = replace or {}
    lines = ["kind\tbytes\tsha256\tmode\trelative_path_under_Raft"]
    for name in OWNERS:
        kind, data = replace.get(name, ("plain", name.encode()))
        lines.append(f"{kind}\t{len(data)}\t{checksum(data)}\t660\tRaft_Data/{name}")
    return "\n".join(lines) + "\n"


class StageTests(unittest.TestCase):
    def test_all_manifest_owners_required(self):
        with tempfile.TemporaryDirectory() as base:
            p = Path(base) / "manifest.tsv"
            p.write_text(manifest_for())
            self.assertEqual(len(read_expected(p)), 82)
            p.write_text("\n".join(manifest_for().splitlines()[:-1]) + "\n")
            with self.assertRaisesRegex(InventoryError, "manifest_missing"):
                read_expected(p)

    def test_stage_single_original_with_sha(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            src = root / "Raft_Data"
            src.mkdir()
            data = b"real-assets-sha-check"
            (src / "resources.assets").write_bytes(data)
            manifest = root / "manifest"
            manifest.write_text(manifest_for({"resources.assets": ("plain", data)}))
            res = stage(src, manifest, root / "output", selected=["resources.assets"])
            self.assertEqual(res["selected_owners"], 1)
            self.assertEqual((root / "output/resources.assets").read_bytes(), data)
            self.assertFalse(res["all_82_serialized_owners"])

    def test_stage_split_requires_all_parts(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            src = root / "Raft_Data"
            src.mkdir()
            sub = src / "sharedassets0.assets"
            sub.mkdir()
            data = b"ABCDEFG"
            (sub / "part-00000").write_bytes(data[:3])
            (sub / "part-00001").write_bytes(data[3:])
            (sub / "README.txt").write_text("verified split")
            manifest = root / "manifest"
            manifest.write_text(manifest_for({"sharedassets0.assets": ("split", data)}))
            stage(src, manifest, root / "out", selected=["sharedassets0.assets"])
            self.assertEqual((root / "out/sharedassets0.assets").read_bytes(), data)
            (sub / "part-00001").rename(sub / "part-00002")
            with self.assertRaisesRegex(InventoryError, "unsafe_split"):
                stage(src, manifest, root / "out2", selected=["sharedassets0.assets"])

    def test_mismatched_sha_does_not_publish(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            src = root / "Raft_Data"
            src.mkdir()
            (src / "level0").write_bytes(b"forged")
            manifest = root / "manifest"
            manifest.write_text(manifest_for())
            with self.assertRaisesRegex(InventoryError, "manifest_original_sha256_mismatch"):
                stage(src, manifest, root / "out", selected=["level0"])
            self.assertFalse((root / "out/level0").exists())

    def test_unsafe_manifest_and_destination_rejected(self):
        with tempfile.TemporaryDirectory() as base:
            root = Path(base)
            src = root / "Raft_Data"
            src.mkdir()
            (src / "level0").write_bytes(b"level0")
            manifest = root / "manifest"
            manifest.write_text(manifest_for() + "plain\t2\t" + "0" * 64 +
                                "\t660\tRaft_Data/../escape\n")
            with self.assertRaisesRegex(InventoryError, "unsafe_manifest_path"):
                read_expected(manifest)
            manifest.write_text(manifest_for())
            with self.assertRaisesRegex(InventoryError, "destination_inside_original_source"):
                stage(src, manifest, src / "output", selected=["level0"])


if __name__ == "__main__":
    unittest.main()
