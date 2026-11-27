"""Independent source-only V12 controls, distinct from V9 and V11."""
import unittest
from copy import deepcopy
import yaml
from scripts import gt_imported_dxt5nm_route_importer as v12
from scripts import gt_imported_png_route_importer as v9
from test_gt_imported_png_route_importer import source,meta,PTR
from test_gt_imported_bc3_route_pixels import tree as bc3_tree

def normal_source():
    return dict(source(),**{k:v for k,v in bc3_tree().items() if k.startswith("m_") and k not in ("m_LightmapFormat","m_ColorSpace")},m_LightmapFormat=3,m_ColorSpace=0)

def normal_meta():
    d=meta();i=d["TextureImporter"];i.update(textureType=1,textureFormat=12,
        bumpmap=dict(heightScale=.25,convertToNormalMap=0,externalNormalMap=0,normalMapFilter=0))
    i["mipmaps"]["sRGBTexture"]=0
    del i["swizzle"]
    return d

def check(s=None,d=None):
    return v12.compare(v12.source_proof(normal_source() if s is None else s),yaml.safe_dump(normal_meta() if d is None else d),PTR)

class NormalImporter(unittest.TestCase):
    def test_supported_and_swizzle_unknown(self):
        self.assertEqual(check(),(6,9,17,1,3))
        d=normal_meta();d["TextureImporter"]["swizzle"]=50462976
        self.assertEqual(check(d=d),(6,9,18,0,3))
    def test_separate_typed_scope(self):
        self.assertIs(type(v12.source_proof(normal_source())),v12.Proof)
        with self.assertRaises(v9.Unproven):v9.compare(v12.source_proof(normal_source()),yaml.safe_dump(meta()),PTR)
        with self.assertRaises(v9.Unproven):v12.compare(v9.source_proof(source()),yaml.safe_dump(normal_meta()),PTR)
    def test_invalid_source(self):
        for k,v in (("m_LightmapFormat",0),("m_ColorSpace",1),("m_TextureFormat",4),("m_CompleteImageSize",79),("m_IsReadable",2),("m_StreamingMipmapsPriority",2**31)):
            with self.subTest(k=k):
                s=normal_source();s[k]=v
                self.assertIsInstance(v12.safe_source(s),str)
    def test_required_source_fields(self):
        for k in v9.SOURCE_FIELDS:
            s=normal_source();del s[k]
            with self.assertRaises(v9.Unproven):check(s)
    def test_single_mip_and_historical_flag(self):
        s=normal_source();s.update(m_MipCount=1,m_CompleteImageSize=64)
        d=normal_meta();d["TextureImporter"]["mipmaps"]["enableMipMap"]=0
        self.assertEqual(check(s,d),(6,9,17,1,3))
        s["m_MipMap"]=True
        with self.assertRaises(v9.Mismatch):check(s,d)
    def test_sampler_controls(self):
        for k,v in (("filterMode",2),("aniso",3),("mipBias",.25),("wrapU",1),("wrapV",1),("wrapW",2)):
            d=normal_meta();d["TextureImporter"]["textureSettings"][k]=v
            with self.assertRaises(v9.Mismatch):check(d=d)
    def test_sentinel_and_missing(self):
        for k,v in (("mipBias",-100),("filterMode",-1)):
            d=normal_meta();d["TextureImporter"]["textureSettings"][k]=v
            with self.assertRaises(v9.Unproven):check(d=d)
        d=normal_meta();del d["TextureImporter"]["textureSettings"]["wrapW"]
        with self.assertRaises(v9.Unproven):check(d=d)
    def test_source_mapping_controls(self):
        for k,v in (("isReadable",0),("streamingMipmaps",1),("streamingMipmapsPriority",3),("textureFormat",4),("maxTextureSize",4096)):
            d=normal_meta();d["TextureImporter"][k]=v
            with self.assertRaises(v9.Mismatch):check(d=d)
        for k,v in (("enableMipMap",0),("sRGBTexture",1)):
            d=normal_meta();d["TextureImporter"]["mipmaps"][k]=v
            with self.assertRaises(v9.Mismatch):check(d=d)
    def test_bumpmap_policy_and_defaults(self):
        for k,v in (("heightScale",.5),("convertToNormalMap",1),("externalNormalMap",1),("normalMapFilter",1)):
            d=normal_meta();d["TextureImporter"]["bumpmap"][k]=v
            with self.assertRaises(v9.Mismatch):check(d=d)
            del d["TextureImporter"]["bumpmap"][k]
            with self.assertRaises(v9.Unproven):check(d=d)
    def test_swizzle_explicit_wrong_or_null(self):
        d=normal_meta();d["TextureImporter"]["swizzle"]=0
        with self.assertRaises(v9.Mismatch):check(d=d)
        d["TextureImporter"]["swizzle"]=None
        with self.assertRaises(v9.Unproven):check(d=d)
    def test_policy_and_platform(self):
        d=normal_meta();d["TextureImporter"]["alphaIsTransparency"]=0
        with self.assertRaises(v9.Mismatch):check(d=d)
        d=normal_meta();d["TextureImporter"]["platformSettings"][0]["overridden"]=1
        with self.assertRaises(v9.Mismatch):check(d=d)
    def test_exact_signed_zero(self):
        s=normal_source();s["m_TextureSettings"]["m_MipBias"]=-0.0
        d=normal_meta();d["TextureImporter"]["textureSettings"]["mipBias"]=0.0
        with self.assertRaises(v9.Mismatch):check(s,d)
        raw=yaml.safe_dump(d).replace("mipBias: 0.0","mipBias: -0")
        self.assertEqual(v12.compare(v12.source_proof(s),raw,PTR),(6,9,17,1,3))
