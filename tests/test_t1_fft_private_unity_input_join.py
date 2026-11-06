"""Synthetic, sourcefree tests of physical FFT input + Unity GPU identity join."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.t1_fft_invocation_pair_gate import SCHEMA
from scripts.t1_fft_private_input_evidence import BYTES, DISPATCH, input_hash, sha
from scripts.t1_fft_private_unity_input_join import join, main, IDENTITY_NAME
from scripts.t1_fft_trace_compare import CAPACITY, INVOCATION_RECORD


def trace():
    rows = [
        INVOCATION_RECORD.pack(i, i, 0, 0, 0, i + 1, 1, 0,
                               0x3f800000, 0x00000001, 0x40000000, 0x00000000)
        for i in range(3)
    ]
    return (struct.pack("<I", len(rows)) + b"".join(rows) +
            bytes((CAPACITY-len(rows)) * INVOCATION_RECORD.size))


class UnityActualInputJoinTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.vulkan = self.root / "Vulkan"
        self.unity = self.root / "Unity"
        self.vulkan.mkdir()
        self.unity.mkdir()
        self.v_src = self.vulkan / "source.rgba32f"
        self.v_but = self.vulkan / "butterfly.rgba32f"
        self.u_src = self.unity / "source.rgba32f"
        self.u_but = self.unity / "butterfly.rgba32f"
        self.identity = self.unity / IDENTITY_NAME
        self.src_bytes = b"\x00" * BYTES
        self.butterfly_bytes = b"\x00\x00\x80\x3f" * (BYTES // 4)
        for file, data in ((self.v_src, self.src_bytes), (self.u_src, self.src_bytes),
                           (self.v_but, self.butterfly_bytes),
                           (self.u_but, self.butterfly_bytes)):
            file.write_bytes(data)
        self.identity.write_bytes(b"OpenGLCore\n0\n0\n")
        self.original = self.root / "original.trace"
        self.candidate = self.root / "unity.trace"
        self.original.write_bytes(trace())
        self.candidate.write_bytes(trace())
        self.manifest = self.root / "private-manifest.json"
        signature = input_hash(self.src_bytes, self.butterfly_bytes)
        dispatch_digest = sha(json.dumps(DISPATCH, sort_keys=True).encode("ascii"))
        self.metadata = {
            "schema": SCHEMA,
            "expected_records_by_site": [1, 1, 1],
            "reference": {
                "role": "original_spirv", "trace_sha256": sha(trace()),
                "shader_sha256": "a" * 64, "input_sha256": signature,
                "dispatch_sha256": dispatch_digest,
            },
            "candidate": {
                "role": "unity_compute_spirv", "trace_sha256": sha(trace()),
                "shader_sha256": "b" * 64, "input_sha256": signature,
                "dispatch_sha256": dispatch_digest,
            },
        }
        self.write_meta()

    def write_meta(self):
        self.manifest.write_text(json.dumps(self.metadata), encoding="utf-8")

    def result(self):
        return join(self.manifest, self.original, self.candidate,
                    self.vulkan, self.unity)

    def test_real_bytes_bound_to_both_sha_and_gpu_copyinput_report(self):
        row = self.result()
        self.assertTrue(row["actual_both_capture_input_blob_pairs_byte_identical"])
        self.assertTrue(row["actual_input_bytes_match_paired_manifest_sha"])
        self.assertTrue(row["exact_pinned_1024x32_seed19_dispatch_declaration_match"])
        self.assertTrue(row["reported_unity_openglcore_gpu_copyinput_zero_mismatch"])
        self.assertFalse(row["unity_compute_shader_or_backend_independently_proven"])
        self.assertFalse(row["android_adreno_water_proven"])
        self.assertEqual(sum(x["paired_invocations"] for x in row["diagnostics"]), 3)

    def test_physical_source_mismatch_even_if_declared_shas_equal(self):
        self.u_src.write_bytes(b"\x01" + self.src_bytes[1:])
        with self.assertRaises(ValueError):
            self.result()

    def test_physical_butterfly_mismatch_even_if_declared_shas_equal(self):
        self.u_but.write_bytes(b"\x01" + self.butterfly_bytes[1:])
        with self.assertRaises(ValueError):
            self.result()

    def test_source_and_butterfly_distinct_roles_required(self):
        self.v_but.write_bytes(self.src_bytes)
        self.u_but.write_bytes(self.src_bytes)
        self.metadata["reference"]["input_sha256"] = input_hash(self.src_bytes, self.src_bytes)
        self.metadata["candidate"]["input_sha256"] = self.metadata["reference"]["input_sha256"]
        self.write_meta()
        with self.assertRaises(ValueError):
            self.result()

    def test_declared_matching_but_false_actual_digest_rejected(self):
        self.metadata["reference"]["input_sha256"] = "c" * 64
        self.metadata["candidate"]["input_sha256"] = "c" * 64
        self.write_meta()
        with self.assertRaises(ValueError):
            self.result()

    def test_false_dispatch_sha_with_equal_declarations_rejected(self):
        self.metadata["reference"]["dispatch_sha256"] = "c" * 64
        self.metadata["candidate"]["dispatch_sha256"] = "c" * 64
        self.write_meta()
        with self.assertRaises(ValueError):
            self.result()

    def test_truncated_and_extra_rgba_bytes_fail_closed(self):
        for delta in (-1, 1):
            with self.subTest(delta=delta):
                self.u_src.write_bytes(self.src_bytes[:BYTES + delta] if delta < 0
                                       else self.src_bytes + b"\x00")
                with self.assertRaises(ValueError):
                    self.result()
        self.u_src.write_bytes(self.src_bytes)

    def test_wrong_backend_gpu_mismatch_and_extra_text_rejected(self):
        for text in (b"Vulkan\n0\n0\n", b"OpenGLCore\n1\n0\n",
                     b"OpenGLCore\n0\n1\n", b"OpenGLCore\n0\n0\nSECRET",
                     b"\xef\xbb\xbfOpenGLCore\n0\n0\n",
                     b"OpenGLCore\n0\n0\n\n", b"OpenGLCore\n0\n0\n" + b"a" * 100,
                     b""):
            with self.subTest(report=text[:18]), self.assertRaises(ValueError):
                self.identity.write_bytes(text)
                self.result()

    def test_valid_crlf_gpu_report(self):
        self.identity.write_bytes(b"OpenGLCore\r\n0\r\n0\r\n")
        self.assertTrue(self.result()["reported_unity_openglcore_gpu_copyinput_zero_mismatch"])

    def test_missing_gpu_report_rejected(self):
        self.identity.unlink()
        with self.assertRaises(ValueError):
            self.result()

    def test_reject_cross_backend_hardlinked_image(self):
        self.u_src.unlink()
        self.u_src.hardlink_to(self.v_src)
        with self.assertRaises(ValueError):
            self.result()

    def test_reject_samefile_source_and_butterfly(self):
        self.u_but.unlink()
        self.u_but.hardlink_to(self.u_src)
        with self.assertRaises(ValueError):
            self.result()

    def test_reject_symlink_in_private_input_and_gpu_report(self):
        for original in (self.u_src, self.identity):
            with self.subTest(file=original.name):
                saved = original.read_bytes()
                original.unlink()
                original.symlink_to(self.v_src)
                with self.assertRaises(ValueError):
                    self.result()
                original.unlink()
                original.write_bytes(saved)

    def test_trace_sha_mismatch_rejected_by_existing_pair_gate(self):
        self.candidate.write_bytes(self.candidate.read_bytes()[:-1] + b"\x01")
        with self.assertRaises(ValueError):
            self.result()

    def test_reject_non_unity_role_even_with_real_images(self):
        self.metadata["candidate"]["role"] = "hlsl_roundtrip_spirv"
        self.write_meta()
        with self.assertRaises(ValueError):
            self.result()

    def test_reject_duplicate_metadata_key(self):
        payload = self.manifest.read_text()
        self.manifest.write_text(payload.replace('"schema":', '"schema":"bad","schema":', 1))
        with self.assertRaises(ValueError):
            self.result()

    def test_public_cli_redacts_hashes_data_and_paths(self):
        import sys
        with patch.object(sys, "argv", ["report", "--manifest", str(self.manifest),
                                        "--original", str(self.original),
                                        "--unity", str(self.candidate),
                                        "--vulkan-input-dir", str(self.vulkan),
                                        "--unity-input-dir", str(self.unity)]):
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertIsNone(main())
        report = out.getvalue()
        self.assertIn("RAFT_T1_ACTUAL_INPUT_JOIN ", report)
        for secret in (self.metadata["reference"]["input_sha256"], str(self.root),
                       "00000001", "3f800000", "OpenGLCore\n0\n0"):
            self.assertNotIn(secret, report)


if __name__ == "__main__":
    unittest.main()
