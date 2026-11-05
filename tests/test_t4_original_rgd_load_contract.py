import unittest
from scripts.b07_probe_original_world_callbacks import fingerprint
from scripts.t4_original_rgd_load_contract import analyze, inspect_original_saveandload_scope, inspect_exact_original_loader_method

HEADER = """public class SaveAndLoad {
 public T Load<T>(string filename) {
   var formatter = new BinaryFormatter();
   formatter.Binder = new LegacyBinder();
   return (T)formatter.Deserialize(FileManager.OpenFile(filename));
 }
}
"""


class OriginalLoaderContractTests(unittest.TestCase):
    def _check(self, s):
        return analyze(s, fingerprint(s))

    def test_synthetic_bound_loader(self):
        v = self._check(HEADER)
        self.assertEqual(v["deserialize_calls"], 1)
        self.assertEqual(v["binder_assignments_in_loaders"], 1)
        self.assertEqual(v["loader_method_count"], 1)
        self.assertEqual(v["generic_loader_count"], 1)
        self.assertFalse(v["original_rgd_deserialized"])

    def test_unknown_original_sha_refused(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            analyze(HEADER)

    def test_source_and_comment_literals_do_not_count_as_calls(self):
        fixture = HEADER.replace("return (T)formatter.Deserialize(FileManager.OpenFile(filename));",
            'var msg = "Deserialize(FileManager.OpenFile(foo))"; // Deserialize(x)\n return default(T);')
        with self.assertRaisesRegex(ValueError, "No executable deserialization"):
            self._check(fixture)

    def test_no_loader_refused(self):
        fixture = "public class A { public void Save() { FileManager.CreateFile(\"x\"); } }"
        with self.assertRaisesRegex(ValueError, "No recognizable"):
            self._check(fixture)

    def test_method_parser_failure_does_not_hide_real_source_file_deserializer(self):
        synthetic = "public class SaveAndLoad { private object Property => x.Deserialize(y); }"
        report = inspect_original_saveandload_scope(synthetic, fingerprint(synthetic))
        self.assertEqual(report["executable_deserialize_sites_in_file"], 1)
        self.assertEqual(report["binder_assignments_in_file"], 0)
        self.assertFalse(report["source_method_parser_resolved"])
        self.assertFalse(report["binder_proves_old_rgds_compatible"])

    def test_source_scope_rejects_textual_false_positive(self):
        synthetic = 'class S { string s = "Deserialize(x)"; /* Deserialize(y) */ }'
        with self.assertRaisesRegex(ValueError, "no executable deserialize"):
            inspect_original_saveandload_scope(synthetic, fingerprint(synthetic))

    def test_source_scope_rejects_wrong_fingerprint(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            inspect_original_saveandload_scope(HEADER, "0" * 64)

    def test_authenticated_loader_method_multiline_brace_and_binder(self):
        source = HEADER.replace("public T Load<T>", "public static T Load<T>").replace(") {", ")\\n {", 1)
        report = inspect_exact_original_loader_method(source, fingerprint(source))
        self.assertEqual(report["loader_deserialize_call_count"], 1)
        self.assertEqual(report["loader_binder_assignment_count"], 1)
        self.assertTrue(report["loader_signature_verified_from_runtime_manifest"])
        self.assertFalse(report["binder_version_runtime_compatibility_tested"])

    def test_authenticated_loader_method_missing_call_fails(self):
        source = HEADER.replace("public T Load<T>", "public static T Load<T>").replace("formatter.Deserialize(", "formatter.Serialize(")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            inspect_exact_original_loader_method(source, fingerprint(source))

    def test_authenticated_loader_method_wrong_sha_fails(self):
        with self.assertRaisesRegex(ValueError, "SHA256"):
            inspect_exact_original_loader_method(HEADER, "0" * 64)

    def test_binder_not_assumed_from_assembly_version(self):
        fixture = HEADER.replace("formatter.Binder = new LegacyBinder();", "")
        self.assertEqual(self._check(fixture)["binder_assignments_in_loaders"], 0)

    def test_unbalanced_original_body_refused(self):
        with self.assertRaisesRegex(ValueError, "Unbalanced"):
            self._check(HEADER.rsplit(" }", 1)[0])

    def test_non_load_named_deserializer_not_lost(self):
        fixture = HEADER.replace("Load<T>", "Read<T>")
        self.assertEqual(self._check(fixture)["loader_methods_with_deserialize"], 1)


if __name__ == "__main__":
    unittest.main()
