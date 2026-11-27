"""Actual authored v22 source + authored native multi-document YAML.

Only the original six-scene census and immutable original pin constants are
replaced with authored equivalents. No injected Texture2D parser, decoder,
pixel comparator, lineage join, B05 parser or local document reader.
"""
from copy import deepcopy
from hashlib import sha1,sha256
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from tools.gt_authored_mesh_binary import witness as w
from tools.gt_authored_serialized_renderer_route import witness as binary
from tools.gt_authored_external_pptr_route import witness as ext
from tools.gt_authored_external_png_keywords import witness as kw
from tools.gt_authored_external_bc3_normal import witness as compressed
from scripts import gt_particle108_export_alpha_diagnostic as alpha
from scripts import gt_particle108_source_pixel_parity as source
from scripts import gt_particle108_local_texture_document as local
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs,exported_texenvs

OWNER="authored-particle.assets"
GUID="d"*32
ZERO="0"*32
ANCHOR=123
PROVIDER="authored-particle.resS"
SLOTS=(1,2,3,1,2,3,1,2,3,1)
EXTERNAL={1:"a"*32,2:"b"*32}
RGBA=bytes((11,23,37,0, 53,71,89,1, 97,113,131,64,
            149,163,181,127, 197,211,223,254, 239,251,17,255))
LOWER=bytes((12,34,56,78))
HEADER="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"

def pin(data):
    return len(data),sha256(data).hexdigest()

def flip_raw(raw,width,height):
    stride=width*4
    return b"".join(raw[y*stride:(y+1)*stride] for y in reversed(range(height)))

