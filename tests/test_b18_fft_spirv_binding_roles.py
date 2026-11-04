"""Source-free B18 negative/positive tests for DXBC -> SPIR-V resource classes."""
import struct
import unittest

from scripts.b18_fft_spirv_binding_roles import check_image_role_classes
def shex_dx(dst=(("S", 2, 4, 0), ("B", 2, 4, 1), ("T", 4, 4, 0))):
    """Synthetic source-free cs_5_0 executable resource declarations."""
    ins = []
    for _, kind, dimension, register in dst:
        op, typ = (88, 7) if kind == 2 else (156, 30)
        ins.extend([(4 << 24) | ((dimension - 1) << 11) | op,
                    (typ << 12) | (1 << 20), register, 0x5555])
    ins.extend([(4 << 24) | 155, 64, 1, 1])
    words = [(5 << 16) | (5 << 4), len(ins) + 2, *ins]
    content = struct.pack("<" + "I" * len(words), *words)
    return (b"DXBC" + b"\x00"*16 + struct.pack("<3I", 1, 44 + len(content), 1)
            + struct.pack("<I", 36) + b"SHEX"
            + struct.pack("<I", len(content)) + content)


def module(sampled=(1, 1, 2), dims=(1, 1, 1), group=(64, 1, 1),
           sets=(0, 0, 0), binds=(0, 1, 2), single_entry=True):
    out = []

    def put(op, *args):
        out.extend([(len(args) + 1) << 16 | op, *args])

    put(15, 5, 1, 0x6e69616d, 0)  # OpEntryPoint, "main".
    if not single_entry:
        put(15, 5, 2, 0x6e69616d, 0)
    put(16, 1, 17, *group)  # LocalSize
    put(22, 10, 32)  # float32
    for i, (sample, dim, descriptor_set, binding) in enumerate(
        zip(sampled, dims, sets, binds), start=0
    ):
        typ = 11 + 3*i
        ptr = typ+1
        var = typ+2
        put(25, typ, 10, dim, 0, 0, 0, sample, 0)
        put(32, ptr, 0, typ)
        put(59, ptr, var, 0)
        put(71, var, 34, descriptor_set)
        put(71, var, 33, binding)
    words = [0x07230203, 0x00010000, 0, 200, 0] + out
    return struct.pack("<" + "I" * len(words), *words)


class B18SPVRoleTests(unittest.TestCase):
    def test_original_t0_t1_u0_to_two_sampled_one_storage(self):
        row = check_image_role_classes(shex_dx(), module())
        self.assertEqual(row["translated_sampled_texture2d_count"], 2)
        self.assertEqual(row["translated_storage_texture2d_count"], 1)
        self.assertFalse(row["individual_original_register_to_spirv_descriptor_mapping_verified"])
        self.assertFalse(row["android_pixels_verified"])

    def test_translated_descriptor_numbers_can_change_without_invented_identity(self):
        row = check_image_role_classes(shex_dx(), module(sets=(1, 1, 2), binds=(4, 7, 0)))
        self.assertFalse(row["individual_original_register_to_spirv_descriptor_mapping_verified"])

    def test_storage_write_changed_to_sampled_texture_refused(self):
        with self.assertRaisesRegex(ValueError, "class count"):
            check_image_role_classes(shex_dx(), module(sampled=(1, 1, 1)))

    def test_sampled_read_changed_to_storage_texture_refused(self):
        with self.assertRaisesRegex(ValueError, "class count"):
            check_image_role_classes(shex_dx(), module(sampled=(2, 1, 2)))

    def test_wrong_2d_dim_or_multisample_refused(self):
        with self.assertRaisesRegex(ValueError, "dimensionality"):
            check_image_role_classes(shex_dx(), module(dims=(1, 2, 1)))

    def test_missing_image_and_extra_image_refused(self):
        for sampled in ((1, 2), (1, 1, 2, 1)):
            rows = len(sampled)
            with self.assertRaisesRegex(ValueError, "image count"):
                check_image_role_classes(shex_dx(), module(
                    sampled=sampled, dims=(1,)*rows,
                    sets=(0,)*rows, binds=tuple(range(rows))))

    def test_duplicated_descriptor_id_refused(self):
        with self.assertRaises(ValueError):
            check_image_role_classes(shex_dx(), module(binds=(0, 0, 2)))

    def test_translated_workgroup_mismatch_refused(self):
        with self.assertRaisesRegex(ValueError, "threadgroup"):
            check_image_role_classes(shex_dx(), module(group=(128, 1, 1)))

    def test_second_entrypoint_not_a_single_compute_stage(self):
        with self.assertRaisesRegex(ValueError, "entrypoint"):
            check_image_role_classes(shex_dx(), module(single_entry=False))

    def test_wrong_source_dxbc_register_refused(self):
        rows = (("S", 2, 4, 2), ("B", 2, 4, 1), ("T", 4, 4, 0))
        with self.assertRaises(ValueError):
            check_image_role_classes(shex_dx(dst=rows), module())


if __name__ == "__main__":
    unittest.main()
