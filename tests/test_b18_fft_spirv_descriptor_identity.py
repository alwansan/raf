"""B18 source-free canaries for explicit DXBC register -> SPIR-V set/binding."""
import struct
import unittest

from scripts.b18_fft_spirv_descriptor_identity import (
    INTERFACES, verify_explicit_descriptor_layout,
)


def original_shex(rows=(("input", 0), ("input", 1), ("output", 0)),
                  group=(64, 1, 1)):
    ops = []
    for kind, reg in rows:
        opcode, typ = (88, 7) if kind == "input" else (156, 30)
        ops.extend([(4 << 24) | (3 << 11) | opcode,
                    (typ << 12) | (1 << 20), reg, 0x5555])
    ops.extend([(4 << 24) | 155, *group])
    w = [(5 << 16) | (5 << 4), 2 + len(ops), *ops]
    content = struct.pack("<" + "I" * len(w), *w)
    return (b"DXBC" + b"\x00"*16 + struct.pack("<3I", 1, 44 + len(content), 1)
            + struct.pack("<I", 36) + b"SHEX"
            + struct.pack("<I", len(content)) + content)


def explicit_spv(profile="A", *, wrong_register=False, wrong_type=False,
                 wrong_group=False, duplicate=False, extra=False):
    layout = INTERFACES[profile]
    locations = [layout[("input", 0)], layout[("input", 1)],
                 layout[("output", 0)]]
    if wrong_register:
        locations[0] = (8, 66)
    if duplicate:
        locations[1] = locations[0]
    # None of these buffers come from the actual Raft game.
    images = [(1, *locations[0]), (1, *locations[1]), (2, *locations[2])]
    if wrong_type:
        images[2] = (1, *locations[2])
    if extra:
        images.append((1, 5, 88))
    output = []

    def put(op, *args):
        output.extend([(len(args) + 1) << 16 | op, *args])

    put(15, 5, 1, 0x6e69616d, 0)
    put(16, 1, 17, *( (128, 1, 1) if wrong_group else (64, 1, 1) ))
    put(22, 10, 32)
    for n, (sampled, set_id, bind_id) in enumerate(images):
        tid, ptr, vid = 11 + 3*n, 12 + 3*n, 13 + 3*n
        put(25, tid, 10, 1, 0, 0, 0, sampled, 0)
        put(32, ptr, 0, tid)
        put(59, ptr, vid, 0)
        put(71, vid, 34, set_id)
        put(71, vid, 33, bind_id)
    words = [0x07230203, 0x00010000, 0, 255, 0, *output]
    return struct.pack("<" + "I" * len(words), *words)


class ExplicitDescriptorTests(unittest.TestCase):
    def test_two_separate_compiler_target_layouts(self):
        for mode in ("A", "B"):
            with self.subTest(mode=mode):
                result = verify_explicit_descriptor_layout(
                    original_shex(), explicit_spv(mode), mode)
                self.assertTrue(result["explicit_descriptor_set_binding_presence_matched"])
                self.assertTrue(result["read_write_image_types_preserved"])
                self.assertFalse(result["same_class_input_image_behavior_distinguished"])
                self.assertFalse(result["android_gpu_pixels_verified"])

    def test_wrong_binding_profile_rejected(self):
        for mode in ("A", "B"):
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "not respected"):
                verify_explicit_descriptor_layout(original_shex(),
                                                  explicit_spv(mode, wrong_register=True), mode)

    def test_wrong_output_type_rejected(self):
        with self.assertRaises(ValueError):
            verify_explicit_descriptor_layout(original_shex(),
                                              explicit_spv(wrong_type=True), "A")

    def test_original_source_register_drift_rejected(self):
        src = original_shex(rows=(("input", 1), ("input", 2), ("output", 0)))
        with self.assertRaises(ValueError):
            verify_explicit_descriptor_layout(src, explicit_spv(), "A")

    def test_cross_profile_rejected(self):
        with self.assertRaises(ValueError):
            verify_explicit_descriptor_layout(original_shex(), explicit_spv("A"), "B")

    def test_duplicate_binding_rejected(self):
        with self.assertRaises(ValueError):
            verify_explicit_descriptor_layout(original_shex(),
                                              explicit_spv(duplicate=True), "A")

    def test_extra_descriptor_rejected(self):
        with self.assertRaises(ValueError):
            verify_explicit_descriptor_layout(original_shex(),
                                              explicit_spv(extra=True), "A")

    def test_workgroup_drift_rejected(self):
        with self.assertRaisesRegex(ValueError, "threadgroup"):
            verify_explicit_descriptor_layout(original_shex(),
                                              explicit_spv(wrong_group=True), "A")

    def test_invalid_profile_refused(self):
        with self.assertRaises(ValueError):
            verify_explicit_descriptor_layout(original_shex(), explicit_spv(), "BAD")

    def test_unsupported_source_binary_refused(self):
        with self.assertRaises(ValueError):
            verify_explicit_descriptor_layout(b"DXBC", explicit_spv(), "A")


if __name__ == "__main__":
    unittest.main()
