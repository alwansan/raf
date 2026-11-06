"""Synthetic bounded nested Android APK/OBB ZIP range tests; no original game bytes."""
import io
import struct
import unittest
import warnings
import zipfile

from scripts.t5_probe_github_artifact_zip_range import LimitedRangeIO, ProbeError
from scripts.t5_probe_signed_nested_zip_range import (
    MemberSliceIO, MAX_TOTAL_TRANSFER, scan_signed_checkpoint, stored_member_offset,
)

PACKAGE = "com.alwansan.raft.androidtest"


def packed(rows, compress=zipfile.ZIP_STORED):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=compress, allowZip64=True) as file:
        for name, data in rows:
            file.writestr(name, data)
    return output.getvalue()


def fake_elf():
    header = bytearray(64)
    header[:7] = b"\x7fELF\x02\x01\x01"
    struct.pack_into("<HHI", header, 16, 3, 183, 1)
    struct.pack_into("<H", header, 52, 64)
    return bytes(header)


def valid_apk(extra=None):
    content = [
        ("AndroidManifest.xml", b"\x03\x00\x08\x00" + b"synthetic-AXML"),
        ("classes.dex", b"dex\n035\0" + b"synthetic-dex"),
        ("lib/arm64-v8a/libil2cpp.so", fake_elf()),
        ("lib/arm64-v8a/libunity.so", fake_elf()),
        ("assets/bin/Data/globalgamemanagers", b"synthetic-unity-global"),
        ("assets/bin/Data/resources.assets", b"synthetic-unity-assets"),
    ]
    if extra:
        content += extra
    return packed(content)


def valid_obb(extra=None):
    content = [
        ("assets/bin/Data/resources.assets", b"synthetic-original-asset"),
        ("assets/bin/Data/sharedassets0.assets", b"synthetic-shared"),
        ("assets/bin/Data/resources.assets.resS", b"synthetic-resS"),
    ]
    if extra:
        content += extra
    return packed(content)


def outer(apk=None, obb=None, compress=zipfile.ZIP_STORED):
    apk = valid_apk() if apk is None else apk
    obb = valid_obb() if obb is None else obb
    data = packed([
        ("Raft-Android-Test.apk", apk),
        ("main.89." + PACKAGE + ".obb", obb),
    ], compress=compress)
    return data, len(apk), len(obb)


def seekable(blob, virtual_length=None, cap=MAX_TOTAL_TRANSFER):
    total = len(blob) if virtual_length is None else virtual_length
    leading = total - len(blob)
    if leading < 0:
        raise ValueError("invalid synthetic length")
    def fetch(start, n):
        if start + n <= leading:
            return b"\0" * n
        if start < leading:
            return b"\0" * (leading - start) + blob[:n - (leading - start)]
        return blob[start - leading:start - leading + n]
    return LimitedRangeIO(total, fetch, budget=cap)


def check(data, apk_size, obb_size, virtual_length=None):
    return scan_signed_checkpoint(seekable(data, virtual_length=virtual_length),
                                  expected_apk_bytes=apk_size,
                                  expected_obb_bytes=obb_size)


