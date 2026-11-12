#!/usr/bin/env python3
"""GT: two PRIVATE, isolated, seven-pass Spectrum ShaderLab structural candidates.

Faithfully combines SHA-authenticated original 7 pass render states and 14
paired original VS/FS stage variants. Each candidate freezes ONE of two real
keyword settings across seven passes. This is NOT an original keyword routed
shader, original Material/GUID binding, Unity import, or Adreno pixel proof.
Original ShaderLab text/HLSL/DXBC/private names are never printed or uploaded.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from scripts.b09_spectrum_topology_contract import (
    OWNER, PASSES, TARGET,
)
from scripts.b09_translate_original_spectrum import validate_packet
from scripts.b09_stage_original_spectrum import _selected_original
from scripts.t3_particle108_source_propstate import serialize_properties
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.w1_depth_shaderlab import quoted, tags, stage_body
from scripts.w1_recover_graphics_programs import translate

MAX_PRIVATE_SHADERLAB_BYTES = 16 * 1024 * 1024
MAX_HLSL_BYTES = 1024 * 1024
EXPECTED_TOTAL_PAIRS = 14
EXPECTED_TOTAL_STAGES = 28


def _physical(p):
    return not any(x.is_symlink() for x in (p, *p.parents))


def _pairs(manifest):
    if (not isinstance(manifest, dict) or
            manifest.get("original_subshader_pass_counts") != [PASSES] or
            manifest.get("original_passes") != PASSES or
            manifest.get("source_topology_attestation", {}).get(
                "authenticated_variant_stage_programs") != EXPECTED_TOTAL_STAGES):
        raise ValueError("Spectrum_authentic_source_topology_missing")
    stages = manifest.get("stages")
    if not isinstance(stages, list) or len(stages) != PASSES:
        raise ValueError("Spectrum_private_stage_manifest_incomplete")
    result = []
    for pi, row in enumerate(stages):
        if (not isinstance(row, dict) or row.get("pass_index") != pi or
                row.get("subshader") != 0 or
                not isinstance(row.get("variant_pairs"), list) or
                len(row["variant_pairs"]) != 2):
            raise ValueError("Spectrum_private_pass_or_keyword_variant_incomplete")
        for vi, pair in enumerate(row["variant_pairs"]):
            if (not isinstance(pair, dict) or pair.get("pair_index") != vi or
                    not isinstance(pair.get("stages"), dict) or
                    set(pair["stages"]) != {"1", "0"}):
                raise ValueError("Spectrum_private_stage_pair_invalid")
            result.append((pi, vi, pair))
    if len(result) != EXPECTED_TOTAL_PAIRS:
        raise ValueError("Spectrum_original_variant_pairs_incomplete")
    return result


def assemble(parsed, manifest, program_texts, state_texts):
    if (not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET or
            not isinstance(parsed.get("m_SubShaders"), list) or
            len(parsed["m_SubShaders"]) != 1):
        raise ValueError("Spectrum_source_shader_identity_changed")
    sub = parsed["m_SubShaders"][0]
    if (not isinstance(sub, dict) or
            not isinstance(sub.get("m_Passes"), list) or
            len(sub["m_Passes"]) != PASSES or
            type(sub.get("m_LOD")) is not int or
            not 0 <= sub["m_LOD"] <= 10000 or
            not isinstance(sub.get("m_Tags"), dict)):
        raise ValueError("Spectrum_source_subshader_topology_invalid")
    rows = _pairs(manifest)
    if (not isinstance(program_texts, dict) or
            set(program_texts) != {
                (p,v,s) for p, v, _ in rows for s in (0, 1)} or
            not isinstance(state_texts, list) or len(state_texts) != PASSES or
            any(type(state) is not str or not state.strip()
                for state in state_texts)):
        raise ValueError("Spectrum_private_source_or_state_pair_incomplete")
    properties, counts = serialize_properties(parsed)
    if (counts["original_authored_property_count"] != 6 or
            counts["original_authored_texture_property_count"] != 2):
        raise ValueError("Spectrum_original_property_schema_changed")
    prefix = ["Shader " + quoted(TARGET) + " {", properties, "SubShader {",
              "LOD " + str(sub["m_LOD"]), tags(sub["m_Tags"])]
    result = []
    for variant in (0, 1):
        lines = prefix[:]
        for pi in range(PASSES):
            vertex, fragment = (
                program_texts[(pi, variant, 1)],
                program_texts[(pi, variant, 0)],
            )
            if any(type(s) is not str or
                   not 0 < len(s.encode("utf-8")) <= MAX_HLSL_BYTES or
                   "\x00" in s for s in (vertex, fragment)):
                raise ValueError("Spectrum_private_original_stage_source_invalid")
            lines.extend([
                "Pass {", state_texts[pi], "HLSLPROGRAM",
                "#pragma target 5.0",
                "#pragma vertex main", "#pragma fragment main",
                stage_body(vertex, fragment), "ENDHLSL", "}",
            ])
        lines.append("}")
        for field, directive in (
                ("m_FallbackName", "Fallback"),
                ("m_CustomEditorName", "CustomEditor")):
            if parsed.get(field):
                lines.append(directive + " " + quoted(parsed[field]))
        lines.append("}")
        shader = "\n".join(lines) + "\n"
        if len(shader.encode("utf-8")) > MAX_PRIVATE_SHADERLAB_BYTES:
            raise ValueError("Spectrum_private_ShaderLab_oversized")
        coverage = pass_coverage(shader)
        if (coverage.get("pass_count") != PASSES or
                coverage.get("subshader_pass_counts") != [PASSES] or
                coverage.get("passes_with_complete_program") != PASSES or
                coverage.get("all_subshaders_programmed") is not True):
            raise ValueError("Spectrum_private_ShaderLab_pass_coverage_wrong")
        result.append(shader)
    return result, counts


def recover(source: Path, repo: Path, packet: Path, manifest_path: Path,
            state_dir: Path, private_dest: Path, safe_out: Path,
            *, translator=translate):
    source, repo, packet, manifest_path, state_dir, private_dest, safe_out = (
        Path(x).absolute() for x in (
            source, repo, packet, manifest_path, state_dir, private_dest, safe_out))
    if (not source.is_dir() or not repo.is_dir() or
            not packet.is_dir() or not state_dir.is_dir() or
            not manifest_path.is_file() or
            private_dest.exists() or safe_out.exists() or
            not private_dest.parent.is_dir() or
            not safe_out.parent.is_dir() or
            any(not _physical(x) for x in
                (source, repo, packet, manifest_path, state_dir, private_dest.parent, safe_out.parent)) or
            any(x.is_relative_to(repo) for x in
                (source, packet, state_dir, private_dest, safe_out)) or
            private_dest.is_relative_to(source) or
            safe_out.is_relative_to(source)):
        raise ValueError("Spectrum_private_ShaderLab_paths_unsafe")
    verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    _, _, tree, attestation = _selected_original(source)
    if (attestation.get("authenticated_original_passes") != PASSES or
            attestation.get("authenticated_variant_stage_programs") != EXPECTED_TOTAL_STAGES):
        raise ValueError("Spectrum_SHA_original_shader_unproven")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest_path.stat().st_size > 256 * 1024 or
            manifest.get("original_owner_sha256") != EXPECTED[OWNER][1]):
        raise ValueError("Spectrum_original_private_packet_unproven")
    validate_packet(packet, manifest)
    parsed = tree["m_ParsedForm"]
    state_texts = []
    from scripts.w1_depth_shaderlab import render_state
    for pi in range(PASSES):
        file = state_dir / f"source-pass-{pi:02d}.state.txt"
        if (not _physical(file) or not file.is_file() or
                not 0 < file.stat().st_size <= 65536):
            raise ValueError("Spectrum_source_original_pass_state_missing")
        raw = file.read_text(encoding="utf-8")
        expected = render_state(parsed["m_SubShaders"][0]["m_Passes"][pi]["m_State"],
                                allow_selective_color_mask=True)
        if raw != expected:
            raise ValueError("Spectrum_original_private_state_not_source_equal")
        state_texts.append(raw)
    rows = _pairs(manifest)
    all_sources = {}
    with tempfile.TemporaryDirectory(prefix="gt-spectrum-shaderlab-input-", dir=private_dest.parent) as scratch:
        temp = Path(scratch)
        cache = {}
        for p, v, pair in rows:
            for stage in (1, 0):
                source_stage = packet / f"s00-p{p:02d}" / f"pair{v:03d}-stage{stage}.dxbc"
                if not _physical(source_stage) or not source_stage.is_file():
                    raise ValueError("Spectrum_original_private_stage_missing")
                raw = source_stage.read_bytes()
                metadata = pair["stages"][str(stage)]
                digest = hashlib.sha256(raw).hexdigest()
                if (digest != metadata.get("sha256") or len(raw) != metadata.get("bytes")):
                    raise ValueError("Spectrum_original_private_stage_SHA_changed")
                key = (stage, digest)
                if key not in cache:
                    stage_folder = temp / f"original-{len(cache)}"
                    stage_folder.mkdir()
                    result = translator(raw, stage, stage_folder)
                    if (not isinstance(result, dict) or
                            result.get("dxbc_sha256") != digest or
                            result.get("stage") != stage or
                            result.get("vulkan11_valid") is not True or
                            result.get("hlsl_recovered") is not True or
                            result.get("roundtrip_vulkan11_valid") is not True):
                        raise ValueError("Spectrum_original_private_stage_translation_rejected")
                    file = stage_folder / "private.hlsl"
                    if not file.is_file() or file.is_symlink() or not 0 < file.stat().st_size <= MAX_HLSL_BYTES:
                        raise ValueError("Spectrum_original_private_HLSL_not_ready")
                    cache[key] = file.read_text(encoding="utf-8")
                all_sources[(p, v, stage)] = cache[key]
        candidates, counts = assemble(parsed, manifest, all_sources, state_texts)
        # Never upload source shader files, intermediate .hlsl, or full program
        # text. Move only two private isolated candidates to runner temp.
        private_dest.mkdir()
        try:
            for vi, shader in enumerate(candidates):
                path = private_dest / f"original-spectrum-7pass-variant-{vi}.shader"
                with path.open("x", encoding="utf-8") as out:
                    out.write(shader)
            result = {
                "schema":1,
                "status":"PRIVATE_ORIGINAL_SPECTRUM_TWO_SEVEN_PASS_SHADERLAB_CANDIDATES",
                "original_SHA_authenticated":True,
                "original_exact_pass_count":PASSES,
                "original_keyword_permutations":2,
                "private_seven_pass_ShaderLab_candidates":len(candidates),
                "private_shaderlab_structural_passes":len(candidates)*PASSES,
                "original_stage_variants_included":len(all_sources),
                "distinct_source_stage_translations":len(cache),
                **counts,
                "original_per_pass_render_states_source_equal":True,
                "original_all_keyword_variants_in_one_shader":False,
                "original_sampler_or_CB0_Material_binding_proven":False,
                "private_shaders_uploaded_or_published":False,
                "original_game_shader_installed":False,
                "Unity2021_import_or_Adreno_pixels_proven":False,
            }
            safe_out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            return result
        except BaseException:
            shutil.rmtree(private_dest, ignore_errors=True)
            raise


def main():
    a = argparse.ArgumentParser(description=__doc__)
    for key in ("source", "repo", "packet", "manifest", "states", "private-dest", "out"):
        a.add_argument("--"+key, type=Path, required=True)
    x=a.parse_args()
    try:
        result=recover(x.source,x.repo,x.packet,x.manifest,x.states,x.private_dest,x.out)
    except BaseException as exc:
        result={"status":"INCONCLUSIVE", "safe_error_type":type(exc).__name__,
                "private_shaders_uploaded_or_published":False,
                "original_game_shader_installed":False,
                "Unity2021_import_or_Adreno_pixels_proven":False}
    print("GT_SPECTRUM_SEVEN_PASS_PRIVATE_SHADERLAB_SAFE " + json.dumps(result, sort_keys=True))
    return 0 if result["status"]=="PRIVATE_ORIGINAL_SPECTRUM_TWO_SEVEN_PASS_SHADERLAB_CANDIDATES" else 2


if __name__=="__main__":
    raise SystemExit(main())
