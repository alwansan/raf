import unittest
from scripts.t1_unity_import_boundary import ACTIVATION, IMPORT, classify


def sample(a, i):
    return {"jobs": [{"name": "unity-private-compute-import", "steps": [
        {"name": ACTIVATION, "conclusion": a}, {"name": IMPORT, "conclusion": i, "started_at": "2026-11-05T08:00:00Z" if i not in ("skipped", None) else None}]}]}


class BoundaryTests(unittest.TestCase):
    def test_activation_failure_does_not_implicate_shader(self):
        result = classify(sample("failure", "skipped"))
        self.assertEqual(result["boundary"], "unity_activation")
        self.assertFalse(result["shader_import_attempted"])

    def test_import_failure_is_distinct(self):
        result = classify(sample("success", "failure"))
        self.assertTrue(result["shader_import_attempted"])
        self.assertEqual(result["boundary"], "unity_import")

    def test_success_does_not_prove_runtime(self):
        self.assertFalse(classify(sample("success", "success"))["unity_runtime_proven"])

    def test_import_conclusion_without_start_is_not_execution_proof(self):
        payload = sample("success", "failure")
        payload["jobs"][0]["steps"][1].pop("started_at")
        self.assertFalse(classify(payload)["shader_import_attempted"])

    def test_gate_order_fails_closed(self):
        payload = sample("success", "success")
        payload["jobs"][0]["steps"].reverse()
        with self.assertRaises(ValueError):
            classify(payload)

    def test_missing_gate_fails_closed(self):
        with self.assertRaises(ValueError):
            classify({"jobs": [{"name": "unity-private-compute-import", "steps": []}]})

    def test_duplicate_gate_fails_closed(self):
        with self.assertRaises(ValueError):
            classify({"jobs": [{"name": "unity-private-compute-import", "steps": [
                {"name": ACTIVATION, "conclusion": "success"},
                {"name": ACTIVATION, "conclusion": "failure"},
                {"name": IMPORT, "conclusion": "success"}]}]})


if __name__ == "__main__":
    unittest.main()
