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
        # Focus queries remain independent; identity checks now fail closed
        # for probes and release, without retaining Java Views across threads.

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

    def test_release_only_targets_original_nonzero_request_view_identity(self):
        source = SOURCE.read_text(encoding="utf-8")
        release = method_body(source, "ReleaseCapture")
        captured = release.index(
            "releaseViewIdentity = Volatile.Read(ref captureViewIdentity);")
        clearing = release.index("Volatile.Write(ref captureViewIdentity, 0);")
        queued = release.index("OnAndroidUi(() =>")
        self.assertLess(captured, clearing)
        self.assertLess(clearing, queued)
        self.assertIn("epoch++;", release)
        self.assertIn("int releaseEpoch = Volatile.Read(ref epoch);", release)
        self.assertIn("releaseEpoch != Volatile.Read(ref epoch) || requested", release)
        nonzero = release.index("releaseViewIdentity == 0")
        identity = release.index(
            "ViewIdentity(view) != releaseViewIdentity", nonzero)
        captured_other = release.index(
            'view.Call<bool>("hasPointerCapture")', identity)
        release_call = release.index(
            'view.Call("releasePointerCapture")', captured_other)
        self.assertLess(queued, nonzero)
        self.assertLess(nonzero, identity)
        self.assertLess(identity, captured_other)
        self.assertLess(captured_other, release_call)
        self.assertEqual(release.count('view.Call("releasePointerCapture")'), 1)
        # Source identity guard protects another focused View. It cannot prove
        # that Android automatically released the former View on focus loss.

    def test_release_never_retains_android_java_view_across_threads(self):
        source = SOURCE.read_text(encoding="utf-8")
        release = method_body(source, "ReleaseCapture")
        captured = release.split("OnAndroidUi(() =>", 1)[0]
        self.assertIn("int releaseViewIdentity;", captured)
        # Comments may mention AndroidJavaObject; reject actual JNI
        # wrapper construction/access before UI-thread dispatch instead.
        self.assertNotIn("new AndroidJavaObject(", captured)
        self.assertNotIn("Call<AndroidJavaObject>", captured)
        self.assertNotIn("GetStatic<AndroidJavaObject>", captured)
        self.assertNotIn("getCurrentFocus", captured)
        self.assertIn(
            'using (var view = activity.Call<AndroidJavaObject>("getCurrentFocus"))',
            release)
        self.assertIn("ViewIdentity(view) != releaseViewIdentity", release)

    def test_release_result_telemetry_is_nonblocking_and_disambiguated(self):
        source = SOURCE.read_text(encoding="utf-8")
        release = method_body(source, "ReleaseCapture")
        for status in ("superseded_generation", "unbound_request_view",
                       "focus_view_unavailable", "focused_view_changed",
                       "target_not_captured", "release_call_returned",
                       "jni_exception", "ui_dispatch_exception"):
            with self.subTest(status=status):
                self.assertIn('"' + status + '"', release)
        self.assertLess(release.index('view.Call("releasePointerCapture")'),
                        release.index('result = "release_call_returned"'))
        self.assertIn("releaseEpoch != Volatile.Read(ref epoch) || requested", release)
        helper = source.split("private static void ReportReleaseOutcome(string result)", 1)[1]
        helper = helper.split("private void ReleaseCapture()", 1)[0]
        self.assertIn('"physical_mouse_capture_release_outcome"', helper)
        self.assertIn("native_release_confirmed=false", helper)
        self.assertIn("catch (Exception)", helper)
        self.assertNotIn("ReportReleaseOutcome(", method_body(source, "Update"))

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
