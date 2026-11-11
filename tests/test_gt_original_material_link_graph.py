"""GT original Renderer->Material identity graph unit tests; no Unity bytes."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from scripts.gt_stage_serialized_owners import OWNERS, InventoryError
from scripts.gt_original_material_link_graph import audit, pointer


def make_manifest():
    rows = ["kind\tbytes\tsha256\tmode\trelative_path_under_Raft"]
    for name in OWNERS:
        data = name.encode()
        rows.append(f"plain\t{len(data)}\t{hashlib.sha256(data).hexdigest()}\t660\tRaft_Data/{name}")
    return "\n".join(rows)+"\n"


class Object:
    def __init__(self, id, type_name, slots=None):
        self.path_id = id
        self.type = SimpleNamespace(name=type_name)
        self.slots = slots

    def read_typetree(self, check_read=False):
        return {"m_Materials": self.slots}


def ptr(fid, pid):
    return {"m_FileID": fid, "m_PathID": pid}


def fixture_loader(_):
    p = Path(_)
    if p.name == "level0":
        objects = [
            Object(10, "MeshRenderer", [ptr(1,20), ptr(0,0)]),
            Object(11, "MeshRenderer", [ptr(1,20)]),
            Object(12, "MeshRenderer", []),
        ]
        external = [SimpleNamespace(path="sharedassets0.assets")]
    else:
        objects = [Object(20, "Material"), Object(25, "Mesh"),
                   Object(26, "MeshRenderer", [ptr(0,20)])]
        external = []
    return SimpleNamespace(file=SimpleNamespace(
        objects={x.path_id: x for x in objects}, externals=external))


class GTMaterialGraphTests(unittest.TestCase):
    def fixture(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        data = root/"stage"
        data.mkdir()
        for n in ("level0", "sharedassets0.assets"):
            (data/n).write_bytes(n.encode())
        manifest = root/"original-manifest.tsv"
        manifest.write_text(make_manifest())
        return data, manifest

    def tearDown(self):
        if hasattr(self, "tmp"):
            self.tmp.cleanup()

    def test_repeated_slot_is_one_unique_material(self):
        data, mf = self.fixture()
        result = audit(data, mf, selected=["level0", "sharedassets0.assets"],
                       loader=fixture_loader)
        c = result["counts"]
        self.assertEqual(c["total_renderer_objects"], 4)
        self.assertEqual(c["all_original_material_slots"], 4)
        self.assertEqual(c["scene_material_slots"], 3)
        self.assertEqual(c["scene_external_material_slots"], 2)
        self.assertEqual(c["scene_null_material_slots"], 1)
        self.assertEqual(c["material_identity_verified"], 3)
        self.assertEqual(c["distinct_referenced_material_objects"], 1)
        self.assertTrue(result["all_original_material_targets_class_verified"])
        self.assertFalse(result["same_export_guid_lineage_verified"])
        self.assertEqual(len(result["original_edge_graph_sha256"]), 64)

    def test_invalid_pointer_fail_closed(self):
        for raw in ({"m_FileID":1, "m_PathID":0},
                    {"m_FileID":-1, "m_PathID":2},
                    {"m_FileID":"1", "m_PathID":2},
                    {"m_FileID":0, "m_PathID":-9},
                    {"m_FileID":0},
                    {"m_FileID":0, "m_PathID":2, "junk":0}):
            with self.subTest(raw=raw):
                with self.assertRaises(InventoryError):
                    pointer(raw)

    def test_wrong_type_not_counted_as_verified(self):
        data, mf = self.fixture()
        def wrong_loader(p):
            x = fixture_loader(p)
            if p.name == "sharedassets0.assets":
                x.file.objects[20] = Object(20, "Mesh")
            return x
        result = audit(data, mf, selected=["level0", "sharedassets0.assets"],
                       loader=wrong_loader)
        self.assertEqual(result["counts"]["wrong_material_target_class"], 3)
        self.assertEqual(result["counts"].get("material_identity_verified", 0), 0)
        self.assertFalse(result["all_original_material_targets_class_verified"])

    def test_unknown_external_provider_stays_unverified(self):
        data, mf = self.fixture()
        def unknown_loader(p):
            x = fixture_loader(p)
            if p.name == "level0":
                x.file.externals[0].path = "another_unknown_assets.bin"
            return x
        result = audit(data, mf, selected=["level0", "sharedassets0.assets"],
                       loader=unknown_loader)
        self.assertEqual(result["counts"]["unresolved_external_provider"], 2)
        self.assertFalse(result["all_original_material_targets_class_verified"])

    def test_authentication_failure_prevents_load(self):
        data, mf = self.fixture()
        (data/"level0").write_bytes(b"forged")
        with self.assertRaisesRegex(InventoryError, "fingerprint_mismatch"):
            audit(data, mf, selected=["level0"], loader=fixture_loader)


if __name__ == "__main__":
    unittest.main()
