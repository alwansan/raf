import copy
import unittest
from types import SimpleNamespace
from tools.gt_particle108_redirect_target import audit as a

class Redirect(unittest.TestCase):
    def fixture(self):
        targets={("resources.assets",101):5,("sharedassets0.assets",102):4,("sharedassets1.assets",103):1}
        row={"source":{"owner":"Raft_Data/sharedassets1.assets","path_id":103},
             "collection_implementation":a.REDIRECT,"container_export_pointer_captured":True,
             "container_export":{"file_id":123,"guid":next(iter(a.ENGINE_FILES)),"type":0},
             "same_texture_sprite_group":True,"sprite_group_count":0}
        return targets,{"nonexportable_texture_sources":[row]}
    def test_exact_builtin_pointer_and_group(self):
        t,b=self.fixture()
        key,ptr,group,count=a.selected_redirect(t,b)
        self.assertEqual(key,("sharedassets1.assets",103))
        self.assertEqual(ptr[0],123)
        self.assertTrue(group)
        self.assertEqual(count,0)
    def test_wrong_type_guid_and_class(self):
        for field,value in (("type",2),("guid","a"*32),("file_id",0)):
            t,b=self.fixture()
            b["nonexportable_texture_sources"][0]["container_export"][field]=value
            with self.assertRaises(ValueError): a.selected_redirect(t,b)
        t,b=self.fixture()
        b["nonexportable_texture_sources"][0]["collection_implementation"]="AssetRipper.Export.UnityProjects.SingleRedirectExportCollection"
        with self.assertRaises(ValueError): a.selected_redirect(t,b)
    def test_duplicate_and_missing_group(self):
        t,b=self.fixture()
        b["nonexportable_texture_sources"].append(copy.deepcopy(b["nonexportable_texture_sources"][0]))
        with self.assertRaises(ValueError): a.selected_redirect(t,b)
        t,b=self.fixture()
        del b["nonexportable_texture_sources"][0]["sprite_group_count"]
        with self.assertRaises(ValueError): a.selected_redirect(t,b)
    def test_numeric_metadata_only(self):
        t=SimpleNamespace(m_Width=2,m_Height=3,m_TextureFormat=12,m_TextureDimension=2,
                          m_ImageCount=1,m_MipCount=2,m_Name="PRIVATE",m_LightmapFormat=0)
        d=a.metadata(t)
        self.assertEqual(d["MipCount"],2)
        self.assertNotIn("Name",d)
        self.assertNotIn("PRIVATE",str(d))
        t.m_Width="2"
        with self.assertRaises(ValueError): a.metadata(t)
if __name__=="__main__":
    unittest.main()
