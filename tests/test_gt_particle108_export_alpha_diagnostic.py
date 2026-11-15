"""Synthetic guards for the Particle108 source-to-export transparency diagnostic."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.gt_particle108_export_alpha_diagnostic import (
    alpha_profile, analyze_exported_images, image_meta_index,
    source_texture_export_map,
    source_material_to_exported_texture_guids,
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
        mapping=source_material_to_exported_texture_guids(
            trace, original_materials, original_source, exported)
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


if __name__ == "__main__":
    unittest.main()
