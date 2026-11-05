"""T5: synthetic Android/Termux Python without os.link, exact delivery bytes.

No APK/OBB/game assets; the module-os proxy has no link attribute at all.
The fallback is no-clobber but cannot promise atomic visibility on abrupt death.
"""
import errno
import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts import reassemble_android_delivery as delivery


def fixture(root):
    name = "Raft-Android-Test.xapk"
    blocks = [b"synthetic-APK-payload-" * 23, b"synthetic-OBB-payload-" * 31]
    parts = []
    for i, payload in enumerate(blocks, 1):
        part_name = name + f".part{i:03d}"
        (root / part_name).write_bytes(payload)
        parts.append({"name": part_name, "bytes": len(payload),
                      "sha256": hashlib.sha256(payload).hexdigest()})
    joined = b"".join(blocks)
    (root / "delivery.json").write_text(json.dumps({"schema": 1, "files": [
        {"name": name, "bytes": len(joined),
         "sha256": hashlib.sha256(joined).hexdigest(), "parts": parts}
    ]}))
    return name, joined


def without_link(fsync=os.fsync):
    """The reassembler receives an os proxy that genuinely lacks 'link'."""
    proxy = SimpleNamespace(fstat=os.fstat, fsync=fsync)
    assert not hasattr(proxy, "link")
    return patch.object(delivery, "os", proxy)


class T5PortableReassemblyTests(unittest.TestCase):
    def test_missing_os_link_assembles_exact_bytes_without_temp(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            name, expected = fixture(root)
            with without_link():
                output = delivery.reassemble(root, name)
            self.assertEqual(output.read_bytes(), expected)
            self.assertFalse((root / (name + ".assembling")).exists())
            self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(),
                             hashlib.sha256(expected).hexdigest())

    def test_missing_os_link_existing_signed_name_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            name, _ = fixture(root)
            original = b"existing-signed-file-not-to-overwrite"
            (root / name).write_bytes(original)
            with without_link(), self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
                delivery.reassemble(root, name)
            self.assertEqual((root / name).read_bytes(), original)

    def test_missing_os_link_competing_creation_during_precheck_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            name, _ = fixture(root)
            output = root / name
            competing = b"competing-verified-output"
            real_exists = Path.exists
            triggered = [False]

            def injected_exists(path):
                if path == output and not triggered[0]:
                    triggered[0] = True
                    self.assertFalse(real_exists(output))
                    output.write_bytes(competing)
                    return False  # Pretend precheck saw absence before competitor.
                return real_exists(path)

            with without_link(), patch.object(Path, "exists", injected_exists):
                with self.assertRaisesRegex(ValueError, "Refusing to overwrite"):
                    delivery.reassemble(root, name)
            self.assertTrue(triggered[0])
            self.assertEqual(output.read_bytes(), competing)

    def test_missing_os_link_bad_full_digest_cleans_owned_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            name, _ = fixture(root)
            meta = json.loads((root / "delivery.json").read_text())
            meta["files"][0]["sha256"] = "0" * 64
            (root / "delivery.json").write_text(json.dumps(meta))
            with without_link(), self.assertRaisesRegex(ValueError, "Assembled file SHA256 mismatch"):
                delivery.reassemble(root, name)
            self.assertFalse((root / name).exists())
            self.assertFalse((root / (name + ".assembling")).exists())

    def test_missing_os_link_write_fsync_error_cleans_owned_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            name, _ = fixture(root)
            simulated_fsync = Mock(side_effect=OSError(errno.ENOSPC, "synthetic-full-disk"))
            with without_link(fsync=simulated_fsync):
                with self.assertRaises(OSError):
                    delivery.reassemble(root, name)
            self.assertEqual(simulated_fsync.call_count, 1)
            self.assertFalse((root / name).exists())
            self.assertFalse((root / (name + ".assembling")).exists())

    def test_corrupted_part_is_rejected_before_exclusive_publish(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            name, _ = fixture(root)
            part = root / (name + ".part002")
            part.write_bytes(b"X" * part.stat().st_size)
            with without_link(), self.assertRaisesRegex(ValueError, "Download part SHA256 mismatch"):
                delivery.reassemble(root, name)
            self.assertFalse((root / name).exists())


if __name__ == "__main__":
    unittest.main()