class NestedRealSignedArtifactTests(unittest.TestCase):
    def test_valid_synthetic_nested_signed_apk_obb_core_and_unity_members(self):
        data, a, o = outer()
        result = check(data, a, o)
        self.assertTrue(result["actual_signed_checkpoint_nested_apk_zip_central_inspected"])
        self.assertTrue(result["actual_signed_checkpoint_nested_obb_zip_central_inspected"])
        self.assertTrue(result["apk"]["android_manifest_binary_xml_magic"])
        self.assertTrue(result["apk"]["dex_magic"])
        self.assertTrue(result["apk"]["arm64_elf64_magic_both_libraries"])
        self.assertEqual(result["apk"]["arm64_so_member_count"], 2)
        self.assertGreater(result["obb"]["unity_assets_extension_count"], 0)
        self.assertFalse(result["actual_inner_apk_obb_sha256_verified"])
        self.assertFalse(result["actual_apk_cryptographic_signature_verified"])
        self.assertFalse(result["actual_device_tested"])

    def test_synthetic_virtual_three_gigabyte_outer_without_bulk_bytes(self):
        blob, a, o = outer()
        parent = seekable(blob, virtual_length=2_974_110_506)
        result = scan_signed_checkpoint(parent, expected_apk_bytes=a, expected_obb_bytes=o)
        self.assertLess(result["remote_ranged_bytes"], MAX_TOTAL_TRANSFER)
        self.assertEqual(parent.length, 2_974_110_506)

    def test_outer_deflated_blob_rejected_no_decompression_fallback(self):
        blob, a, o = outer(compress=zipfile.ZIP_DEFLATED)
        with self.assertRaisesRegex(ProbeError, "not_stored"):
            check(blob, a, o)

    def test_original_signed_inner_sizes_pinned_fail_closed(self):
        blob, a, o = outer()
        with self.assertRaisesRegex(ProbeError, "manifest_size_drift"):
            check(blob, a + 1, o)
        with self.assertRaisesRegex(ProbeError, "manifest_size_drift"):
            check(blob, a, o + 1)

    def test_apk_without_arm64_unity_lib_refused(self):
        bad = packed([
            ("AndroidManifest.xml", b"\x03\x00\x08\x00"),
            ("classes.dex", b"dex\n035\0"),
            ("lib/arm64-v8a/libil2cpp.so", fake_elf()),
        ])
        blob, a, o = outer(apk=bad)
        with self.assertRaisesRegex(ProbeError, "arm64_core_missing"):
            check(blob, a, o)

    def test_apk_with_invalid_arm64_binary_magic_refused(self):
        bad = packed([
            ("AndroidManifest.xml", b"\x03\x00\x08\x00"),
            ("classes.dex", b"dex\n035\0"),
            ("lib/arm64-v8a/libil2cpp.so", b"not-an-ELF"),
            ("lib/arm64-v8a/libunity.so", fake_elf()),
        ])
        blob, a, o = outer(apk=bad)
        with self.assertRaisesRegex(ProbeError, "core_binary_magic_missing"):
            check(blob, a, o)

    def test_nonbinary_androidmanifest_refused(self):
        fake = packed([
            ("AndroidManifest.xml", b"<manifest/>"),
            ("classes.dex", b"dex\n035\0"),
            ("lib/arm64-v8a/libil2cpp.so", fake_elf()),
            ("lib/arm64-v8a/libunity.so", fake_elf()),
        ])
        blob, a, o = outer(apk=fake)
        with self.assertRaisesRegex(ProbeError, "core_binary_magic_missing"):
            check(blob, a, o)

    def test_obb_without_unity_asset_paths_refused(self):
        blob, a, o = outer(obb=packed([("only-meta.txt", b"fixture")]))
        with self.assertRaisesRegex(ProbeError, "no_asset_payload"):
            check(blob, a, o)

    def test_nested_zip_traversal_and_symlinks_refused(self):
        blob, a, o = outer(obb=valid_obb(extra=[("assets/../escape", b"data")]))
        with self.assertRaisesRegex(ProbeError, "unsafe_zip_member"):
            check(blob, a, o)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("assets/bin/Data/resources.assets", b"real")
            link = zipfile.ZipInfo("assets/bin/Data/hidden")
            link.create_system = 3
            link.external_attr = 0o120777 << 16
            z.writestr(link, "outside")
        blob, a, o = outer(obb=buffer.getvalue())
        with self.assertRaisesRegex(ProbeError, "nested_symlink_member"):
            check(blob, a, o)

    def test_nested_duplicates_refused(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            payload = valid_obb(extra=[("assets/bin/Data/resources.assets", b"duplicate")])
        blob, a, o = outer(obb=payload)
        with self.assertRaisesRegex(ProbeError, "nested_duplicate_name"):
            check(blob, a, o)

    def test_parent_range_budget_blocks_before_download(self):
        blob, a, o = outer()
        parent = seekable(blob, cap=60)
        with self.assertRaisesRegex(ProbeError, "budget_exhausted"):
            scan_signed_checkpoint(parent, expected_apk_bytes=a, expected_obb_bytes=o)

    def test_stored_offset_sanity_rejects_wrong_outer_method(self):
        blob, a, o = outer()
        parent = seekable(blob)
        with zipfile.ZipFile(parent) as archive:
            member = archive.getinfo("Raft-Android-Test.apk")
            self.assertEqual(member.compress_type, zipfile.ZIP_STORED)
            start = stored_member_offset(parent, archive, member)
            self.assertGreater(start, member.header_offset)
            start_data = MemberSliceIO(parent, start, member.file_size)
            with zipfile.ZipFile(start_data) as inner:
                self.assertIn("AndroidManifest.xml", inner.namelist())
            member.compress_type = zipfile.ZIP_DEFLATED
            with self.assertRaisesRegex(ProbeError, "not_stored"):
                stored_member_offset(parent, archive, member)


if __name__ == "__main__":
    unittest.main()
