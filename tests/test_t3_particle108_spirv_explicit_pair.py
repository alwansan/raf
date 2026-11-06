"""Source-free two explicit VKD3D graphics profiles: full SPIR-V relocation proof."""
import json
import struct
import unittest

from scripts.t3_particle108_explicit_map_packet import private_packets
from scripts import t3_particle108_spirv_explicit_pair as m

SOURCE=(
    ("sampler",90,(1,)),
    ("srv",88,(3,)),
    ("cbuffer",89,(2,8)),
)

def op(code,*payload):
    return [(len(payload)+1)<<16 | code,*payload]

def synthetic_stage(packet,stage,*,swap=False,drop=False,add_name=False,alias=False,
                    graphics_interface=False,invalid_interface_decoration=False):
    rows=[line.split() for line in packet.splitlines()[1:]]
    destinations=[(int(x[2]),int(x[3])) for x in rows]
    if swap:
        destinations[0],destinations[1]=destinations[1],destinations[0]
    if alias:
        destinations[1]=destinations[0]
    words=[0x07230203,0x00010300,0,256,0]
    words+=op(15,0 if stage else 4,2,0x6e69616d,0)
    words+=op(30,10)
    words+=op(32,20,2,10)
    for i in range(3):
        vid=30+i
        words+=op(59,20,vid,2)
        words+=op(71,vid,34,destinations[i][0])
        if not drop or i!=1:
            words+=op(71,vid,33,destinations[i][1])
    if graphics_interface:
        # Real SPIR-V VS/FS modules contain Input and Output OpVariables in
        # addition to uniform/image/sampler descriptors. These variables must
        # remain undecorated with DescriptorSet/Binding, and not affect mapping.
        words+=op(30,11)
        words+=op(32,21,1,11)
        words+=op(32,22,3,11)
        words+=op(59,21,40,1)
        words+=op(59,22,41,3)
        if invalid_interface_decoration:
            words+=op(71,40,34,4)
            words+=op(71,40,33,33)
    if add_name:
        words+=op(5,30,0x00306263)
    return struct.pack("<"+"I"*len(words),*words)

class DualExplicitVkd3dPairTests(unittest.TestCase):
    def setUp(self):
        self.packets,_=private_packets(SOURCE,1)
        self.a=synthetic_stage(self.packets["A"],1)
        self.b=synthetic_stage(self.packets["B"],1)
    def check(self,a=None,b=None,pa=None,pb=None):
        return m.verify_pair(pa or self.packets["A"],pb or self.packets["B"],
                             a if a is not None else self.a,
                             b if b is not None else self.b,1)

    def test_two_profiles_preserve_same_original_variable_and_full_program(self):
        result=self.check()
        self.assertEqual(result["source_registers_mapped_under_both_profiles"],3)
        self.assertEqual(result["chosen_explicit_target_layouts_verified"],2)
        self.assertTrue(result["same_source_to_spirv_variable_identity_across_profiles"])
        self.assertTrue(result["whole_spirv_program_identical_except_descriptor_literals"])
        self.assertFalse(result["shaderlab_compiled_or_android_pixels_verified"])
        self.assertFalse(result["source_register_numbers_spirv_IDS_descriptor_coordinates_published"])
        for secret in ("cb2","t3","s1","T3MAP1",'"30"','"37"'):
            self.assertNotIn(secret,json.dumps(result))

    def test_real_graphics_input_and_output_variables_are_not_descriptors(self):
        a=synthetic_stage(self.packets["A"],1,graphics_interface=True)
        b=synthetic_stage(self.packets["B"],1,graphics_interface=True)
        result=self.check(a=a,b=b)
        self.assertEqual(result["source_registers_mapped_under_both_profiles"],3)
        self.assertTrue(result["whole_spirv_program_identical_except_descriptor_literals"])

    def test_forged_descriptor_on_graphics_input_variable_is_rejected(self):
        a=synthetic_stage(self.packets["A"],1,graphics_interface=True)
        b=synthetic_stage(self.packets["B"],1,graphics_interface=True,
                          invalid_interface_decoration=True)
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_SPV_BINDING_COVERAGE"):
            self.check(a=a,b=b)

    def test_swapped_same_class_source_binding_fails_even_with_correct_multiset(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_SAME_SOURCE_VARIABLE_CHANGED"):
            self.check(b=synthetic_stage(self.packets["B"],1,swap=True))

    def test_malformed_spirv_missing_descriptor_half_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_SPV_BINDING_PAIRS"):
            self.check(b=synthetic_stage(self.packets["B"],1,drop=True))

    def test_duplicate_spirv_target_rejected(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_SPV_BINDING_ALIAS"):
            self.check(b=synthetic_stage(self.packets["B"],1,alias=True))

    def test_non_binding_program_change_is_not_hidden_by_normalization(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_NON_DESCRIPTOR_INSTRUCTIONS_CHANGED"):
            self.check(b=synthetic_stage(self.packets["B"],1,add_name=True))

    def test_source_packet_wrong_stage_or_profile_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_PAIR_HEADER"):
            self.check(pb=self.packets["B"].replace("T3MAP1 V B","T3MAP1 P B"))

    def test_source_packet_duplicate_register_key_rejected(self):
        rows=self.packets["A"].splitlines()
        rows[2]=" ".join((rows[1].split()[0:2]+rows[2].split()[2:]))
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_PAIR_ALIAS"):
            self.check(pa="\n".join(rows)+"\n")

    def test_spirv_wrong_stage_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"T3_SPIRV_STAGE_ENTRYPOINT"):
            self.check(b=synthetic_stage(self.packets["B"],0))

    def test_profile_pairs_must_have_distinct_explicit_target_locations(self):
        wrong=self.packets["B"].splitlines()
        same=self.packets["A"].splitlines()
        for n in range(1,len(wrong)):
            w=wrong[n].split()
            a=same[n].split()
            w[2:]=a[2:]
            wrong[n]=" ".join(w)
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_EXPLICIT_SOURCE_MAP_DIFFERENCE"):
            self.check(pb="\n".join(wrong)+"\n")

if __name__=="__main__":
    unittest.main()
