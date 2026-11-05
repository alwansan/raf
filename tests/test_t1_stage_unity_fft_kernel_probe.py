"""Synthetic contract tests only; no Unity Editor or Android/device proof."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.t1_stage_unity_fft_kernel_probe import (
    ORIGINAL_FFT_OBJECT_SHA256, authenticate_owner, stage, validate_private_manifest,
)

# Deliberately synthetic authored shader; NOT the game's shader source.
SHADER = ("#pragma kernel TestA\n#pragma kernel TestB\n"
          "[numthreads(64,1,1)] void TestA(uint3 id: SV_DispatchThreadID) { }\n"
          "[numthreads(64,1,1)] void TestB(uint3 id: SV_DispatchThreadID) { }\n")


def manifest():
    rows = []
    for bank in (0, 1):
        for r in (32, 64, 128, 256, 512):
            for pass_index in (0, 1):
                slot = ((r.bit_length()-1)-5)*2 + bank*10 + pass_index
                rows.append({"compiled_slot": slot, "resolution": r, "bank": bank,
                             "pass_index": pass_index, "expected_group_x": 2*r,
                             "kernel_name": "TestA" if pass_index == 0 else "TestB",
                             "keywords": []})
    return {"schema_version": 1,
            "candidate_provenance": "B48_SOURCE_SELECTED_COMPILED_CANDIDATES_ONLY",
            "original_fft_object_sha256": ORIGINAL_FFT_OBJECT_SHA256,
            "original_unity_kernel_mapping_proven": False,
            "authored_compute_sha256": hashlib.sha256(SHADER.encode()).hexdigest(),
            "rows": rows}


class T1FftUnityProbeStagingTests(unittest.TestCase):
    def test_20_original_candidates_do_not_imply_20_runtime_kernel_names(self):
        result = validate_private_manifest(manifest(), SHADER.encode())
        self.assertEqual(result["compiled_candidate_rows"], 20)
        self.assertEqual(result["unique_authored_kernel_names"], 2)
        self.assertFalse(result["original_unity_runtime_mapping_proven"])

    def test_stage_isolated_project_without_owning_game_or_claiming_unity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            compute = root / "private.compute"
            compute.write_text(SHADER)
            editor = root / "T1FftKernelRuntimeProbe.cs"
            editor.write_text("class T1FftKernelRuntimeProbe {} // original_unity_mapping_proven=false")
            project = root / "isolated-unity"
            result = stage(compute, manifest(), editor, project)
            self.assertTrue(result["staged"])
            self.assertFalse(result["actual_unity_import_or_execution"])
            self.assertFalse(result["android_gpu_executed"])
            self.assertEqual((project / "Assets/T1Private/FFTProbe.compute").read_text(), SHADER)
            self.assertEqual((project / "ProjectSettings/ProjectVersion.txt").read_text().strip(),
                             "m_EditorVersion: 2021.3.45f2")
            self.assertEqual(json.loads((project / "Assets/T1Private/PrivateProbeManifest.json").read_text())["rows"],
                             manifest()["rows"])
            with self.assertRaisesRegex(ValueError, "overwrite"):
                stage(compute, manifest(), editor, project)

    def test_source_identity_or_fake_runtime_proof_fails_closed(self):
        for field, value in [
            ("authored_compute_sha256", "0"*64),
            ("original_fft_object_sha256", "0"*64),
            ("candidate_provenance", "RUNTIME_PROVEN"),
            ("original_unity_kernel_mapping_proven", True),
        ]:
            with self.subTest(field=field):
                trial = manifest()
                trial[field] = value
                with self.assertRaises(ValueError):
                    validate_private_manifest(trial, SHADER.encode())

    def test_original_source_selector_and_workgroup_negative_controls(self):
        for field, value in [
            ("compiled_slot", 13), ("resolution", 20),
            ("bank", 3), ("pass_index", True),
            ("expected_group_x", 999),
        ]:
            with self.subTest(field=field):
                trial = manifest()
                trial["rows"][0][field] = value
                with self.assertRaises(ValueError):
                    validate_private_manifest(trial, SHADER.encode())

    def test_kernel_and_keyword_negative_controls(self):
        for field, value in [
            ("kernel_name", "MISSING"), ("kernel_name", "../TestA"),
            ("keywords", ["SAME", "SAME"]),
            ("keywords", ["GOOD", 1]),
            ("keywords", ["BAD;INJECT"]),
        ]:
            with self.subTest(field=field):
                trial = manifest()
                trial["rows"][0][field] = value
                with self.assertRaises(ValueError):
                    validate_private_manifest(trial, SHADER.encode())

    def test_no_original_claims_on_missing_owner_or_invalid_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "sharedassets0.assets"
            fake.write_bytes(b"not the original owner")
            with self.assertRaisesRegex(ValueError, "bytes/SHA256"):
                authenticate_owner(fake)
            with self.assertRaises(ValueError):
                validate_private_manifest(manifest(), b"\x00")
            with self.assertRaises(ValueError):
                validate_private_manifest(manifest(), b"not a compute shader")
            link = Path(tmp) / "link"
            link.symlink_to(fake)
            with self.assertRaises(ValueError):
                authenticate_owner(link)

    def test_aggregate_result_does_not_expose_private_kernel_names(self):
        result = json.dumps(validate_private_manifest(manifest(), SHADER.encode()))
        self.assertNotIn("TestA", result)
        self.assertNotIn("TestB", result)
        self.assertNotIn("runtime_kernel_id", result)


if __name__ == "__main__":
    unittest.main()
