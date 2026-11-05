"""Source-free T4 Load<T> filename-path instrumentation controls."""
import hashlib
import unittest

from scripts.instrument_android_runtime_operations import (
    body_bounds, trace_caught_original_load_error, wrap,
)

SIGNATURE = "public static T Load<T>(string filename)"
ORIGINAL = """class SaveAndLoad {
    public static T Load<T>(string filename) {
        try { return (T)Deserialize(filename); }
        catch (System.Exception) { return default(T); }
    }
}"""


class LoadArgumentSnapshotTests(unittest.TestCase):
    def test_exact_original_body_is_present_and_load_snapshot_is_finally_only(self):
        start, end = body_bounds(ORIGINAL, SIGNATURE)
        before = ORIGINAL[start:end]
        wrapped = wrap(ORIGINAL, SIGNATURE, "save", "filename")
        self.assertIn(before, wrapped)
        self.assertEqual(wrapped.count('"Load.argumentFileSnapshot"'), 1)
        self.assertEqual(wrapped.count('"Load.argumentFileSnapshot.unavailable"'), 1)
        self.assertIn("System.IO.File.Exists(filename)", wrapped)
        self.assertIn("new System.IO.FileInfo(filename).Length == 0L", wrapped)
        self.assertLess(wrapped.index("} finally { "), wrapped.index('"Load.argumentFileSnapshot"'))
        self.assertLess(wrapped.index('"Load.argumentFileSnapshot"'),
                        wrapped.index("AndroidRuntimeLog.EndOperation"))
        self.assertIn("readback_and_deserialization_unverified=true", wrapped)
        self.assertNotIn("Path.Combine(", wrapped)
        self.assertNotIn("filename =", wrapped)

    def test_only_load_in_save_area_gets_snapshot(self):
        self.assertNotIn("Load.argumentFileSnapshot",
                         wrap(ORIGINAL, SIGNATURE, "world", "filename"))
        other = "public static int LoadOther(string filename) { return 1; }"
        self.assertNotIn("Load.argumentFileSnapshot",
                         wrap(other, "public static int LoadOther(string filename)", "save"))
        save = "private void Save(string filename, RGD raftgamedata) { return; }"
        self.assertNotIn("Load.argumentFileSnapshot",
                         wrap(save, "private void Save(string filename, RGD raftgamedata)", "save"))

    def test_load_snapshot_cannot_create_or_rewrite_game_files(self):
        source = SIGNATURE + " { return default(T); }"
        wrapped = wrap(source, SIGNATURE, "save", "filename")
        self.assertNotIn("System.IO.File.Create(", wrapped)
        self.assertNotIn("System.IO.File.Write", wrapped)
        self.assertNotIn("File.ReadAllBytes", wrapped)
        self.assertNotIn("WorldHasBeenRecieved = true", wrapped)
        self.assertIn("catch (System.Exception) { }", wrapped)
        self.assertIn("return default(T);", wrapped)

    def test_caught_exception_and_snapshot_coexist_and_original_catch_remains(self):
        with_caught = trace_caught_original_load_error(ORIGINAL)
        wrapped = wrap(with_caught, SIGNATURE, "save", "filename")
        self.assertIn('"Load.caughtException"', wrapped)
        self.assertIn('"Load.argumentFileSnapshot"', wrapped)
        self.assertIn("catch (System.Exception)", wrapped)
        self.assertIn("return default(T);", wrapped)
        self.assertEqual(wrapped.count("return (T)Deserialize(filename);"), 1)

    def test_source_gate_and_duplicate_instrumentation_fail_closed(self):
        wrapped = wrap(ORIGINAL, SIGNATURE, "save", "filename")
        with self.assertRaisesRegex(ValueError, "duplicate operation"):
            wrap(wrapped, SIGNATURE, "save", "filename")
        changed = ORIGINAL.replace("Deserialize(filename)", "Erase(filename)")
        self.assertNotEqual(hashlib.sha256(changed.encode()).hexdigest(),
                            hashlib.sha256(ORIGINAL.encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
