"""T2 WATER-001: source-only conservative Foam RHS classifier regression.

Run: python3 -m unittest -v test_t2_foam_rhs_origin_guard_regression.py
This is NOT a Mono.Cecil, Unity, shader, or device test.
"""
import unittest
from t2_foam_rhs_origin_guard import classify_rhs


class FoamRhsOriginGuardRegression(unittest.TestCase):
    def test_known_producers(self):
        cases = {
            'ldnull': 'NULL', 'newobj': 'CONSTRUCTOR',
            'ldfld': 'FIELD_READ', 'ldsfld': 'STATIC_FIELD_READ',
            'ldloc': 'LOCAL_READ', 'ldarg': 'ARGUMENT_READ',
        }
        for opcode, expected in cases.items():
            with self.subTest(opcode=opcode):
                self.assertEqual(classify_rhs([opcode]), expected)

    def test_short_forms_are_not_addresses(self):
        for i in range(4):
            for prefix, expected in [('ldloc', 'LOCAL_READ'), ('ldarg', 'ARGUMENT_READ')]:
                with self.subTest(prefix=prefix, index=i):
                    self.assertEqual(classify_rhs([f'{prefix}.{i}']), expected)
        for opcode in ('ldloc.s', 'ldarg.s', 'ldloca.s', 'ldarga.s',
                       'ldloc.4', 'ldarg.4', 'ldloca', 'ldarga'):
            with self.subTest(rejected=opcode):
                self.assertEqual(classify_rhs([opcode]), 'UNKNOWN')

    def test_call_requires_original_nonvoid_signature(self):
        for opcode in ('call', 'callvirt'):
            with self.subTest(opcode=opcode):
                self.assertEqual(classify_rhs([opcode]), 'UNKNOWN')
                self.assertEqual(classify_rhs([opcode], call_returns_value=True), 'CALL_RESULT')
                self.assertEqual(classify_rhs([opcode], call_returns_value=1), 'UNKNOWN')
                self.assertEqual(classify_rhs([opcode], call_returns_value='true'), 'UNKNOWN')

    def test_control_flow_and_stack_ambiguity_are_rejected(self):
        for opcode in ('br.s', 'brtrue.s', 'beq', 'bne.un', 'leave.s',
                       'switch', 'ret', 'throw', 'stfld', 'stsfld', 'stloc',
                       'pop', 'dup', 'ldind.ref', 'ldelem.ref'):
            with self.subTest(opcode=opcode):
                self.assertEqual(classify_rhs(['ldfld', opcode]), 'UNKNOWN')

    def test_single_producer_only(self):
        for ops in (['ldloc', 'ldloc'], ['ldnull', 'newobj'],
                    ['ldfld', 'call'], ['ldfld', 'ldsfld'],
                    ['castclass', 'ldloc'], ['castclass'], [],
                    ['nop'], ['ldfld', 'dup']):
            with self.subTest(ops=ops):
                self.assertEqual(classify_rhs(ops, call_returns_value=True), 'UNKNOWN')

    def test_nops_and_postproducer_cast(self):
        self.assertEqual(classify_rhs(['nop', 'ldfld', 'castclass', 'nop']), 'FIELD_READ')
        self.assertEqual(classify_rhs(['ldloc.0', 'castclass']), 'LOCAL_READ')
        self.assertEqual(classify_rhs(['nop', 'CALLVIRT', 'castclass'], call_returns_value=True), 'CALL_RESULT')

    def test_invalid_inputs(self):
        for value in (None, '', 'ldfld', 3, {}, [], [None], ['ldfld', 3]):
            with self.subTest(value=value):
                self.assertEqual(classify_rhs(value), 'UNKNOWN')

    def test_no_claim_of_runtime_alias_identity(self):
        # Matching origin categories do NOT prove matching runtime Texture objects.
        self.assertEqual(classify_rhs(['ldfld']), classify_rhs(['ldfld']))
        self.assertEqual(classify_rhs(['ldloc.0']), classify_rhs(['ldloc.1']))


if __name__ == '__main__':
    unittest.main()
