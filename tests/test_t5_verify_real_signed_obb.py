"""Original OBB 2.3GB SHA+outer CRC contract, using only tiny synthetic bytes."""
import hashlib
from pathlib import Path
import unittest
import zlib

from scripts.t5_probe_github_artifact_zip_range import ProbeError
from scripts.t5_verify_real_signed_obb import (
    OBB_BYTES, MAX_OBB_TRANSFER, RANGE_CHUNK, hash_original_obb,
)


class OriginalMainObbStreamTests(unittest.TestCase):
    @staticmethod
    def original_fixture(payload=b"synthetic-obb-bytes"):
        return hashlib.sha256(payload).hexdigest(), zlib.crc32(payload) & 0xFFFFFFFF

    def test_full_source_claim_sha_and_outer_crc_both_match(self):
        data = b"source-verified-test-zip" * 4
        sha, crc = self.original_fixture(data)
        requests = []
        start = 31337

        def fetch(offset, size):
            requests.append((offset, size))
            return data[offset - start:offset - start + size]

        result = hash_original_obb(
            fetch, start, len(data), sha, crc,
            authentic_length=len(data), max_transfer=len(data),
            chunk_bytes=7)
        self.assertEqual(result["real_obb_bytes_fully_hashed"], len(data))
        self.assertTrue(result["real_obb_full_sha256_matches_original_delivery_manifest"])
        self.assertTrue(result["real_obb_stream_crc32_matches_signed_checkpoint_central_directory"])
        self.assertEqual(result["real_obb_sha256_prefix_12"], sha[:12])
        self.assertEqual(result["real_obb_range_requests"], len(requests))
        self.assertEqual(requests[0][0], start)
        self.assertEqual(requests[-1][0] + requests[-1][1], start + len(data))

    def test_wrong_manifest_sha_rejected_after_complete_crc_match(self):
        source = b"private-original-content-not-in-this-fixture"
        _, crc = self.original_fixture(source)
        with self.assertRaisesRegex(ProbeError, "sha256_obb_mismatch"):
            hash_original_obb(lambda off, count: source[off:off + count],
                              0, len(source), "0" * 64, crc,
                              authentic_length=len(source), max_transfer=1000)

    def test_wrong_outer_zip_crc_rejected_after_complete_sha_match(self):
        source = b"sample"
        sha, crc = self.original_fixture(source)
        with self.assertRaisesRegex(ProbeError, "outer_zip_obb_crc32_mismatch"):
            hash_original_obb(lambda off, count: source[off:off + count],
                              0, len(source), sha, crc ^ 1,
                              authentic_length=len(source), max_transfer=1000)

    def test_corrupted_payload_detected_even_if_same_size(self):
        payload = b"original"
        sha, crc = self.original_fixture(payload)
        altered = b"criginal"
        with self.assertRaisesRegex(ProbeError, "sha256_obb_mismatch"):
            hash_original_obb(lambda off, count: altered[off:off + count],
                              0, len(payload), sha, crc,
                              authentic_length=len(payload), max_transfer=1000)

    def test_short_remote_response_rejected_early(self):
        raw = b"very-short"
        sha, crc = self.original_fixture(raw)
        with self.assertRaisesRegex(ProbeError, "remote_range_incomplete"):
            hash_original_obb(lambda off, count: b"x" * max(0, count - 1),
                              0, len(raw), sha, crc,
                              authentic_length=len(raw), max_transfer=1000,
                              chunk_bytes=4)

    def test_remote_exception_redacted(self):
        raw = b"abcdefgh"
        sha, crc = self.original_fixture(raw)
        def bad_fetch(_start, _amount):
            raise RuntimeError("Private signed URL should not appear in report")
        with self.assertRaisesRegex(ProbeError, "remote_range_incomplete"):
            hash_original_obb(bad_fetch, 0, len(raw), sha, crc,
                              authentic_length=len(raw), max_transfer=100)

    def test_hard_cap_disallows_obb_larger_than_limit_without_network(self):
        called = []
        def fetch(a, n):
            called.append((a, n))
            return b""
        for budget in (100, OBB_BYTES - 1):
            with self.subTest(budget=budget):
                with self.assertRaisesRegex(ProbeError, "original_obb_stream_cap"):
                    hash_original_obb(fetch, 0, OBB_BYTES, "a" * 64, 0,
                                      max_transfer=budget)
        self.assertEqual(called, [])
        self.assertLess(OBB_BYTES, MAX_OBB_TRANSFER)
        self.assertLessEqual(RANGE_CHUNK, 4 * 1024 * 1024)

    def test_wrong_immutable_original_length_disallows_network(self):
        called = []
        def fetch(a, n):
            called.append((a, n))
            return b""
        for length in (0, OBB_BYTES - 1, OBB_BYTES + 1, True):
            with self.subTest(length=length):
                with self.assertRaisesRegex(ProbeError, "original_obb_stream_cap"):
                    hash_original_obb(fetch, 0, length, "a" * 64, 0)
        self.assertEqual(called, [])

    def test_malformed_digest_crc_or_chunk_range_rejected(self):
        raw = b"something"
        sha, crc = self.original_fixture(raw)
        combos = [
            {"manifest_sha": "foo"},
            {"manifest_sha": sha.upper()},
            {"manifest_sha": True},
            {"expected_outer_crc": -1},
            {"expected_outer_crc": 0x100000000},
            {"expected_outer_crc": True},
            {"chunk_bytes": 0},
            {"chunk_bytes": RANGE_CHUNK + 1},
            {"start": -1},
        ]
        for kwargs in combos:
            with self.subTest(kwargs=kwargs):
                args = dict(start=0, length=len(raw),
                            manifest_sha=sha, expected_outer_crc=crc,
                            authentic_length=len(raw), max_transfer=100)
                args.update(kwargs)
                with self.assertRaisesRegex(ProbeError, "original_obb_stream_cap"):
                    hash_original_obb(lambda off, n: raw[off:off + n], **args)


if __name__ == "__main__":
    unittest.main()
