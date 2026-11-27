"""Oracle-only tests. Fabricated receipts never become actual Unity evidence."""
import copy
import tempfile
import unittest
from pathlib import Path
from scripts import gt_imported_alpha_pixels as gate


class OracleTests(unittest.TestCase):
    def setUp(self):
        self.h=gate.hashes()
        self.r={"schema_version":1,"run_id":"test-mock","status":"OBSERVED","Unity_version":gate.EDITOR_VERSION,
                "backend":"Vulkan","active_color_space":"Linear","synthetic_only":True,
                "Unity_render_executed":True,"Android_device":False,"production_pixels":False,"XAPK":False,
                "rendered_case_count":8,"reimport_count":5,"shader_sha256":self.h[gate.SHADER],
                "probe_sha256":self.h[gate.PROBE],"png_sha256":self.h[gate.PNG],"png_sha256_after":self.h[gate.PNG],
                "graphics_device_name":"MOCK ONLY","cases":[]}
        for name,(mode,srgb,binding,tint,src,dst) in gate.CASES.items():
            row=dict(name=name,alpha_source=mode,srgb_import=srgb,srgb_graphics_format=srgb,bound_texture=binding,
                     filter_mode="Point",wrap_mode="Clamp",texture_shape="Texture2D",texture_type="Default",
                     compression="Uncompressed",npot_scale="None",png_sha256=self.h[gate.PNG],readable=True,
                     mipmaps_enabled=False,alpha_is_transparency=False,width=gate.WIDTH,height=gate.HEIGHT,mip_count=1,
                     aniso_level=0,src_blend=src,dst_blend=dst,checked_pixel_count=gate.WIDTH*gate.HEIGHT,
                     texture_format="RGBA32",graphics_format="mock",asset_guid="f"*32,material_id=99,tint=list(tint),samples=[])
            for y in range(gate.HEIGHT):
                for x in range(gate.WIDTH):
                    row["samples"].append(dict(x=x,y=y,imported_rgba8=gate.expected_rgba8(mode,x),
                                               observed=gate.expected_pixel(name,x)))
            self.r["cases"].append(row)

    def check(self):
        return gate.validate(self.r,"test-mock",self.h,0)

    def test_positive_oracle_only(self):
        self.assertEqual(self.check()["actual_Vulkan_RGBA_pixels_verified"],192)

    def test_actual_png_deterministic_and_stage_only(self):
        import struct,zlib
        data=gate.png_bytes()
        self.assertEqual(data[:8],b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II",data[16:24]),(6,4))
        n=struct.unpack(">I",data[33:37])[0]
        self.assertEqual(data[37:41],b"IDAT")
        row=zlib.decompress(data[41:41+n])
        self.assertEqual(row[1:5],bytes([0,0,0,255]))
        self.assertEqual(row[5:9],bytes([64,64,64,0]))
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/"project"
            self.assertFalse(gate.stage(p)["Unity_render_executed"])
            self.assertEqual((p/gate.PNG).read_bytes(),data)
            with self.assertRaisesRegex(ValueError,"fresh_project"):
                gate.stage(p)

    def test_verify_file_success_reason_not_missing(self):
        import json
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)
            raw,out=root/"mock.json",root/"verified.json"
            raw.write_text(json.dumps(self.r))
            result=gate.verify_file(raw,out,"test-mock",0)
            self.assertEqual(result["status"],"PASS_AUTHORED_IMPORTED_ALPHA_VULKAN")
            self.assertEqual(result["reason"],"independent_imported_and_rendered_RGBA_validation_passed")
            self.assertEqual(json.loads(out.read_text()),result)

    def test_wrong_process_exit(self):
        with self.assertRaisesRegex(ValueError,"process_required"):
            gate.validate(self.r,"test-mock",self.h,1)

    def test_stale_png(self):
        self.r["png_sha256_after"]="0"*64
        with self.assertRaisesRegex(ValueError,"png_sha256_after"):
            self.check()

    def test_wrong_imported_alpha(self):
        self.r["cases"][0]["samples"][1]["imported_rgba8"][3]=255
        with self.assertRaisesRegex(ValueError,"imported_RGBA8_mismatch"):
            self.check()

    def test_wrong_rendered_alpha(self):
        self.r["cases"][0]["samples"][1]["observed"][3]=1.
        with self.assertRaisesRegex(ValueError,"rendered_RGBA_mismatch"):
            self.check()

    def test_duplicate_coordinate(self):
        self.r["cases"][0]["samples"][1]["x"]=0
        with self.assertRaisesRegex(ValueError,"pixel_coordinate"):
            self.check()

    def test_bad_material_identity(self):
        self.r["cases"][2]["material_id"]=101
        with self.assertRaisesRegex(ValueError,"same_asset_and_material"):
            self.check()

    def test_wrong_srgb_setting(self):
        self.r["cases"][3]["srgb_graphics_format"]=False
        with self.assertRaisesRegex(ValueError,"srgb_graphics_format"):
            self.check()

    def test_wrong_control_cannot_pass_on_baseline(self):
        self.r["cases"][4]["samples"]=copy.deepcopy(self.r["cases"][0]["samples"])
        with self.assertRaisesRegex(ValueError,"rendered_RGBA_mismatch"):
            self.check()

    def test_duplicate_json(self):
        with self.assertRaisesRegex(ValueError,"duplicate_receipt"):
            gate.strict_json('{"a":1,"a":2}')

    def test_nonfinite(self):
        self.r["cases"][0]["samples"][1]["observed"][0]=float("nan")
        with self.assertRaisesRegex(ValueError,"finite_RGBA"):
            self.check()


if __name__=="__main__":
    unittest.main()
