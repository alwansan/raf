"""Source-only authored V9 controls. Actual exporter witness separate."""
import unittest
from copy import deepcopy
import yaml
from scripts import gt_imported_png_route_importer as v9
from scripts import gt_imported_png_route_pixels as v8

GUID="abcdef0123456789abcdef0123456789"
PTR=(GUID,2800000,3)

def source():
    return dict(m_Width=2,m_Height=2,m_TextureFormat=4,m_MipCount=2,m_ImageCount=1,
                m_TextureDimension=2,m_CompleteImageSize=20,m_ColorSpace=1,m_IsReadable=True,
                m_StreamingMipmaps=0,m_StreamingMipmapsPriority=-2,m_LightmapFormat=0,
                m_TextureSettings=dict(m_FilterMode=1,m_Aniso=2,m_MipBias=-.625,
                                       m_WrapU=0,m_WrapV=2,m_WrapW=3))

def meta():
    return dict(fileFormatVersion=2,guid=GUID,TextureImporter=dict(textureShape=1,textureType=0,
        textureSettings=dict(serializedVersion=2,filterMode=1,aniso=2,mipBias=-.625,wrapU=0,wrapV=2,wrapW=3),
        mipmaps=dict(enableMipMap=1,sRGBTexture=1),isReadable=1,streamingMipmaps=0,streamingMipmapsPriority=-2,
        textureFormat=4,maxTextureSize=2048,nPOTScale=0,alphaUsage=1,alphaIsTransparency=1,swizzle=50462976,
        compressionQuality=50,platformSettings=[dict(serializedVersion=3,buildTarget="DefaultTexturePlatform",
            maxTextureSize=2048,textureFormat=-1,textureCompression=2,compressionQuality=50,resizeAlgorithm=0,
            crunchedCompression=0,allowsAlphaSplitting=0,overridden=0,androidETC2FallbackOverride=0,
            forceMaximumCompressionQuality_BC6H_BC7=0)]))

def check(tree=None,doc=None,ptr=PTR):
    return v9.compare(v9.source_proof(source() if tree is None else tree),yaml.safe_dump(meta() if doc is None else doc),ptr)

class ImporterTests(unittest.TestCase):
    def test_exact(self):
        self.assertEqual(check(),(6,9,17))
    def test_required_source(self):
        for k in v9.SOURCE_FIELDS:
            with self.subTest(k=k):
                s=source();del s[k]
                with self.assertRaises(v9.Unproven):check(s)
    def test_color_enum_unknown(self):
        s=source();s["m_ColorSpace"]=-1
        with self.assertRaises(v9.Unproven):check(s)
    def test_bool_not_truthiness(self):
        s=source();s["m_IsReadable"]=2
        with self.assertRaises(v9.Unproven):check(s)
    def test_single_mip(self):
        s=source();s.update(m_MipCount=1,m_CompleteImageSize=16)
        d=meta();d["TextureImporter"]["mipmaps"]["enableMipMap"]=0
        self.assertEqual(check(s,d),(6,9,17))
        s["m_MipMap"]=True
        with self.assertRaises(v9.Mismatch):check(s,d)
    def test_sampler_drift(self):
        for k,val in (("filterMode",2),("aniso",3),("mipBias",.25),("wrapU",1),("wrapV",1),("wrapW",2)):
            with self.subTest(k=k):
                d=meta();d["TextureImporter"]["textureSettings"][k]=val
                with self.assertRaises(v9.Mismatch):check(doc=d)
    def test_sentinel(self):
        for k,val in (("mipBias",-100),("filterMode",-1),("aniso",-1),("wrapU",-1)):
            with self.subTest(k=k):
                d=meta();d["TextureImporter"]["textureSettings"][k]=val
                self.assertIn("sampler_fields_present",v8.importer(yaml.safe_dump(d),PTR))
                with self.assertRaisesRegex(v9.Unproven,"sampler_default"):check(doc=d)
    def test_missing_and_legacy(self):
        for k in v9.SAMPLER_FIELDS:
            d=meta();del d["TextureImporter"]["textureSettings"][k]
            with self.assertRaises(v9.Unproven):check(doc=d)
        d=meta();d["TextureImporter"]["textureSettings"]["wrapMode"]=1
        with self.assertRaises(v9.Unproven):check(doc=d)
    def test_signed_zero(self):
        s=source();s["m_TextureSettings"]["m_MipBias"]=-0.0
        d=meta();d["TextureImporter"]["textureSettings"]["mipBias"]=0.0
        with self.assertRaises(v9.Mismatch):check(s,d)
        raw=yaml.safe_dump(d).replace("mipBias: 0.0","mipBias: -0")
        self.assertEqual(v9.compare(v9.source_proof(s),raw,PTR),(6,9,17))
    def test_exact_float32(self):
        d=meta();d["TextureImporter"]["textureSettings"]["mipBias"]=-.625000001
        self.assertEqual(check(doc=d),(6,9,17))
    def test_source_mapping_drift(self):
        for k in ("isReadable","streamingMipmaps","streamingMipmapsPriority","textureFormat","maxTextureSize"):
            d=meta();d["TextureImporter"][k]+=1
            with self.assertRaises(v9.Mismatch):check(doc=d)
        for k in ("enableMipMap","sRGBTexture"):
            d=meta();d["TextureImporter"]["mipmaps"][k]=0
            with self.assertRaises(v9.Mismatch):check(doc=d)
    def test_policy_drift(self):
        for k in ("nPOTScale","alphaUsage","alphaIsTransparency","swizzle","compressionQuality"):
            d=meta();d["TextureImporter"][k]+=1
            with self.assertRaises(v9.Mismatch):check(doc=d)
    def test_platform_policy(self):
        for k in ("textureFormat","textureCompression","overridden","crunchedCompression","maxTextureSize"):
            d=meta();d["TextureImporter"]["platformSettings"][0][k]+=1
            with self.assertRaises(v9.Mismatch):check(doc=d)
        d=meta();d["TextureImporter"]["platformSettings"].append(deepcopy(d["TextureImporter"]["platformSettings"][0]))
        with self.assertRaises(v9.Unproven):check(doc=d)
    def test_missing_is_unknown(self):
        d=meta();del d["TextureImporter"]["alphaUsage"]
        with self.assertRaises(v9.Unproven):check(doc=d)
    def test_wrong_guid(self):
        with self.assertRaises(v9.Unproven):check(ptr=("1234567890abcdef1234567890abcdef",2800000,3))
    def test_duplicate_keys(self):
        raw=yaml.safe_dump(meta()).replace("  alphaUsage: 1","  alphaUsage: 1\n  alphaUsage: 1")
        with self.assertRaises(v9.Unproven):v9.compare(v9.source_proof(source()),raw,PTR)
