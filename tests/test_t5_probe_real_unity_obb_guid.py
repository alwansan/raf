"""Bounded signed APK/OBB Unity GUID marker source-free controls.

The original proprietary marker payload never enters the public repository.
"""
import io
import struct
import unittest
import warnings
import zipfile

from scripts.t5_probe_github_artifact_zip_range import LimitedRangeIO, ProbeError
from scripts.t5_probe_real_unity_obb_guid import (
    MARKER, compare_unity_obb_guid, inspect_checkpoint,
)


def build_zip(*rows):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w", allowZip64=True) as archive:
        for name, value in rows:
            archive.writestr(name, value)
    return data.getvalue()


def payload(marker=None):
    contents = [("assets/bin/Data/sample", b"synthetic-unity-resource")]
    if marker is not None:
        contents.append((MARKER, marker))
    return build_zip(*contents)


def compare(a, b):
    with zipfile.ZipFile(io.BytesIO(a)) as apk:
        with zipfile.ZipFile(io.BytesIO(b)) as obb:
            return compare_unity_obb_guid(apk, obb)


def simulated_signed_checkpoint(apk, obb):
    raw = build_zip(
        ("Raft-Android-Test.apk", apk),
        ("main.89.com.alwansan.raft.androidtest.obb", obb),
    )
    def fetch(offset, count):
        return raw[offset:offset + count]
    return LimitedRangeIO(len(raw), fetch, budget=1024 * 1024)


class RealUnityObbGuidSourceFreeTests(unittest.TestCase):
    def test_both_realistic_guid_markers_match_bytewise(self):
        data = compare(payload(b"\x00\x01-GUID-UNIQUE"), payload(b"\x00\x01-GUID-UNIQUE"))
        self.assertEqual(data["unity_obb_guid_marker_identity"], "both_present_byte_identical")
        self.assertTrue(data["unity_internal_engine_guid_verified"])
        self.assertEqual(data["marker_exact_bytes_compared"], 14)
        self.assertFalse(data["unity_obb_guid_embedded_value_revealed"])
        self.assertFalse(data["actual_installed_phone_obb_mount_verified"])

    def test_both_absent_markers_are_not_an_identity_match(self):
        data = compare(payload(), payload())
        self.assertEqual(data["unity_obb_guid_marker_identity"], "both_absent_identity_unavailable")
        self.assertFalse(data["unity_internal_engine_guid_verified"])
        self.assertFalse(data["apk_unity_obb_guid_marker_present"])
        self.assertFalse(data["obb_unity_obb_guid_marker_present"])
        self.assertEqual(data["marker_exact_bytes_compared"], 0)

    def test_one_sided_markers_rejected_not_silent_unavailable(self):
        for apk, obb in ((payload(b"GUID"), payload()),
                         (payload(), payload(b"GUID"))):
            with self.subTest(apk_has_marker=MARKER.encode() in apk):
                with self.assertRaisesRegex(ProbeError, "one_sided"):
                    compare(apk, obb)

    def test_actual_different_equal_size_marker_payloads_rejected(self):
        with self.assertRaisesRegex(ProbeError, "marker_mismatch"):
            compare(payload(b"fake-guid-1"), payload(b"fake-guid-2"))

    def test_zero_length_and_large_marker_rejected(self):
        for marker in (b"", b"A" * 257):
            with self.subTest(length=len(marker)):
                with self.assertRaisesRegex(ProbeError, "invalid_size_type"):
                    compare(payload(marker), payload(marker))

    def test_marker_path_lookalikes_do_not_claim_proven_guid(self):
        for fake in ("assets/unity_obb_guid.txt",
                     "Assets/unity_obb_guid",
                     "assets/bin/Data/unity_obb_guid"):
            with self.subTest(fake=fake):
                apk = build_zip((fake, b"synthetic-identity"))
                obb = build_zip((fake, b"synthetic-identity"))
                value = compare(apk, obb)
                self.assertEqual(value["unity_obb_guid_marker_identity"],
                                 "both_absent_identity_unavailable")

    def test_duplicate_unity_guid_entries_rejected_even_if_same_payload(self):
        def double():
            data = io.BytesIO()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                with zipfile.ZipFile(data, "w") as archive:
                    archive.writestr(MARKER, b"good")
                    archive.writestr(MARKER, b"good")
            return data.getvalue()
        with self.assertRaisesRegex(ProbeError, "marker_duplicate"):
            compare(double(), payload(b"good"))

    def test_corrupted_local_header_name_rejected_before_payload(self):
        data = bytearray(payload(b"test"))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            member = archive.getinfo(MARKER)
        at = member.header_offset + 30 + len(MARKER) - 1
        data[at] ^= 1
        with self.assertRaisesRegex(ValueError, "local member header name"):
            compare(bytes(data), payload(b"test"))

    def test_marker_crc_corruption_fails_closed(self):
        data = bytearray(payload(b"stored-content"))
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            marker = archive.getinfo(MARKER)
        crc_at = marker.header_offset + 14
        data[crc_at] ^= 1
        with self.assertRaisesRegex(ValueError, "local member header CRC"):
            compare(bytes(data), payload(b"stored-content"))

    def test_full_signed_checkpoint_simulated_package_and_markers(self):
        a = payload(b"guid-same")
        o = payload(b"guid-same")
        stream = simulated_signed_checkpoint(a, o)
        result = inspect_checkpoint(stream, expected_apk_bytes=len(a), expected_obb_bytes=len(o))
        self.assertTrue(result["unity_internal_engine_guid_verified"])
        self.assertEqual(result["real_nested_apk_zip_member_count"], 2)
        self.assertEqual(result["real_nested_obb_zip_member_count"], 2)
        self.assertLess(result["real_original_HTTP206_bytes"], 1024 * 1024)
        self.assertFalse(result["game_ready_or_GPU_pixels_verified"])

    def test_signed_checkpoint_wrong_outer_apk_obb_sizes_fail_closed(self):
        a, o = payload(), payload()
        stream = simulated_signed_checkpoint(a, o)
        with self.assertRaisesRegex(ProbeError, "file_size_drift"):
            inspect_checkpoint(stream, expected_apk_bytes=len(a) + 1,
                               expected_obb_bytes=len(o))

    def test_signed_checkpoint_deflated_outer_member_not_accepted(self):
        a, o = payload(), payload()
        data = io.BytesIO()
        with zipfile.ZipFile(data, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr("Raft-Android-Test.apk", a)
            z.writestr("main.89.com.alwansan.raft.androidtest.obb", o)
        raw = data.getvalue()
        stream = LimitedRangeIO(len(raw),
                                lambda off, n: raw[off:off + n], budget=1024 * 1024)
        with self.assertRaisesRegex(ProbeError, "not_stored"):
            inspect_checkpoint(stream, expected_apk_bytes=len(a), expected_obb_bytes=len(o))

    def test_range_budget_exhaustion_refuses_archive(self):
        a, o = payload(), payload()
        src = simulated_signed_checkpoint(a, o)
        src.remaining = 20
        with self.assertRaisesRegex(ProbeError, "budget_exhausted"):
            inspect_checkpoint(src, expected_apk_bytes=len(a), expected_obb_bytes=len(o))


if __name__ == "__main__":
    unittest.main()
