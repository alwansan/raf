"""GT ZIP2 original Mesh/Texture reference graph: no game bytes in fixtures."""
from __future__ import annotations

import hashlib
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from scripts.gt_stage_serialized_owners import OWNERS, InventoryError
from scripts.gt_original_mesh_texture_graph import audit, texenvs, resolve


def ptr(fid, pid):
    return {"m_FileID": fid, "m_PathID": pid}


def original_manifest():
    lines = ["kind\tbytes\tsha256\tmode\trelative_path_under_Raft"]
    for n in OWNERS:
        b = n.encode()
        lines.append(f"plain\t{len(b)}\t{hashlib.sha256(b).hexdigest()}\t660\tRaft_Data/{n}")
    return "\n".join(lines) + "\n"


def slot(name, fid, pid, uv=True):
    data = {"m_Texture": ptr(fid, pid)}
    if uv:
        data.update({"m_Scale": {"x": 1.0, "y": 1.0},
                     "m_Offset": {"x": 0.0, "y": 0.0}})
    return [name, data]


class Obj:
    def __init__(self, ident, typ, tree=None):
        self.path_id = ident
        self.type = SimpleNamespace(name=typ)
        self.tree = tree or {}

    def read_typetree(self, check_read=False):
        return self.tree


def mkloader(source):
    if source.name == "level0":
        objects = [
            Obj(1, "MeshFilter", {"m_Mesh": ptr(1, 200)}),
            Obj(2, "MeshFilter", {"m_Mesh": ptr(0, 0)}),
            Obj(3, "SkinnedMeshRenderer", {"m_Mesh": ptr(1, 200)}),
            Obj(4, "Material", {"m_SavedProperties":{"m_TexEnvs":[
                slot("_MainTex",1,201),slot("_Mask",0,0)]}}),
            Obj(5, "Mesh"),
            Obj(6, "MeshFilter", {"m_Mesh": ptr(0, 5)}),
        ]
        externals = [SimpleNamespace(path="sharedassets0.assets")]
    else:
        objects = [
            Obj(200, "Mesh"), Obj(201, "Texture2D"),
            Obj(202, "Texture2DArray"),
            Obj(11, "Material", {"m_SavedProperties":{"m_TexEnvs":[
                slot("_Array",0,202)]}}),
        ]
        externals = []
    return SimpleNamespace(file=SimpleNamespace(
        objects={obj.path_id:obj for obj in objects}, externals=externals))


class SourceMeshTextureGraphTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.stage = self.root / "stage"
        self.stage.mkdir()
        for name in ("level0", "sharedassets0.assets"):
            (self.stage/name).write_bytes(name.encode())
        self.mf = self.root/"RAFT_FILE_MANIFEST.tsv"
        self.mf.write_text(original_manifest())

    def tearDown(self):
        self.temp.cleanup()

    def run_audit(self, loader=mkloader):
        return audit(self.stage,self.mf,selected=[
            "level0","sharedassets0.assets"],loader=loader)

    def test_mesh_and_texture_target_class_identity(self):
        d = self.run_audit()
        c = d["counts"]
        self.assertEqual(c["mesh_component_slots"],4)
        self.assertEqual(c["mesh_bound"],3)
        self.assertEqual(c["mesh_null"],1)
        self.assertEqual(c["mesh_target_class_verified"],3)
        self.assertEqual(c["distinct_referenced_meshes"],2)
        self.assertEqual(c["scene_mesh_component_slots"],4)
        self.assertEqual(c["texture_property_slots"],3)
        self.assertEqual(c["texture_bound"],2)
        self.assertEqual(c["texture_null"],1)
        self.assertEqual(c["texture_target_class_verified"],2)
        self.assertEqual(c["distinct_referenced_textures"],2)
        self.assertEqual(d["texture_target_class_usage"]["Texture2D"],1)
        self.assertEqual(d["texture_target_class_usage"]["Texture2DArray"],1)
        self.assertEqual(c["source_texture_uv_transforms_present"],3)
        self.assertTrue(d["all_source_texture_targets_verified"])
        self.assertTrue(d["all_source_mesh_targets_verified"])
        self.assertFalse(d["android_gpu_render_verified"])
        self.assertEqual(len(d["original_graph_sha256"]),64)

    def test_wrong_mesh_target_class_is_reported(self):
        def load(p):
            env=mkloader(p)
            if p.name == "sharedassets0.assets":
                env.file.objects[200]=Obj(200,"Texture2D")
            return env
        d=self.run_audit(load)
        self.assertEqual(d["counts"]["mesh_target_wrong_class"],2)
        self.assertFalse(d["all_source_mesh_targets_verified"])

    def test_wrong_texture_target_class_is_reported(self):
        def load(p):
            env=mkloader(p)
            if p.name == "sharedassets0.assets":
                env.file.objects[201]=Obj(201,"Mesh")
            return env
        d=self.run_audit(load)
        self.assertEqual(d["counts"]["texture_target_wrong_class"],1)
        self.assertFalse(d["all_source_texture_targets_verified"])

    def test_undeclared_external_is_not_guessed(self):
        def load(p):
            env=mkloader(p)
            if p.name == "level0":
                env.file.externals[0].path="mystery.bundle"
            return env
        d=self.run_audit(load)
        self.assertEqual(d["counts"]["mesh_unresolved_provider"],2)
        self.assertEqual(d["counts"]["texture_unresolved_provider"],1)
        self.assertFalse(d["all_source_mesh_targets_verified"])
        self.assertFalse(d["all_source_texture_targets_verified"])

    def test_builtin_transport_is_separate(self):
        kind,target=resolve("level0",1,{"level0":["Library/unity default resources"]})
        self.assertEqual((kind,target),("engine",None))

    def test_invalid_pointer_and_texenvs_fail_closed(self):
        bad = [
            {"m_SavedProperties":{"m_TexEnvs":[slot("x",1,0)]}},
            {"m_SavedProperties":{"m_TexEnvs":[slot("x",0,5),slot("x",0,6)]}},
            {"m_SavedProperties":{"m_TexEnvs":[["x",{"m_Texture":ptr(0,3),
                             "m_Scale":{"x":1,"y":1}}]]}},
            {"m_SavedProperties":{"m_TexEnvs":[["x",{"m_Texture":ptr(0,3),
                             "m_Scale":{"x":float("nan"),"y":1},
                             "m_Offset":{"x":0,"y":0}}]]}},
        ]
        for t in bad:
            with self.subTest(t=t), self.assertRaises(InventoryError):
                texenvs(t)
        with self.assertRaises(InventoryError):
            resolve("level0",2,{"level0":["sharedassets0.assets"]})

    def test_forged_owner_fails_before_reader(self):
        (self.stage/"level0").write_bytes(b"changed")
        with self.assertRaisesRegex(InventoryError,"fingerprint_mismatch"):
            self.run_audit()


if __name__=="__main__":
    unittest.main()
