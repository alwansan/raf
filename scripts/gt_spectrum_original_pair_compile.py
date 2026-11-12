#!/usr/bin/env python3
"""GT: compile all 7x2 original Spectrum VS/FS pairings in private Vulkan scratch.

Read B09 SHA-authenticated original ZIP2 StagePacket and manifest. No original
DXBC, HLSL, SPIR-V, GUID, source shader name or ShaderLab is published.
A combined stage compile proves source *compatibility in glslang only*; it
does not prove original Unity pass-state, keyword selection, Sampler/CB upload,
Android Vulkan compiler, or phone pixels. Do not install into game.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.b09_spectrum_topology_contract import PASSES, TARGET
from scripts.b09_translate_original_spectrum import validate_packet
from scripts.w1_depth_shaderlab import stage_body
from scripts.w1_recover_graphics_programs import translate

EXPECTED_PAIRS = PASSES * 2
EXPECTED_STAGES = EXPECTED_PAIRS * 2
MAX_HLSL = 1024 * 1024
MAX_PAIRED_HLSL = 2 * MAX_HLSL + 4096
MAX_SPV = 8 * 1024 * 1024


def _physical(path):
    return not any(x.is_symlink() for x in (path, *path.parents))


def _invoke(args):
    try:
        r = subprocess.run(args, check=False, stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           timeout=120)
        return r.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _paired_rows(manifest):
    if (not isinstance(manifest, dict)
            or manifest.get("original_subshader_pass_counts") != [PASSES]
            or manifest.get("original_passes") != PASSES
            or manifest.get("source_topology_attestation", {}).get(
                "authenticated_variant_stage_programs") != EXPECTED_STAGES
            or manifest.get("shaderlab_reconstructed") is not False
            or manifest.get("device_pixels_verified") is not False):
        raise ValueError("original_Spectrum_source_attestation_incomplete")
    stages = manifest.get("stages")
    if not isinstance(stages, list) or len(stages) != PASSES:
        raise ValueError("original_Spectrum_seven_passes_required")
    rows = []
    for p, entry in enumerate(stages):
        if (not isinstance(entry, dict) or entry.get("pass_index") != p
                or entry.get("subshader") != 0
                or not isinstance(entry.get("variant_pairs"), list)
                or len(entry["variant_pairs"]) != 2):
            raise ValueError("original_Spectrum_pass_or_variant_drift")
        for v, pair in enumerate(entry["variant_pairs"]):
            if (not isinstance(pair, dict) or pair.get("pair_index") != v
                    or not isinstance(pair.get("stages"), dict)
                    or set(pair["stages"]) != {"1", "0"}):
                raise ValueError("original_Spectrum_VS_FS_pair_missing")
            rows.append((p, v, pair))
    if len(rows) != EXPECTED_PAIRS:
        raise ValueError("original_Spectrum_paired_variants_incomplete")
    return rows


def compile_private(packet: Path, manifest_path: Path, scratch: Path,
                    *, translator=translate, invoke=_invoke,
                    validator=validate_packet):
    packet, manifest_path, scratch = map(
        lambda x: Path(x).absolute(), (packet, manifest_path, scratch))
    if (not packet.is_dir() or not manifest_path.is_file()
            or not scratch.is_dir() or not _physical(packet)
            or not _physical(manifest_path) or not _physical(scratch)
            or scratch.is_relative_to(packet)
            or manifest_path.is_relative_to(packet)
            or manifest_path.stat().st_size > 256 * 1024):
        raise ValueError("original_Spectrum_private_path_invalid")
    report = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = _paired_rows(report)
    # Performs complete original stage SHA/segment/pass and source metadata
    # validation, not a name-only blob identity guess.
    validator(packet, report)

    rounds = 0
    translated = {}
    with tempfile.TemporaryDirectory(prefix="gt-spectrum-paired-private-", dir=scratch) as tmp:
        root = Path(tmp)
        for p, v, pair in rows:
            hlsl = {}
            for stage in (1, 0):
                raw_path = packet / f"s00-p{p:02d}" / f"pair{v:03d}-stage{stage}.dxbc"
                if not _physical(raw_path) or not raw_path.is_file():
                    raise ValueError("original_Spectrum_stage_path_untrusted")
                meta = pair["stages"][str(stage)]
                raw = raw_path.read_bytes()
                if (len(raw) != meta.get("bytes") or
                        hashlib.sha256(raw).hexdigest() != meta.get("sha256")):
                    raise ValueError("original_Spectrum_DXBC_SHA_drift")
                cache_key = (stage, meta["sha256"])
                if cache_key not in translated:
                    folder = root / f"s{stage}-original-{len(translated)}"
                    folder.mkdir()
                    result = translator(raw, stage, folder)
                    if (not isinstance(result, dict)
                            or result.get("dxbc_sha256") != meta["sha256"]
                            or result.get("stage") != stage
                            or result.get("vulkan11_valid") is not True
                            or result.get("hlsl_recovered") is not True
                            or result.get("roundtrip_vulkan11_valid") is not True):
                        raise ValueError("original_Spectrum_stage_translation_unproven")
                    content = (folder / "private.hlsl").read_bytes()
                    if not 0 < len(content) <= MAX_HLSL or b"\x00" in content:
                        raise ValueError("original_Spectrum_HLSL_size_invalid")
                    translated[cache_key] = content.decode("utf-8")
                hlsl[stage] = translated[cache_key]
            combined = stage_body(hlsl[1], hlsl[0])
            if not 0 < len(combined.encode("utf-8")) <= MAX_PAIRED_HLSL:
                raise ValueError("original_Spectrum_pair_program_oversized")
            candidate = root / f"pass{p:02d}-pair{v:03d}.hlsl"
            candidate.write_text(combined, encoding="utf-8")
            for stage, stage_name, macro in (
                    (1, "vert", "SHADER_STAGE_VERTEX"),
                    (0, "frag", "SHADER_STAGE_FRAGMENT")):
                output = root / f"pass{p:02d}-pair{v:03d}-s{stage}.spv"
                cmd = ["glslangValidator", "-V", "-D", "--target-env", "vulkan1.1",
                       "-D" + macro + "=1", "-S", stage_name,
                       "-e", "main", "-o", str(output), str(candidate)]
                if not invoke(cmd):
                    return {
                        "status": "PRIVATE_COMBINED_STAGE_COMPILE_BLOCKED",
                        "first_failed_pass": p,
                        "first_failed_variant": v,
                        "first_failed_stage": stage,
                        "compiled_stages_before_first_failure": rounds,
                        "private_shaders_published": False,
                        "original_shader_installed_into_Unity": False,
                        "Adreno_pixels_verified": False,
                    }
                if (not _physical(output) or not output.is_file()
                        or not 20 <= output.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1",
                                       str(output)])):
                    return {
                        "status": "PRIVATE_COMBINED_SPIRV_INVALID",
                        "first_failed_pass": p,
                        "first_failed_variant": v,
                        "first_failed_stage": stage,
                        "compiled_stages_before_first_failure": rounds,
                        "private_shaders_published": False,
                        "original_shader_installed_into_Unity": False,
                        "Adreno_pixels_verified": False,
                    }
                rounds += 1

    return {
        "schema": 1,
        "status": "PRIVATE_ORIGINAL_SPECTRUM_SEVEN_PASS_PAIR_GLSLANG_VALID",
        "original_SHA_verified_passes": PASSES,
        "original_VS_FS_keyword_pairs": EXPECTED_PAIRS,
        "original_combined_compiled_stage_variants": rounds,
        "distinct_private_original_stage_translations": len(translated),
        "all_seven_original_source_passes_preserved": True,
        "private_shaders_published": False,
        "original_shader_installed_into_Unity": False,
        "original_Unity_source_ShaderLab_and_Material_sampler_parity_proven": False,
        "Android_Unity_2021_shader_import_proven": False,
        "Adreno_pixels_verified": False,
    }


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--packet", type=Path, required=True)
    a.add_argument("--stage-report", type=Path, required=True)
    a.add_argument("--scratch", type=Path, required=True)
    a.add_argument("--out", type=Path, required=True)
    p = a.parse_args()
    output = p.out.absolute()
    if (output.exists() or output.is_symlink()
            or not output.parent.is_dir() or not _physical(output.parent)
            or output.is_relative_to(p.packet.absolute())
            or output.is_relative_to(Path.cwd().absolute())):
        raise SystemExit("private_spectrum_report_path_unsafe")
    try:
        result = compile_private(p.packet, p.stage_report, p.scratch)
    except BaseException as exc:
        result = {
            "status": "INCONCLUSIVE",
            "safe_error_type": type(exc).__name__,
            "private_shaders_published": False,
            "original_shader_installed_into_Unity": False,
            "Adreno_pixels_verified": False,
        }
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("GT_ORIGINAL_SPECTRUM_PRIVATE_PAIR_PROBE_SAFE " +
          json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PRIVATE_ORIGINAL_SPECTRUM_SEVEN_PASS_PAIR_GLSLANG_VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