class LocalDocumentPixels(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.original=self.root/"source";self.data=self.original/"Raft_Data"
        self.data.mkdir(parents=True)
        self.project=self.root/"project";self.assets=self.project/"Assets"
        self.assets.mkdir(parents=True)
        self.doc=self.assets/"embedded.asset";self.meta=self.assets/"embedded.asset.meta"
        self.manifest=self.root/"manifest.tsv";self.trace_path=self.root/"trace.json"
        self.reports={}
        self.build()

    def build(self,mode="rgba",*,inline=False,converted=False):
        schemas,objects=binary.fixture()
        texture=objects[821];mat=objects[811]
        ids={1:28,2:28,3:28,801:48,**{100+i:21 for i in range(5)}}
        authored={801:deepcopy(objects[801])}
        source_bytes={1:bytes((11,23,37,0, 53,71,89,128, 97,113,131,64,149,163,181,255)),
                      2:bytes((31,13,17,255, 73,17,98,1, 9,13,31,254, 14,63,81,0))}
        for i,raw in source_bytes.items():
            t=deepcopy(texture)
            t.update(m_Name="Authored texture "+str(i),m_Width=2,m_Height=2,m_TextureFormat=4,
                     m_CompleteImageSize=16,m_MipCount=1,m_LightmapFormat=0,
                     m_StreamData=dict(path="",offset=0,size=0))
            t["image data"]=list(raw);authored[i]=t
            p=self.assets/f"tex{i}.png"
            Image.frombytes("RGBA",(2,2),flip_raw(raw,2,2)).save(p)
            p.with_suffix(".png.meta").write_text(
                f"fileFormatVersion: 2\nguid: {EXTERNAL[i]}\nTextureImporter:\n  textureShape: 1\n  alphaIsTransparency: 1\n")
        if mode=="rgba":
            self.width,self.height,self.fmt=3,2,4
            top,lower=RGBA,LOWER
            self.expected=Image.frombytes("RGBA",(3,2),flip_raw(top,3,2))
        else:
            self.width,self.height,self.fmt=5,7,12
            top,lower=compressed.TOP[compressed.A],compressed.LOWER
            self.expected=compressed.independent_packed(top)
        self.payload=top+lower
        self.provider=b"PREFIX!"+self.payload+b"TRAILER!"
        (self.data/PROVIDER).write_bytes(self.provider)
        t=deepcopy(texture)
        t.update(m_Name="Authored local texture",m_Width=self.width,m_Height=self.height,
                 m_TextureFormat=self.fmt,m_CompleteImageSize=len(self.payload),m_MipCount=2,
                 m_LightmapFormat=0,m_ColorSpace=0,m_StreamData=dict(
                     path="" if inline else "archive:/CAB-authored/"+PROVIDER,
                     offset=0 if inline else 7,size=0 if inline else len(self.payload)))
        t["image data"]=list(self.payload) if inline else [];authored[3]=t
        self.trace={"schema_version":1,"export_instance":"f"*32,"objects":[]}
        for i in range(5):
            m=deepcopy(mat);m["m_Name"]="Authored material "+str(i)
            m["m_Shader"]=ext.ptr(0,801)
            m["m_SavedProperties"]["m_TexEnvs"]=[
                (f"_Texture{j}",{"m_Texture":ext.ptr(0,SLOTS[2*i+j]),"m_Scale":{"x":1.0,"y":.75},
                                 "m_Offset":{"x":.125,"y":.25}}) for j in range(2)]
            authored[100+i]=m
            self.trace["objects"].append(self.row(21,100+i,2100000+i,GUID,2))
        for i in (1,2,3):
            self.trace["objects"].append(self.row(28,i,ANCHOR if i==3 else 2800000,
                GUID if i==3 else EXTERNAL[i],2 if i==3 else 3))
        self.owner_bytes,self.object_rows=ext.serialize(schemas,ids,authored,[])
        (self.data/OWNER).write_bytes(self.owner_bytes)
        raw=("kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n"
             f"plain\t{len(self.provider)}\t{sha256(self.provider).hexdigest()}\t660\tRaft_Data/{PROVIDER}\n").encode()
        self.manifest.write_bytes(raw)
        self.manifest_blob=sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        # The census is from actual parsed authored objects, not fabricated
        # Texture2D trees; only the unrelated original scene selectors are stubbed.
        env=w.UnityPy.load(self.owner_bytes)
        self.assertEqual(env.file.header.version,22)
        self.assertEqual({p:o.type.value for p,o in env.file.objects.items()},ids)
        self.materials={(OWNER,100+i):normalize_texenvs(
            env.file.objects[100+i].read_typetree()["m_SavedProperties"]["m_TexEnvs"]) for i in range(5)}
        self.targets={}
        for slots in self.materials.values():
            for pointer,uv in slots.values():
                self.assertEqual(pointer[0],0)
                key=(OWNER,pointer[1]);self.targets[key]=self.targets.get(key,0)+1
        self.assertEqual(sum(self.targets.values()),10)
        self.assertEqual(len(self.targets),3)
        self.export_fmt=4 if converted else self.fmt
        self.export_mips=1 if converted else 2
        self.export_payload=flip_raw(self.expected.tobytes(),self.width,self.height) if converted else self.payload
        self.write_document()
        self.meta.write_text("fileFormatVersion: 2\nguid: "+GUID+"\nNativeFormatImporter:\n  mainObjectFileID: 2100000\n")
        self.trace_path.write_text(json.dumps(self.trace))

    def row(self,cls,pid,fid,guid,kind):
        return {"class_id":cls,"source":{"owner":OWNER,"path_id":pid},
                "export":{"file_id":fid,"guid":guid,"type":kind},"exportable":True}

    def write_document(self,*,payload=None,width=None,height=None,mips=None,fmt=None):
        text=HEADER
        for i in range(5):
            text+=f"--- !u!21 &{2100000+i}\nMaterial:\n  m_SavedProperties:\n    m_TexEnvs:\n"
            for j in range(2):
                t=SLOTS[2*i+j]
                ptr=f"{{fileID: {ANCHOR}}}" if t==3 else f"{{fileID: 2800000, guid: {EXTERNAL[t]}, type: 3}}"
                text+=f"    - _Texture{j}:\n        m_Texture: {ptr}\n"
                text+="        m_Scale: {x: 1, y: 0.75}\n        m_Offset: {x: 0.125, y: 0.25}\n"
        payload=self.export_payload if payload is None else payload
        text+=f"--- !u!28 &{ANCHOR}\nTexture2D:\n"
        fields={"m_Width":self.width if width is None else width,
                "m_Height":self.height if height is None else height,
                "m_TextureFormat":self.export_fmt if fmt is None else fmt,
                "m_MipCount":self.export_mips if mips is None else mips,
                "m_ImageCount":1,"m_TextureDimension":2,"m_CompleteImageSize":len(payload),
                "m_MipsStripped":0,"m_LightmapFormat":0,"m_ColorSpace":0}
        text+="".join(f"  {k}: {v}\n" for k,v in fields.items())
        text+=f"  m_PlatformBlob: []\n  image data: {len(payload)}\n  _typelessdata: {payload.hex()}\n"
        text+="  m_StreamData:\n    serializedVersion: 2\n    offset: 0\n    size: 0\n    path: \n"
        self.doc.write_text(text)

    def mutate(self,old,new):
        s=self.doc.read_text();self.assertIn(old,s);self.doc.write_text(s.replace(old,new,1))

    def audit(self,label=None):
        def census(*a,**kw):
            kw["private_local_texture_targets"].update(self.targets)
            kw["private_material_texenvs"].update(self.materials)
            return {"status":alpha.material_source.STATUS}
        before={p:p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with patch.object(source,"SHADER_OWNERS",{OWNER:pin(self.owner_bytes)}), \
             patch.object(source,"MANIFEST_BLOB",self.manifest_blob), \
             patch.object(alpha.material_source,"run",side_effect=census), \
             patch.object(alpha.texture_source,"run",return_value={"status":alpha.texture_source.STATUS,
                    "original_selected_typed_Texture2D28_targets":3}):
            report=alpha.audit(self.original,self.manifest,self.project,self.trace_path)
        self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        private=json.dumps(report)
        self.assertNotIn(OWNER,private);self.assertNotIn(GUID,private)
        self.assertNotIn(self.export_payload.hex(),private)
        self.assertFalse(report["source_original_all_three_Texture2D_as_exported_images_verified"])
        self.assertFalse(report["original_local_Type0_texture_has_exported_image_proof"])
        self.assertFalse(report["android_device_fire_pixels_verified"])
        if label and os.environ.get("GT_LOCAL_DOCUMENT_EVIDENCE"):
            out=Path(os.environ["GT_LOCAL_DOCUMENT_EVIDENCE"])/label
            out.mkdir(parents=True,exist_ok=False)
            (out/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
            if label in ("rgba32-compiled","bc3-compiled","bc3-converted","alpha-loss","vertical-flip"):
                shutil.copytree(self.original,out/"source")
                shutil.copytree(self.project,out/"project")
                shutil.copy2(self.manifest,out/"manifest.tsv")
                shutil.copy2(self.trace_path,out/"trace.json")
                (out/"source-pins.json").write_text(json.dumps({"owner":w.commit(self.owner_bytes),
                    "objects":self.object_rows,"provider":w.commit(self.provider),
                    "manifest_git_blob":self.manifest_blob},indent=2)+"\n")
        return report

    def check_exact(self,r,fmt,export_fmt,n):
        self.assertEqual(r["status"],alpha.LOCAL_COMPARED_STATUS)
        p=r["source_export_document_local_top_mip_parity"]
        self.assertEqual(p["status"],"EXACT_RGBA8",p)
        self.assertEqual((p["source_format"],p["serialized_export_format"]),(fmt,export_fmt))
        self.assertEqual(p["comparison"]["pixel_coordinates_compared"],n)
        self.assertTrue(p["document_snapshot_verified"])
        self.assertTrue(r["original_local_Type0_original_and_exported_pixels_compared"])
        self.assertTrue(r["original_local_Type0_texture_pixel_alpha_verified"])
        self.assertTrue(r["all_three_source_export_RGBA8_samples_equal"],r)
        self.assertEqual(r["source_export_byte_bound_top_mip_parity"]["exact_rgba8_targets"],2)
        self.assertEqual(r["same_export_original_Material_TexEnv_PPtr_slots_exact"],10)
        self.assertFalse(p["lower_mip_parity_proven"])

    def check_unproved(self,reason,label=None):
        r=self.audit(label)
        p=r["source_export_document_local_top_mip_parity"]
        self.assertEqual(p["status"],"UNPROVEN",p)
        self.assertEqual(p["reason"],reason,p)
        self.assertFalse(r["all_three_source_export_RGBA8_samples_equal"])
        self.assertEqual(r["source_export_byte_bound_top_mip_parity"]["exact_rgba8_targets"],2)
        return r

    def test_real_rgba32_stream_both_typetree_backends(self):
        boost=w.TypeTreeHelper.read_typetree_boost
        self.assertTrue(callable(boost))
        for name,cb in (("compiled",boost),("python",False)):
            with patch.object(w.TypeTreeHelper,"read_typetree_boost",cb):
                r=self.audit("rgba32-"+name)
                self.check_exact(r,4,4,6)
                self.assertEqual(r["source_export_document_local_top_mip_parity"]["source_payload_kind"],"stream")

    def test_real_bc3_stream_both_typetree_backends(self):
        self.build("bc3")
        boost=w.TypeTreeHelper.read_typetree_boost
        for name,cb in (("compiled",boost),("python",False)):
            with patch.object(w.TypeTreeHelper,"read_typetree_boost",cb):
                self.check_exact(self.audit("bc3-"+name),12,12,35)

    def test_real_bc3_source_to_rgba32_native_document(self):
        self.build("bc3",converted=True)
        self.check_exact(self.audit("bc3-converted"),12,4,35)

    def test_inline_source(self):
        self.build(inline=True)
        r=self.audit("inline")
        self.check_exact(r,4,4,6)
        self.assertEqual(r["source_export_document_local_top_mip_parity"]["source_payload_kind"],"inline")

    def test_lower_mip_only_changes_stay_outside_top_mip_claim(self):
        data=bytearray(self.export_payload);data[-1]^=1
        self.write_document(payload=bytes(data))
        self.check_exact(self.audit("lower-mip-only"),4,4,6)

    def test_actual_alpha_loss(self):
        data=bytearray(self.export_payload)
        data[3:24:4]=bytes((255,)*6)
        self.write_document(payload=bytes(data))
        r=self.audit("alpha-loss");p=r["source_export_document_local_top_mip_parity"]
        self.assertEqual(p["status"],"PIXEL_DRIFT")
        self.assertEqual(p["comparison"]["alpha_loss_pixels"],5)
        self.assertTrue(p["comparison"]["rgb_samples_equal"])
        self.assertTrue(r["texture_alpha_loss_from_original_proven"])
        self.assertEqual(r["texture_all_source_transparency_lost_in_export_targets"],1)
        self.assertFalse(r["all_three_source_export_RGBA8_samples_equal"])

    def test_vertical_rearrangement_not_net_alpha_loss(self):
        data=flip_raw(self.export_payload[:24],3,2)+self.export_payload[24:]
        self.write_document(payload=data)
        r=self.audit("vertical-flip");p=r["source_export_document_local_top_mip_parity"]
        self.assertEqual(p["status"],"PIXEL_DRIFT")
        self.assertTrue(p["comparison"]["alpha_vertical_flip_only_match"])
        self.assertEqual(p["comparison"]["alpha_loss_pixels"],0)
        self.assertFalse(r["texture_alpha_loss_from_original_proven"])

    def test_transparent_RGB_drift(self):
        data=bytearray(self.export_payload);data[0]^=1
        self.write_document(payload=bytes(data))
        r=self.audit("transparent-rgb-drift");p=r["source_export_document_local_top_mip_parity"]
        self.assertEqual(p["status"],"PIXEL_DRIFT")
        self.assertTrue(p["comparison"]["alpha_samples_equal"])
        self.assertEqual(p["comparison"]["rgb_mismatch_pixels"],1)
        self.assertFalse(r["all_three_source_export_RGBA8_samples_equal"])

    def test_dimension_change_no_coordinate_proof(self):
        self.write_document(payload=bytes(16),width=2,height=2,mips=1,fmt=4)
        r=self.audit("dimensions")
        self.assertEqual(r["source_export_document_local_top_mip_parity"]["status"],"DIMENSION_MISMATCH")
        self.assertFalse(r["original_local_Type0_original_and_exported_pixels_compared"])
        self.assertFalse(r["all_three_source_export_RGBA8_samples_equal"])

    def test_wrong_class_and_stripped(self):
        for bad in ("--- !u!117 &123","--- !u!28 &123 stripped"):
            self.write_document();self.mutate("--- !u!28 &123",bad)
            self.check_unproved("local_document_wrong_class_or_stripped","class-"+str(len(bad)))

    def test_duplicate_anchor(self):
        with self.doc.open("a") as f:f.write("--- !u!28 &123\nTexture2D: {}\n")
        with self.assertRaisesRegex(ValueError,"Duplicate anchor"):
            self.audit()

    def test_invalid_header_not_swallowed(self):
        with self.doc.open("a") as f:f.write("--- !u!28 &124 invalid\nTexture2D: {}\n")
        self.check_unproved("local_document_invalid_serialized_header","malformed-header")

    def test_duplicate_payload_key(self):
        self.mutate("  image data: 28","  image data: 28\n  image data: 28")
        self.check_unproved("local_document_duplicate_or_invalid_key","duplicate-payload")

    def test_bad_hex_and_size(self):
        self.mutate(self.export_payload.hex(),self.export_payload.hex()[:-2])
        self.check_unproved("local_export_payload_hex_mismatch","bad-hex")
        self.write_document();self.mutate("  image data: 28","  image data: 27")
        self.check_unproved("local_export_payload_length_mismatch","bad-length")

    def test_unpinned_export_provider_even_if_present(self):
        (self.assets/"fake.resS").write_bytes(self.export_payload)
        self.mutate("    path: \n","    path: fake.resS\n")
        self.check_unproved("local_export_stream_not_authenticated","export-provider")

    def test_source_provider_mutation(self):
        b=bytearray(self.provider);b[-1]^=1;(self.data/PROVIDER).write_bytes(b)
        self.check_unproved("pinned_pixel_provider_SHA_mismatch","stale-source-provider")

    def test_duplicate_global_guid_outside_material_docs(self):
        (self.assets/"alias.asset").write_text("not YAML")
        (self.assets/"alias.asset.meta").write_text("guid: "+GUID+"\n")
        self.check_unproved("local_document_duplicate_meta_guid","duplicate-guid")

    def test_other_trace_claims_global_local_anchor(self):
        self.trace["objects"].append(self.row(28,999,ANCHOR,GUID,2))
        self.trace_path.write_text(json.dumps(self.trace))
        self.check_unproved("local_texture_global_trace_collision","trace-collision")

    def test_unscoped_local_trace(self):
        self.trace["objects"][-1]["export"]={"file_id":ANCHOR,"guid":ZERO,"type":0}
        self.trace_path.write_text(json.dumps(self.trace))
        self.check_unproved("local_texture_document_route_unproved","unscoped-trace")

    def test_material_snapshot_rejoin_rejects_drift(self):
        before=self.doc.read_bytes()
        original=alpha.compare_local
        def altered(*args):
            self.mutate("m_Scale: {x: 1, y: 0.75}","m_Scale: {x: 1, y: 0.5}")
            try:return original(*args)
            finally:self.doc.write_bytes(before)
        with patch.object(alpha,"compare_local",side_effect=altered):
            self.check_unproved("local_document_material_snapshot_drift","snapshot-drift")

    def test_numeric_hex_lexeme_preserved_without_integer_coercion(self):
        body=("Texture2D:\n  m_Width: 1\n  m_Height: 1\n  m_TextureFormat: 4\n"
              "  m_MipCount: 1\n  m_ImageCount: 1\n  m_TextureDimension: 2\n"
              "  m_CompleteImageSize: 4\n  m_LightmapFormat: 0\n"
              "  image data: 4\n  _typelessdata: 00010203\n"
              "  m_StreamData: {path: '', offset: 0, size: 0}\n")
        image,fmt=local.decode_export_body(body)
        self.assertEqual((fmt,image.tobytes()),(4,b"\x00\x01\x02\x03"))

    def test_alias_and_unsupported_usage(self):
        self.mutate("  m_LightmapFormat: 0","  m_LightmapFormat: 3")
        self.check_unproved("local_texture_unsupported_usage","unsupported-usage")
        self.write_document();self.mutate("  m_Width: 3","  m_Width: &fake 3")
        self.check_unproved("local_document_yaml_alias_or_anchor","yaml-anchor")

if __name__=="__main__":
    unittest.main()
