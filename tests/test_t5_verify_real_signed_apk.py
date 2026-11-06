"""Synthetic T5 signed APK full digest/badging/apksigner contract; no real APK."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts.t5_probe_github_artifact_zip_range import ProbeError
from scripts.t5_verify_real_signed_apk import (
    CHUNK_BYTES, PACKAGE, MAX_PAYLOAD_BYTES,
    parse_aapt_badging, parse_apksigner, stream_bounded_apk, android_tools,
)


def example_signer(*, v2=True):
    return ("Verifies\n"
            "Verified using v1 scheme (JAR signing): true\n"
            "Verified using v2 scheme (APK Signature Scheme v2): " +
            str(v2).lower() + "\n"
            "Verified using v3 scheme (APK Signature Scheme v3): false\n"
            "Verified using v4 scheme (APK Signature Scheme v4): false\n"
            "Number of signers: 1\n"
            "Signer #1 certificate SHA-256 digest: " + "a" * 64 + "\n")


class SignedApkAuthenticityTests(unittest.TestCase):
    def test_actual_bounded_full_byte_digest_matches_but_never_means_certificate(self):
        data = b"t5-fixture-byte-content"
        digest = hashlib.sha256(data).hexdigest()
        calls = []
        def fetch(offset, count):
            calls.append((offset, count))
            return data[offset - 300:offset - 300 + count]
        with tempfile.TemporaryDirectory() as d:
            file = Path(d) / "source.apk"
            result = stream_bounded_apk(fetch, 300, len(data), file, digest,
                                        max_bytes=100, chunk_bytes=4,
                                        expected_length=len(data))
            self.assertEqual(file.read_bytes(), data)
        self.assertEqual(result["fully_streamed_signed_apk_bytes"], len(data))
        self.assertTrue(result["original_delivery_manifest_apk_sha256_matched"])
        self.assertEqual(result["full_original_signed_apk_digest_prefix_12"], digest[:12])
        self.assertTrue(all(n <= 4 for _, n in calls))

    def test_manifest_digest_mismatch_refused_even_for_unchanged_size(self):
        raw = b"synthetic"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ProbeError, "digest_mismatch"):
                stream_bounded_apk(lambda pos, n: raw[pos:pos + n], 0,
                                   len(raw), Path(d) / "s.apk", "f" * 64,
                                   max_bytes=100, chunk_bytes=3,
                                   expected_length=len(raw))

    def test_short_or_incorrect_remote_response_is_refused(self):
        data = b"abcdefgh"
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ProbeError, "remote_range_incomplete"):
                stream_bounded_apk(lambda _, n: b"0" * (n - 1), 0, 8,
                                   Path(d) / "x.apk", "e" * 64,
                                   max_bytes=100, chunk_bytes=4,
                                   expected_length=8)

    def test_full_673mb_is_pinned_and_oversize_rejected_before_file_creation(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "x.apk"
            for kwargs in ({"expected_length": 673}, {"max_bytes": 100}):
                with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ProbeError, "size_cap"):
                    stream_bounded_apk(lambda _offset, _size: b"a", 0, 672853870,
                                       p, "0" * 64, **kwargs)
                self.assertFalse(p.exists())
        self.assertLess(672853870, MAX_PAYLOAD_BYTES)
        self.assertLess(CHUNK_BYTES, MAX_PAYLOAD_BYTES)

    def test_valid_signer_schemes_and_cert_are_categorical_only(self):
        result = parse_apksigner(example_signer())
        self.assertTrue(result["apksigner_crypto_verified"])
        self.assertTrue(result["apksigner_signature_schemes_verified"]["v2"])
        self.assertFalse(result["apksigner_signature_schemes_verified"]["v3"])
        self.assertEqual(result["apksigner_signer_count"], 1)
        self.assertEqual(result["apksigner_certificate_sha256_prefix_12"], "a" * 12)

    def test_signer_fails_without_real_verifies_marker_or_cert(self):
        for output in ("", "Verified using v2 scheme (APK Signature Scheme v2): true\n",
                       "Verifies\nVerified using v2 scheme (APK Signature Scheme v2): true\n"):
            with self.subTest(value=output), self.assertRaises(ProbeError):
                parse_apksigner(output)

    def test_false_scheme_v1_v2_v3_with_cert_is_not_accepted(self):
        x = example_signer(v2=False).replace(
            "Verified using v1 scheme (JAR signing): true",
            "Verified using v1 scheme (JAR signing): false")
        with self.assertRaisesRegex(ProbeError, "output_incomplete"):
            parse_apksigner(x)

    def test_binary_manifest_package_and_version_are_enforced(self):
        result = parse_aapt_badging(
            "package: name='" + PACKAGE + "' versionCode='89' versionName='1'\n", "89")
        self.assertTrue(result["binary_manifest_identity_matches_original_delivery"])
        self.assertEqual(result["version_code_from_signed_binary_AndroidManifest"], "89")

    def test_lookalike_package_or_version_or_duplicate_badging_refused(self):
        for value in (
            "package: name='com.other.raft.androidtest' versionCode='89' versionName='1'\n",
            "package: name='" + PACKAGE + "' versionCode='88' versionName='1'\n",
            "package: name='" + PACKAGE + "' versionCode='89' versionName='1'\n" * 2,
            "not a real Android manifest",
        ):
            with self.subTest(value=value[:70]), self.assertRaises(ProbeError):
                parse_aapt_badging(value, "89")

    def test_build_tools_fail_closed_without_sdk_and_no_install(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ProbeError, "build_tools_unavailable"):
                android_tools(Path(d))


if __name__ == "__main__":
    unittest.main()
