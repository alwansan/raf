"""Synthetic SPIR-V opcode controls; no original game binaries or identifiers."""
import struct
import unittest
from scripts import t3_smoke34_spirv_usersemantic_annotations as a

SECRET = "PRIVATE_SOURCE_SEMANTIC_NEVER_LEAK"


def inst(op, *words):
    return [((len(words) + 1) << 16) | op, *words]


def string_words(value):
    data = value.encode("ascii") + b"\0"
    data += b"\0" * (-len(data) % 4)
    return struct.unpack("<" + "I" * (len(data)//4), data)


def module(*, names=False, extension=False, annotations=False,
           duplicate=False, member=False, locations=(0, 1)):
    words = [a.MAGIC, 0x00010300, 0, 40, 0]
    if extension:
        words += inst(a.OP_EXTENSION, *string_words(a.EXTENSION))
    for i, loc in enumerate(locations):
        ident = 10+i
        words += inst(a.OP_VARIABLE, 2, ident, a.STORAGE_INPUT)
        words += inst(a.OP_DECORATE, ident, a.DECORATION_LOCATION, loc)
        if names:
            words += inst(a.OP_NAME, ident, *string_words(SECRET+str(i)))
        if annotations:
            words += inst(a.OP_DECORATE_STRING_GOOGLE, ident,
                          a.DECORATION_HLSL_SEMANTIC,
                          *string_words(SECRET + str(i)))
        if duplicate and i == 0:
            words += inst(a.OP_DECORATE_STRING_GOOGLE, ident,
                          a.DECORATION_HLSL_SEMANTIC,
                          *string_words(SECRET + str(i)))
        if member and i == 0:
            words += inst(a.OP_MEMBER_DECORATE_STRING_GOOGLE, ident, 0,
                          a.DECORATION_HLSL_SEMANTIC,
                          *string_words(SECRET))
    return struct.pack("<" + "I" * len(words), *words)


def rows():
    return [{"semantic": SECRET, "index": i, "system_value": 0, "type": 3,
             "register": i, "mask": 15, "used_mask": 7, "stream": 0}
            for i in range(2)]


def reflected(locations=(0, 1)):
    return {"inputs": [{"location": loc, "type": "vec4"} for loc in locations],
            "outputs": [], "resource_slots": {}}


class ExplicitSemanticsTests(unittest.TestCase):
    def test_no_hlsl_extension_means_no_mapping_even_with_opname(self):
        parsed = a.parse_private_spirv(module(names=True))
        self.assertFalse(parsed["extension_present"])
        census = a.classify_original_and_spirv(rows(), reflected(), parsed)
        self.assertEqual(census["spv_semantic_decorated_input_variables"], 0)
        self.assertEqual(census["source_semantics_without_explicit_spv_label"], 2)
        self.assertEqual(census["register_location_same_number_candidates"], 2)
        self.assertEqual(census["spv_hlsl_semantic_extension_present"], 0)
        self.assertNotIn(SECRET, str(census))

    def test_true_explicit_annotations_match_synthetically_only(self):
        binary = module(names=True, extension=True, annotations=True)
        census = a.classify_original_and_spirv(rows(), reflected(),
                                                 a.parse_private_spirv(binary))
        self.assertEqual(census["spv_explicit_semantic_matches_original"], 2)
        self.assertEqual(census["source_semantics_without_explicit_spv_label"], 0)
        self.assertEqual(census["register_location_same_number_type_width_candidates"], 2)
        self.assertNotIn(SECRET, str(census))
        self.assertEqual(set(census), set(a.FIELDS))

    def test_renumbered_locations_do_not_erase_an_explicit_annotation(self):
        binary = module(extension=True, annotations=True, locations=(6, 7))
        census = a.classify_original_and_spirv(rows(), reflected((6, 7)),
                                                 a.parse_private_spirv(binary))
        self.assertEqual(census["spv_explicit_semantic_matches_original"], 2)
        self.assertEqual(census["register_location_same_number_candidates"], 0)

    def test_annotations_without_declared_extension_rejected(self):
        with self.assertRaisesRegex(ValueError, "extension_not_declared"):
            a.parse_private_spirv(module(annotations=True))

    def test_duplicate_semantic_decorations_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_private_SPIRV_HlslSemantic"):
            a.parse_private_spirv(module(extension=True, annotations=True, duplicate=True))

    def test_member_annotations_fail_closed_not_treated_as_variable(self):
        with self.assertRaisesRegex(ValueError, "member_semantic_decoration"):
            a.parse_private_spirv(module(extension=True, member=True))

    def test_binary_header_and_length_fail_closed(self):
        for b in (b"garbage", b"abcd"*6, b"\x00"*20, module()[:-1]):
            with self.subTest(raw_size=len(b)), self.assertRaises(ValueError):
                a.parse_private_spirv(b)

    def test_duplicate_spirv_location_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate_private_SPIRV_located_user_input"):
            a.parse_private_spirv(module(locations=(0, 0)))

    def test_reflection_location_disagreement_rejected(self):
        with self.assertRaisesRegex(ValueError, "SPIRV_binary_input_location_disagrees"):
            a.classify_original_and_spirv(rows(), reflected((3, 4)),
                                          a.parse_private_spirv(module()))

    def test_invalid_semantic_type_and_malicious_field_rejected(self):
        bad = rows()
        bad[0]["type"] = True
        with self.assertRaisesRegex(ValueError, "invalid_private_original_DXBC_signature_field"):
            a.classify_original_and_spirv(bad, reflected(),
                                          a.parse_private_spirv(module()))
        malicious = reflected()
        malicious["inputs"][0]["secret"] = SECRET
        with self.assertRaisesRegex(ValueError, "invalid_or_duplicate_private_reflected_input"):
            a.classify_original_and_spirv(rows(), malicious,
                                          a.parse_private_spirv(module()))

    def test_system_value_sentinel_is_excluded(self):
        extra = rows() + [{"semantic": "SV_POSITION", "index": 0,
                           "system_value": 1, "type": 3, "register": 0xffffffff,
                           "mask": 15, "used_mask": 15, "stream": 0}]
        c = a.classify_original_and_spirv(extra, reflected(),
                                           a.parse_private_spirv(module()))
        self.assertEqual(c["original_dx_user_input_records"], 2)

    def test_annotation_not_matching_original_semantic_does_not_forge(self):
        source = rows()
        source[0]["semantic"] = "CHANGED_PRIVATE_ID"
        c = a.classify_original_and_spirv(source, reflected(),
            a.parse_private_spirv(module(extension=True, annotations=True)))
        self.assertEqual(c["spv_explicit_semantic_matches_original"], 1)
        self.assertEqual(c["spv_explicit_semantic_unmatched_original"], 1)
        self.assertEqual(c["source_semantics_without_explicit_spv_label"], 1)


if __name__ == "__main__":
    unittest.main()
