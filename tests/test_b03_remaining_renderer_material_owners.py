import hashlib
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from scripts.b03_remaining_renderer_material_owners import (
    SourceError, read_manifest, select_residual, restore_provider,
)


def obj(pid, kind, slots):
    return SimpleNamespace(
        path_id=pid, type=SimpleNamespace(name=kind),
        read_typetree=lambda check_read=False: {"m_Materials": slots},
    )


class RemainingOwnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = self.root / "manifest.tsv"
        self.manifest.write_text(
            "kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n" +
            "plain\t4\t" + hashlib.sha256(b"DATA").hexdigest() +
            "\t660\tRaft_Data/secondary.assets\n")
        self.data = read_manifest(self.manifest)

    def test_selects_only_unstaged_unique_manifest_owner(self):
        scene = [obj(1, "MeshRenderer", [
            {"m_FileID": 1, "m_PathID": 44},
            {"m_FileID": 2, "m_PathID": 55},
        ])]
        r = select_residual(scene, ["resources.assets", "secondary.assets"], self.data)
        self.assertEqual(r, Counter({"secondary.assets": 1}))

    def test_unknown_owner_path_rejected(self):
        scene = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 44}])]
        with self.assertRaises(SourceError):
            select_residual(scene, ["missing.assets"], self.data)

    def test_ambiguous_manifest_basename_rejected(self):
        self.manifest.write_text(self.manifest.read_text() +
            "plain\t4\t" + hashlib.sha256(b"DATA").hexdigest() +
            "\t660\tRaft_Data/other/secondary.assets\n")
        scene = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 44}])]
        with self.assertRaises(SourceError):
            select_residual(scene, ["secondary.assets"], read_manifest(self.manifest))

    def test_plain_exact_bytes_sha_only(self):
        checkout = self.root / "zip2"
        stage = self.root / "stage"
        stage.mkdir()
        source = checkout / "Raft" / "Raft_Data" / "secondary.assets"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"DATA")
        record = self.data["secondary.assets"]
        result = restore_provider(checkout, record, stage)
        self.assertEqual(result.read_bytes(), b"DATA")

    def test_tampered_plain_refused_and_cleans_partial(self):
        checkout = self.root / "zip2"
        stage = self.root / "stage"
        stage.mkdir()
        source = checkout / "Raft" / "Raft_Data" / "secondary.assets"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"FAKE")
        with self.assertRaises(SourceError):
            restore_provider(checkout, self.data["secondary.assets"], stage)
        self.assertEqual(list(stage.iterdir()), [])

    def test_chunk_order_and_original_sha_authenticated(self):
        checkout = self.root / "zip2"
        stage = self.root / "stage"
        stage.mkdir()
        source = checkout / "Raft" / "Raft_Data" / "secondary.assets"
        source.mkdir(parents=True)
        (source / "part-00000").write_bytes(b"DA")
        (source / "part-00001").write_bytes(b"TA")
        record = {**self.data["secondary.assets"], "kind": "split"}
        result = restore_provider(checkout, record, stage)
        self.assertEqual(result.read_bytes(), b"DATA")

    def test_missing_chunk_refused(self):
        checkout = self.root / "zip2"
        stage = self.root / "stage"
        stage.mkdir()
        source = checkout / "Raft" / "Raft_Data" / "secondary.assets"
        source.mkdir(parents=True)
        (source / "part-00000").write_bytes(b"DA")
        (source / "part-00002").write_bytes(b"TA")
        record = {**self.data["secondary.assets"], "kind": "split"}
        with self.assertRaises(SourceError):
            restore_provider(checkout, record, stage)

    def test_stage_does_not_clobber_existing_asset(self):
        checkout = self.root / "zip2"
        stage = self.root / "stage"
        stage.mkdir()
        (stage / "secondary.assets").write_bytes(b"existing")
        with self.assertRaises(SourceError):
            restore_provider(checkout, self.data["secondary.assets"], stage)
        self.assertEqual((stage / "secondary.assets").read_bytes(), b"existing")

    def test_manifest_traversal_refused(self):
        self.manifest.write_text(self.manifest.read_text() +
            "plain\t4\t" + hashlib.sha256(b"DATA").hexdigest() +
            "\t660\tRaft_Data/../bad.assets\n")
        with self.assertRaises(SourceError):
            read_manifest(self.manifest)

    def test_no_source_id_leak_in_plan(self):
        scene = [obj(11, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 412345}])]
        r = select_residual(scene, ["secondary.assets"], self.data)
        self.assertEqual(list(r.keys()), ["secondary.assets"])
        self.assertNotIn("412345", str(r))


if __name__ == "__main__":
    unittest.main()
