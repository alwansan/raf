"""Synthetic name SHA to original managed field identity, no Raft source."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.probe_fft_monoscript_field import inspect, classify_compute_shader_occurrences


class OriginalMonoScriptFieldTests(unittest.TestCase):
    def test_resolves_only_name_sha_and_redacts_all_class_field_names(self):
        code = 'namespace Custom.Water { public class WaterBridge { public UnityEngine.ComputeShader originalFFT; private int x; } }'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "WaterBridge.cs"
            path.write_text(code)
            expected = hashlib.sha256(b"Custom.Water.WaterBridge").hexdigest()
            result = inspect(Path(tmp), expected)
            self.assertTrue(result["original_managed_type_matched"])
            self.assertEqual(result["matches"][0]["original_field_type_compute_shader_declarations"], 1)
            self.assertNotIn("WaterBridge", str(result))
            self.assertNotIn("originalFFT", str(result))
            self.assertFalse(result["serialized_compute_field_offset_verified"])

    def test_mismatch_is_not_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "Missing.cs").write_text("class Missing {}")
            self.assertFalse(inspect(Path(tmp), "0" * 64)["original_managed_type_matched"])


    def test_classifies_field_and_parameter_without_leaking_names(self):
        raw = ("class Example {\n"
               " [SerializeField] private UnityEngine.ComputeShader fftShader;\n"
               " void Foo(UnityEngine.ComputeShader runtimeInput) {} \n"
               " public UnityEngine.ComputeShader Output { get; set; }\n"
               " }")
        result = classify_compute_shader_occurrences(raw)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["kind"], "declared_field_candidate")
        self.assertEqual(result[1]["kind"], "typed_parameter_candidate")
        self.assertEqual(result[2]["kind"], "property_candidate")
        self.assertNotIn("fftShader", str(result))
        self.assertNotIn("runtimeInput", str(result))



    def test_inherited_compute_shader_source_is_reported_without_class_names(self):
        child = ("namespace World.Water {\n"
                 "public class WaterBridge : WaterParent { void F(){} }\n}")
        parent = ("namespace World.Water {\n"
                  "public class WaterParent : MonoBehaviour {\n"
                  "  public UnityEngine.ComputeShader originalFFT;\n"
                  "}\n}")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p / "WaterBridge.cs").write_text(child)
            (p / "WaterParent.cs").write_text(parent)
            expected = hashlib.sha256(b"World.Water.WaterBridge").hexdigest()
            output = inspect(p, expected)
            self.assertTrue(output["original_managed_type_matched"])
            chain = output["matches"][0]["bounded_original_base_type_analysis"]
            self.assertEqual(len(chain), 1)
            self.assertEqual(chain[0]["direct_field_candidates"], 1)
            self.assertNotIn("WaterParent", str(chain))
            self.assertNotIn("originalFFT", str(chain))



if __name__ == "__main__":
    unittest.main()
