"""Source-free controls for same-variable identity in two explicit FFT maps."""
import struct
import unittest

from scripts.b18_fft_spirv_descriptor_identity import INTERFACES
from scripts.b18_spirv_variable_identity import (
    normalized_image_decorations, verify_pair,
)


def module(profile="A", *, swap=False, drift=False, missing=False,
           duplicate=False, extra=False):
    addresses = [
        INTERFACES[profile][("input",0)],
        INTERFACES[profile][("input",1)],
        INTERFACES[profile][("output",0)]
    ]
    if swap:
        addresses[0],addresses[1] = addresses[1],addresses[0]
    words = []
    def emit(op,*values):
        words.extend([((len(values)+1)<<16)|op, *values])
    emit(15, 5, 1, 0x6e69616d, 0)
    emit(16, 1, 17, 64, 1, 1)
    emit(22, 10, 16 if drift else 32)
    for i,(set_id,bind_id) in enumerate(addresses):
        img,ptr,var=11+i*3,12+i*3,13+i*3
        emit(25,img,10,1,0,0,0,1 if i<2 else 2,0)
        emit(32,ptr,0,img)
        if not missing or i != 1:
            emit(59,ptr,var,0)
        emit(71,var,34,set_id)
        emit(71,var,33,bind_id)
        if duplicate and i == 0:
            emit(71,var,33,bind_id)
    if extra:
        emit(59,30,31,0)
        emit(71,31,34,1)
        emit(71,31,33,55)
    whole=[0x07230203,0x00010000,0,256,0,*words]
    return struct.pack("<"+"I"*len(whole),*whole)


class IdentityTests(unittest.TestCase):
    def test_source_free_two_map_example_stable(self):
        report=verify_pair(module("A"),module("B"))
        self.assertTrue(report["different_target_mapping_preserves_input_variable_identities"])
        self.assertTrue(report["full_spirv_program_equivalent_after_only_descriptor_literal_mask"])
        self.assertEqual(report["source_register_keys_proven_distinct"],3)
        self.assertFalse(report["runtime_t0_t1_input_values_independently_tested"])
        self.assertFalse(report["unity_or_android_gpu_verified"])

    def test_swapped_two_read_variables_fail_even_when_type_count_and_descriptor_set_match(self):
        # Both resources remain sampled Texture2D, so class/count alone passes.
        # Source-register-to-variable ID identity must still reject the swap.
        with self.assertRaisesRegex(ValueError,"identity changed"):
            verify_pair(module("A"),module("B",swap=True))

    def test_non_binding_shader_instruction_drift_rejected(self):
        with self.assertRaisesRegex(ValueError,"Non-descriptor"):
            verify_pair(module("A"),module("B",drift=True))

    def test_missing_declared_variable_rejected(self):
        with self.assertRaisesRegex(ValueError,"declared variable"):
            verify_pair(module("A"),module("B",missing=True))

    def test_duplicate_decoration_rejected(self):
        with self.assertRaisesRegex(ValueError,"Repeated"):
            verify_pair(module("A"),module("B",duplicate=True))

    def test_extra_descriptor_rejected(self):
        with self.assertRaisesRegex(ValueError,"Incomplete"):
            verify_pair(module("A"),module("B",extra=True))

    def test_invalid_header_rejected(self):
        damaged=b"NOPE"+module("A")[4:]
        with self.assertRaisesRegex(ValueError,"header"):
            verify_pair(damaged,module("B"))

    def test_truncated_instruction_rejected(self):
        with self.assertRaises(ValueError):
            verify_pair(module("A")[:-4],module("B"))

    def test_invalid_profile_rejected(self):
        with self.assertRaises(ValueError):
            normalized_image_decorations(module("A"),"UNRECOGNIZED")

    def test_correct_source_register_selections_return_same_ids(self):
        _,left=normalized_image_decorations(module("A"),"A")
        _,right=normalized_image_decorations(module("B"),"B")
        self.assertEqual(left,right)
        self.assertEqual(len(left),3)
        self.assertEqual(len(set(left.values())),3)


if __name__ == "__main__":
    unittest.main()
