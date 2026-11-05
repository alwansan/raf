import unittest

from scripts.t1_spirv_interface_component_audit import audit


def stage(model, storage, *, component=1, scalar="OpTypeFloat 32", duplicate=False):
    return f"""
    OpEntryPoint {model} %1 "main" %5 %7
    OpDecorate %5 Location 3
    OpDecorate %5 Component {component}
    {'OpDecorate %7 Location 3' if duplicate else 'OpDecorate %7 BuiltIn Position'}
    {'OpDecorate %7 Component 1' if duplicate else ''}
    %2 = {scalar}
    %3 = OpTypeVector %2 2
    %4 = OpTypePointer {storage} %3
    %5 = OpVariable %4 {storage}
    %7 = OpVariable %4 {storage}
    """


class InterfaceAuditTests(unittest.TestCase):
    def test_component_match_and_builtin_exclusion(self):
        result = audit(stage("Vertex", "Output"), stage("Fragment", "Input"))
        self.assertTrue(result["compatible_numeric_coverage"])
        self.assertEqual(result["fragment_components"], 2)

    def test_shift_and_scalar_mismatch_are_separate(self):
        result = audit(stage("Vertex", "Output"),
                       stage("Fragment", "Input", component=2, scalar="OpTypeInt 32 0"))
        self.assertEqual(result["missing_components"], 1)
        self.assertEqual(result["scalar_type_mismatches"], 1)
        self.assertFalse(result["compatible_numeric_coverage"])

    def test_overlapping_or_unrepresentable_locations_rejected(self):
        for fragment in (stage("Fragment", "Input", duplicate=True),
                         stage("Fragment", "Input", component=3)):
            with self.assertRaises(ValueError):
                audit(stage("Vertex", "Output"), fragment)
