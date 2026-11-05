"""Synthetic original Shader owner→same-instance export and ShaderLab metadata guards."""
import copy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts import t3_material_shader_same_export as m


class ShaderSameExport(unittest.TestCase):
    def fixture(self):
        src={(m.OWNER,i):("sharedassets0.assets",((i-1)%10)+1) for i in range(1,42)}
        shaders=set(src.values())
        w1={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        b02={"schema_version":1,"export_instance":"a"*32,"objects":[
            {"class_id":28,"source":{"owner":"sharedassets6.assets","path_id":700},
             "export":{"file_id":2800000,"guid":"f"*32,"type":3}}]}
        pointers={}
        for j in range(1,11):
            # Distinct GUIDs for distinct source Shader objects
            g=f"{j:032x}"
            w1["objects"].append({"class_id":48,
                "source":{"owner":"sharedassets0.assets","path_id":j},
                "collection_type":"SyntheticShaderCollection","exportable":True,
                "export":{"file_id":4800000,"guid":g,"type":3}})
            pointers[j]=(4800000,g,"3")
        actual={}
        for i in range(1,42):
            key=(2100000+i,"b"*32,"3")
            j=((i-1)%10)+1
            w1["objects"].append({"class_id":21,"collection_type":"SyntheticMaterialCollection",
                "exportable":True,"source":{"owner":m.OWNER,"path_id":i},
                "export":{"file_id":2100000+i,"guid":"b"*32,"type":2},
                "shader_source":{"owner":"sharedassets0.assets","path_id":j},
                "shader_export":{"file_id":pointers[j][0],"guid":pointers[j][1],"type":3}})
            actual[key]=pointers[j]
        def fake_metadata(_assets, guids):
            return {"selected_shader_files":len(guids),"all_export_shader_files":len(guids),
                    "shaderlab_total_parsed_passes":len(guids)*2,
                    "shaderlab_passes_with_program_blocks":0,
                    "shaderlab_sources_with_programs":0,
                    "shaderlab_sources_with_no_passes":0,
                    "shaderlab_braces_balanced":len(guids)}
        return src,shaders,w1,b02,actual,Path("/fake/Assets"),fake_metadata
    def check(self,args=None):
        a=list(args or self.fixture())
        return m.selected_compare(*a[:-1],shader_meta_fn=a[-1])
    def test_41_original_material_to_10_typed_shader_exact_PPtr(self):
        r=self.check()
        self.assertEqual(r["status"],"SCOPED_ORIGINAL_SHADER_POINTER_AND_SHADERLAB_META_MATCH")
        self.assertEqual(r["actual_exported_material_shader_fields_exact"],41)
        self.assertEqual(r["selected_custom_ShaderLab_meta_targets"],10)
        self.assertFalse(r["original_Shader_program_variants_or_GPU_pixels_verified"])
    def test_wrong_original_shader_target_in_same_export_rejected(self):
        a=list(self.fixture());a[2]["objects"][-1]["shader_source"]={"owner":"sharedassets0.assets","path_id":999}
        with self.assertRaises(ValueError):self.check(a)
    def test_wrong_actual_yaml_shader_guid_rejected(self):
        a=list(self.fixture());a[4][(2100001,"b"*32,"3")]=(4800000,"e"*32,"3")
        with self.assertRaises(ValueError):self.check(a)
    def test_missing_original_shader_target_export_row_rejected(self):
        a=list(self.fixture());a[2]["objects"].pop(0)
        with self.assertRaises(ValueError):self.check(a)
    def test_missing_actual_Material_shader_document_rejected(self):
        a=list(self.fixture());a[4].pop((2100001,"b"*32,"3"))
        with self.assertRaises(ValueError):self.check(a)
    def test_mixed_export_instance_refused(self):
        a=list(self.fixture());a[3]["export_instance"]="d"*32
        with self.assertRaises(ValueError):self.check(a)
    def test_missing_custom_ShaderLab_meta_not_silent(self):
        a=list(self.fixture())
        def missing(assets,guids): return {"selected_shader_files":len(guids)-1}
        a[-1]=missing
        with self.assertRaises(ValueError):self.check(a)
    def test_export_shader_duplicate_GUID_collision_not_faithful(self):
        a=list(self.fixture());a[2]["objects"][1]["export"]=a[2]["objects"][0]["export"].copy()
        with self.assertRaises(ValueError):self.check(a)
    def test_real_shader_metadata_guids_and_ShaderLab_structural_not_device(self):
        with TemporaryDirectory() as tmp:
            assets=Path(tmp)/"Assets";assets.mkdir()
            gid="e"*32
            (assets/"t.shader").write_text('Shader "Synthetic" {SubShader {Pass {CGPROGRAM\nfloat4 f() {return 0;}\nENDCG}}}')
            (assets/"t.shader.meta").write_text("guid: "+gid+"\nShaderImporter:\n")
            r=m.shader_metadata(assets,{gid})
            self.assertEqual(r["selected_shader_files"],1)
            self.assertEqual(r["shaderlab_passes_with_program_blocks"],1)
            self.assertEqual(r["shaderlab_sources_with_programs"],1)
    def test_missing_meta_or_wrong_meta_guid_rejected(self):
        with TemporaryDirectory() as tmp:
            assets=Path(tmp)/"Assets";assets.mkdir()
            gid="e"*32
            (assets/"t.shader").write_text('Shader "Synthetic" {}')
            (assets/"t.shader.meta").write_text("guid: "+"d"*32+"\n")
            with self.assertRaises(ValueError):m.shader_metadata(assets,{gid})
    def test_no_private_original_ids_in_public_aggregate(self):
        r=str(self.check())
        self.assertNotIn("sharedassets0",r)
        self.assertNotIn("b"*32,r)
        self.assertNotIn("shader_source",r)
if __name__=="__main__":unittest.main()
