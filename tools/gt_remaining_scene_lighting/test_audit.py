import hashlib
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from tools.gt_remaining_scene_lighting.audit import census, pointer, verified_scene, AuditError

def o(name,cid,pid,d):
    return SimpleNamespace(type=SimpleNamespace(name=name,value=cid),path_id=pid,read_typetree=lambda **kw:d)

def pp(p=0,f=0):
    return {"m_FileID":f,"m_PathID":p}

def blob(b):
    return hashlib.sha1(("blob %d\0"%len(b)).encode()+b).hexdigest()

class TestCensus(unittest.TestCase):
    def test_empty_complete(self):
        r=census([o("LightmapSettings",157,1,{"m_Lightmaps":[]}),o("MeshRenderer",23,2,{"m_LightmapIndex":65535})])
        self.assertTrue(r["no_baked_lightmap_assignments_observed"])
    def test_unknown_not_empty(self):
        self.assertFalse(census([o("LightmapSettings",157,1,None)])["no_baked_lightmap_assignments_observed"])
        self.assertFalse(census([o("LightmapSettings",157,1,{"m_Lightmaps":[]}),o("MeshRenderer",23,2,None)])["no_baked_lightmap_assignments_observed"])
    def test_signed_id_and_local_type(self):
        t=o("Texture2D",28,-5,None)
        self.assertEqual(pointer(pp(-5),{-5:t},("Texture2D",28)),"local_typed")
        self.assertEqual(pointer(pp(-5,1),{-5:t},("Texture2D",28)),"external_unverified")
    def test_color_slot_and_wrong_type(self):
        maps=[{"m_LightmapColor":pp(3),"m_LightmapDir":pp(),"m_ShadowMask":pp()}]
        a=[o("LightmapSettings",157,1,{"m_Lightmaps":maps}),o("MeshRenderer",23,2,{"m_LightmapIndex":0})]
        self.assertEqual(census(a+[o("Texture2D",28,3,None)])["counts"]["renderer_complete_local_links"],1)
        self.assertEqual(census(a+[o("Mesh",43,3,None)])["counts"]["renderer_unresolved_map_links"],1)
    def test_ambiguous_and_reserved(self):
        a=[o("LightmapSettings",157,1,{"m_Lightmaps":[]}),o("LightmapSettings",157,2,None),o("MeshRenderer",23,3,{"m_LightmapIndex":65534})]
        r=census(a)
        self.assertFalse(r["no_baked_lightmap_assignments_observed"])
        self.assertEqual(r["counts"]["renderer_reserved_unverified"],1)
    def test_actual_light_owner_and_sun(self):
        a=[o("Light",108,1,{"m_GameObject":pp(2),"m_Enabled":1,"m_Intensity":2.,"m_Range":4.}),
           o("GameObject",1,2,{"m_IsActive":1}),o("RenderSettings",104,3,{"m_Sun":pp(1),"m_AmbientMode":0})]
        r=census(a)["counts"]
        self.assertEqual(r["light_owner_local_typed"],1)
        self.assertEqual(r["light_owner_self_active_yes"],1)
        self.assertEqual(r["render_settings_sun_local_typed"],1)
    def test_duplicate_rejected(self):
        with self.assertRaises(AuditError):
            census([o("Light",108,1,{}),o("Mesh",43,1,{})])
    def test_plain_and_split_fingerprints(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);data=root/"Raft"/"Raft_Data";data.mkdir(parents=True);tmp=root/"tmp";tmp.mkdir()
            a,b=b"authored a",b"authored b"
            p=data/"level6";p.write_bytes(a)
            row={"level":6,"kind":"plain","bytes":len(a),"git_object":blob(a),"sha256":hashlib.sha256(a).hexdigest()}
            with verified_scene(root,row,tmp) as f:self.assertEqual(f.read_bytes(),a)
            p.write_bytes(b)
            with self.assertRaises(AuditError):
                with verified_scene(root,row,tmp):pass
            p=data/"level30";p.mkdir()
            (p/"part-00000").write_bytes(a);(p/"part-00001").write_bytes(b)
            row={"level":30,"kind":"split","bytes":len(a+b),"sha256":hashlib.sha256(a+b).hexdigest(),
                 "parts":[{"name":"part-00000","bytes":len(a),"blob":blob(a)},{"name":"part-00001","bytes":len(b),"blob":blob(b)}]}
            with verified_scene(root,row,tmp) as f:self.assertEqual(f.read_bytes(),a+b)
            self.assertFalse((tmp/"level30").exists())
            row["parts"].reverse()
            with self.assertRaises(AuditError):
                with verified_scene(root,row,tmp):pass
if __name__=="__main__":
    unittest.main()
