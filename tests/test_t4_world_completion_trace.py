"""T4 source-free controls: log a real world-ready write, never fabricate it."""
import hashlib
import unittest

from scripts.b07_world_coroutine_trace import ENTRY
from scripts.instrument_android_runtime_operations import (
    instrument, trace_original_world_completion,
)

ORIGINAL = (
    "using System.Collections;\n"
    "class Raft_Network {\n"
    " public IEnumerator WorldHasBeenLoaded() {"
    + ENTRY +
    "  string decoy = \"WorldHasBeenRecieved = true; BroadCastToScene(x);\";\n"
    "  Helper.BroadCastToScene(1);\n"
    "  if (ready)\n"
    "    WorldHasBeenRecieved = true;\n"
    "  else\n"
    "    RecoverWithoutChangingWorldFlag();\n"
    "  yield return null;\n"
    " }\n"
    "}\n"
)


class T4OriginalCompletionTests(unittest.TestCase):
    def test_exact_statement_scoped_trace_preserves_branch_and_coroutine(self):
        actual = trace_original_world_completion(ORIGINAL)
        self.assertEqual(actual.count("WorldHasBeenLoaded.originalCompletionAssigned"), 1)
        self.assertIn("  if (ready)\n    { WorldHasBeenRecieved = true;", actual)
        self.assertIn("  else\n    RecoverWithoutChangingWorldFlag();", actual)
        self.assertEqual(actual.count("yield return null;"), 1)
        self.assertEqual(actual.count("WorldHasBeenLoaded.firstMoveNext"), 1)
        self.assertEqual(actual.count("WorldHasBeenRecieved = true;"), ORIGINAL.count("WorldHasBeenRecieved = true;"))
        self.assertIn("#if UNITY_ANDROID && !UNITY_EDITOR", actual)
        block_start = actual.index("{ WorldHasBeenRecieved = true;\n#if")
        block_end = actual.index("#endif\n}", block_start) + len("#endif\n}")
        self.assertEqual(
            actual[:block_start] + "WorldHasBeenRecieved = true;" + actual[block_end:],
            ORIGINAL,
        )

    def test_same_gated_instrument_adapter_runs_after_manifest_sha(self):
        m = {"sources": {"Raft_Network": {"sha256": hashlib.sha256(ORIGINAL.encode()).hexdigest(),
               "area": "session", "methods": []}}}
        actual = instrument("Raft_Network", ORIGINAL, m)
        self.assertEqual(actual.count("WorldHasBeenLoaded.originalCompletionAssigned"), 1)
        self.assertEqual(actual.count("WorldHasBeenRecieved = true;"), 2)
        with self.assertRaisesRegex(ValueError, "Unknown adapted original revision"):
            instrument("Raft_Network", ORIGINAL.replace("yield return null;", "yield break;"), m)

    def test_missing_genuine_assignment_is_rejected(self):
        candidate = ORIGINAL.replace("WorldHasBeenRecieved = true;\n  else", "CallNotReady();\n  else")
        with self.assertRaisesRegex(ValueError, "one original world assignment"):
            trace_original_world_completion(candidate)

    def test_two_assignments_are_rejected(self):
        candidate = ORIGINAL.replace(
            "    WorldHasBeenRecieved = true;\n  else",
            "    WorldHasBeenRecieved = true;\n    WorldHasBeenRecieved = true;\n  else",
        )
        with self.assertRaisesRegex(ValueError, "one original world assignment"):
            trace_original_world_completion(candidate)

    def test_comment_or_string_decoys_are_not_genuine(self):
        candidate = ORIGINAL.replace(
            "    WorldHasBeenRecieved = true;\n  else",
            "    // WorldHasBeenRecieved = true;\n    NotReady();\n  else",
        )
        with self.assertRaisesRegex(ValueError, "one original world assignment"):
            trace_original_world_completion(candidate)

    def test_broadcast_after_completion_is_rejected(self):
        candidate = ORIGINAL.replace("  Helper.BroadCastToScene(1);\n", "").replace(
            "  yield return null;", "  Helper.BroadCastToScene(1);\n  yield return null;"
        )
        with self.assertRaisesRegex(ValueError, "following scene broadcast"):
            trace_original_world_completion(candidate)

    def test_missing_b07_entry_refused(self):
        with self.assertRaisesRegex(ValueError, "B07 authenticated"):
            trace_original_world_completion(ORIGINAL.replace(ENTRY, "", 1))

    def test_reapplying_trace_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicate world completion"):
            trace_original_world_completion(trace_original_world_completion(ORIGINAL))

    def test_wrong_method_return_type_refused(self):
        with self.assertRaisesRegex(ValueError, "B07 authenticated"):
            trace_original_world_completion(ORIGINAL.replace("IEnumerator WorldHasBeenLoaded", "void WorldHasBeenLoaded"))

    def test_fake_assignment_in_other_method_not_accepted(self):
        candidate = ORIGINAL.replace(
            "    WorldHasBeenRecieved = true;\n  else",
            "    NotReady();\n  else",
        ).replace("  yield return null;\n }\n", "  yield return null;\n }\n void Other() { WorldHasBeenRecieved = true; }\n")
        with self.assertRaises(ValueError):
            trace_original_world_completion(candidate)


if __name__ == "__main__":
    unittest.main()
