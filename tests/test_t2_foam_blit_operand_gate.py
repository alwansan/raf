"""Pure fixture checks, not authentication or execution of original Foam IL."""
import unittest
from scripts.t2_foam_blit_operand_gate import (
    BLIT_SIGNATURE, Unresolved, classify_two_pass_blits,
)


def blit(pass_num, src="Texture", dst="RenderTexture", mat="Material", indexes=(0, 1, 2)):
    return [("ldarg", (indexes[0], src)),
            ("ldarg", (indexes[1], dst)) if dst != "NULL" else ("ldnull", None),
            ("ldarg", (indexes[2], mat)),
            ("ldc.i4", pass_num),
            ("call", BLIT_SIGNATURE)]


class BlitOperandGateTests(unittest.TestCase):
    def test_two_exact_passes_and_distinct_type_roles(self):
        result = classify_two_pass_blits(blit(0) + blit(1, src="RenderTexture", dst="NULL", indexes=(3, 4, 2)))
        self.assertEqual(result["sites"], [
            {"pass": 0, "source": "Texture", "destination": "RenderTexture",
             "source_producer": "arg", "destination_producer": "arg"},
            {"pass": 1, "source": "RenderTexture", "destination": "null",
             "source_producer": "arg", "destination_producer": "null"},
        ])
        self.assertIs(result["normalized_fixture_only"], True)
        self.assertIs(result["original_assembly_authenticated"], False)
        self.assertIs(result["original_texture_instance_identity_proven"], False)
        self.assertIs(result["Unity_or_Android_pixels_verified"], False)

    def test_local_store_load_preserves_typed_producer(self):
        left = [("ldarg", (0, "Texture")), ("stloc", 8), ("ldloc", 8)]
        first = left + blit(0)[1:]
        result = classify_two_pass_blits(first + blit(1))
        self.assertEqual(result["sites"][0]["source_producer"], "arg")

    def test_exact_overload_required(self):
        variants = [
            ("UnityEngine.Graphics", "Blit", ("UnityEngine.Texture", "UnityEngine.RenderTexture", "UnityEngine.Material"), True),
            ("UnityEngine.Graphics", "Blit", BLIT_SIGNATURE[2], False),
            ("UnityEngine.Graphics", "DrawTexture", BLIT_SIGNATURE[2], True),
            ("Other.Graphics", "Blit", BLIT_SIGNATURE[2], True),
            list(BLIT_SIGNATURE),
        ]
        for descriptor in variants:
            with self.subTest(desc=descriptor), self.assertRaises(Unresolved):
                classify_two_pass_blits(blit(0)[:-1] + [("call", descriptor)] + blit(1))

    def test_il_producer_not_inferred_from_field_call_or_branch(self):
        for op, data in [("ldfld", "field"), ("callvirt", "GetTexture"),
                         ("br.s", 4), ("castclass", "Texture"), ("ret", None),
                         ("leave", 2), ("throw", None)]:
            with self.subTest(op=op), self.assertRaises(Unresolved):
                classify_two_pass_blits([(op, data)] + blit(0) + blit(1))

    def test_duplicate_missing_or_unknown_pass_rejected(self):
        for instructions in [blit(0), blit(0) + blit(0), blit(1) + blit(1),
                             blit(0) + blit(3), blit(1) + blit(2)]:
            with self.subTest(length=len(instructions)), self.assertRaises(Unresolved):
                classify_two_pass_blits(instructions)

    def test_bad_argument_types_and_positions_rejected(self):
        invalid = [
            blit(0,src="Material")+blit(1),
            blit(0,dst="Texture")+blit(1),
            blit(0,mat="Texture")+blit(1),
            blit(0,src="NULL")+blit(1),
            [("ldnull",None)] + blit(0)[1:] + blit(1),
            [("ldc.i4", 0)] + blit(0)[1:] + blit(1),
        ]
        for instructions in invalid:
            with self.subTest(instructions=instructions[:3]), self.assertRaises(Unresolved):
                classify_two_pass_blits(instructions)

    def test_strict_argument_and_local_indices(self):
        for instructions in [
            [("ldarg", (True, "Texture"))] + blit(0) + blit(1),
            [("ldarg", (65536, "Texture"))] + blit(0) + blit(1),
            [("ldloc", 0)] + blit(0) + blit(1),
            [("ldnull",None), ("stloc",True)] + blit(0) + blit(1),
            [("ldc.i4",True)] + blit(0) + blit(1),
        ]:
            with self.subTest(first=instructions[0]), self.assertRaises(Unresolved):
                classify_two_pass_blits(instructions)

    def test_fail_closed_on_extra_stack_and_stack_budget(self):
        with self.assertRaises(Unresolved):
            classify_two_pass_blits([("ldnull", None)] + blit(0) + blit(1))
        with self.assertRaises(Unresolved):
            classify_two_pass_blits([("ldnull", None)]*33 + blit(0) + blit(1))
        with self.assertRaises(Unresolved):
            classify_two_pass_blits([("nop",None)]*129)

    def test_wrong_descriptor_and_malformed_instruction_rejected(self):
        for prefix in [[("call", "Blit")], [("ldarg", (0, 7))], [("nop",True)],
                       [(None,None)], ["bad"], [("ldarg", [0,"Texture",3])]]:
            with self.subTest(prefix=prefix), self.assertRaises(Unresolved):
                classify_two_pass_blits(prefix + blit(0) + blit(1))

    def test_reversed_source_destination_operand_order_fails(self):
        bad = blit(0)
        bad[0], bad[1] = bad[1], bad[0]
        with self.assertRaises(Unresolved):
            classify_two_pass_blits(bad + blit(1))


if __name__ == "__main__":
    unittest.main()
