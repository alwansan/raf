import unittest
from scripts.b07_probe_original_world_callbacks import fingerprint
from scripts.t4_original_filemanager_contract import inspect

S = """public class SaveAndLoad {
 public static T Load<T>(string filename) {
  try { return (T)new BinaryFormatter().Deserialize(FileManager.OpenFile(filename)); }
  catch (System.Exception ex) { return default(T); }
 }
 public static void Save(object obj, string filename) { FileManager.CreateFile(filename); }
}
"""
F = """public class FileManager {
 public static System.IO.Stream OpenFile(string p) {
  try { return System.IO.File.OpenRead(p); }
  catch (System.Exception ex) { throw; }
 }
 public static System.IO.Stream CreateFile(string p) { return System.IO.File.Create(p); }
}
"""


def verify(s=S, f=F):
    return inspect(s, f, fingerprint(s), fingerprint(f))


class TestT4FileManager(unittest.TestCase):
    def test_unique_targets_counted_without_runtime_success(self):
        r = verify()
        self.assertTrue(r["read"]["unique_target"])
        self.assertTrue(r["write"]["unique_target"])
        self.assertEqual(r["read"]["direct_io_site_count"], 1)
        self.assertEqual(r["read"]["internal_catch_site_count"], 1)
        self.assertFalse(r["rgd_create_save_reopen_proven"])

    def test_source_hash_gate_rejects_different_source(self):
        with self.assertRaisesRegex(ValueError, "fingerprints"):
            inspect(S, F, "0"*64, fingerprint(F))

    def test_filemanager_hash_gate_rejects_different_source(self):
        with self.assertRaisesRegex(ValueError, "fingerprints"):
            inspect(S, F, fingerprint(S), "0"*64)

    def test_comment_string_fake_edge_masked(self):
        s = S.replace("FileManager.CreateFile(filename);",
                      'string fake = "FileManager.OpenFile(x)"; // FileManager.CreateFile(y)\n FileManager.CreateFile(filename);')
        self.assertEqual(verify(s=s)["write"]["possible_overloads"], 1)

    def test_missing_load_edge_rejected(self):
        with self.assertRaisesRegex(ValueError, "direct call"):
            verify(s=S.replace("FileManager.OpenFile(filename)", "Unknown.OpenFile(filename)"))

    def test_missing_concrete_target_classified_unknown(self):
        r = verify(f=F.replace("OpenFile(", "Unknown("))
        self.assertFalse(r["read"]["unique_target"])
        self.assertIsNone(r["read"]["direct_io_site_count"])
        self.assertEqual(r["read"]["unresolved_original_name_tokens"], 0)

    def test_overload_not_falsely_resolved(self):
        f = F.replace(" public static System.IO.Stream CreateFile(string p)",
                      " public static System.IO.Stream CreateFile(string p, bool second) { return System.IO.File.OpenWrite(p); }\n"
                      " public static System.IO.Stream CreateFile(string p)")
        r = verify(f=f)
        self.assertEqual(r["write"]["possible_overloads"], 2)
        self.assertIsNone(r["write"]["direct_io_site_count"])
        self.assertFalse(r["write"]["unique_target"])

    def test_comment_fake_catch_masked(self):
        f = F.replace("return System.IO.File.OpenRead(p);",
                      'string fake = "catch (E) {}"; // catch (Y) {}\n return System.IO.File.OpenRead(p);')
        self.assertEqual(verify(f=f)["read"]["internal_catch_site_count"], 1)

    def test_original_load_catch_missing_rejected(self):
        with self.assertRaisesRegex(ValueError, "catch contract"):
            verify(s=S.replace("catch (System.Exception ex) { return default(T); }", ""))

    def test_fake_class_declaration_rejected(self):
        with self.assertRaisesRegex(ValueError, "declaration"):
            verify(f=F.replace("class FileManager", "class Other /* class FileManager */"))


if __name__ == "__main__":
    unittest.main()
