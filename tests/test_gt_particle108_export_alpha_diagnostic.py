"""Synthetic guards for the Particle108 source-to-export transparency diagnostic."""
import tempfile
import unittest
from pathlib import Path
import sys
import types
from unittest.mock import patch, MagicMock

from PIL import Image

from scripts.gt_particle108_export_alpha_diagnostic import (
    alpha_profile, analyze_exported_images, image_meta_index,
    source_texture_export_map,
    source_material_to_exported_texture_guids,
    verify_external_texture_guid_subset,
    classify_original_local_texture_trace,
    original_local_type0_source_pixel_alpha,
)


class OriginalParticle108ExportAlphaTests(unittest.TestCase):
    def test_image_alpha_histograms_distinguish_opaque_partial_and_cutout(self):
        image = Image.new("RGBA", (3, 1), (1, 2, 3, 255))
        image.putpixel((1, 0), (1, 2, 3, 0))
        image.putpixel((2, 0), (1, 2, 3, 128))
        result = alpha_profile(image)
        self.assertTrue(result["has_explicit_alpha"])
        self.assertFalse(result["all_opaque"])
        self.assertTrue(result["has_partially_transparent_pixels"])
        self.assertTrue(result["fully_transparent_pixel_present"])
        opaque = alpha_profile(Image.new("RGB", (1, 1), (1, 2, 3)))
        self.assertTrue(opaque["all_opaque"])
        self.assertFalse(opaque["has_explicit_alpha"])
        self.assertFalse(opaque["has_transparent_pixels"])

    def test_source_to_export_uses_class28_and_exact_ids_not_names(self):
        originals = {("sharedassets0.assets", i): 1 for i in (11, 12, 13)}
        rows = [{
            "class_id": 28,
            "source": {"owner": "Raft_Data/sharedassets0.assets", "path_id": i},
            "export": {"file_id": 2800000, "guid": format(i, "032x"), "type": 3},
        } for i in (11, 12, 13)]
        trace = {"schema_version": 1, "export_instance": "a" * 32, "objects": rows}
        mapped = source_texture_export_map(trace, originals)
        self.assertEqual(len(mapped), 3)
        self.assertEqual(len(set(mapped.values())), 3)
        with self.assertRaisesRegex(ValueError, "duplicated_original"):
            source_texture_export_map(
                dict(trace, objects=rows + [rows[0]]), originals)
        with self.assertRaisesRegex(ValueError, "not_unique"):
            duplicate = [dict(x, export=dict(x["export"])) for x in rows]
            duplicate[1]["export"]["guid"] = duplicate[0]["export"]["guid"]
            source_texture_export_map(dict(trace, objects=duplicate), originals)

    def test_exact_guid_image_meta_and_alpha_scanned_without_editing_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp) / "Assets"
            assets.mkdir()
            wanted = set()
            for i in range(1, 4):
                guid = format(i, "032x")
                wanted.add(guid)
                texture = assets / f"only-private-sample-{i}.png"
                if i == 1:
                    image = Image.new("RGB", (2, 1), (2, 2, 2))
                else:
                    image = Image.new("RGBA", (2, 1), (2, 2, 2, 255))
                    image.putpixel((0, 0), (2, 2, 2, 0 if i == 2 else 128))
                image.save(texture)
                meta = texture.with_suffix(".png.meta")
                meta.write_text(
                    f"fileFormatVersion: 2\nguid: {guid}\nTextureImporter:\n"
                    "  alphaSource: 1\n  alphaIsTransparency: 1\n"
                    "  sRGBTexture: 1\n  mipmapEnabled: 1\n",
                    encoding="utf-8")
            original_bytes = {
                path.name: path.read_bytes() for path in assets.rglob("*") if path.is_file()}
            index = image_meta_index(assets, wanted)
            counts, importers = analyze_exported_images(index)
            self.assertEqual(counts["linked_exported_images_decoded"], 3)
            self.assertEqual(counts["all_opaque"], 1)
            self.assertEqual(counts["has_explicit_alpha"], 2)
            self.assertEqual(counts["has_partially_transparent_pixels"], 1)
            self.assertEqual(counts["fully_transparent_pixel_present"], 1)
            self.assertEqual(importers["alphaSource"], {"1": 3})
            self.assertEqual(
                original_bytes,
                {path.name: path.read_bytes() for path in assets.rglob("*") if path.is_file()},
            )

    def test_missing_selected_guid_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp) / "Assets"
            assets.mkdir()
            with self.assertRaisesRegex(ValueError, "importer_missing"):
                image_meta_index(assets, {"a" * 32, "b" * 32, "c" * 32})


    def test_same_export_direct_3_texture_trace_checks_only_proven_external_PPtrs(self):
        # A material-local type0 pointer must not be given a fabricated
        # external importer GUID merely because all three source textures
        # appear independently in the same-export trace.
        a=("sharedassets0.assets",1)
        b=("sharedassets0.assets",2)
        local=("sharedassets0.assets",3)
        direct={a:"a"*32,b:"b"*32,local:"c"*32}
        materials={a:"a"*32,b:"b"*32}
        verify_external_texture_guid_subset(direct,materials)
        verify_external_texture_guid_subset(None,materials)
        with self.assertRaisesRegex(ValueError,"original_texture_trace_and_Material_YAML_GUID_mismatch"):
            verify_external_texture_guid_subset(direct,dict(materials,bad="d"*32))
        with self.assertRaisesRegex(ValueError,"original_texture_trace_and_Material_YAML_GUID_mismatch"):
            verify_external_texture_guid_subset(direct,{a:"e"*32,b:"b"*32})

    def test_sha_original_local_top_mip_can_be_classified_without_fabricating_exported_image(self):
        from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
        with tempfile.TemporaryDirectory() as tmp:
            owner="sharedassets0.assets"
            path=Path(tmp)/"Raft_Data"/owner
            path.parent.mkdir()
            path.write_bytes(b"synthetic owner; source SHA mocked deliberately")
            image=Image.new("RGBA",(2,1),(7,8,9,255))
            image.putpixel((1,0),(7,8,9,128))
            obj=MagicMock()
            obj.path_id=123
            obj.type.name="Texture2D"
            obj.read.return_value.image=image
            env=MagicMock()
            env.file.objects={123:obj}
            unity_mod=types.ModuleType("UnityPy")
            unity_mod.load=lambda selected:env
            local={(owner,123):(987,"0"*32,0)}
            with (patch.dict(sys.modules,{"UnityPy":unity_mod}),
                  patch("scripts.w1_stage_zip2_owners.fingerprint",
                        return_value=SHADER_OWNERS[owner])):
                proof=original_local_type0_source_pixel_alpha(Path(tmp),local)
                self.assertTrue(proof["original_local_Type0_Texture2D28_source_top_mip_alpha_decoded"])
                self.assertTrue(proof["original_local_Type0_Texture2D28_source_top_mip_alpha_profile"]["has_partially_transparent_pixels"])
                self.assertFalse(proof["original_local_Type0_texture_has_exported_image_proof"])
                self.assertFalse(proof["original_local_Type0_original_and_exported_pixels_compared"])
            with patch.dict(sys.modules,{"UnityPy":unity_mod}):
                with self.assertRaisesRegex(ValueError,"source_owner_SHA_drift"):
                    original_local_type0_source_pixel_alpha(Path(tmp),local)

    def test_original_local_type0_PPtr_exact_same_export_source_trace_without_external_GUID(self):
        local=("sharedassets0.assets",3)
        source={"owner":"Raft_Data/sharedassets0.assets","path_id":3}
        export={"file_id":2800000,"guid":"b"*32,"type":0}
        trace={"objects":[{"class_id":28,"source":source,"export":export}]}
        pointers={local:(2800000,"b"*32,0)}
        proof=classify_original_local_texture_trace(trace,pointers)
        self.assertTrue(proof["same_export_original_local_PPtr_matches_Texture2D28_trace"])
        self.assertEqual(proof["original_local_Type0_Texture2D_export_status"],
                         "ORIGINAL_LOCAL_POINTER_EXACT_TRACE_MATCH")
        self.assertFalse(proof["original_local_Type0_external_GUID_inferred"])
        different={local:(2800000,"a"*32,0)}
        mismatch=classify_original_local_texture_trace(trace,different)
        self.assertFalse(mismatch["same_export_original_local_PPtr_matches_Texture2D28_trace"])
        self.assertEqual(mismatch["original_local_Type0_Texture2D_export_status"],
                         "SOURCE_TEXTURE_TRACE_POINTER_DIFFERS_FROM_LOCAL_MATERIAL_PPTR")
        missing=classify_original_local_texture_trace({"objects":[]},pointers)
        self.assertEqual(missing["same_export_original_local_Texture2D28_trace_rows"],0)
        with self.assertRaisesRegex(ValueError,"ambiguous_source"):
            classify_original_local_texture_trace(
                {"objects":[trace["objects"][0],trace["objects"][0]]},pointers)

    def test_local_type0_Texture2D_is_proven_original_but_not_fabricated_image_guid(self):
        originals={("sharedassets0.assets",i):1 for i in (1,2,3)}
        original_materials={}
        exported={}
        trace={"schema_version":1,"export_instance":"f"*32,"objects":[]}
        # Nine external refs to two originals; one source-exact local type0
        # pointer to the third original. Never publish private game IDs.
        slots=[1,2,1,2,1,2,1,2,1,3]
        for material_no in range(5):
            key=("sharedassets0.assets",100+material_no)
            guid=f"{100+material_no:032x}"
            trace["objects"].append({
                "class_id":21,
                "source":{"owner":"Raft_Data/sharedassets0.assets","path_id":100+material_no},
                "export":{"file_id":2100000,"guid":guid,"type":2},
            })
            props={}
            dst={}
            for j in range(2):
                target=slots[2*material_no+j]
                label=f"_Texture{j}"
                uv=(1.0,1.0,0.0,0.0)
                props[label]=((0,target),uv)
                dst[label]=(((123,"0"*32,0) if target==3
                            else (2800000,f"{target:032x}",3)),uv)
            original_materials[key]=props
            exported[(2100000,guid)]=dst
        metrics={}
        local_pointers={}
        result=source_material_to_exported_texture_guids(
            trace,original_materials,originals,exported,metrics=metrics,
            private_local_pointers=local_pointers)
        self.assertEqual(len(local_pointers),1)
        self.assertEqual(next(iter(local_pointers.values())),(123,"0"*32,0))
        self.assertEqual(len(result),2)
        self.assertEqual(metrics["source_Type0_local_original_Texture2D_targets"],1)
        self.assertEqual(metrics["source_Type0_local_texture_pointer_slots"],1)
        self.assertEqual(metrics["source_to_export_texture_UV_pairs_verified"],10)
        self.assertEqual(metrics["exported_Texture2D_PPtr_type_0"],1)
        self.assertEqual(metrics["exported_Texture2D_PPtr_type_3"],9)
        self.assertEqual(metrics["source_Texture2D_to_export_GUIDs_unique"],2)
        # A type0 GUID hint, including nonzero, is never accepted as an
        # external image GUID; it remains an unresolved original PPtr.
        last=exported[(2100000,f"{104:032x}")]
        last["_Texture1"]=((123,"a"*32,0),(1.0,1.0,0.0,0.0))
        flagged={}
        mapped=source_material_to_exported_texture_guids(
            trace,original_materials,originals,exported,metrics=flagged)
        self.assertEqual(len(mapped),2)
        self.assertEqual(flagged["source_Type0_PPtr_nonzero_GUID_hints_not_used_as_export_image"],1)
        self.assertNotIn("a"*32,set(mapped.values()))
        # Even for type0, malformed GUID text or empty fileID is rejected.
        last["_Texture1"]=((123,"bad",0),(1.0,1.0,0.0,0.0))
        with self.assertRaisesRegex(ValueError,"broken_same_export_particle_texture_Material_ref"):
            source_material_to_exported_texture_guids(
                trace,original_materials,originals,exported)

    def test_same_export_material_texenv_fallback_uses_exact_original_texture_guids(self):
        original_source = {("sharedassets0.assets", i): 1 for i in (1, 2, 3)}
        original_materials = {}
        exported = {}
        trace = {"schema_version": 1, "export_instance": "f" * 32, "objects": []}
        texture_ids = [1, 2, 3, 1, 2, 3, 1, 2, 3, 1]
        for i in range(5):
            source_key = ("sharedassets0.assets", 100+i)
            exported_guid = f"{100+i:032x}"
            original_properties = {}
            exported_properties = {}
            trace["objects"].append({
                "class_id":21,
                "source":{"owner":"Raft_Data/sharedassets0.assets","path_id":100+i},
                "export":{"file_id":2100000,"guid":exported_guid,"type":2},
            })
            for j in range(2):
                prop = f"_Texture{j}"
                original_tex_id=texture_ids[2*i+j]
                uv=(1.0,1.0,0.0,0.0)
                original_properties[prop]=((0,original_tex_id),uv)
                exported_properties[prop]=(
                    (2800000,f"{original_tex_id:032x}",3),uv)
            original_materials[source_key]=original_properties
            exported[(2100000,exported_guid)]=exported_properties
        counters={}
        mapping=source_material_to_exported_texture_guids(
            trace, original_materials, original_source, exported, metrics=counters)
        self.assertEqual(counters["source_original_Material21"],5)
        self.assertEqual(counters["selected_source_materials_with_export_trace"],5)
        self.assertEqual(counters["source_original_TexEnv_slots_compared"],10)
        self.assertEqual(counters["exported_Texture2D_PPtr_fileID_nonzero"],10)
        self.assertEqual(counters["exported_Texture2D_PPtr_type_3"],10)
        self.assertEqual(counters["source_to_export_texture_UV_pairs_verified"],10)
        self.assertEqual(counters["source_Texture2D_to_export_GUIDs_unique"],3)
        self.assertEqual(len(mapping),3)
        self.assertEqual(mapping[("sharedassets0.assets",1)],f"{1:032x}")
        self.assertEqual(set(mapping.values()),{f"{i:032x}" for i in (1,2,3)})
        modified={k:dict(v) for k,v in exported.items()}
        first=next(iter(modified.values()))
        first["_Texture0"]=((2800000,"a"*32,3),(1.0,1.0,0.0,0.0))
        with self.assertRaisesRegex(ValueError,"maps_to_two_export_GUIDs"):
            source_material_to_exported_texture_guids(
                trace,original_materials,original_source,modified)
        modified={k:dict(v) for k,v in exported.items()}
        first=next(iter(modified.values()))
        first["_Texture0"]=((2800000,f"{1:032x}",3),(0.5,1.0,0.0,0.0))
        with self.assertRaisesRegex(ValueError,"changed_same_export_particle_texture_UV"):
            source_material_to_exported_texture_guids(
                trace,original_materials,original_source,modified)
        modified={k:dict(v) for k,v in exported.items()}
        first=next(iter(modified.values()))
        first["_Texture0"]=((0,"0"*32,0),(1.0,1.0,0.0,0.0))
        failed_counts={}
        with self.assertRaisesRegex(ValueError,"broken_same_export_particle_texture_Material_ref"):
            source_material_to_exported_texture_guids(
                trace,original_materials,original_source,modified,metrics=failed_counts)
        self.assertEqual(failed_counts["exported_Texture2D_PPtr_fileID_null"],1)
        self.assertEqual(failed_counts["exported_Texture2D_PPtr_type_0"],1)
        self.assertEqual(failed_counts["source_original_TexEnv_slots_compared"],1)


if __name__ == "__main__":
    unittest.main()
