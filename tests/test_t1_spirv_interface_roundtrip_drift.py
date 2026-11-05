import unittest

from scripts.t1_spirv_interface_component_audit import audit
from scripts.t1_spirv_interface_roundtrip_drift import compare


def stage(model, storage, location=3, scalar="OpTypeFloat 32"):
    return f"""
    OpEntryPoint {model} %1 "main" %5
    OpDecorate %5 Location {location}
    OpDecorate %5 Component 1
    %2 = {scalar}
    %3 = OpTypeVector %2 2
    %4 = OpTypePointer {storage} %3
    %5 = OpVariable %4 {storage}
    """


class RoundtripDriftTests(unittest.TestCase):
    def test_coordinated_location_shift_evades_per_pair_coverage(self):
        source = stage("Vertex", "Output"), stage("Fragment", "Input")
        derived = stage("Vertex", "Output", 4), stage("Fragment", "Input", 4)
        self.assertTrue(audit(*source)["compatible_numeric_coverage"])
        self.assertTrue(audit(*derived)["compatible_numeric_coverage"])
        for row in compare(*source, *derived).values():
            self.assertEqual(row["removed_component_keys"], 2)
            self.assertEqual(row["added_component_keys"], 2)
            self.assertFalse(row["exact_numeric_map_match"])

    def test_type_drift_without_key_drift_and_unchanged_vertex(self):
        source = stage("Vertex", "Output"), stage("Fragment", "Input")
        report = compare(*source, source[0], stage("Fragment", "Input", scalar="OpTypeInt 32 1"))
        self.assertTrue(report["vertex"]["exact_numeric_map_match"])
        self.assertEqual(report["fragment"]["changed_types_at_shared_keys"], 2)
        self.assertEqual(report["fragment"]["removed_component_keys"], 0)
