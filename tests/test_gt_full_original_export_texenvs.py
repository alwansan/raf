"""GT full original 82-owner Material Texture source→AssetRipper export join tests.

Synthetic originals only: no proprietary bytes or real object identities.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from scripts.gt_stage_serialized_owners import OWNERS, InventoryError
from scripts.gt_full_original_export_texenvs import original, inspect


class Obj:
    def __init__(self,path_id,typ,prop=None):
        self.path_id=path_id
        self.type=SimpleNamespace(name=typ)
        self.prop=prop

    def read_typetree(self,check_read=False):
        return {"m_SavedProperties":{"m_TexEnvs":[
            ["_MainTex",{"m_Texture":{"m_FileID":0,"m_PathID":self.prop},
                         "m_Scale":{"x":1.0,"y":1.0},
                         "m_Offset":{"x":0.0,"y":0.0}}]]}}


def fake_loader(path):
    return SimpleNamespace(objects=[Obj(123,"Material",124),Obj(124,"Texture2D")])


def fixture(root):
    stage=root/"source"
    stage.mkdir()
    manifest=root/"manifest.tsv"
    rows=["kind\tbytes\tsha256\tmode\trelative_path_under_Raft"]
    trace={"schema_version":1,"export_instance":"f"*32,"objects":[]}
    exported={}
    for ix,name in enumerate(OWNERS):
        raw=name.encode()
        (stage/name).write_bytes(raw)
        rows.append(f"plain\t{len(raw)}\t{hashlib.sha256(raw).hexdigest()}\t660\tRaft_Data/{name}")
        mg=f"{ix+1:032x}"
        tg=f"{ix+1001:032x}"
        trace["objects"].extend([
            {"class_id":21,
             "source":{"owner":name,"path_id":123},
             "export":{"file_id":2100000,"guid":mg,"type":2}},
            {"class_id":28,
             "source":{"owner":name,"path_id":124},
             "export":{"file_id":2800000,"guid":tg,"type":3}}
        ])
        exported[(2100000,mg)]={"_MainTex":((2800000,tg,3),(1.,1.,0.,0.))}
    manifest.write_text("\n".join(rows)+"\n")
    trace_path=root/"same-instance.json"
    trace_path.write_text(json.dumps(trace))
    project=root/"ExportedProject"
    project.mkdir()
    return stage,manifest,trace_path,project,exported


class GTFullSourceExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source,self.manifest,self.trace,self.project,self.exported=fixture(self.root)

    def test_all_eighty_two_exact_internal_texture_bindings(self):
        r=inspect(self.source,self.manifest,self.project,self.trace,
            loader=fake_loader,exported_parser=lambda project:self.exported)
        self.assertEqual(r["original_material_objects"],len(OWNERS))
        self.assertEqual(r["exact_internal_targets_compared"],len(OWNERS))
        self.assertEqual(r["wrong_internal_targets"],0)
        self.assertEqual(r["uv_transform_slots_compared"],len(OWNERS))
        self.assertTrue(r["all_texture_targets_proven"])
        self.assertFalse(r["android_gpu_verified"])
        self.assertFalse(r["exported_materials_modified"])
        self.assertNotIn("sharedassets0",json.dumps(r))
        self.assertNotIn("_MainTex",json.dumps(r))

    def test_wrong_exported_texture_guid_produces_detectable_mismatch(self):
        actual=dict(self.exported)
        first=next(iter(actual))
        actual[first]={"_MainTex":((2800000,"e"*32,3),(1.,1.,0.,0.))}
        r=inspect(self.source,self.manifest,self.project,self.trace,
            loader=fake_loader,exported_parser=lambda project:actual)
        self.assertEqual(r["wrong_internal_targets"],1)
        self.assertFalse(r["source_slots_faithful_with_resolved_scope"])

    def test_invalid_source_digest_fails_before_matching(self):
        (self.source/OWNERS[0]).write_bytes(b"corrupted")
        with self.assertRaisesRegex(InventoryError,"fingerprint_mismatch"):
            inspect(self.source,self.manifest,self.project,self.trace,
                loader=fake_loader,exported_parser=lambda project:self.exported)

    def test_unknown_trace_or_source_is_fail_closed(self):
        bad=json.loads(self.trace.read_text())
        bad["objects"]=[]
        self.trace.write_text(json.dumps(bad))
        with self.assertRaises(ValueError):
            inspect(self.source,self.manifest,self.project,self.trace,
                loader=fake_loader,exported_parser=lambda project:self.exported)

    def test_source_selection_rejects_duplicates(self):
        with self.assertRaises(InventoryError):
            original(self.source,self.manifest,selected=[OWNERS[0],OWNERS[0]],
                     loader=fake_loader)


if __name__=="__main__":
    unittest.main()
