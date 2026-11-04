"""Source-free synthetic negative controls for B07's coroutine entry probe."""
import unittest

from scripts.b07_probe_original_world_callbacks import fingerprint, method_body
from scripts.b07_world_coroutine_trace import (
    ENTRY, TRACE_OPERATION, _instrument_pinned,
)


SOURCE = """using System;
using System.Collections;
public class Raft_Network {
    public IEnumerator WorldHasBeenLoaded() {
        string decoy = "yield return nope; WorldHasBeenRecieved = true;";
        yield return "scene";
        if (true) { yield return "assets"; }
        throw new InvalidOperationException("synthetic-failure");
    }
    public void NextMethod() { }
}
"""


def adapt(source, source_pin=None, body_pin=None):
    method_sha = fingerprint(method_body(source, "WorldHasBeenLoaded")[1])
    return _instrument_pinned(
        source, source_pin or fingerprint(source), body_pin or method_sha,
    )


class B07WorldCoroutineTraceTests(unittest.TestCase):
    def test_inject_once_at_first_movenext_preserving_original_body(self):
        adapted = adapt(SOURCE)
        body = method_body(SOURCE, "WorldHasBeenLoaded")[1]
        self.assertEqual(method_body(adapted, "WorldHasBeenLoaded")[1], ENTRY + body)
        self.assertEqual(adapted.replace(ENTRY, "", 1), SOURCE)
        self.assertEqual(adapted.count(TRACE_OPERATION), 1)
        self.assertEqual(adapted.count("yield return"), SOURCE.count("yield return"))
        self.assertEqual(adapted.count("WorldHasBeenRecieved = true;"), SOURCE.count("WorldHasBeenRecieved = true;"))
        self.assertIn("public void NextMethod() { }", adapted)
        self.assertIn("#if UNITY_ANDROID && !UNITY_EDITOR", adapted)

    def test_changed_original_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "source SHA"):
            _instrument_pinned(SOURCE + "\n//changed", fingerprint(SOURCE),
                               fingerprint(method_body(SOURCE, "WorldHasBeenLoaded")[1]))

    def test_changed_body_sha_rejected(self):
        with self.assertRaisesRegex(ValueError, "body SHA"):
            _instrument_pinned(SOURCE, fingerprint(SOURCE), "0" * 64)

    def test_wrong_return_type_rejected(self):
        s = SOURCE.replace("public IEnumerator WorldHasBeenLoaded()", "public bool WorldHasBeenLoaded()")
        with self.assertRaisesRegex(ValueError, "body SHA/type"):
            adapt(s)

    def test_fake_yield_only_in_string_rejected(self):
        s = SOURCE.replace('yield return "scene";', 'var marker = "yield return scene";').replace(
            'if (true) { yield return "assets"; }', "if (true) { var value = 1; }"
        )
        with self.assertRaisesRegex(ValueError, "no iterator yield"):
            adapt(s)

    def test_preprocessor_original_body_rejected(self):
        s = SOURCE.replace('yield return "scene";', '#if UNITY_ANDROID\n        yield return "scene";\n#endif')
        with self.assertRaisesRegex(ValueError, "conditional original iterator"):
            adapt(s)

    def test_ambiguous_declarations_rejected(self):
        s = SOURCE + "\npublic class Extra { public IEnumerator WorldHasBeenLoaded() { yield return null; } }"
        # Original-method finder rejects ambiguity on its own, not via source pin.
        with self.assertRaisesRegex(ValueError, "one original"):
            adapt(s)

    def test_double_instrumentation_rejected(self):
        updated = adapt(SOURCE)
        with self.assertRaisesRegex(ValueError, "source SHA"):
            _instrument_pinned(
                updated, fingerprint(SOURCE),
                fingerprint(method_body(SOURCE, "WorldHasBeenLoaded")[1]),
            )

    def test_production_pins_cannot_accept_synthetic_fixture(self):
        from scripts.b07_world_coroutine_trace import instrument_original_coroutine
        with self.assertRaisesRegex(ValueError, "source SHA"):
            instrument_original_coroutine(SOURCE)


if __name__ == "__main__":
    unittest.main()
