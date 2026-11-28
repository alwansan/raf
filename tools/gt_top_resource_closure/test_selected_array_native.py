import unittest
import numpy as np
from tools.gt_top_resource_closure import selected_array_native as n

class NativeArrayTests(unittest.TestCase):
    def test_ranges_cover_all_22_without_padding_or_overlap(self):
        rr=list(n.ranges(1024,1024,2,11))
        self.assertEqual(len(rr),22)
        self.assertEqual(rr[-1][2]+rr[-1][3],2796256)
        self.assertEqual(rr[10][3],16)
        self.assertEqual(rr[11][2],1398128)
    def test_authored_all_mips_and_controls(self):
        cal=n.cal_payload()
        expected=n.decoded(cal,8,8,2,4)
        self.assertEqual(len(cal),224)
        self.assertEqual(n.calibrate(expected,expected),"raw_first")
        self.assertEqual(n.calibrate([x[:,::-1] for x in expected],expected),"flipped")
        with self.assertRaises(n.old.Failure):
            n.calibrate([x[::-1] for x in expected],expected)
        wrong=[x.copy() for x in expected]
        wrong[1]=wrong[0][:,::2,::2].copy()
        with self.assertRaises(n.old.Failure):n.calibrate(wrong,expected)
    def test_compare_preserves_alpha_error_and_wrong_layer(self):
        e=n.decoded(n.cal_payload(),8,8,2,4)
        a=[x.copy() for x in e]
        a[0][0,0,0,3]=1-a[0][0,0,0,3]
        rows=n.summarize(a,e,"raw_first")
        self.assertEqual(rows[0]["per_layer"][0]["alpha_mismatches_over_1e_5"],1)
        self.assertGreater(rows[0]["reversed_layer_control"][0]["RGBA_mismatches_over_1_div_255"],0)
    def test_partial_raw_matches_and_fail_closed_extent(self):
        raw=n.cal_payload()
        self.assertEqual(n.raw_matches(raw,raw,8,8,2,4),8)
        changed=bytearray(raw);changed[0]^=1
        self.assertEqual(n.raw_matches(raw,bytes(changed),8,8,2,4),7)
        with self.assertRaises(n.old.Failure):
            n.raw_matches(raw,raw[:-1],8,8,2,4)
    def test_safe_transfer_does_not_disclose_names_or_accept_truthy_values(self):
        record=n.safe_transfer({"phase":"private-name","failure_category":"private-path","accepted":1,"loaded_array":True,"guid":"secret"})
        self.assertEqual(record["phase"],"unknown")
        self.assertEqual(record["failure_category"],"other")
        self.assertIs(record["accepted"],False)
        self.assertIs(record["loaded_array"],True)
        self.assertNotIn("guid",record)
    def test_reference_controls_require_both_native_object_and_runtime_matches(self):
        def row(name,match):
            return {"name":name,"material_loaded":True,"shader_matches":True,"has_property":True,
                    "source_yaml_unchanged":True,"serialized_texture_matches":match,"runtime_texture_matches":match}
        rows=[row("type3",False),row("type2",True),row("wrong_guid",False),row("wrong_fileid",False)]
        self.assertTrue(n.read_reference_cases(rows)["native_type2_only_resolves"])
        rows[3]["runtime_texture_matches"]=True
        self.assertFalse(n.read_reference_cases(rows)["native_type2_only_resolves"])
    def test_reference_variants_only_change_the_intended_slot(self):
        from tools.gt_top_resource_closure import selected_material_reference as m
        guid="1234567890abcdef1234567890abcdef"
        body="\nMaterial:\n  m_Shader: {fileID: 4800000, guid: 0123456789abcdef0123456789abcdef, type: 3}\n  m_SavedProperties:\n    m_TexEnvs:\n    - _GT:\n        m_Texture: {fileID: 18700000, guid: "+guid+", type: 3}\n        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n"
        variants=m.make_variants(body,"_GT",guid,18700000,3)
        self.assertEqual(sum(a!=b for a,b in zip(variants["type2"],variants["type3"],strict=True)),1)
        self.assertIn("fileID: 18700001",variants["wrong_fileid"])
        with self.assertRaises(ValueError):m.make_variants(body,"_Wrong",guid,18700000,3)
if __name__=="__main__": unittest.main()
