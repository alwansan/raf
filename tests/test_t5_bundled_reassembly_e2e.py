"""T5: real packaging entrypoint -> copied release CLI -> split transport -> ZIP bytes.

All APK/OBB bytes are synthetic ZIP fixtures. This does not run Unity,
produce signed game media, or demonstrate an Android device installation.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import package_android_delivery as delivery


_BOOTSTRAP_WITHOUT_LINK = (
    "import os, runpy, sys; "
    "assert hasattr(os, 'link'), 'control requires a POSIX Python runtime'; "
    "del os.link; "
    "assert not hasattr(os, 'link'); "
    "sys.argv = [sys.argv[1], sys.argv[2]]; "
    "runpy.run_path(sys.argv[0], run_name='__main__')"
)


class T5BundledReassemblyE2E(unittest.TestCase):
    def create_delivery(self, root):
        apk = root / "synthetic.apk"
        obb = root / "synthetic.obb"
        with zipfile.ZipFile(apk, "w", compression=zipfile.ZIP_STORED) as z:
            z.writestr("classes.dex", b"FAKE-DEX-PAYLOAD-" * 90)
        with zipfile.ZipFile(obb, "w", compression=zipfile.ZIP_STORED) as z:
            z.writestr("assets/bin/Data/level0", b"FAKE-UNITY-ASSET-" * 96)
        badging = root / "badging.txt"
        badging.write_text(
            "package: name='com.alwansan.raft.androidtest' versionCode='77' "
            "versionName='synthetic'\nsdkVersion:'23'\ntargetSdkVersion:'35'\n"
        )
        output = root / "release"
        # Exercise the actual packaging CLI entrypoint, not just package().
        # Tiny split limits force 3 logical output files into multiple parts.
        original_package = delivery.package

        def small_transport(*args, **kwargs):
            self.assertFalse(kwargs)
            return original_package(*args, part_bytes=257, asset_limit=500)

        with patch.object(delivery, "package", side_effect=small_transport), patch.object(
            sys, "argv",
            ["package_android_delivery.py", "--apk", str(apk),
             "--obb", str(obb), "--badging", str(badging),
             "--version-code", "77", "--output", str(output)]
        ):
            delivery.main()
        script = output / "reassemble.py"
        source = Path(delivery.__file__).with_name("reassemble_android_delivery.py")
        self.assertEqual(script.read_bytes(), source.read_bytes(),
                         "Release-bundled reassembler must equal production source")
        meta = json.loads((output / "delivery.json").read_text())
        self.assertEqual(meta["schema"], 1)
        self.assertTrue(meta["companion_required"])
        self.assertEqual(len(meta["files"]), 3)
        for record in meta["files"]:
            self.assertGreater(len(record["parts"]), 1)
            self.assertFalse((output / record["name"]).exists())
        return apk, obb, output, meta

    def cli_without_link(self, root, logical_name):
        script = root / "reassemble.py"
        return subprocess.run(
            [sys.executable, "-c", _BOOTSTRAP_WITHOUT_LINK,
             str(script), logical_name],
            cwd=root, capture_output=True, text=True, timeout=20,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        )

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "link"),
                         "Isolated missing-link CLI simulation needs POSIX Python")
    def test_actual_bundled_cli_reassembles_all_three_exact_files(self):
        with tempfile.TemporaryDirectory() as folder:
            apk, obb, out, meta = self.create_delivery(Path(folder))
            originals = {
                "Raft-Android-Test.apk": apk.read_bytes(),
                f"main.77.{delivery.PACKAGE}.obb": obb.read_bytes(),
            }
            for row in meta["files"]:
                result = self.cli_without_link(out, row["name"])
                self.assertEqual(result.returncode, 0, result.stderr)
                assembled = (out / row["name"]).read_bytes()
                self.assertEqual(len(assembled), row["bytes"])
                self.assertEqual(hashlib.sha256(assembled).hexdigest(), row["sha256"])
                if row["name"] in originals:
                    self.assertEqual(assembled, originals[row["name"]])
                else:
                    self.assertEqual(row["name"], "Raft-Android-Test.xapk")
                    with zipfile.ZipFile(out / row["name"]) as z:
                        self.assertIsNone(z.testzip())
                        self.assertEqual(z.read(delivery.PACKAGE + ".apk"), apk.read_bytes())
                        obb_name = f"main.77.{delivery.PACKAGE}.obb"
                        member = f"Android/obb/{delivery.PACKAGE}/{obb_name}"
                        self.assertEqual(z.read(member), obb.read_bytes())
                        self.assertEqual(json.loads(z.read("manifest.json"))["version_code"], "77")
                self.assertFalse((out / (row["name"] + ".assembling")).exists())

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "link"),
                         "Isolated missing-link CLI simulation needs POSIX Python")
    def test_actual_bundled_cli_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            _, _, out, _ = self.create_delivery(Path(folder))
            output = out / "Raft-Android-Test.xapk"
            sentinel = b"PRE-EXISTING-SIGNED-DELIVERY-DO-NOT-REPLACE"
            output.write_bytes(sentinel)
            result = self.cli_without_link(out, output.name)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing to overwrite output", result.stderr)
            self.assertEqual(output.read_bytes(), sentinel)
            self.assertFalse((out / (output.name + ".assembling")).exists())

    @unittest.skipUnless(os.name == "posix" and hasattr(os, "link"),
                         "Isolated missing-link CLI simulation needs POSIX Python")
    def test_actual_bundled_cli_rejects_corrupted_part_before_publishing(self):
        with tempfile.TemporaryDirectory() as folder:
            _, _, out, meta = self.create_delivery(Path(folder))
            row = next(r for r in meta["files"] if r["name"] == "Raft-Android-Test.xapk")
            part = out / row["parts"][1]["name"]
            part.write_bytes(b"X" * part.stat().st_size)
            result = self.cli_without_link(out, row["name"])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Download part SHA256 mismatch", result.stderr)
            self.assertFalse((out / row["name"]).exists())
            self.assertFalse((out / (row["name"] + ".assembling")).exists())


if __name__ == "__main__":
    unittest.main()
