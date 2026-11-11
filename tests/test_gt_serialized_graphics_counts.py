"""Synthetic original-object ownership and metadata fidelity tests for GT."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from scripts.gt_stage_serialized_owners import OWNERS, InventoryError
from scripts.gt_serialized_graphics_counts import inspect


def manifest():
    rows = ["kind\tbytes\tsha256\tmode\trelative_path_under_Raft"]
    for name in OWNERS:
        payload = name.encode()
        rows.append("plain\t{}\t{}\t660\tRaft_Data/{}".format(
            len(payload), hashlib.sha256(payload).hexdigest(), name))
    return "\n".join(rows) + "\n"


class Obj:
    def __init__(self, pid, typ, tree=None):
        self.path_id = pid
        self.type = SimpleNamespace(name=typ)
        self.tree = tree or {}

    def read_typetree(self, check_read=False):
        return self.tree


def loader(_):
    objects = [
        Obj(1, "Mesh", {"m_SubMeshes": [1, 2]}),
        Obj(2, "Texture2D", {"m_TextureFormat": 47, "m_ColorSpace": 1}),
        Obj(3, "Texture2D", {"m_TextureFormat": 4, "m_ColorSpace": 0}),
        Obj(4, "Material"),
        Obj(5, "Shader"),
        Obj(6, "ComputeShader"),
        Obj(7, "MeshRenderer"),
    ]
    return SimpleNamespace(file=SimpleNamespace(objects={o.path_id: o for o in objects}))


class Tests(unittest.TestCase):
    def test_source_owner_identity_and_graphics_shape(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            stage = root / "stage"
            stage.mkdir()
            (stage / "sharedassets1.assets").write_bytes(b"sharedassets1.assets")
            m = root / "manifest.tsv"
            m.write_text(manifest())
            report = inspect(stage, m, selected=["sharedassets1.assets"], loader=loader)
            self.assertEqual(report["counts"]["all_owned_serialized_objects"], 7)
            self.assertEqual(report["counts"]["Texture2D"], 2)
            self.assertEqual(report["counts"]["Mesh"], 1)
            self.assertEqual(report["counts"]["Material"], 1)
            self.assertEqual(report["counts"]["Shader"], 1)
            self.assertEqual(report["counts"]["ComputeShader"], 1)
            self.assertEqual(report["mesh_submesh_count_distribution"]["2"], 1)
            self.assertEqual(report["decode_counts"]["texture_format_color_decoded"], 2)
            self.assertFalse(report["all_82_owners_authenticated"])
            self.assertFalse(report["android_render_verified"])

    def test_mismatch_rejected_before_reader(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            src = root / "stage"
            src.mkdir()
            (src / "level0").write_bytes(b"notoriginal")
            m = root / "manifest.tsv"
            m.write_text(manifest())
            with self.assertRaisesRegex(InventoryError, "staged_owner_fingerprint_mismatch"):
                inspect(src, m, selected=["level0"], loader=loader)

    def test_duplicate_identity_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            src = root / "stage"
            src.mkdir()
            (src / "level0").write_bytes(b"level0")
            m = root / "manifest.tsv"
            m.write_text(manifest())
            def duplicate_loader(_):
                a = Obj(1, "Mesh")
                b = Obj(1, "Material")
                return SimpleNamespace(file=SimpleNamespace(objects={0: a, 1: b}))
            with self.assertRaisesRegex(InventoryError, "duplicate_or_invalid_source_object_identity"):
                inspect(src, m, selected=["level0"], loader=duplicate_loader)


if __name__ == "__main__":
    unittest.main()
