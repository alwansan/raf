"""Regression: ambiguous aapt package declarations must not attest an APK/OBB pair."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, mock

from scripts import t5_verify_apk_obb_pair as verifier


class BadgingUniquenessTests(TestCase):
    def test_duplicate_package_lines_are_rejected(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            apk = root / verifier.APK_NAME
            obb = root / ("main.89." + verifier.PACKAGE + ".obb")
            delivery = root / "delivery.json"
            apk.write_bytes(b"apk fixture")
            obb.write_bytes(b"obb fixture")
            def entry(path):
                size, digest = verifier._sha(path)
                return {"name": path.name, "bytes": size, "sha256": digest,
                        "parts": [{"name": path.name, "bytes": size, "sha256": digest}]}
            # The XAPK logical record is metadata only in this checker.
            xapk = root / verifier.XAPK_NAME
            xapk.write_bytes(b"xapk fixture")
            delivery.write_text(json.dumps({
                "schema": 1, "package": verifier.PACKAGE, "version_code": "89",
                "companion_required": True, "transport_only_parts": True,
                "files": [entry(apk), entry(obb), entry(xapk)]
            }), encoding="utf-8")
            line = "package: name='com.alwansan.raft.androidtest' versionCode='89' versionName='1.0'\n"
            with mock.patch.object(verifier, "_zip_structure", return_value=5):
                self.assertTrue(verifier.verify_pair(delivery, apk, obb, line)["aapt_apk_package_version_match"])
                for ambiguous in (line + line,
                                  line + "package: name='other.app' versionCode='89' versionName='1'\n",
                                  line + "package: name='com.alwansan.raft.androidtest' versionCode='90' versionName='1'\n"):
                    with self.subTest(ambiguous=ambiguous):
                        with self.assertRaisesRegex(ValueError, "APK identity"):
                            verifier.verify_pair(delivery, apk, obb, ambiguous)
