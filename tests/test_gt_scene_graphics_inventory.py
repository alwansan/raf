"""Synthetic regressions for GT's pinned-scene graphics inventory, no UnityPy needed."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from scripts.gt_scene_graphics_inventory import (
    InventoryError, checked_stage, manifest_scenes, scan,
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def manifest_text(entries=None) -> str:
    entries = entries or {}
    rows = ["kind\tbytes\tsha256\tmode\trelative_path_under_Raft"]
    for i in range(40):
        name = f"level{i}"
        kind, payload = entries.get(name, ("plain", b"test-" + name.encode()))
        rows.append(f"{kind}\t{len(payload)}\t{sha(payload)}\t660\tRaft_Data/{name}")
    return "\n".join(rows) + "\n"


class FakeObject:
    def __init__(self, path_id, typ, data=None):
        self.path_id = path_id
        self.type = SimpleNamespace(name=typ)
        self.data = data or {}

    def read_typetree(self, check_read=False):
        return self.data


def fake_loader(_path):
    objects = [
        FakeObject(1, "MeshRenderer", {"m_Materials": [{"m_FileID": 0, "m_PathID": 2}]}),
        FakeObject(2, "Material"),
        FakeObject(3, "Mesh"),
        FakeObject(4, "Texture2D"),
    ]
    return SimpleNamespace(file=SimpleNamespace(
        objects={obj.path_id: obj for obj in objects}, externals=[]))


class GTInventoryTests(unittest.TestCase):
    def test_plain_scene_authenticated_and_owned_objects_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "Raft_Data"
            src.mkdir()
            (src / "level0").write_bytes(b"test-level0")
            mf = root / "manifest.tsv"
            mf.write_text(manifest_text(), encoding="utf-8")
            report = scan(src, mf, (0,), loader=fake_loader)
            self.assertEqual(report["scenes_examined"], 1)
            self.assertFalse(report["all_40_scene_headers_authenticated"])
            self.assertEqual(report["counts"]["original_owned_Mesh"], 1)
            self.assertEqual(report["counts"]["original_owned_Texture2D"], 1)
            self.assertEqual(report["counts"]["original_material_slots"], 1)
            self.assertEqual(report["counts"]["local_material_target_verified"], 1)
            self.assertFalse(report["rendered_in_android_game_verified"])

    def test_split_reassembly_requires_ordered_parts_and_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "Raft_Data"
            src.mkdir()
            entry = src / "level30"
            entry.mkdir()
            payload = b"123456789abc"
            (entry / "part-00000").write_bytes(payload[:5])
            (entry / "part-00001").write_bytes(payload[5:])
            (entry / "README.txt").write_text("split")
            staged = checked_stage(src, "level30", ("split", len(payload), sha(payload)),
                                   root / "staging")
            self.assertEqual(staged.read_bytes(), payload)
            (entry / "part-00001").rename(entry / "part-00003")
            with self.assertRaisesRegex(InventoryError, "incomplete_split"):
                checked_stage(src, "level30", ("split", len(payload), sha(payload)),
                              root / "staging2")

    def test_wrong_digest_or_lfs_pointer_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "source"
            src.mkdir()
            (src / "level1").write_bytes(b"not-the-source")
            with self.assertRaisesRegex(InventoryError, "size_or_sha256_mismatch"):
                checked_stage(src, "level1", ("plain", 4, sha(b"real")), root / "stage")

    def test_manifest_rejects_duplicate_or_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            mf = Path(tmp) / "manifest.tsv"
            content = manifest_text()
            content += content.splitlines()[1] + "\n"
            mf.write_text(content)
            with self.assertRaisesRegex(InventoryError, "duplicate_scene"):
                manifest_scenes(mf)
            mf.write_text(manifest_text() + "plain\t1\t" + "0" * 64
                          + "\t660\tRaft_Data/../level0\n")
            with self.assertRaisesRegex(InventoryError, "unsafe_manifest_path"):
                manifest_scenes(mf)

    def test_missing_authentication_fails_before_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "source"
            src.mkdir()
            mf = root / "manifest.tsv"
            mf.write_text(manifest_text())
            with self.assertRaisesRegex(InventoryError, "missing_original_scene"):
                scan(src, mf, (0,), loader=fake_loader)


if __name__ == "__main__":
    unittest.main()
