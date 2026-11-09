import copy
import unittest
from t3_smoke_pass_state_gate_v2 import audit, load_metadata

class PassStateTests(unittest.TestCase):
    def sample(self):
        p = dict(name="Forward", src_blend="SrcAlpha", dst_blend="OneMinusSrcAlpha",
                 blend_op="Add", zwrite=False, cull="Off", color_mask=15,
                 alpha_clip=False, program_present=True)
        s = dict(identity_role="smoke_linked_34_use_shader48",
                 smoke_named_renderer_count=17, material_slot_count=34,
                 source_sha256="a"*64, passes=[p])
        return dict(schema="t3-smoke-pass-state-v2", original=s,
                    exported=copy.deepcopy(s))
    def test_nested_duplicate_state_rejected(self):
        d = self.sample()
        import json
        raw = json.dumps(d).replace('"src_blend": "SrcAlpha"',
                                    '"src_blend": "One", "src_blend": "SrcAlpha"', 1)
        with self.assertRaisesRegex(ValueError, "duplicate_json_key:src_blend"):
            load_metadata(raw)

    def test_top_level_duplicate_side_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_json_key:original"):
            load_metadata('{"original": {}, "original": {}, "exported": {}}')

    def test_valid_json_metadata_accepted(self):
        import json
        self.assertEqual(audit(load_metadata(json.dumps(self.sample())))["status"],
                         "SCOPED_PASS_STATE_MATCH")

    def test_match(self):
        self.assertEqual(audit(self.sample())["status"], "SCOPED_PASS_STATE_MATCH")
    def test_blend_factor_mismatch(self):
        d=self.sample();d["exported"]["passes"][0]["dst_blend"]="One"
        self.assertIn("pass[0].dst_blend",audit(d)["mismatches"])
    def test_order_mismatch(self):
        d=self.sample()
        for s in (d["original"],d["exported"]):
            s["passes"].append(dict(s["passes"][0],name="Shadow"))
        d["exported"]["passes"].reverse()
        self.assertIn("pass[0].name",audit(d)["mismatches"])
    def test_missing_state_fails(self):
        d=self.sample();del d["exported"]["passes"][0]["color_mask"]
        with self.assertRaisesRegex(ValueError,"incomplete_pass_state"):audit(d)
    def test_unknown_alpha_fails(self):
        d=self.sample();d["exported"]["passes"][0]["alpha_clip"]=None
        with self.assertRaisesRegex(ValueError,"unknown_render_state"):audit(d)
    def test_wrong_identity_fails(self):
        d=self.sample();d["original"]["identity_role"]="fire_108_use_shader"
        with self.assertRaisesRegex(ValueError,"wrong_shader_identity"):audit(d)
    def test_boolean_mask_fails(self):
        d=self.sample();d["original"]["passes"][0]["color_mask"]=True
        with self.assertRaisesRegex(ValueError,"invalid_color_mask"):audit(d)
    def test_source_mismatch_fails(self):
        d=self.sample();d["exported"]["source_sha256"]="b"*64
        with self.assertRaisesRegex(ValueError,"different_original_source"):audit(d)

    def test_unhashable_blend_array_fails_closed(self):
        d=self.sample();d["exported"]["passes"][0]["src_blend"]=["SrcAlpha"]
        with self.assertRaisesRegex(ValueError,"invalid_blend_factor"):audit(d)
    def test_unhashable_cull_dict_fails_closed(self):
        d=self.sample();d["original"]["passes"][0]["cull"]={"value":"Off"}
        with self.assertRaisesRegex(ValueError,"invalid_render_enum"):audit(d)
    def test_missing_side_fails_closed(self):
        d=self.sample();del d["exported"]
        with self.assertRaisesRegex(ValueError,"missing_original_or_exported"):audit(d)

if __name__ == "__main__":
    unittest.main()
