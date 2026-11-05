import unittest
from scripts.t3_stage_io_drift import classify_stage_io


class StageIOClassificationTests(unittest.TestCase):
    def test_equal(self):
        a = {"inputs": [{"location": 0, "type": "vec2"}], "outputs": []}
        result = classify_stage_io(a, a)
        self.assertEqual(result["inputs_identical"], 1)
        self.assertEqual(result["outputs_identical"], 1)

    def test_location_remap(self):
        a = {"inputs": [{"location": 0, "type": "vec4"}], "outputs": []}
        b = {"inputs": [{"location": 3, "type": "vec4"}], "outputs": []}
        result = classify_stage_io(a, b)
        self.assertEqual(result["inputs_location_only_remap_candidate"], 1)

    def test_type_change(self):
        a = {"inputs": [{"location": 0, "type": "vec4"}], "outputs": []}
        b = {"inputs": [{"location": 0, "type": "vec3"}], "outputs": []}
        result = classify_stage_io(a, b)
        self.assertEqual(result["inputs_same_location_type_changes"], 1)
        self.assertEqual(result["inputs_location_only_remap_candidate"], 0)

    def test_reject_duplicate(self):
        a = {"inputs": [{"location": 0, "type": "vec4"}, {"location": 0, "type": "vec3"}], "outputs": []}
        with self.assertRaises(ValueError):
            classify_stage_io(a, a)

    def test_no_private_type_in_output(self):
        a = {"inputs": [{"location": 0, "type": "PRIVATE_TYPE_SENTINEL"}], "outputs": []}
        self.assertNotIn("PRIVATE_TYPE_SENTINEL", str(classify_stage_io(a, a)))


if __name__ == "__main__":
    unittest.main()
