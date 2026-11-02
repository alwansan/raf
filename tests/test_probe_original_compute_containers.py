"""No game assets, shader bytes or Unity binaries used by these tests."""
import struct
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from scripts.probe_original_compute_containers import scan_blob, inspect_regular_sources


def synthetic_dxbc():
    payload = b"PERSONAL_SHADER_BINARY_MUST_NEVER_LEAK"
    header = bytearray(36 + 8 + len(payload))
    header[:4] = b"DXBC"
    struct.pack_into("<III", header, 20, 1, len(header), 1)
    struct.pack_into("<I", header, 32, 36)
    header[36:40] = b"SHEX"
    struct.pack_into("<I", header, 40, len(payload))
    header[44:] = payload
    return bytes(header)


class ComputeContainerTests(unittest.TestCase):
    def test_finds_valid_dxbc_without_disclosing_shader(self):
        data = b"serialized" + synthetic_dxbc() + b"padding"
        report = scan_blob(data)
        self.assertEqual(report["candidate_dxbc_magic_count"], 1)
        self.assertEqual(len(report["valid_dxbc_containers"]), 1)
        self.assertEqual(report["valid_dxbc_containers"][0]["offset_in_original_object"], 10)
        self.assertEqual(report["valid_dxbc_containers"][0]["chunk_tags"], {"SHEX": 1})
        self.assertFalse(report["valid_dxbc_containers"][0]["program_bytes_exported"])
        self.assertNotIn("PERSONAL_SHADER_BINARY_MUST_NEVER_LEAK", str(report))

    def test_rejects_fake_dxbc_magic_and_bounds(self):
        report = scan_blob(b"DXBC" + b"\x00" * 80)
        self.assertEqual(report["candidate_dxbc_magic_count"], 1)
        self.assertEqual(report["valid_dxbc_containers"], [])
        with self.assertRaisesRegex(ValueError, "bounded"):
            scan_blob(b"a" * (64 * 1024 * 1024 + 1))

    def test_inspects_only_owned_compute_objects_and_skips_lfs_pointer(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            regular = root / "sharedassets1.assets"
            regular.write_bytes(b"regular original fixture")
            missing = root / "resources.assets"
            missing.write_text("version https://git-lfs.github.com/spec/v1\n")
            shader = SimpleNamespace(
                type=SimpleNamespace(name="ComputeShader"),
                path_id=42,
                get_raw_data=lambda: b"private" + synthetic_dxbc(),
            )
            mesh = SimpleNamespace(type=SimpleNamespace(name="Mesh"), path_id=7)
            stub = SimpleNamespace(file=SimpleNamespace(objects={1: shader, 2: mesh}))
            with patch.dict(sys.modules, {"UnityPy": SimpleNamespace(load=lambda _: stub)}), patch(
                "scripts.probe_original_compute_containers.serialized_sources",
                return_value=[missing, regular]
            ):
                report = inspect_regular_sources(root)
            self.assertEqual(report["regular_unity_sources_examined"], 1)
            self.assertEqual(report["unavailable_lfs_owners"], ["resources.assets"])
            self.assertEqual(report["compute_objects_examined"], 1)
            self.assertFalse(report["all_nine_original_compute_objects_examined"])
            self.assertFalse(report["original_shaders_recovered"])
            self.assertFalse(report["original_source_modified"])
            self.assertNotIn("PERSONAL_SHADER_BINARY_MUST_NEVER_LEAK", str(report))


if __name__ == "__main__":
    unittest.main()
