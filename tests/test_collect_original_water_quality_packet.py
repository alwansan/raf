import unittest
from types import SimpleNamespace
from scripts.collect_original_water_quality_packet import quality_script_identity

class QualityPacketTests(unittest.TestCase):
    def setUp(self):
        self.owner=SimpleNamespace(externals=[SimpleNamespace(path='archive:/globalgamemanagers.assets')])
        self.identity={'namespace':'UltimateWater','class':'WaterQualitySettings'}
        self.scripts={('globalgamemanagers.assets',7):self.identity}

    def test_resolves_typed_external_script_only(self):
        self.assertIs(quality_script_identity({'m_Script':{'m_FileID':1,'m_PathID':7}},self.owner,self.scripts),self.identity)
        for ptr in (None,{}, {'m_FileID':True,'m_PathID':7},{'m_FileID':2,'m_PathID':7}, {'m_FileID':1,'m_PathID':8}):
            self.assertIsNone(quality_script_identity({'m_Script':ptr},self.owner,self.scripts))

    def test_refuses_wrong_namespace_class_and_external_owner(self):
        for namespace,cls in (('Other','WaterQualitySettings'),('UltimateWater','Water')):
            scripts={('globalgamemanagers.assets',7):{'namespace':namespace,'class':cls}}
            self.assertIsNone(quality_script_identity({'m_Script':{'m_FileID':1,'m_PathID':7}},self.owner,scripts))
        self.owner.externals[0].path='../../unrelated.assets'
        self.assertIsNone(quality_script_identity({'m_Script':{'m_FileID':1,'m_PathID':7}},self.owner,self.scripts))

    def test_local_script_pointer_is_supported_without_external_guess(self):
        self.scripts[('resources.assets',7)]=self.identity
        self.assertIs(quality_script_identity({'m_Script':{'m_FileID':0,'m_PathID':7}},self.owner,self.scripts),self.identity)

if __name__=='__main__':unittest.main()
