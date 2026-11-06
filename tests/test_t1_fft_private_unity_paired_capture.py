"""Independent adversarial tests for direct-original-vs-Unity FFT private trace join."""
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.t1_fft_private_input_evidence import (
    BYTES, DISPATCH, SCHEMA as EVIDENCE_SCHEMA, input_hash, sha,
)
from scripts.t1_fft_trace_compare import CAPACITY, INVOCATION_RECORD
from scripts.t1_fft_private_unity_paired_capture import (
    EXPECTED_SITE_COUNTS, make_manifest, save_and_join, main,
)


def generate_trace(*, swapped=False):
    rows = []
    for site, count in enumerate(EXPECTED_SITE_COUNTS):
        for i in range(count):
            coord = (i + 1, (i // 4) % 32, 0)
            if swapped and site == 1:
                coord = (0, coord[1], 0)
            rows.append(INVOCATION_RECORD.pack(
                site, i, 0, 0, 0, *coord,
                0x3f800000, 0x40000000, 0x40400000, 0x40800000))
    if sum(EXPECTED_SITE_COUNTS) != 384:
        raise AssertionError("Unexpected synthetic site census")
    return (struct.pack("<I", len(rows)) + b"".join(rows) +
            b"\x00" * ((CAPACITY - len(rows)) * INVOCATION_RECORD.size))


class PrivateOriginalUnityCaptureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.vulkan = self.root / "Vulkan"
        self.unity = self.root / "Unity"
        self.vulkan.mkdir()
        self.unity.mkdir()
        self.source = b"\0" * BYTES
        self.butterfly = b"\0\0\x80\x3f" * (BYTES // 4)
        for root in (self.vulkan, self.unity):
            (root / "source.rgba32f").write_bytes(self.source)
            (root / "butterfly.rgba32f").write_bytes(self.butterfly)
        (self.unity / "input_identity.rgba32f").write_bytes(b"OpenGLCore\n0\n0\n")
        self.reference = self.vulkan / "trace.bin"
        self.candidate = self.unity / "trace.bin"
        self.reference.write_bytes(generate_trace())
        self.candidate.write_bytes(generate_trace(swapped=True))
        self.shader = self.root / "T1TracePass0.compute"
        self.shader.write_bytes(
            b"#pragma kernel main\n[numthreads(64,1,1)] "
            b"void main(uint3 dispatch : SV_DispatchThreadID) { }\n")
        self.original_evidence = self.root / "direct-original.json"
        self.manifest = self.root / "meta.json"
        self.evidence = {
            "schema": EVIDENCE_SCHEMA,
            "stage": "original_spirv",
            "input_sha256": input_hash(self.source, self.butterfly),
            "dispatch_sha256": sha(json.dumps(DISPATCH, sort_keys=True).encode("ascii")),
            "shader_sha256": sha(b"private simulated direct original-SPIRV recorder"),
            "trace_sha256": sha(self.reference.read_bytes()),
            "records_by_site": list(EXPECTED_SITE_COUNTS),
        }
        self.save_evidence()

    def save_evidence(self):
        self.original_evidence.write_text(json.dumps(self.evidence), encoding="utf-8")

    def call(self):
        return save_and_join(
            self.manifest, self.original_evidence, self.reference,
            self.candidate, self.vulkan, self.unity, self.shader)

    def test_real_direct_original_sidecar_to_unity_join_diagnoses_drift(self):
        result = self.call()
        self.assertEqual(result["status"],
                         "private_actual_original_spirv_vs_unity_declared_keyed_input_join")
        self.assertTrue(result["actual_physical_input_pairs_sha_bound_to_original_private_sidecar"])
        self.assertTrue(result["actual_gpu_copy_input_report_required"])
        self.assertEqual(result["original_and_unity_keyed_trace_site_coverage"], [64, 256, 64])
        self.assertFalse(result["original_runtime_findkernel_mapping_proven"])
        self.assertFalse(result["unity_gpu_shader_compiled_binary_attested_independently"])
        self.assertFalse(result["android_adreno_water_proven"])
        self.assertEqual(result["diagnostics"][1]["coordinate_zero_collapse_by_axis"]["x"], 256)
        self.assertEqual(self.manifest.stat().st_mode & 0o777, 0o600)
        metadata = json.loads(self.manifest.read_text())
        self.assertEqual(metadata["reference"]["role"], "original_spirv")
        self.assertEqual(metadata["candidate"]["role"], "unity_compute_spirv")
        self.assertEqual(metadata["reference"]["shader_sha256"],
                         self.evidence["shader_sha256"])

    def test_reference_must_be_direct_original_spirv_not_hlsl_vulkan(self):
        self.evidence["stage"] = "hlsl_roundtrip_spirv"
        self.save_evidence()
        with self.assertRaises(ValueError):
            self.call()
        self.assertFalse(self.manifest.exists())

    def test_forged_original_trace_sha_is_rejected(self):
        self.evidence["trace_sha256"] = "a" * 64
        self.save_evidence()
        with self.assertRaises(ValueError):
            self.call()

    def test_false_original_shader_or_input_sidecar_stage_rejected(self):
        for change in ({"schema": "fake"}, {"shader_sha256": "invalid"},
                       {"input_sha256": "1" * 64},
                       {"dispatch_sha256": "2" * 64},
                       {"records_by_site": [64, 255, 64]}):
            good = dict(self.evidence)
            self.evidence.update(change)
            self.save_evidence()
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.call()
            self.evidence = good
            self.save_evidence()

    def test_tampered_unity_physical_source_with_signed_original_sidecar_rejected(self):
        p = self.unity / "source.rgba32f"
        p.write_bytes(b"\x01" + self.source[1:])
        with self.assertRaises(ValueError):
            self.call()

    def test_tampered_original_vulkan_image_versus_actual_original_input_sha(self):
        p = self.vulkan / "butterfly.rgba32f"
        p.write_bytes(self.butterfly[:-1] + b"\x00")
        with self.assertRaises(ValueError):
            self.call()

    def test_fake_copy_input_marker_or_gpu_mismatch_rejected(self):
        p = self.unity / "input_identity.rgba32f"
        for proof in (b"", b"Vulkan\n0\n0\n", b"OpenGLCore\n1\n0\n",
                      b"OpenGLCore\n0\n1\n", b"OpenGLCore\n0\n0\nFAKE",
                      b"OpenGLCore\n0\n0\n\n"):
            with self.subTest(proof=proof[:18]):
                p.write_bytes(proof)
                with self.assertRaises(ValueError):
                    self.call()

    def test_reject_truncated_or_extended_capture_blob(self):
        for name, data in (("source", self.source), ("butterfly", self.butterfly)):
            p = self.unity / (name + ".rgba32f")
            for corrupt in (data[:-1], data + b"\0"):
                p.write_bytes(corrupt)
                with self.subTest(name=name, size=len(corrupt)), self.assertRaises(ValueError):
                    self.call()
            p.write_bytes(data)

    def test_reject_bad_trace_coverage_and_duplicate_keys(self):
        self.candidate.write_bytes(generate_trace()[:-1])
        with self.assertRaises(ValueError):
            self.call()
        self.candidate.write_bytes(generate_trace())
        corrupted = bytearray(self.candidate.read_bytes())
        # overwrite second record with first to create duplicate key in site0
        row = INVOCATION_RECORD.size
        corrupted[4 + row:4 + 2 * row] = corrupted[4:4 + row]
        self.candidate.write_bytes(corrupted)
        with self.assertRaises(ValueError):
            self.call()

    def test_original_and_unity_trace_cannot_be_same_underlying_file(self):
        self.candidate.unlink()
        self.candidate.hardlink_to(self.reference)
        with self.assertRaises(ValueError):
            self.call()

    def test_source_and_butterfly_cannot_alias_inside_capture(self):
        p = self.unity / "butterfly.rgba32f"
        p.unlink()
        p.hardlink_to(self.unity / "source.rgba32f")
        with self.assertRaises(ValueError):
            self.call()

    def test_original_and_unity_image_cannot_be_hardlinks(self):
        p = self.unity / "source.rgba32f"
        p.unlink()
        p.hardlink_to(self.vulkan / "source.rgba32f")
        with self.assertRaises(ValueError):
            self.call()

    def test_symlink_to_shader_or_evidence_is_forbidden(self):
        for p in (self.shader, self.original_evidence):
            original = p.read_bytes()
            p.unlink()
            p.symlink_to(self.reference)
            with self.subTest(file=p.name), self.assertRaises(ValueError):
                self.call()
            p.unlink()
            p.write_bytes(original)

    def test_incorrect_shader_trace_entry_and_traversing_workflow_path(self):
        self.shader.write_bytes(b"#pragma kernel wrong\n" + b"A" * 100)
        with self.assertRaises(ValueError):
            self.call()
        self.shader.write_bytes(b"#pragma kernel main\nvoid main(){ }")
        with self.assertRaises(ValueError):
            self.call()

    def test_output_manifest_cannot_overwrite_another_evidence_file(self):
        self.manifest.write_text("PRIVATE_KEEP", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.call()
        self.assertEqual(self.manifest.read_text(), "PRIVATE_KEEP")

    def test_failure_does_not_emit_hashes_or_original_trace_bytes(self):
        with patch.object(sys, "argv", ["capture", "--manifest", str(self.manifest),
                "--original-evidence", str(self.original_evidence),
                "--original", str(self.reference), "--unity", str(self.candidate),
                "--vulkan-input-dir", str(self.vulkan),
                "--unity-input-dir", str(self.unity),
                "--unity-shader", str(self.shader)]):
            log = io.StringIO()
            with redirect_stdout(log):
                self.assertEqual(main(), 0)
            visible = log.getvalue()
            self.assertIn("RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN", visible)
            for private in (self.evidence["shader_sha256"],
                            self.evidence["input_sha256"], str(self.root),
                            "PRIVATE_KEEP", "private simulated"):
                self.assertNotIn(private, visible)

    def test_cli_fail_closed_and_redacts_private_file_content(self):
        self.evidence["stage"] = "hlsl_roundtrip_spirv"
        self.save_evidence()
        with patch.object(sys, "argv", ["capture", "--manifest", str(self.manifest),
                "--original-evidence", str(self.original_evidence),
                "--original", str(self.reference), "--unity", str(self.candidate),
                "--vulkan-input-dir", str(self.vulkan),
                "--unity-input-dir", str(self.unity),
                "--unity-shader", str(self.shader)]):
            err = io.StringIO()
            with redirect_stderr(err), self.assertRaises(SystemExit) as context:
                main()
            self.assertEqual(context.exception.code, 2)
            self.assertNotIn("hlsl_roundtrip_spirv", err.getvalue())
            self.assertNotIn(str(self.root), err.getvalue())


class OptInOriginalUnityWorkflowContract(unittest.TestCase):
    """Source-only guard preventing a translated HLSL surrogate becoming reference."""

    def workflow(self):
        path = Path(__file__).resolve().parents[1] / ".github/workflows/raft-t1-fft-unity-input-identity.yml"
        return path.read_text(encoding="utf-8")

    def test_genuine_direct_original_spirv_is_the_reference(self):
        workflow = self.workflow()
        self.assertIn("python3 -m scripts.t1_fft_original_trace_vulkan --project", workflow)
        self.assertIn("--export-private-trace t1-original-derived-unity/T1VulkanCapture/trace.bin", workflow)
        self.assertIn("--export-private-evidence t1-original-derived-unity/T1VulkanCapture/original_trace_evidence.json", workflow)
        self.assertNotIn("python3 -m scripts.t1_fft_pass0_vulkan_trace --project", workflow)
        self.assertIn("python3 -m scripts.t1_fft_candidate_keyed_trace_audit", workflow)

    def test_unity_trace_and_copyinput_are_real_private_gpu_fixture(self):
        workflow = self.workflow()
        self.assertIn("T1PrivateFftInputIdentityTests.cs", workflow)
        self.assertIn("T1FftInputIdentity.compute", workflow)
        self.assertIn("T1TracePass0.compute", workflow)
        self.assertIn("--unity t1-original-derived-unity/T1UnityCapture/trace.bin", workflow)
        self.assertIn("--vulkan-input-dir t1-original-derived-unity/T1VulkanCapture", workflow)
        self.assertIn("--unity-input-dir t1-original-derived-unity/T1UnityCapture", workflow)

    def test_private_join_after_real_unity_and_before_unsafe_numeric_inference(self):
        workflow = self.workflow()
        capture = workflow.index("python3 -m scripts.t1_fft_original_trace_vulkan")
        imported = workflow.index("Execute exact original-derived FFT ComputeShader import and two-pass GPU dispatch")
        joined = workflow.index("python3 -m scripts.t1_fft_private_unity_paired_capture")
        old_compare = workflow.index("python3 -m scripts.t1_fft_readback_parity")
        cleanup = workflow.index("Destroy ALL private shader assets")
        self.assertLess(capture, imported)
        self.assertLess(imported, joined)
        self.assertLess(joined, old_compare)
        self.assertLess(old_compare, cleanup)
        self.assertIn("--original-evidence t1-original-derived-unity/T1VulkanCapture/original_trace_evidence.json", workflow)
        self.assertIn("--unity-shader t1-original-derived-unity/Assets/T1TracePass0.compute", workflow)
        self.assertIn("--manifest t1-original-derived-unity/T1PrivateActualPair.json", workflow)

    def test_shared_mutex_and_push_optin_prevent_native_xapk_collision(self):
        workflow = self.workflow()
        self.assertIn("environment: UNITY_LICENSE", workflow)
        self.assertIn("group: raft-native-engine-", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("if: github.event_name == 'workflow_dispatch' || contains(github.event.head_commit.message, '[t1-paired-replay]')", workflow)
        self.assertIn("ZIP2_SHA: 15964ea8f246b6e076ce26b60931ee2e1a9a2385", workflow)
        self.assertIn("CLI_SHA256: 1de550a620ee92e05e920b6db7d431621440b60b2577f04b4a997dc92a58cb0a", workflow)
        self.assertIn("if: always()", workflow)
        self.assertNotIn("upload-artifact", workflow)
        self.assertNotIn("cancel-in-progress: true", workflow)


if __name__ == "__main__":
    unittest.main()
