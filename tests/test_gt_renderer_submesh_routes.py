"""Authored asymmetric triangle submeshes, real YAML/PNG, private trace fixture."""
from copy import deepcopy
from pathlib import Path
import json
import struct
import tempfile
import unittest
from types import SimpleNamespace as NS
from hashlib import sha256
from PIL import Image
import yaml

from scripts import gt_renderer_submesh_routes as routes
from scripts import patch_export_lineage
from scripts.b03_verify_renderer_material_links import audit as old_audit


def src(pid):return {"m_FileID":0,"m_PathID":pid}
def loc(fid):return {"fileID":fid}
def ext(fid,guid):return {"fileID":fid,"guid":guid,"type":2}
def guid(n):return f"ab{n:030x}"


class FixtureDumper(yaml.SafeDumper):
    def represent_mapping(self,tag,mapping,flow_style=None):
        if isinstance(mapping,dict) and set(mapping) in ({"fileID"},{"fileID","guid","type"}):
            flow_style=True
        return super().represent_mapping(tag,mapping,flow_style)


class OrderedRoutes(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.project=Path(self.tmp.name);self.assets=self.project/"Assets";self.assets.mkdir()
        self.owner="level1";self.objects={};self.docs={};self.mappings=[]
        self.scene=guid(100)
        self.mesh=guid(200)
        self.channels=[{"stream":0,"offset":0,"format":0,"dimension":3}]+[
            {"stream":0,"offset":0,"format":0,"dimension":0} for _ in range(3)]+[
            {"stream":0,"offset":12,"format":0,"dimension":2}]
        self.indices=struct.pack("<6H",0,1,2,0,2,1)
        tree={"m_VertexData":{"m_VertexCount":6,"m_Channels":self.channels},
              "m_IndexFormat":0,"m_IndexBuffer":list(self.indices),
              "m_SubMeshes":[{"firstByte":0,"indexCount":3,"topology":0,"baseVertex":0,"firstVertex":0,"vertexCount":3},
                             {"firstByte":6,"indexCount":3,"topology":0,"baseVertex":3,"firstVertex":3,"vertexCount":3}]}
        exported=deepcopy(tree);exported["m_IndexBuffer"]=self.indices.hex()
        self.add(43,4,self.mesh,4300000,routes.mesh_layout(tree),exported)
        self.add(1,1,self.scene,100,{"m_Component":[{"component":src(2)},{"component":src(3)}]},
                 {"m_Component":[{"component":loc(101)},{"component":loc(102)}]})
        self.add(33,2,self.scene,101,{"m_GameObject":src(1),"m_Mesh":src(4)},
                 {"m_GameObject":loc(100),"m_Mesh":ext(4300000,self.mesh)})
        self.add(23,3,self.scene,102,{"m_GameObject":src(1),"m_Materials":[src(5),src(6)]},
                 {"m_GameObject":loc(100),"m_Materials":[ext(2100000,guid(5)),ext(2100000,guid(6))]})
        for n in (5,6):
            self.add(48,n+10,guid(n+10),4800000,None,None)
            self.add(28,n+20,guid(n+20),2800000,None,None)
            uv={"m_Scale":{"x":1.0,"y":2.0},"m_Offset":{"x":0.125,"y":0.25}}
            old={"m_Texture":src(n+20),**uv}
            new={"m_Texture":ext(2800000,guid(n+20)),**deepcopy(uv)}
            self.add(21,n,guid(n),2100000,
                {"m_Shader":src(n+10),"m_SavedProperties":{"m_TexEnvs":[["_MainTex",old]]}},
                {"m_Shader":ext(4800000,guid(n+10)),"m_SavedProperties":{"m_TexEnvs":[{"_MainTex":new}]}})
            sh=self.assets/f"shader{n}.shader"
            sh.write_text('Shader "Authored/Test" { SubShader { Pass {} } }')
            self.meta(sh,guid(n+10),"ShaderImporter:\n")
            p=self.assets/f"tex{n}.png";Image.new("RGBA",(2,2),(n,20,30,255)).save(p)
            self.meta(p,guid(n+20),"TextureImporter:\n  textureShape: 1\n")

    def meta(self,p,g,tail=""):
        Path(str(p)+".meta").write_text("guid: "+g+"\n"+tail)
    def add(self,cls,pid,g,fid,source,export):
        self.objects[(self.owner,pid)]=(cls,source)
        if export is not None:self.docs[(g,fid)]=(cls,export)
        self.mappings.append({"class_id":cls,"source":{"owner":self.owner,"path_id":pid},
            "export":{"guid":g,"file_id":fid,"type":2},"exportable":True})
    def write(self):
        grouped={}
        for (g,fid),(cls,tree) in self.docs.items():
            grouped.setdefault(g,[]).append((fid,cls,tree))
        for g,rows in grouped.items():
            path=self.assets/(g+(".mat" if rows[0][1]==21 else ".asset"))
            text="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
            for fid,cls,tree in rows:
                text+=f"--- !u!{cls} &{fid}\n"+yaml.dump({routes.CLASSES[cls]:tree},Dumper=FixtureDumper,sort_keys=False,default_flow_style=False)
            path.write_text(text);self.meta(path,g)
    def run_audit(self):
        self.write()
        instance="f"*32
        a={"schema_version":1,"export_instance":instance,"objects":[r for r in self.mappings if r["class_id"] in {21,48,28}]}
        b={"schema_version":1,"export_instance":instance,"meshes":[{k:v for k,v in r.items() if k!="class_id"} for r in self.mappings if r["class_id"]==43]}
        c={"schema_version":1,"export_instance":instance,"components":[r for r in self.mappings if r["class_id"] in routes.COMPONENTS]}
        m=routes.traces(a,b,c);files,docs=routes.actual_index(self.project,m)
        result=routes.compare(self.objects,{self.owner:[]},m,files,docs)
        self.assertNotIn("_MainTex",json.dumps(result))
        self.assertNotIn(self.scene,json.dumps(result))
        return result
    def test_actual_yaml_ordered_two_submeshes(self):
        result=self.run_audit()
        self.assertTrue(result["selected_renderer_routes_preserved"])
        self.assertEqual(result["counts"]["complete_submesh_material_identity_routes"],2)
        self.assertFalse(result["vertex_payload_or_UV_samples_verified"])
    def test_swap_two_existing_materials_rejected_even_equal_population(self):
        self.docs[(self.scene,102)][1]["m_Materials"].reverse()
        result=self.run_audit()
        self.assertFalse(result["selected_renderer_routes_preserved"])
        self.assertEqual(result["reason_counts"]["ordered_pointer_target_mismatch"],1)
        old=old_audit(self.project)
        self.assertTrue(old["local_reference_structure_valid"])
        self.assertTrue(old["all_material_slots_authenticated"])
    def test_uv_descriptor_drift(self):
        self.docs[(self.mesh,4300000)][1]["m_VertexData"]["m_Channels"][4]["offset"]=16
        self.assertIn("mesh_index_submesh_or_UV_layout_drift",self.run_audit()["reason_counts"])
    def test_index_order_drift(self):
        self.docs[(self.mesh,4300000)][1]["m_IndexBuffer"]=struct.pack("<6H",0,2,1,0,2,1).hex()
        self.assertIn("mesh_index_submesh_or_UV_layout_drift",self.run_audit()["reason_counts"])
    def test_submesh_wrong_base_vertex(self):
        self.docs[(self.mesh,4300000)][1]["m_SubMeshes"][1]["baseVertex"]=0
        self.assertIn("submesh_index_outside_vertex_range",self.run_audit()["reason_counts"])
    def test_wrong_shader_valid_identity(self):
        self.docs[(guid(5),2100000)][1]["m_Shader"]=ext(4800000,guid(16))
        self.assertIn("ordered_pointer_target_mismatch",self.run_audit()["reason_counts"])
    def test_wrong_texture_valid_identity(self):
        self.docs[(guid(5),2100000)][1]["m_SavedProperties"]["m_TexEnvs"][0]["_MainTex"]["m_Texture"]=ext(2800000,guid(26))
        self.assertIn("ordered_pointer_target_mismatch",self.run_audit()["reason_counts"])
    def test_uv_transform_drift(self):
        self.docs[(guid(5),2100000)][1]["m_SavedProperties"]["m_TexEnvs"][0]["_MainTex"]["m_Offset"]["x"]=0.5
        self.assertEqual(self.objects[(self.owner,5)][1]["m_SavedProperties"]["m_TexEnvs"][0][1]["m_Offset"]["x"],0.125)
        self.assertIn("material_texenv_UV_drift",self.run_audit()["reason_counts"])
    def test_missing_mesh_filter_membership(self):
        self.docs[(self.scene,100)][1]["m_Component"].pop(0)
        self.assertIn("mesh_filter_gameobject_membership_mismatch",self.run_audit()["reason_counts"])
    def test_missing_renderer_trace_unproven(self):
        self.mappings=[r for r in self.mappings if r["class_id"]!=23]
        result=self.run_audit()
        self.assertIn("missing_source_export_trace",result["reason_counts"])
    def test_extra_material_slot_not_guessed(self):
        self.objects[(self.owner,3)][1]["m_Materials"].append(src(6))
        self.docs[(self.scene,102)][1]["m_Materials"].append(ext(2100000,guid(6)))
        self.assertIn("non_one_to_one_submesh_material_policy",self.run_audit()["reason_counts"])
    def test_wrong_exportable_type0_not_promoted(self):
        next(r for r in self.mappings if r["class_id"]==23)["export"]["type"]=0
        self.assertIn("unproven_exportable_global_target",self.run_audit()["reason_counts"])
    def test_skinned_renderer_direct_mesh_path(self):
        source=self.objects[(self.owner,3)][1]
        source["m_Mesh"]=src(4)
        self.objects[(self.owner,3)]=(137,source)
        cls,actual=self.docs[(self.scene,102)]
        actual["m_Mesh"]=ext(4300000,self.mesh)
        self.docs[(self.scene,102)]=(137,actual)
        next(r for r in self.mappings if r["class_id"]==23)["class_id"]=137
        self.objects[(self.owner,1)][1]["m_Component"].pop(0)
        self.docs[(self.scene,100)][1]["m_Component"].pop(0)
        del self.objects[(self.owner,2)]
        del self.docs[(self.scene,101)]
        self.mappings=[r for r in self.mappings if r["class_id"]!=33]
        self.assertTrue(self.run_audit()["selected_renderer_routes_preserved"])

    def test_original_owner_byte_snapshot_passed_to_parser_and_drift_rejected(self):
        root=self.project/"authored-source";root.mkdir()
        raw=b"authored owner bytes; metadata fixture only"
        p=root/self.owner;p.write_bytes(raw)
        digest=sha256(raw).hexdigest()
        seen=[]
        def loader(data):
            self.assertIs(type(data),bytes)
            self.assertEqual(data,raw);seen.append(True)
            obj=NS(type=NS(name="MeshRenderer"),path_id=3,
                   read_typetree=lambda:self.objects[(self.owner,3)][1])
            return NS(file=NS(objects={3:obj},externals=[]))
        records={"Raft_Data/"+self.owner:("plain",len(raw),digest)}
        objects,externals=routes.source_records(root,records,[self.owner],loader=loader)
        self.assertEqual(objects,{(self.owner,3):self.objects[(self.owner,3)]})
        self.assertEqual(externals,{self.owner:[]})
        p.write_bytes(b"x"+raw[1:])
        with self.assertRaisesRegex(ValueError,"SHA_mismatch"):
            routes.source_records(root,records,[self.owner],loader=loader)
        self.assertEqual(seen,[True])

    def test_valid_but_wrong_mesh_filter_gameobject(self):
        self.add(1,9,guid(109),900,{"m_Component":[]},{"m_Component":[]})
        self.docs[(self.scene,101)][1]["m_GameObject"]=ext(900,guid(109))
        result=self.run_audit()
        self.assertFalse(result["selected_renderer_routes_preserved"])
        self.assertIn("ordered_pointer_target_mismatch",result["reason_counts"])

    def test_native_wrong_class_cannot_pass_imported_texture_fallback(self):
        p=self.assets/"tex5.png"
        p.unlink();Path(str(p)+".meta").unlink()
        wrong=self.assets/"wrong.asset"
        wrong.write_text("%YAML 1.1\n--- !u!84 &2800000\nRenderTexture:\n  m_Width: 2\n")
        self.meta(wrong,guid(25))
        self.assertIn("export_target_wrong_class",self.run_audit()["reason_counts"])

    def test_mixed_instance_refused(self):
        a={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        b={"schema_version":1,"export_instance":"b"*32,"meshes":[]}
        c={"schema_version":1,"export_instance":"a"*32,"components":[]}
        with self.assertRaisesRegex(ValueError,"mixed_or_invalid_export_instance"):routes.traces(a,b,c)
    def test_trace_hook_same_instance_opt_in(self):
        raw=Path("android-port/Experiments/ExportLineage/RaftExportLineage.cs").read_bytes()
        result=patch_export_lineage.add_renderer_lineage(raw)
        self.assertEqual(result.count(b'json.WriteString("export_instance", instance)'),3)
        self.assertIn(b'asset.ClassID is not (1 or 23 or 33 or 137)',result)
        self.assertIn(b'RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE',result)
        self.assertEqual(result.count(b'CaptureRendererComponents('),2)
        self.assertNotIn(b'RAFT_PRIVATE_EXPORT_RENDERER_LINEAGE',patch_export_lineage.add_mesh_lineage(raw))
        start=result.index(b"private static void CaptureRendererComponents(")
        end=result.index(b"private static void Identity(",start)
        capture=result[start:end]
        self.assertIn(b"collection.ExportableAssets",capture)
        self.assertIn(b"if (!collection.Exportable)",capture)
        self.assertNotIn(b"collection.Assets)",capture)

if __name__=="__main__":unittest.main()
