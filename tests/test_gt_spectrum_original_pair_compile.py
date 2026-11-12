"""GT: source-free tests for private authenticated Spectrum 7-pass pair gate.

No Raft DXBC, HLSL, SPIR-V, or original Shader bytes are loaded by these tests.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.b09_spectrum_topology_contract import PASSES, BLOB_SEQUENCES
from scripts.gt_spectrum_original_pair_compile import (
    EXPECTED_STAGES, EXPECTED_PAIRS, _paired_rows, compile_private,
)


def _fixture(packet: Path, *, count: int = PASSES) -> dict:
    stages = []
    for p in range(count):
        pairs = []
        folder = packet / f"s00-p{p:02d}"
        folder.mkdir()
        for v in range(2):
            stage_rows = {}
            for stage, name in ((1, "progVertex"), (0, "progFragment")):
                data = ("fake-stage-%d-%d-%d" % (p, v, stage)).encode()
                file = folder / ("pair%03d-stage%d.dxbc" % (v, stage))
                file.write_bytes(data)
                stage_rows[str(stage)] = {
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                    "original_blob_index": BLOB_SEQUENCES[name][2 * p + v],
                }
            pairs.append({"pair_index": v, "stages": stage_rows})
        stages.append({"subshader": 0, "pass_index": p, "variant_pairs": pairs})
    return {
        "original_subshader_pass_counts": [PASSES],
        "original_passes": PASSES,
        "source_topology_attestation": {
            "authenticated_variant_stage_programs": EXPECTED_STAGES},
        "shaderlab_reconstructed": False,
        "device_pixels_verified": False,
        "stages": stages,
    }


class PrivateSpectrumCompileTest(unittest.TestCase):
    def test_count_and_order_of_all_authentic_pass_variant_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _fixture(Path(tmp))
            rows = _paired_rows(manifest)
            self.assertEqual(len(rows), 14)
            self.assertEqual([(p, v) for p, v, _ in rows],
                             [(p, v) for p in range(7) for v in (0, 1)])
            self.assertEqual(EXPECTED_PAIRS, 14)
            self.assertEqual(EXPECTED_STAGES, 28)

    def test_source_free_synthetic_roundtrip_all_28_stage_variants(self):
        with tempfile.TemporaryDirectory(prefix="gt-spectrum-synthetic-") as tmp:
            private = Path(tmp) / "private"
            scratch = Path(tmp) / "scratch"
            private.mkdir()
            scratch.mkdir()
            manifest = _fixture(private)
            report = Path(tmp) / "stage.json"
            report.write_text(json.dumps(manifest), encoding="utf-8")
            translations = []
            compiles = []
            def fake_translate(raw: bytes, stage: int, folder: Path):
                translations.append((hashlib.sha256(raw).hexdigest(), stage))
                (folder / "private.hlsl").write_text(
                    "float4 main() : SV_Target { return float4(1,1,1,1); }\n",
                    encoding="utf-8")
                return {
                    "dxbc_sha256": hashlib.sha256(raw).hexdigest(),
                    "stage": stage, "vulkan11_valid": True,
                    "hlsl_recovered": True,
                    "roundtrip_vulkan11_valid": True,
                }
            def fake_compiler(command: list[str]):
                if command[0] == "glslangValidator":
                    compiles.append(command)
                    output = Path(command[command.index("-o") + 1])
                    output.write_bytes(b"\x03\x02\x23\x07" + b"\0" * 20)
                    return True
                if command[0] == "spirv-val":
                    return Path(command[-1]).read_bytes().startswith(
                        b"\x03\x02\x23\x07")
                self.fail("unexpected tool invocation")
            result = compile_private(
                private, report, scratch, translator=fake_translate,
                invoke=fake_compiler, validator=lambda _p, _m: {})
            self.assertEqual(
                result["status"], "PRIVATE_ORIGINAL_SPECTRUM_SEVEN_PASS_PAIR_GLSLANG_VALID")
            self.assertEqual(result["original_SHA_verified_passes"], PASSES)
            self.assertEqual(result["original_VS_FS_keyword_pairs"], 14)
            self.assertEqual(result["original_combined_compiled_stage_variants"], 28)
            self.assertEqual(len(compiles), 28)
            self.assertEqual(len(translations), 28)
            self.assertFalse(result["original_shader_installed_into_Unity"])
            self.assertFalse(result["Android_Unity_2021_shader_import_proven"])
            self.assertFalse(result["Adreno_pixels_verified"])
            self.assertFalse(result["private_shaders_published"])
            self.assertEqual(set(scratch.iterdir()), set())

    def test_seven_original_passes_cannot_shrink_to_phone_floor_six(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _fixture(Path(tmp), count=6)
            with self.assertRaisesRegex(ValueError, "seven_passes"):
                _paired_rows(manifest)

    def test_reordered_or_replaced_source_program_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = _fixture(Path(tmp))
            for mutation in ("wrong_order", "absent_stage", "wrong_variant"):
                sample = copy.deepcopy(manifest)
                if mutation == "wrong_order":
                    sample["stages"][1]["pass_index"] = 5
                elif mutation == "absent_stage":
                    del sample["stages"][0]["variant_pairs"][0]["stages"]["0"]
                else:
                    sample["stages"][0]["variant_pairs"][0]["pair_index"] = 2
                with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                    _paired_rows(sample)

    def test_sha_drift_rejected_before_compiling_any_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / "private"
            scratch = Path(tmp) / "scratch"
            private.mkdir()
            scratch.mkdir()
            manifest = _fixture(private)
            report = Path(tmp) / "stage.json"
            report.write_text(json.dumps(manifest), encoding="utf-8")
            (private / "s00-p00" / "pair000-stage1.dxbc").write_bytes(b"altered")
            called = []
            def no_translate(*args):
                called.append(True)
                raise AssertionError("must never be called after SHA drift")
            with self.assertRaisesRegex(ValueError, "DXBC_SHA_drift"):
                compile_private(
                    private, report, scratch,
                    translator=no_translate,
                    invoke=lambda _: True,
                    validator=lambda _p, _m: {})
            self.assertFalse(called)

    def test_failed_compiler_does_not_claim_complete_or_phone_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            private = Path(tmp) / "private"
            scratch = Path(tmp) / "scratch"
            private.mkdir()
            scratch.mkdir()
            manifest = _fixture(private)
            report = Path(tmp) / "stage.json"
            report.write_text(json.dumps(manifest), encoding="utf-8")
            def translate(raw, stage, folder):
                (folder / "private.hlsl").write_text(
                    "float4 main():SV_Target{return 0;}",
                    encoding="utf-8")
                return {"dxbc_sha256": hashlib.sha256(raw).hexdigest(),
                        "stage": stage, "vulkan11_valid": True,
                        "hlsl_recovered": True, "roundtrip_vulkan11_valid": True}
            result = compile_private(
                private, report, scratch, translator=translate,
                invoke=lambda _: False, validator=lambda _p, _m: {})
            self.assertEqual(result["status"], "PRIVATE_COMBINED_STAGE_COMPILE_BLOCKED")
            self.assertEqual(result["first_failed_pass"], 0)
            self.assertEqual(result["first_failed_variant"], 0)
            self.assertEqual(result["first_failed_stage"], 1)
            self.assertFalse(result["Adreno_pixels_verified"])
            self.assertFalse(result["original_shader_installed_into_Unity"])


if __name__ == "__main__":
    unittest.main()
