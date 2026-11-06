"""T4 isolated Android View identity audit; no device/Unity acceptance implied.

Run: python3 -m unittest tests/test_t4_pointer_view_identity_contract.py
The test records the current source gap without claiming a phone reproduction.
"""
import pathlib
import re
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"


def method_body(source, name):
    match = re.search(r"private void " + re.escape(name) + r"\(\)", source)
    if not match:
        raise AssertionError("Missing method " + name)
    start = source.index("{", match.end())
    depth = 0
    for i in range(start, len(source)):
        depth += (source[i] == "{") - (source[i] == "}")
        if depth == 0:
            return source[start:i + 1]
    raise AssertionError("Unterminated method " + name)


class PointerViewIdentityAudit(unittest.TestCase):
    def test_capture_operations_retrieve_focus_independently(self):
        source = SOURCE.read_text(encoding="utf-8")
        methods = ("RequestCapture", "ProbeCapturedPointer", "ReleaseCapture")
        bodies = {name: method_body(source, name) for name in methods}
        for name, body in bodies.items():
            with self.subTest(name=name):
                self.assertIn('getCurrentFocus', body)
        # Independent focus queries are NOT evidence of same View identity.
        # A future fix should explicitly bind request/probe/release to the
        # same capture target and replace this characterization test.

    def test_epoch_guards_do_not_encode_view_identity(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("currentEpoch != Volatile.Read(ref epoch)", method_body(source, "RequestCapture"))
        self.assertIn("token != Volatile.Read(ref epoch)", method_body(source, "ProbeCapturedPointer"))
        self.assertIn("releaseEpoch != Volatile.Read(ref epoch)", method_body(source, "ReleaseCapture"))
        self.assertNotIn("captureViewIdentity", source)
        # Generation guards prevent stale asynchronous callbacks but do not
        # identify which Android View currently owns pointer capture.


if __name__ == "__main__":
    unittest.main()
