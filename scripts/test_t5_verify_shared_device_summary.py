#!/usr/bin/env python3
"""Regression controls for T5's read-only CL evidence gate."""
import unittest
from copy import deepcopy
from scripts.t5_verify_shared_device_summary import verify

PACK = "a" * 64
SOURCE = "b" * 40
def fixture():
    rows = []
    for n in range(1, 7):
        key = f"T3-{n:02d}"
        rows.append({"case_id": key, "worker": "T3", "result": {
            "id": key, "status": "EVIDENCE_READY", "pack_sha256": PACK,
            "image_uri": "content://media/external/downloads/123",
            "observed": ("contract=true gl_error=0x0 png_bytes=123 "
                         "png_sha256=" + "c"*64 + " "
                         "capture=verified-GLSurfaceView-overlay-on-window "
                         "verified_surface_pixels=true")}})
    return {"session": "test", "pack_sha256": PACK, "app_source": SOURCE, "results": rows}

class GateTests(unittest.TestCase):
    def test_complete(self):
        self.assertEqual(verify(fixture()), [])
    def test_missing(self):
        a = fixture()
        a["results"].pop()
        self.assertTrue(any("missing T3" in e for e in verify(a)))
    def test_duplicate(self):
        a = fixture()
        a["results"].append(deepcopy(a["results"][0]))
        self.assertTrue(any("duplicate" in e for e in verify(a)))
    def test_pack_mismatch(self):
        a = fixture()
        a["results"][0]["result"]["pack_sha256"] = "d"*64
        self.assertTrue(any("pack mismatch" in e for e in verify(a)))
    def test_black_or_unverified_capture(self):
        a = fixture()
        a["results"][0]["result"]["observed"] = "contract=true gl_error=0x0 png_bytes=123 png_sha256=" + "c"*64
        self.assertTrue(any("unverified" in e for e in verify(a)))
    def test_zero_png(self):
        a = fixture()
        a["results"][0]["result"]["observed"] = a["results"][0]["result"]["observed"].replace("png_bytes=123", "png_bytes=0")
        self.assertTrue(any("PNG metadata" in e for e in verify(a)))
    def test_embedded_false_markers(self):
        a = fixture()
        a["results"][0]["result"]["observed"] = (
            "not_capture=verified-GLSurfaceView-overlay-on-window "
            "unverified_surface_pixels=true not_gl_error=0x0 "
            "not_contract=true png_bytes=123 png_sha256=" + "c"*64
        )
        self.assertTrue(any("unverified" in e for e in verify(a)))

    def test_duplicate_conflicting_markers(self):
        a = fixture()
        a["results"][0]["result"]["observed"] += " verified_surface_pixels=false"
        self.assertTrue(any("unverified" in e for e in verify(a)))

    def test_png_bytes_trailing_garbage(self):
        a = fixture()
        a["results"][0]["result"]["observed"] = a["results"][0]["result"]["observed"].replace(
            "png_bytes=123", "png_bytes=123junk")
        self.assertTrue(any("PNG metadata" in e for e in verify(a)))

    def test_wrong_identity(self):
        a = fixture()
        a["results"][0]["result"]["id"] = "T3-99"
        self.assertTrue(any("identity mismatch" in e for e in verify(a)))

if __name__ == "__main__":
    unittest.main()
