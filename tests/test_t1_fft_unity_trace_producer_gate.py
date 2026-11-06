"""Source-only adversarial controls for private final-stage Unity FFT producer contract."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout, redirect_stderr

from scripts.t1_fft_invocation_pair_gate import SCHEMA
from scripts.t1_fft_trace_compare import INVOCATION_SIZE
from scripts.t1_fft_unity_trace_producer_gate import (
    ORIGINAL_OBJECT_SHA256, check, main, ASSET_PREAMBLE,
)


def digest(blob):
    return hashlib.sha256(blob).hexdigest()


class PrivateUnityProducerStageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "isolated-unity"
        self.assets = self.root / "Assets/T1OriginalDerived"
        self.assets.mkdir(parents=True)
        self.capture = self.root / "T1UnityCapture"
        self.capture.mkdir()
        self.stage = self.root / "T1ReplayStage.txt"
        self.stage.write_bytes(b"complete")
        self.trace_content = b"\0" * INVOCATION_SIZE
        (self.capture / "trace.bin").write_bytes(self.trace_content)
        (self.capture / "input_identity.rgba32f").write_bytes(b"OpenGLCore\n0\n0\n")
        self.trace_shader = self.root / "Assets/T1TracePass0.compute"
        self.trace_shader.write_bytes(ASSET_PREAMBLE + b"void main(uint3 id : SV_DispatchThreadID){}")
        self.candidate_content = []
        rows = []
        for i in (0, 1):
            code = ASSET_PREAMBLE + ("// synthetic candidate slot %d\n" % i).encode() + b"void main(){}"
            self.candidate_content.append(code)
            (self.assets / ("FFT_Candidate_%02d.compute" % i)).write_bytes(code)
            rows.append({
                "compiled_slot": i, "candidate_sha256": digest(code),
                "expected_group_x": 64,
                "source_property": "Src" + str(i),
                "butterfly_property": "Butterfly" + str(i),
                "output_property": "Out" + str(i),
            })
        self.rows = rows
        self.sidecar = {
            "schema_version": 1, "original_fft_object_sha256": ORIGINAL_OBJECT_SHA256,
            "selected_compiled_slots": [0, 1], "resources": self.rows,
            "original_authored_resource_names_proven": False,
            "original_runtime_kernel_mapping_proven": False,
            "unity_gpu_dispatch_executed": False,
            "android_device_proven": False,
        }
        self.pair = {
            "schema": SCHEMA,
            "expected_records_by_site": [64, 256, 64],
            "reference": {
                "role": "original_spirv",
                "shader_sha256": digest(b"private original"),
                "trace_sha256": digest(b"independent original trace"),
                "input_sha256": digest(b"matching physical image inputs"),
                "dispatch_sha256": digest(b"one dispatch"),
            },
            "candidate": {
                "role": "unity_compute_spirv",
                "shader_sha256": digest(self.trace_shader.read_bytes()),
                "trace_sha256": digest(self.trace_content),
                "input_sha256": digest(b"matching physical image inputs"),
                "dispatch_sha256": digest(b"one dispatch"),
            },
        }
        self.resfile = self.assets / "PrivateGpuResources.json"
        self.manifest = self.root / "T1PrivateActualPair.json"
        self.save()

    def save(self):
        self.resfile.write_text(json.dumps(self.sidecar), encoding="utf-8")
        self.manifest.write_text(json.dumps(self.pair), encoding="utf-8")

    def verify(self):
        return check(self.root, self.manifest)

    def test_real_source_only_positive_contract_and_no_runtime_claim(self):
        report = self.verify()
        self.assertEqual(report["original_derived_candidate_slots_physically_sha_bound"], 2)
        self.assertTrue(report["private_unity_trace_shader_and_output_physically_sha_bound"])
        self.assertTrue(report["private_unity_producer_complete_stage_file_verified"])
        for name in ("unity_compiler_shader_binary_independently_attested",
                     "unity_nunit_stage_file_is_signed_attestation",
                     "actual_original_vs_unity_numeric_parity_proven_here",
                     "original_authored_runtime_findkernel_proven",
                     "android_adreno_water_proven",
                     "private_candidate_symbols_shas_pixels_or_trace_bytes_exported"):
            self.assertFalse(report[name], name)

    def test_reject_incomplete_stale_unexpected_stage(self):
        for stage in (b"", b"trace_dispatch", b"trace_buffer_readback",
                      b"complete\n", b"complete\0", b"completex",
                      b"X" * 64):
            with self.subTest(stage=stage[:15]):
                self.stage.write_bytes(stage)
                with self.assertRaises(ValueError):
                    self.verify()
        self.stage.write_bytes(b"complete")

    def test_stage_file_symlink_rejected(self):
        self.stage.unlink()
        self.stage.symlink_to(self.manifest)
        with self.assertRaises(ValueError):
            self.verify()

    def test_tampered_derived_first_or_second_candidate_rejected(self):
        for i in (0, 1):
            path = self.assets / ("FFT_Candidate_%02d.compute" % i)
            original = path.read_bytes()
            path.write_bytes(original + b"t")
            with self.subTest(slot=i), self.assertRaises(ValueError):
                self.verify()
            path.write_bytes(original)

    def test_reject_wrong_original_object_slot_or_expected_group(self):
        for kind in ("original_fft_object_sha256", "selected_compiled_slots", "group"):
            self.sidecar["original_fft_object_sha256"] = ORIGINAL_OBJECT_SHA256
            self.sidecar["selected_compiled_slots"] = [0, 1]
            self.rows[0]["expected_group_x"] = 64
            if kind == "original_fft_object_sha256":
                self.sidecar[kind] = "f" * 64
            elif kind == "selected_compiled_slots":
                self.sidecar[kind] = [1, 0]
            else:
                self.rows[0]["expected_group_x"] = 32
            self.save()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                self.verify()
        self.sidecar["original_fft_object_sha256"] = ORIGINAL_OBJECT_SHA256
        self.sidecar["selected_compiled_slots"] = [0, 1]
        self.rows[0]["expected_group_x"] = 64
        self.save()

    def test_false_runtime_original_binding_flags_rejected(self):
        for name in ("original_authored_resource_names_proven",
                     "original_runtime_kernel_mapping_proven",
                     "unity_gpu_dispatch_executed", "android_device_proven"):
            self.sidecar[name] = True
            self.save()
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.verify()
            self.sidecar[name] = False
        self.save()

    def test_resource_property_alias_invalid_or_overlong(self):
        for invalid in (self.rows[0]["source_property"], "bad name", "!" * 2, "x" * 125):
            self.rows[0]["butterfly_property"] = invalid
            self.save()
            with self.subTest(value=invalid[:12]), self.assertRaises(ValueError):
                self.verify()
        self.rows[0]["butterfly_property"] = "Butterfly0"
        self.save()

    def test_bad_resource_metadata_bounded_and_duplicate_fields(self):
        for blob in (b"", b"Z" * 9000, b'{"schema_version":1,"schema_version":2}',
                     b'{"a":NaN}', b'[]'):
            self.resfile.write_bytes(blob)
            with self.subTest(blob=blob[:18]), self.assertRaises(
                    (ValueError, json.JSONDecodeError)):
                self.verify()

    def test_wrong_candidate_role_or_pair_coverage_rejected(self):
        for key, invalid in (("role", "hlsl_roundtrip_spirv"),
                             ("role", "original_spirv")):
            self.pair["candidate"][key] = invalid
            self.save()
            with self.assertRaises(ValueError):
                self.verify()
        self.pair["candidate"]["role"] = "unity_compute_spirv"
        self.pair["expected_records_by_site"] = [64, 255, 64]
        self.save()
        with self.assertRaises(ValueError):
            self.verify()

    def test_wrong_shader_or_trace_sha_rejected(self):
        for key in ("shader_sha256", "trace_sha256"):
            self.pair["candidate"][key] = "f" * 64
            self.save()
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify()
            if key == "shader_sha256":
                self.pair["candidate"][key] = digest(self.trace_shader.read_bytes())
            else:
                self.pair["candidate"][key] = digest(self.trace_content)
        self.save()

    def test_reject_hardlink_trace_shader_alias_candidate(self):
        a = self.assets / "FFT_Candidate_00.compute"
        self.trace_shader.unlink()
        self.trace_shader.hardlink_to(a)
        self.pair["candidate"]["shader_sha256"] = digest(a.read_bytes())
        self.save()
        with self.assertRaises(ValueError):
            self.verify()

    def test_bad_trace_file_size_and_fake_copyinput_report(self):
        path = self.capture / "trace.bin"
        for corrupt in (self.trace_content[:-1], self.trace_content + b"\0"):
            path.write_bytes(corrupt)
            self.pair["candidate"]["trace_sha256"] = digest(corrupt)
            self.save()
            with self.assertRaises(ValueError):
                self.verify()
        path.write_bytes(self.trace_content)
        self.pair["candidate"]["trace_sha256"] = digest(self.trace_content)
        self.save()
        self.capture.joinpath("input_identity.rgba32f").write_bytes(b"OpenGLCore\n1\n0\n")
        with self.assertRaises(ValueError):
            self.verify()

    def test_resource_directory_or_capture_symlink_rejected(self):
        self.stage.write_bytes(b"complete")
        self.capture.joinpath("input_identity.rgba32f").write_bytes(b"OpenGLCore\n0\n0\n")
        old = self.assets / "PrivateGpuResources.json"
        old.unlink()
        old.symlink_to(self.manifest)
        with self.assertRaises(ValueError):
            self.verify()

    def test_cli_redacts_all_private_names_hashes_and_paths(self):
        output = io.StringIO()
        with patch("sys.argv", ["t1-producer", "--project", str(self.root),
                                "--pair-manifest", str(self.manifest)]):
            with redirect_stdout(output):
                self.assertEqual(main(), 0)
        result = output.getvalue()
        self.assertIn("RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER", result)
        for secret in (str(self.root), self.rows[0]["source_property"],
                       self.rows[1]["output_property"], self.pair["candidate"]["shader_sha256"],
                       ORIGINAL_OBJECT_SHA256, "SV_DispatchThreadID"):
            self.assertNotIn(secret, result)

    def test_cli_failure_never_prints_original_assets(self):
        self.stage.write_bytes(b"PRIVATE_ORIGINAL_SHADER")
        error = io.StringIO()
        with patch("sys.argv", ["t1-producer", "--project", str(self.root),
                                "--pair-manifest", str(self.manifest)]):
            with redirect_stderr(error), self.assertRaises(SystemExit) as result:
                main()
        self.assertEqual(result.exception.code, 2)
        self.assertNotIn("PRIVATE_ORIGINAL_SHADER", error.getvalue())
        self.assertNotIn(str(self.root), error.getvalue())


if __name__ == "__main__":
    unittest.main()
