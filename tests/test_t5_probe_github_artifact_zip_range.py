"""Source-free bounded-range ZIP inventory cases; never fetch real original assets."""
import io
import json
import unittest
import warnings
import zipfile
from unittest import mock

from scripts.t5_probe_github_artifact_zip_range import (
    ARTIFACTS, LimitedRangeIO, ProbeError, _kind, _safe_member,
    _sanitized_manifest, inspect_envelope, probe_one,
)

PACKAGE = "com.alwansan.raft.androidtest"


def manifest():
    def entry(name, num):
        return {
            "name": name, "bytes": num, "sha256": "a" * 64,
            "parts": [{"name": name, "bytes": num, "sha256": "a" * 64}],
        }
    return {
        "schema": 1, "package": PACKAGE, "version_code": "86",
        "files": [
            entry("Raft-Android-Test.apk", 11),
            entry("main.86." + PACKAGE + ".obb", 50),
            entry("Raft-Android-Test.xapk", 61),
        ],
    }


def zipbytes(rows=None):
    if rows is None:
        rows = [("delivery.json", json.dumps(manifest()).encode()),
                ("Raft-Android-Test.apk.part001", b"fixture-apk"),
                ("main.86." + PACKAGE + ".obb.part001", b"fixture-obb"),
                ("misc/ignore-me.json", b"only a synthetic fixture")]
    fp = io.BytesIO()
    with zipfile.ZipFile(fp, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for name, data in rows:
            z.writestr(name, data)
    return fp.getvalue()


def stream(blob, *, virtual_size=None, budget=4 * 1024 * 1024):
    # Large virtual sparse remote ZIP; no huge memory/disk allocation.
    real_size = len(blob)
    full_size = real_size if virtual_size is None else virtual_size
    front = full_size - real_size
    if front < 0:
        raise ValueError("impossible virtual length")

    def fetch(offset, length):
        if offset + length <= front:
            return b"\0" * length
        if offset < front:
            lead = front - offset
            return b"\0" * lead + blob[:length - lead]
        return blob[offset - front:offset - front + length]

    return LimitedRangeIO(full_size, fetch, budget=budget)


class ArtifactRangeProbeTests(unittest.TestCase):
    def test_valid_small_signed_delivery_envelope_metadata_not_inner_digests(self):
        io_stream = stream(zipbytes())
        result = inspect_envelope(io_stream)
        self.assertEqual(result["file_type_counts"]["apk"], 1)
        self.assertEqual(result["file_type_counts"]["obb"], 1)
        self.assertEqual(result["delivery_manifest"]["version_code"], "86")
        self.assertEqual(result["delivery_manifest"]["logical_file_bytes"]["obb"], 50)
        self.assertEqual(result["delivery_manifest"]["logical_transport_part_counts"]["xapk"], 1)
        self.assertFalse(result["original_inner_file_hashes_verified"])
        self.assertFalse(result["apk_signature_verified"])
        self.assertFalse(result["android_device_tested"])
        self.assertLess(io_stream.transferred, len(zipbytes()) * 6)

    def test_virtual_six_gigabyte_zip_uses_sparse_tail_ranges_not_bulk_download(self):
        z = zipbytes()
        io_stream = stream(z, virtual_size=5_948_243_524)
        result = inspect_envelope(io_stream)
        self.assertEqual(result["member_count"], 4)
        self.assertLess(io_stream.transferred, 4 * 1024 * 1024)
        self.assertEqual(io_stream.length, 5_948_243_524)

    def test_unsigned_checkpoint_archive_without_manifest_remains_proof_bounded(self):
        report = inspect_envelope(stream(zipbytes([
            ("Raft-Android-Test.apk", b"fixture"),
            ("main.86." + PACKAGE + ".obb.part001", b"data"),
        ])))
        self.assertIsNone(report["delivery_manifest"])
        self.assertEqual(report["file_type_counts"]["obb"], 1)
        self.assertFalse(report["original_inner_file_hashes_verified"])

    def test_unsafe_member_and_duplicates_rejected_without_contents(self):
        for name in ("../escape", "/assets/file", "assets//file",
                     "assets/./file", "assets/../file",
                     "C:/Windows/file", "assets\\file"):
            with self.subTest(name=name), self.assertRaises(ProbeError):
                inspect_envelope(stream(zipbytes([(name, b"foo")])))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with self.assertRaises(ProbeError):
                inspect_envelope(stream(zipbytes([("a.txt", b"1"),
                                                  ("a.txt", b"2")])))

    def test_archive_symlink_and_encrypted_members_refused(self):
        fp = io.BytesIO()
        with zipfile.ZipFile(fp, "w") as z:
            link = zipfile.ZipInfo("safe/alias")
            link.create_system = 3
            link.external_attr = (0o120777 << 16)
            z.writestr(link, "safe/data")
        with self.assertRaises(ProbeError):
            inspect_envelope(stream(fp.getvalue()))
        # Synthetic flag mutation in both central and local header.
        raw = bytearray(zipbytes([("data.bin", b"ok")]))
        for sig, at in ((b"PK\x03\x04", 6), (b"PK\x01\x02", 8)):
            i = raw.find(sig)
            self.assertGreaterEqual(i, 0)
            raw[i + at] |= 1
        with self.assertRaises(ProbeError):
            inspect_envelope(stream(bytes(raw)))

    def test_zip_bomb_manifest_not_extracted(self):
        big = zipbytes([("delivery.json", b"x" * 100001)])
        with self.assertRaisesRegex(ProbeError, "manifest_member_exceeds_limit"):
            inspect_envelope(stream(big))

    def test_duplicate_json_key_and_false_manifest_file_bytes_refused(self):
        raw = b'{"schema":1,"schema":1}'
        with self.assertRaises(ProbeError):
            inspect_envelope(stream(zipbytes([("delivery.json", raw)])))
        invalid = manifest()
        invalid["files"][0]["bytes"] = 12
        with self.assertRaisesRegex(ProbeError, "manifest_bytes_inconsistent"):
            inspect_envelope(stream(zipbytes([("delivery.json", json.dumps(invalid).encode())])))

    def test_part_classification_and_no_private_names_repeated(self):
        self.assertEqual(_kind("main.86." + PACKAGE + ".obb.part001"), "obb")
        self.assertEqual(_kind("Raft-Android-Test.apk.part023"), "apk")
        self.assertEqual(_kind("Raft-Android-Test.xapk.part100"), "xapk")
        self.assertEqual(_kind("delivery.json"), "manifest")
        self.assertEqual(_kind("anything.bin"), "other")
        with self.assertRaises(ProbeError):
            _safe_member("private\\resource")

    def test_short_read_and_remote_budget_are_fail_closed(self):
        blob = zipbytes()
        short = LimitedRangeIO(len(blob), lambda _s, n: b"x" * (n - 1))
        with self.assertRaisesRegex(ProbeError, "remote_range_incomplete"):
            inspect_envelope(short)
        io_stream = stream(blob, budget=70)
        with self.assertRaisesRegex(ProbeError, "budget_exhausted"):
            inspect_envelope(io_stream)

    def test_metadata_gate_authenticates_artifact_before_remote_bytes(self):
        artifact = ARTIFACTS[0]
        expected = {
            "id": artifact[0], "name": artifact[1], "size_in_bytes": artifact[2],
            "digest": artifact[3], "expired": False,
            "workflow_run": {
                "id": 42058825739,
                "head_sha": "e9c358eda01785b65e4eb14f18723da426635628",
            },
        }
        with mock.patch("scripts.t5_probe_github_artifact_zip_range._github_request",
                        return_value={**expected, "digest": "sha256:" + "0" * 64}):
            with self.assertRaisesRegex(ProbeError, "metadata_changed"):
                probe_one(artifact, "synthetic-token")
        with mock.patch("scripts.t5_probe_github_artifact_zip_range._github_request",
                        return_value={**expected, "workflow_run": {"id": 1}}):
            with self.assertRaisesRegex(ProbeError, "source_run_link_mismatch"):
                probe_one(artifact, "synthetic-token")

    def test_original_manifest_unverified_even_if_per_file_sha_shape_valid(self):
        data = _sanitized_manifest(manifest())
        self.assertTrue(data["inner_file_digests_not_read_or_verified"])
        self.assertEqual(data["logical_transport_part_counts"], {"apk": 1, "obb": 1, "xapk": 1})
        data = manifest()
        data["files"][1]["parts"][0]["sha256"] = "not-a-sha"
        with self.assertRaises(ProbeError):
            _sanitized_manifest(data)


if __name__ == "__main__":
    unittest.main()
