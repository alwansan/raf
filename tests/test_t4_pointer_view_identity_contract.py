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

    def test_mismatched_probe_fails_back_before_accepting_other_view_capture(self):
        source = SOURCE.read_text(encoding="utf-8")
        body = method_body(source, "ProbeCapturedPointer")
        mismatch = body.index("requestedIdentity == 0 || probedIdentity != requestedIdentity")
        fallback = body.index("ObserveNativeCapture(token, false);", mismatch)
        early_return = body.index("return;", fallback)
        active = body.index("bool active = view != null", early_return)
        self.assertLess(mismatch, fallback)
        self.assertLess(fallback, early_return)
        self.assertLess(early_return, active)
        # This is a source ordering contract, not proof of Android pointer
        # capture, camera direction, or a working Raft cursor on a device.

    def test_uninitialized_identity_cannot_accept_foreign_view_capture(self):
        source = SOURCE.read_text(encoding="utf-8")
        probe = method_body(source, "ProbeCapturedPointer")
        request = method_body(source, "RequestCapture")
        self.assertIn("requestedIdentity == 0 || probedIdentity != requestedIdentity", probe)
        self.assertIn("Volatile.Write(ref captureViewIdentity, 0);", request)
        self.assertLess(
            request.index("Volatile.Write(ref captureViewIdentity, 0);"),
            request.index("OnAndroidUi(() =>"))
        # Request without a focused View leaves identity zero; a later probe
        # must not trust capture belonging to another focused View.

    def test_epoch_guards_do_not_encode_view_identity(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn("currentEpoch != Volatile.Read(ref epoch)", method_body(source, "RequestCapture"))
        self.assertIn("token != Volatile.Read(ref epoch)", method_body(source, "ProbeCapturedPointer"))
        self.assertIn("releaseEpoch != Volatile.Read(ref epoch)", method_body(source, "ReleaseCapture"))
        # Generation guards alone do not identify the View. A separate,
        # non-invasive diagnostic now compares the request and probe Views.
        self.assertIn("captureViewIdentity", source)
        self.assertIn('"identityHashCode"', source)
        self.assertIn("probedIdentity != requestedIdentity", method_body(source, "ProbeCapturedPointer"))
        self.assertIn("Volatile.Write(ref captureViewIdentity, ViewIdentity(view))", method_body(source, "RequestCapture"))
        self.assertIn("Volatile.Write(ref captureViewIdentity, 0)", method_body(source, "ReleaseCapture"))
        self.assertIn('"physical_mouse_capture_view_changed"', source)
        # This is diagnostic only; do not change capture or legacy axis routing.


if __name__ == "__main__":
    unittest.main()
