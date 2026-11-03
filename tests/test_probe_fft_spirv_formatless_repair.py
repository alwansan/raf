"""Only synthetic SPIR-V: exercise narrowly scoped private format repair."""
import struct
import unittest
from scripts.probe_fft_spirv_formatless_repair import restore_formatless_write
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_spirv_operation_profile import image_operation_profile


def module(fmt, capability):
    operations = [(17, [1])]
    if capability:
        operations.append((17, [56]))
    operations += [
        (22, [1, 32]), (25, [2, 1, 1, 0, 0, 0, 2, fmt]),
        (32, [3, 0, 2]), (59, [3, 4, 0]),
        (71, [4, 33, 2]), (71, [4, 34, 0]),
        (99, [8, 9, 10]), (95, [3, 7, 11, 12])]
    words = [0x07230203, 0x10000, 0, 20, 0]
    for op, values in operations:
        words.extend([(len(values) + 1) << 16 | op, *values])
    return struct.pack("<" + "I" * len(words), *words)


def attempt(orig=None, translated=None):
    a = module(0, True) if orig is None else orig
    b = module(1, False) if translated is None else translated
    return restore_formatless_write(
        b, image_resource_contracts(a), image_operation_profile(a))


class FormatlessRepairTests(unittest.TestCase):
    def test_repairs_only_format_and_capability(self):
        source = module(1, False)
        restored = attempt(translated=source)
        self.assertEqual(image_resource_contracts(restored),
                         image_resource_contracts(module(0, True)))
        self.assertTrue(image_operation_profile(restored)[
            "storage_image_write_without_format_capability_declared"])
        self.assertEqual(len(restored), len(source) + 8)
        self.assertEqual(source, module(1, False))

    def test_unexpected_original_format_fails(self):
        with self.assertRaisesRegex(ValueError, "format"):
            attempt(orig=module(2, True))

    def test_changed_roundtrip_format_fails(self):
        with self.assertRaisesRegex(ValueError, "format"):
            attempt(translated=module(2, False))

    def test_missing_original_capability_fails(self):
        with self.assertRaisesRegex(ValueError, "capability"):
            attempt(orig=module(0, False))

    def test_already_formatless_roundtrip_fails(self):
        with self.assertRaisesRegex(ValueError, "difference"):
            attempt(translated=module(0, True))

    def test_invalid_truncated_input_fails(self):
        with self.assertRaises(ValueError):
            attempt(translated=module(1, False)[:-2])
        with self.assertRaises(ValueError):
            attempt(translated=b"BAD!" + module(1, False)[4:])


if __name__ == "__main__":
    unittest.main()
