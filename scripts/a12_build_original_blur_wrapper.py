"""Privately reconstruct exact original two-pass Subsurface Blur ShaderLab from DXBC.

Depends on already authenticated W1 original bytecode/ShaderLab primitives, but
changes no W1 source. No original program text, resource names or ShaderLab
output is committed, logged, attached or installed by this CPU-only experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from scripts.a12_probe_original_blur_passes import (
    TARGET, SHADER_OWNERS, original_shader, inspect_shader,
)
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate, command
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.w1_rebind_depth_resources import rebind, signature_inputs
from scripts.w1_depth_shaderlab import (
    decode_empty_parameters, render_state, quoted, tags, stage_body,
)
from scripts.run_original_dxbc_translation_probe import version_tokens

OBJECT_SHA256 = "c9341848367eaedb12e551ce9061b1eea728f54f2069ef1a3c12c4a4a2e9bb52"
PARSED_SHA256 = "865e5529986469f18fd3158612f925647599e8b5126187be0c87d490ff6d2aa3"


def wrapper(parsed, stage_sources):
    """Only exact original 1-subshader, 2-pass and empty-props layout permitted."""
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Blur ShaderLab original name changed")
    if parsed.get("m_PropInfo", {}).get("m_Props"):
        raise ValueError("Nonempty original property block needs exact serializer")
    subs = parsed.get("m_SubShaders")
    if not isinstance(subs, list) or [len(s["m_Passes"]) for s in subs] != [2]:
        raise ValueError("Original Blur two-pass topology changed")
    if set(stage_sources) != {(0, 0), (0, 1)}:
        raise ValueError("Missing original Blur pass stage pairs")
    lines = ["Shader " + quoted(TARGET) + " {", "Properties {}"]
    for si, sub in enumerate(subs):
        lines.extend(["SubShader {", "LOD " + str(sub["m_LOD"]), tags(sub["m_Tags"])])
        for pi, p in enumerate(sub["m_Passes"]):
            if p["m_Type"] != 0:
                raise ValueError("Unexpected Blur pass type")
            vertex, fragment, shader_model = stage_sources[(si, pi)]
            if shader_model not in ("4.0", "4.1", "5.0", "5.1"):
                raise ValueError("Unsupported original Shader Model for Blur")
            lines.extend(["Pass {", render_state(p["m_State"]), "HLSLPROGRAM",
                          "#pragma target " + shader_model,
                          "#pragma vertex main", "#pragma fragment main",
                          stage_body(vertex, fragment), "ENDHLSL", "}"])
        lines.append("}")
    if parsed.get("m_FallbackName"):
        lines.append("Fallback " + quoted(parsed["m_FallbackName"]))
    if parsed.get("m_CustomEditorName"):
        lines.append("CustomEditor " + quoted(parsed["m_CustomEditorName"]))
    lines.append("}")
    return "\n".join(lines) + "\n"


def build(root, repo, out):
    report = {
        "status": "incomplete",
        "genuine_original_source_pinned": False,
        "private_shaderlab_constructed": False,
        "shaderlab_installed": False,
        "original_meta_or_guid_modified": False,
        "numeric_or_visual_equivalence": False,
        "unity_or_android_executed": False,
        "water_or_fft_build_ready": False,
    }
    phase = "source"
    subphase = "source_sha"
    active_pass = None
    active_stage = None
    try:
        owner, object_sha, tree = original_shader(root, repo)
        if object_sha != OBJECT_SHA256:
            raise ValueError("Original Subsurface Blur Shader object fingerprint drift")
        parsed = tree["m_ParsedForm"]
        parsed_sha = hashlib.sha256(json.dumps(
            parsed, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")).hexdigest()
        if parsed_sha != PARSED_SHA256:
            raise ValueError("Original parsed shader topology fingerprint drift")
        report["genuine_original_source_pinned"] = True
        report["original_object_sha256"] = object_sha
        report["original_parsed_form_sha256"] = parsed_sha
        subphase = "source_platform_tables"
        tables = [(p, records(s)) for p, s in decoded_platforms(tree) if p == 4]
        if len(tables) != 1:
            raise ValueError("Original D3D11 blur platform table missing or ambiguous")
        entries = tables[0][1]
        subphase = "source_pass_linkage"
        graph = inspect_shader(parsed, entries)
        report["original_passes"] = graph["original_pass_count"]
        report["original_stage_programs"] = graph["linked_stage_programs"]
        if (graph["original_pass_count"] != 2 or graph["unpaired_original_passes"] or
            graph["non_normal_passes"] or graph["parameter_index_layout_unresolved"] or
            graph["stages_with_keyword_permutations"]):
            raise ValueError("Original Blur graph requires unsupported explicit recovery")

        phase = "stages"
        with tempfile.TemporaryDirectory(prefix="a12-blur-private-hlsl-") as temp:
            folder = Path(temp)
            generated = {}
            stages = []
            for si, sub in enumerate(parsed["m_SubShaders"]):
                for pi, p in enumerate(sub["m_Passes"]):
                    active_pass = pi
                    pair = {}
                    permutations = []
                    versions = []
                    for field, stage in (("progVertex", 1), ("progFragment", 0)):
                        active_stage = stage
                        subphase = "original_stage_variant"
                        program = p[field]
                        variants = stage_variants(program)
                        if len(variants) != 1:
                            raise ValueError("Original Blur stage requires multiple variant recovery")
                        bucket, vi, meta = variants[0]
                        if meta.get("m_KeywordIndices"):
                            raise ValueError("Original Blur keyword permutation unresolved")
                        permutations.append((bucket, variant_key(meta)))
                        subphase = "original_parameter_index"
                        param_table = program["m_ParameterBlobIndices"]
                        if bucket is None or len(param_table) != len(program["m_PlayerSubPrograms"]):
                            raise ValueError("Original Blur parameter table layout unsupported")
                        index = param_table[bucket][vi]
                        if type(index) is not int or not 0 <= index < len(entries):
                            raise ValueError("Original Blur parameter table index invalid")
                        seg, raw_params = entries[index]
                        subphase = "original_parameter_payload"
                        report["last_original_parameter_size"] = len(raw_params)
                        report["last_original_parameter_sha256"] = hashlib.sha256(raw_params).hexdigest()
                        parameter = decode_empty_parameters(raw_params)
                        subphase = "original_stage_bytecode"
                        original, link = linked_program(meta, entries, stage)
                        versions.append(version_tokens(original)[0]["shader_model"])
                        private = folder / ("pass%d-stage%d" % (pi, stage))
                        private.mkdir()
                        subphase = "private_dxbc_translation"
                        translated = translate(original, stage, private)
                        if not translated["hlsl_recovered"] or not translated["roundtrip_vulkan11_valid"]:
                            raise ValueError("Original Blur stage translation did not validate")
                        subphase = "serialized_resource_rebinding"
                        rebound, binding = rebind(
                            (private / "private.hlsl").read_text(), program, p["m_NameIndices"],
                            original_inputs=signature_inputs(original) if stage == 1 else None,
                        )
                        pair[stage] = rebound
                        stages.append({
                            "subshader": si, "pass_index": pi, "stage_code": stage,
                            "original_dxbc_sha256": translated["dxbc_sha256"],
                            "private_hlsl_sha256": hashlib.sha256(rebound.encode()).hexdigest(),
                            "original_parameter_sha256": hashlib.sha256(raw_params).hexdigest(),
                            "original_parameter_bytes": len(raw_params),
                            "original_parameter_segment": seg,
                            "parameters_empty": parameter["overrides_empty"],
                            "original_blob_index": link["blob_index"],
                            "bindings": binding,
                            "source_private": True,
                            "vulkan11_valid": translated["vulkan11_valid"],
                            "roundtrip_vulkan11_valid": translated["roundtrip_vulkan11_valid"],
                        })
                    subphase = "paired_original_stage_permutation"
                    active_stage = None
                    if permutations[0] != permutations[1]:
                        raise ValueError("Original Blur paired stage permutation mismatch")
                    generated[(si, pi)] = (
                        pair[1], pair[0], ".".join(map(str, max(versions)))
                    )
                    combined = folder / ("pass%d-combined.hlsl" % pi)
                    combined.write_text(stage_body(pair[1], pair[0]))
                    for stage, macro in ((1, "VERTEX"), (0, "FRAGMENT")):
                        active_stage = stage
                        subphase = "rebuilt_stage_vulkan_validation"
                        output = folder / ("pass%d-stage%d-validated.spv" % (pi, stage))
                        valid = command([
                            "glslangValidator", "-V", "-D", "-DSHADER_STAGE_" + macro + "=1",
                            "-S", "vert" if stage == 1 else "frag",
                            "-e", "main", "-o", str(output), str(combined)
                        ]) and command(["spirv-val", "--target-env", "vulkan1.1", str(output)])
                        stages[-2 if stage == 1 else -1]["wrapped_stage_vulkan11_valid"] = valid
                    if not all(r.get("wrapped_stage_vulkan11_valid") for r in stages[-2:]):
                        raise ValueError("Original Blur rebound stage failed Vulkan1.1 validation")
            phase = "shaderlab"
            active_stage = None
            active_pass = None
            subphase = "original_shaderlab_state"
            result = wrapper(parsed, generated)
            report.update({
                "status": "private_shaderlab_recovered",
                "private_shaderlab_constructed": True,
                "shaderlab_sha256": hashlib.sha256(result.encode()).hexdigest(),
                "shaderlab_bytes": len(result.encode()),
                "preserved_passes": len(generated),
                "stages": stages,
                "no_proprietary_source_published": True,
            })
    except BaseException as exc:
        # Only diagnostic phase/type; never disclose private code or original
        # property values from arbitrary decoder exceptions.
        report["status"] = "blocked"
        report["failure_phase"] = phase
        report["failure_subphase"] = subphase
        report["failure_original_pass_index"] = active_pass
        report["failure_stage_code"] = active_stage
        report["failure_type"] = type(exc).__name__
        safe = json.dumps(report, sort_keys=True)
        out.write_text(safe + "\n", encoding="utf-8")
        print("RAFT_A12_BLUR_WRAPPER " + safe)
        raise ValueError("Original Blur private wrapper incomplete at phase " + phase) from None
    safe = json.dumps(report, sort_keys=True)
    out.write_text(safe + "\n", encoding="utf-8")
    print("RAFT_A12_BLUR_WRAPPER " + safe)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    build(args.source, args.repo, args.out)
