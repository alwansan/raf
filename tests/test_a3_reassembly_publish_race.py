"""A3 reproducible final publication race in split Android delivery reassembler.

Uses only tiny synthetic part files; does not create native APK or use original
Raft assets. Inject competing writer after the last existence *check* but
before the original Path.rename call.
"""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.reassemble_android_delivery import reassemble


def fixture(root):
    name = "Raft-Android-Test.xapk"
    blocks = (b"fake-signed-apk-" * 7, b"fake-companion-obb-" * 9)
    parts = []
    for i, data in enumerate(blocks, 1):
        filename = f"{name}.part{i:03}"
        (root / filename).write_bytes(data)
        parts.append({"name": filename, "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest()})
    combined = b"".join(blocks)
    manifest = {"schema": 1, "files": [{
        "name": name, "bytes": len(combined),
        "sha256": hashlib.sha256(combined).hexdigest(), "parts": parts}]}
    (root / "delivery.json").write_text(json.dumps(manifest))
    return name, combined


class A3ReassemblyPublicationTests(unittest.TestCase):
    def test_valid_split_package_still_assembles_byte_for_byte(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name, expected = fixture(root)
            result = reassemble(root, name)
            self.assertEqual(result.read_bytes(), expected)
            self.assertFalse((root / (name + ".assembling")).exists())

    def test_competing_output_created_after_second_precheck_must_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name, _ = fixture(root)
            output = root / name
            sentinel = b"preserve-previously-published-signed-xapk"
            original_exists = Path.exists
            checks = [0]
            def exists_with_competing_writer(path):
                if path == output:
                    checks[0] += 1
                    if checks[0] == 2:
                        # Existing code returns False to caller then uses
                        # POSIX rename, which *replaces* this new file.
                        self.assertFalse(original_exists(output))
                        output.write_bytes(sentinel)
                        return False
                return original_exists(path)
            with patch.object(Path, "exists", exists_with_competing_writer):
                with self.assertRaisesRegex(ValueError, "Refusing to overwrite output"):
                    reassemble(root, name)
            self.assertEqual(checks[0], 2)
            self.assertEqual(output.read_bytes(), sentinel)
            self.assertFalse((root / (name + ".assembling")).exists())

    def test_existing_output_never_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name, _ = fixture(root)
            output = root / name
            output.write_bytes(b"do-not-replace")
            with self.assertRaisesRegex(ValueError, "Refusing to overwrite output"):
                reassemble(root, name)
            self.assertEqual(output.read_bytes(), b"do-not-replace")
            self.assertFalse((root / (name + ".assembling")).exists())

    def test_hash_mismatch_removes_only_owned_temporary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name, _ = fixture(root)
            manifest = json.loads((root / "delivery.json").read_text())
            manifest["files"][0]["sha256"] = "0" * 64
            (root / "delivery.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Assembled file SHA256 mismatch"):
                reassemble(root, name)
            self.assertFalse((root / name).exists())
            self.assertFalse((root / (name + ".assembling")).exists())


    def test_unsupported_android_hardlinks_fail_without_publishing_partial_output(self):
        import errno
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            name, _ = fixture(root)
            with patch("scripts.reassemble_android_delivery.os.link",
                       side_effect=OSError(errno.EPERM, "shared-storage-hardlink-denied")):
                with self.assertRaisesRegex(OSError, "Termux home"):
                    reassemble(root, name)
            self.assertFalse((root / name).exists())
            self.assertFalse((root / (name + ".assembling")).exists())



if __name__ == "__main__":
    unittest.main()
