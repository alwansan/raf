"""T2 source-free SPIR-V typed variable and explicit register mapping controls."""
import struct
import unittest

from scripts.t2_foam_explicit_descriptor_identity import (
    MAGIC, declared_spirv_interface, interface_address, verify_profile_identity,
)


def ins(op, *args):
    return [((len(args) + 1) << 16) | op, *args]


def generate(profile="D", count=1, cb=1, *, switch=False,
             add_non_binding_drift=False, original_override=None):
    if profile not in ("A", "B", "D"):
        raise ValueError("test profile")
    words = [MAGIC,0x00010300,0x12345678,1000,0]
    words += ins(25,100,1,2,0,0,0,1,0)  # OpTypeImage
    words += ins(26,101)                  # OpTypeSampler
    words += ins(30,102)                  # OpTypeStruct
    words += ins(32,200,0,100)          # image pointer
    words += ins(32,201,0,101)          # sampler pointer
    words += ins(32,202,2,102)          # uniform CB pointer
    for i in range(count):
        words += ins(59,200,300+i,0)
        words += ins(59,201,400+i,0)
    for i in range(cb):
        words += ins(59,202,500+i,2)
    for kind, base, n in (("image",300,count),("sampler",400,count),("cb",500,cb)):
        for i in range(n):
            if profile in ("A","B"):
                set_,binding=interface_address(profile,kind,i)
            elif kind == "image":
                set_,binding=0,(6+i if count == 5 else 2+i)
            elif kind == "sampler":
                set_,binding=0,i+1
            else:
                set_,binding=0,i
            if original_override is not None and kind=="image" and i==0:
                set_,binding=original_override
            var_id=base+(n-i-1 if switch and kind=="image" else i)
            words += ins(71,var_id,33,binding)
            words += ins(71,var_id,34,set_)
    if add_non_binding_drift:
        words += ins(0) # OpNop is not a descriptor decoration.
    return struct.pack("<"+"I"*len(words),*words)


class OriginalFoamExplicitRegisterTests(unittest.TestCase):
    def test_exact_explicit_two_maps_and_original_baseline(self):
        actual=verify_profile_identity(generate("D"),generate("A"),
                                       generate("B"),generate("D"),1,1)
        self.assertTrue(actual["source_native_dxbc_to_compiled_original_spirv_id_verified"])
        self.assertTrue(actual["full_original_spirv_graph_equal_after_only_descriptor_literals_mask"])
        self.assertEqual(actual["distinct_explicit_profiles_proven"],2)
        self.assertEqual(actual["source_register_to_default_compiled_descriptors"],[
            {"source_kind":"cb","original_dxbc_register":0,
             "compiled_image_sampler_or_cb_set":0,"compiled_binding":0},
            {"source_kind":"image","original_dxbc_register":0,
             "compiled_image_sampler_or_cb_set":0,"compiled_binding":2},
            {"source_kind":"sampler","original_dxbc_register":0,
             "compiled_image_sampler_or_cb_set":0,"compiled_binding":1},
        ])
        self.assertFalse(actual["original_material_upload_or_sampler_state_verified"])
        self.assertFalse(actual["proprietary_shader_code_identifiers_disclosed"])

    def test_real_foam_five_texture_case(self):
        a=verify_profile_identity(generate("D",5),generate("A",5),
                                  generate("B",5),generate("D",5),5,1)
        rows=a["source_register_to_default_compiled_descriptors"]
        self.assertEqual(len(rows),11)
        self.assertEqual([r["compiled_binding"] for r in rows if r["source_kind"]=="image"],
                         [6,7,8,9,10])
        self.assertEqual([r["compiled_binding"] for r in rows if r["source_kind"]=="sampler"],
                         [1,2,3,4,5])

    def test_set_identity_is_not_discarded_for_equal_binding(self):
        _,i=declared_spirv_interface(generate("A"))
        self.assertIn((3,11),i["image"])
        self.assertIn((3,41),i["sampler"])
        self.assertIn((0,0),i["cb"])

    def test_swapping_source_resource_var_id_blocked_even_if_counts_equal(self):
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D",5),generate("A",5),
                                    generate("B",5,switch=True),generate("D",5),5,1)

    def test_missing_original_baseline_register_parity_blocked(self):
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D"),generate("A"),
                                    generate("B"),generate("D",original_override=(0,77)),1,1)

    def test_original_graph_drift_beyond_descriptor_mask_rejected(self):
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D"),generate("A"),
                                    generate("B",add_non_binding_drift=True),
                                    generate("D"),1,1)

    def test_default_graph_drift_beyond_descriptor_mask_rejected(self):
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D",add_non_binding_drift=True),
                                    generate("A"),generate("B"),generate("D"),1,1)

    def test_profile_binding_wrong_numeric_slot_rejected(self):
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D"),
                                    generate("A",original_override=(3,90)),
                                    generate("B"),generate("D"),1,1)

    def test_missing_cb_definition_rejected(self):
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D"),generate("A"),
                                    generate("B"),generate("D"),1,0)

    def test_missing_sampler_definition_rejected(self):
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D"),generate("A"),
                                    generate("B"),generate("D"),0,1)

    def test_numeric_bound_and_ambiguous_type_rejected(self):
        for val in (True, -1, 7, 1.2,"1",None):
            with self.subTest(val=val), self.assertRaises(ValueError):
                verify_profile_identity(generate("D"),generate("A"),
                                        generate("B"),generate("D"),val,1)

    def test_truncated_or_forged_spirv_header_rejected(self):
        for b in (b"",generate("D")[:-4],b"\x00"*24,
                  bytes([0])*20):
            with self.subTest(n=len(b)), self.assertRaises(ValueError):
                declared_spirv_interface(b)

    def test_duplicate_binding_decorations_rejected(self):
        blob=generate("D")
        words=list(struct.unpack("<"+"I"*(len(blob)//4),blob))
        words += ins(71,300,33,5)
        with self.assertRaises(ValueError):
            declared_spirv_interface(struct.pack("<"+"I"*len(words),*words))

    def test_nondecorated_variable_id_change_rejected(self):
        a=list(struct.unpack("<"+"I"*(len(generate("A"))//4),generate("A")))
        a[3]=123  # Identifier bound changes, not just decoration.
        with self.assertRaises(ValueError):
            verify_profile_identity(generate("D"),struct.pack("<"+"I"*len(a),*a),
                                    generate("B"),generate("D"),1,1)

    def test_unknown_undecorated_op_does_not_become_resource(self):
        blob=generate("D")
        normalized,data=declared_spirv_interface(blob)
        self.assertEqual(sum(len(x) for x in data.values()),3)
        self.assertGreater(len(normalized),10)

    def test_disallowed_interface_profile_or_kind_or_slot_rejected(self):
        for profile,kind,index in (("C","image",1),("A","uav",1),
                                   ("B","image",-1),("A","sampler",True),
                                   ("A","image",6)):
            with self.subTest(profile=profile,kind=kind,index=index),self.assertRaises(ValueError):
                interface_address(profile,kind,index)


if __name__=="__main__":
    unittest.main()
