"""Independent oracle unit controls. Mock receipts are not runtime evidence."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts import gt_submesh_route_pixels as gate


class Oracle(unittest.TestCase):
    def setUp(self):
        self.h=gate.hashes()
        self.guids={p:f"ab{i:030x}" for i,p in enumerate(
            (gate.PNG_A,gate.PNG_B,gate.MESH,gate.DECOY,gate.MAT_A,gate.MAT_B),1)}
        self.r=dict(schema_version=1,run_id="mock",status="OBSERVED",Unity_version=gate.EDITOR_VERSION,
                    backend="Vulkan",active_color_space="Linear",synthetic_only=True,Unity_render_executed=True,
                    Android_device=False,production_pixels=False,XAPK=False,source_paths=gate.INPUTS,
                    source_sha256_before=[self.h[p] for p in gate.INPUTS],source_sha256_after=[self.h[p] for p in gate.INPUTS],
                    graphics_device_name="MOCK ONLY",imported=[],cases=[])
        for p in (gate.PNG_A,gate.PNG_B):
            self.r["imported"].append(dict(path=p,guid=self.guids[p],filter="Point",wrap="Clamp",shape="Texture2D",
              alpha_source="FromInput",compression="Uncompressed",srgb=False,graphics_srgb=False,readable=True,mipmaps=False,
              width=4,height=2,mip_count=1,format="RGBA32",rgba8=[c for y in range(2) for x in range(4) for c in gate.texel(p,x,y)]))
        for name in gate.NAMES:
            mesh,slots=gate.case_spec(name);base=[0,4] if mesh==gate.MESH else [4,0]
            row=dict(name=name,mesh=mesh,mesh_guid=self.guids[mesh],mesh_instance=1 if mesh==gate.MESH else 2,
                submesh_count=2,vertex_count=8,checked_pixel_count=32,base_vertices=base,
                indices0=[i+base[0] for i in gate.INDICES],indices1=[i+base[1] for i in gate.INDICES],
                vertices=list(gate.VERTICES),uv0=list(gate.UV),slots=[],pixels=[])
            for s in slots:
                row["slots"].append(dict(s,material_guid=self.guids[s["material"]],
                    material_instance=3 if s["material"]==gate.MAT_A else 4,
                    texture_guid=self.guids.get(s["texture"],"")))
            row["pixels"]=[dict(x=x,y=y,observed=gate.expected_pixel(name,x,y)) for y in range(4) for x in range(8)]
            self.r["cases"].append(row)
    def check(self):return gate.validate(self.r,"mock",self.h,0)
    def test_mock_contract_and_pixel_equivalence(self):
        r=self.check();self.assertEqual(r["actual_Vulkan_RGBA_pixels_verified"],320)
        self.assertTrue(r["swapped_materials_and_reversed_mesh_same_pixels_distinct_observed_bindings"])
    def test_color_property_white_texture_literal_linear_values(self):
        rgba=gate.expected_pixel("white_texture",0,0)
        for actual,expected in zip(rgba,[0.6038273388553378,0.21404114048223255,0.05087608817155679,1.]):
            self.assertAlmostEqual(actual,expected,places=12)
        # Non-sRGB texture sample 32/255 is not separately linearized.
        self.assertAlmostEqual(gate.expected_pixel("baseline",0,0)[0],32/255*0.6038273388553378,places=12)

    def test_gamma_color_instead_of_linear_rejected(self):
        self.r["cases"][4]["pixels"][0]["observed"]=[.8,.5,.25,1.]
        with self.assertRaisesRegex(ValueError,"numeric_vector_mismatch"):self.check()

    def test_stage_no_render(self):
        with TemporaryDirectory() as t:
            p=Path(t)/"project";self.assertFalse(gate.stage(p)["Unity_render_executed"])
            self.assertNotEqual((p/gate.PNG_A).read_bytes(),(p/gate.PNG_B).read_bytes())
    def test_swapped_slots_not_baseline(self):
        self.r["cases"][0]["slots"].reverse()
        with self.assertRaisesRegex(ValueError,"receipt_contract:material"):self.check()
    def test_wrong_mesh_routes_not_swapped_slots(self):
        self.r["cases"][2]["mesh"]=gate.MESH
        with self.assertRaisesRegex(ValueError,"receipt_contract:mesh"):self.check()
    def test_corrupt_index_range(self):
        self.r["cases"][0]["indices1"][0]=0
        with self.assertRaisesRegex(ValueError,"receipt_contract:indices1"):self.check()
    def test_uv_drift(self):
        self.r["cases"][0]["uv0"][1]=.25
        with self.assertRaisesRegex(ValueError,"numeric_vector_mismatch"):self.check()
    def test_wrong_texture_faked_pixels(self):
        self.r["cases"][3]["pixels"]=self.r["cases"][0]["pixels"]
        with self.assertRaisesRegex(ValueError,"numeric_vector_mismatch"):self.check()
    def test_wrong_shader_identity(self):
        self.r["cases"][7]["slots"][0]["shader"]=gate.SHADER_A
        with self.assertRaisesRegex(ValueError,"receipt_contract:shader"):self.check()
    def test_duplicate_coordinate(self):
        self.r["cases"][0]["pixels"][1]["x"]=0
        with self.assertRaisesRegex(ValueError,"invalid_pixel_coordinate"):self.check()
    def test_actual_import_color_mismatch(self):
        self.r["imported"][0]["rgba8"][0]=255
        with self.assertRaisesRegex(ValueError,"receipt_contract:rgba8"):self.check()
    def test_drift_input_hash(self):
        self.r["source_sha256_after"][0]="0"*64
        with self.assertRaisesRegex(ValueError,"receipt_contract:source_sha256_after"):self.check()
    def test_no_process_success(self):
        with self.assertRaisesRegex(ValueError,"process_required"):gate.validate(self.r,"mock",self.h,2)
    def test_wrong_distinct_guid(self):
        for case in self.r["cases"]:
            for slot in case["slots"]:
                slot["material_guid"]=self.guids[gate.MAT_A]
        with self.assertRaisesRegex(ValueError,"distinct_persistent_assets"):self.check()


if __name__=="__main__":unittest.main()
