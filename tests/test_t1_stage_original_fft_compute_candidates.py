"""Adversarial source-free controls for T1 authentic FFT -> Unity importer staging."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.t1_stage_original_fft_compute_candidates import (
    FILES, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
    ORIGINAL_FFT_OBJECT_SHA256, sanitize_translated_compute,
    validate_import_candidate_manifest, stage_original_candidates,
)


class OriginalDerivedCandidateControls(unittest.TestCase):
    def shader(self, x):
        return ("[numthreads(%d,1,1)]\nvoid main(uint3 id : SV_DispatchThreadID) { }\n" % x).encode()

    def test_valid_single_kernel_translation_keeps_body_untouched(self):
        s = self.shader(64)
        out = sanitize_translated_compute(s, 64)
        self.assertEqual(out, b"#pragma kernel main\n" + s)
        self.assertNotIn(b"#pragma kernel main", s)

    def test_unsafe_or_unsupported_source_fails_closed(self):
        bad = [
            (b"", 64), (b"a\x00b", 64), (self.shader(64), 128),
            (b"#pragma kernel main\n" + self.shader(64), 64),
            (b"[numthreads(64,1,1)]\nvoid absent(){}\n", 64),
            (self.shader(64), 63), (self.shader(64) + b"\xff", 64),
        ]
        for code, x in bad:
            with self.subTest(x=x, sha=hashlib.sha256(code).hexdigest()[:8]):
                with self.assertRaises(ValueError):
                    sanitize_translated_compute(code, x)

    def fixture(self, root):
        result = {"schema_version": 1,
                  "provenance": "DXBC_VKD3D_SPIRVCROSS_ROUNDTRIP_NOT_AUTHORED",
                  "original_fft_object_sha256": ORIGINAL_FFT_OBJECT_SHA256,
                  "candidate_count": FILES, "rows": [],
                  "original_runtime_kernel_mapping_proven": False,
                  "unity_import_proven": False, "android_gpu_proven": False}
        for slot in range(FILES):
            x = EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[slot]
            rel = "Assets/T1OriginalDerived/FFT_Candidate_%02d.compute" % slot
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            blob = sanitize_translated_compute(self.shader(x), x)
            p.write_bytes(blob)
            result["rows"].append({
                "compiled_slot": slot, "compute_asset": rel,
                "candidate_sha256": hashlib.sha256(blob).hexdigest(),
                "original_dxbc_sha256": hashlib.sha256(("fake-but-synthetic-%d" % slot).encode()).hexdigest(),
                "expected_group_x": x, "runtime_kernel_identity_proven": False,
            })
        return result

    def test_all_twenty_synthetic_unique_paths_with_explicit_false_gates(self):
        with tempfile.TemporaryDirectory() as d:
            result = validate_import_candidate_manifest(self.fixture(Path(d)), Path(d))
            self.assertEqual(result["candidate_slots_authenticated"], 20)
            self.assertFalse(result["runtime_mapping_proven"])
            self.assertFalse(result["unity_import_proven"])

    def test_provenance_runtime_claim_and_slot_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = self.fixture(root)
            changes = [
                lambda x: x.update({"original_runtime_kernel_mapping_proven": True}),
                lambda x: x.update({"unity_import_proven": True}),
                lambda x: x.update({"android_gpu_proven": True}),
                lambda x: x.update({"provenance": "ORIGINAL_AUTHORED"}),
                lambda x: x["rows"][2].update({"compiled_slot": 3}),
                lambda x: x["rows"][4].update({"expected_group_x": 999}),
                lambda x: x["rows"][6].update({"runtime_kernel_identity_proven": True}),
                lambda x: x["rows"][0].update({"compute_asset": "../outside.compute"}),
                lambda x: x["rows"][3].update({"candidate_sha256": "0" * 64}),
                lambda x: x["rows"].pop(),
            ]
            for mutation in changes:
                changed = copy.deepcopy(source)
                mutation(changed)
                with self.subTest(idx=changes.index(mutation)):
                    with self.assertRaises(ValueError):
                        validate_import_candidate_manifest(changed, root)

    def test_missing_private_candidate_cannot_pass(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rows = self.fixture(root)
            (root / rows["rows"][7]["compute_asset"]).unlink()
            with self.assertRaises(ValueError):
                validate_import_candidate_manifest(rows, root)

    def test_original_stager_never_overwrites_existing_project(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            project = root / "old"
            project.mkdir()
            sentinel = project / "keep.txt"
            sentinel.write_text("DO-NOT-TOUCH")
            with self.assertRaises(ValueError):
                stage_original_candidates(root / "missing", project)
            self.assertEqual(sentinel.read_text(), "DO-NOT-TOUCH")

    def test_no_original_words_or_recovered_source_in_public_manifest(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            result = self.fixture(root)
            body = json.dumps(result, sort_keys=True)
            self.assertNotIn("float2", body)
            self.assertNotIn("SV_DispatchThreadID", body)
            self.assertNotIn("#pragma kernel", body)
            self.assertNotIn("original_runtime_kernel_mapping_proven\": true", body.lower())


if __name__ == "__main__":
    unittest.main()
