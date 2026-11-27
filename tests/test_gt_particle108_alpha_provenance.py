"""Authored YAML and PNG integration tests for production Particle108 audit.

Only original source readers are replaced with authored metadata; actual
Material YAML parser, lineage join, image importer guard and PIL decoder run.
"""
from copy import deepcopy
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image

from scripts import gt_particle108_export_alpha_diagnostic as alpha


class AlphaProvenance(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / "project"
        self.assets = self.project / "Assets"
        self.assets.mkdir(parents=True)
        self.original = self.root / "authored-source"
        self.original.mkdir()
        self.trace_path = self.root / "trace.json"
        self.owner = "authored.assets"
        self.targets = {(self.owner, 1):4, (self.owner, 2):3, (self.owner, 3):3}
        self.source = {}
        self.trace = {"schema_version":1,"export_instance":"f"*32,"objects":[]}
        self.uv = (1.,1.,0.,0.)
        self.mat_slots = [1,2,3,1,2,3,1,2,3,1]
        self.local = set()
        self.overrides = {}
        for i in range(5):
            key=(self.owner,100+i)
            self.source[key]={f"_Texture{j}":((0,self.mat_slots[i*2+j]),self.uv) for j in range(2)}
            self.trace["objects"].append(self.row(21,100+i,2100000,f"{100+i:032x}",2))
        for i in range(1,4):
            self.trace["objects"].append(self.row(28,i,2800000,f"{i:032x}",3))
            image=Image.new("RGBA",(2,1),(20,10,5,255))
            image.putpixel((0,0),(0,0,0,0 if i==1 else 128))
            image.save(self.assets/f"tex{i}.png")
            (self.assets/f"tex{i}.png.meta").write_text(
                f"fileFormatVersion: 2\nguid: {i:032x}\nTextureImporter:\n"
                f"  textureShape: 1\n  alphaSource: {i-1}\n"
                "  alphaIsTransparency: 1\n  sRGBTexture: 1\n  mipmapEnabled: 1\n")

    def row(self,cls,pathid,fid,guid,kind):
        return {"class_id":cls,"source":{"owner":self.owner,"path_id":pathid},
                "export":{"file_id":fid,"guid":guid,"type":kind}}

    def write_project(self):
        for i in range(5):
            p=self.assets/f"mat{i}.mat"
            text="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n  m_SavedProperties:\n    m_TexEnvs:\n"
            for j in range(2):
                t=self.mat_slots[i*2+j]
                pointer=(123,"0"*32,0) if t in self.local else (2800000,f"{t:032x}",3)
                fid,guid,kind=self.overrides.get((i,j),pointer)
                text+=f"    - _Texture{j}:\n        m_Texture: {{fileID: {fid}, guid: '{guid}', type: {kind}}}\n"
                text+="        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n"
            p.write_text(text)
            (p.with_suffix(".mat.meta")).write_text(f"fileFormatVersion: 2\nguid: {100+i:032x}\n")
        self.trace_path.write_text(json.dumps(self.trace))

    def audit(self):
        self.write_project()
        def material(*args,**kwargs):
            kwargs["private_local_texture_targets"].update(self.targets)
            kwargs["private_material_texenvs"].update(self.source)
            return {"status":alpha.material_source.STATUS}
        before={p:p.read_bytes() for p in self.assets.rglob("*") if p.is_file()}
        try:
            with patch.object(alpha.material_source,"run",side_effect=material), \
                 patch.object(alpha.texture_source,"run",return_value={
                     "status":alpha.texture_source.STATUS,
                     "original_selected_typed_Texture2D28_targets":3}):
                return alpha.audit(self.original,self.root/"not-an-original-manifest",self.project,self.trace_path)
        finally:
            self.assertEqual(before,{p:p.read_bytes() for p in self.assets.rglob("*") if p.is_file()})

    def remove_trace(self, target):
        self.trace["objects"]=[r for r in self.trace["objects"]
                               if not (r["class_id"]==28 and r["source"]["path_id"]==target)]

    def test_real_yaml_png_complete_trace_and_importer_hazards(self):
        result=self.audit()
        self.assertEqual(result["status"],alpha.STATUS)
        self.assertEqual(result["same_export_original_Material_TexEnv_PPtr_slots_exact"],10)
        self.assertTrue(result["all_selected_texture_targets_independently_traced"])
        self.assertEqual(result["actual_exported_alpha_image_counts"]["nonopaque_source_image_alphaSource_none"],1)
        self.assertEqual(result["actual_exported_alpha_image_counts"]["nonopaque_source_image_alphaSource_input"],1)
        self.assertEqual(result["actual_exported_alpha_image_counts"]["nonopaque_source_image_alphaSource_grayscale"],1)
        self.assertFalse(result["correct_runtime_particle_shader_blend_proven"])

    def test_missing_direct_trace_does_not_authorize_inferred_texture(self):
        self.remove_trace(3)
        result=self.audit()
        self.assertEqual(result["status"],alpha.UNPROVEN_STATUS)
        self.assertEqual(result["same_export_original_Material_TexEnv_PPtr_slots_exact"],7)
        self.assertEqual(result["independently_traced_external_targets"],2)
        self.assertEqual(result["inferred_external_targets"],1)
        self.assertFalse(result["source_original_all_three_Texture2D_as_exported_images_verified"])

    def test_missing_trace_cannot_hide_wrong_known_guid(self):
        self.remove_trace(3)
        self.trace["objects"][-2]["export"]["guid"]="e"*32
        with self.assertRaisesRegex(ValueError,"original_texture_trace_and_Material_YAML_PPtr_mismatch"):
            self.audit()

    def test_wrong_file_id_even_with_correct_guid_and_image(self):
        self.overrides[(0,0)]=(123,f"{1:032x}",3)
        with self.assertRaisesRegex(ValueError,"invalid_same_export_Texture2D_image_pointer"):
            self.audit()

    def test_wrong_type_even_with_correct_guid_and_file_id(self):
        for i,t in enumerate(self.mat_slots):
            if t==1:
                self.overrides[divmod(i,2)]=(2800000,f"{1:032x}",2)
        with self.assertRaisesRegex(ValueError,"original_texture_trace_and_Material_YAML_PPtr_mismatch"):
            self.audit()

    def test_local_type0_never_proves_export_target_even_equal_triple(self):
        self.local.add(3)
        self.trace["objects"][-1]["export"]={"file_id":123,"guid":"0"*32,"type":0}
        result=self.audit()
        self.assertEqual(result["status"],alpha.PARTIAL_STATUS)
        self.assertEqual(result["same_export_original_Material_TexEnv_PPtr_slots_exact"],7)
        self.assertEqual(result["local_type0_rows_equal_unscoped"],1)
        self.assertEqual(result["local_type0_Material_document_count"],3)
        self.assertFalse(result["local_type0_exported_target_identity_proven"])
        self.assertFalse(result["original_material_exact_texture_PPtr_and_UV_routes_checked"])

    def test_local_row_before_conflicting_external_does_not_hide_conflict(self):
        self.local.add(3)
        local=self.trace["objects"].pop()
        local["export"]={"file_id":123,"guid":"0"*32,"type":0}
        self.trace["objects"].insert(0,local)
        self.trace["objects"][-1]["export"]["guid"]="e"*32
        with self.assertRaisesRegex(ValueError,"original_texture_trace_and_Material_YAML_PPtr_mismatch"):
            self.audit()

    def test_conflicting_local_slots_without_optional_outparam(self):
        self.local.add(3)
        self.overrides[(1,0)]=(456,"0"*32,0)
        self.write_project()
        from scripts.b05_verify_material_texenv_bindings import exported_texenvs
        with self.assertRaisesRegex(ValueError,"conflicting_exported_PPtrs"):
            alpha.source_material_to_exported_texture_guids(
                self.trace,self.source,self.targets,exported_texenvs(self.project))

    def test_array_importer_cannot_be_counted_as_plain_texture2d(self):
        meta=self.assets/"tex1.png.meta"
        meta.write_text(meta.read_text().replace("textureShape: 1","textureShape: 4"))
        with self.assertRaisesRegex(ValueError,"selected_particle_Texture2D_not_exported_as_image"):
            self.audit()

    def test_outside_material_alias_cannot_hide_selected_document(self):
        self.trace["objects"].append(self.row(21,999,2100000,f"{100:032x}",2))
        with self.assertRaisesRegex(ValueError,"selected_particle_Material_export_document_collision"):
            self.audit()

    def test_duplicate_texture_row_after_local_still_rejected(self):
        self.trace["objects"][-1]["export"]={"file_id":123,"guid":"0"*32,"type":0}
        self.trace["objects"].append(deepcopy(self.trace["objects"][-1]))
        with self.assertRaisesRegex(ValueError,"duplicated_original_particle_Texture2D_export"):
            self.audit()


if __name__=="__main__":
    unittest.main()
