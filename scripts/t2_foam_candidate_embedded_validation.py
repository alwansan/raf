"""T2: compile HLSLPROGRAM bodies extracted from the *assembled* Foam ShaderLab.

Input must be private source-authentic candidate in runner scratch. No shader
code, identifiers, compiler stdout/stderr, SPIR-V or named buffers are exposed.
Vulkan 1.1 validation is NOT Unity import, CB0 upload, or Adreno pixel proof.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from scripts.b20_private_foam_packet import _physical
from scripts.t2_foam_original_pair_compile import MAX_SPV
from scripts.b49_shaderlab_pass_contract import pass_coverage

LIMIT_BYTES = 4 * 1024 * 1024
BEGIN = re.compile(r"(?m)^[ \t]*HLSLPROGRAM[ \t]*\r?$")
END = re.compile(r"(?m)^[ \t]*ENDHLSL[ \t]*\r?$")
TARGET = re.compile(r"(?m)^[ \t]*#pragma[ \t]+target[ \t]+([45]\.[01])[ \t]*\r?$")
VERTEX = re.compile(r"(?m)^[ \t]*#pragma[ \t]+vertex[ \t]+main[ \t]*\r?$")
FRAGMENT = re.compile(r"(?m)^[ \t]*#pragma[ \t]+fragment[ \t]+main[ \t]*\r?$")
ORDER = ((0, 1), (0, 0), (1, 1), (1, 0))


def extract_embedded_programs(candidate):
    """Fail closed on unexpected tokens, unbalanced scopes, or duplicate pragmas."""
    if (not isinstance(candidate, str)
            or not 0 < len(candidate.encode("utf-8")) <= LIMIT_BYTES
            or "\0" in candidate):
        raise ValueError("candidate_invalid_or_unbounded")
    coverage = pass_coverage(candidate)
    if (coverage["pass_count"] != 2 or coverage["passes_with_complete_program"] != 2
            or coverage["subshader_pass_counts"] != [2]
            or not coverage["all_subshaders_programmed"]
            or not coverage["pass_braces_balanced"]):
        raise ValueError("candidate_not_two_complete_subshader_passes")
    starts, stops = list(BEGIN.finditer(candidate)), list(END.finditer(candidate))
    if len(starts) != 2 or len(stops) != 2:
        raise ValueError("embedded_program_boundary_not_two")
    programs = []
    for index in range(2):
        a, b = starts[index], stops[index]
        if a.end() >= b.start() or (index and stops[index - 1].end() >= a.start()):
            raise ValueError("embedded_program_overlap_or_reorder")
        code = candidate[a.end():b.start()].strip()
        if not 0 < len(code.encode("utf-8")) <= 2 * 1024 * 1024 + 4096:
            raise ValueError("embedded_program_body_size")
        targets = TARGET.findall(code)
        if len(targets) != 1 or len(VERTEX.findall(code)) != 1 or len(FRAGMENT.findall(code)) != 1:
            raise ValueError("embedded_original_stage_pragma_unresolved")
        # Source-verified original models should stay per-pass; do not infer
        # them from stage order or fabricate constants in this validator.
        if "#if defined(SHADER_STAGE_VERTEX)" not in code or (
                "#elif defined(SHADER_STAGE_FRAGMENT)" not in code):
            raise ValueError("embedded_stage_select_missing")
        programs.append(code)
    return tuple(programs)


def _invoke(args):
    try:
        return subprocess.run(args, stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              timeout=100, check=False).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def compile_embedded(candidate, scratch, invoke=_invoke):
    candidate, scratch = Path(candidate).absolute(), Path(scratch).absolute()
    if (not candidate.is_file() or not _physical(candidate)
            or candidate.stat().st_size > LIMIT_BYTES or
            not scratch.is_dir() or not _physical(scratch)
            or scratch.is_relative_to(candidate)):
        raise ValueError("private_candidate_or_scratch_invalid")
    bodies = extract_embedded_programs(candidate.read_text(encoding="utf-8"))
    validated = []
    with tempfile.TemporaryDirectory(prefix="t2-foam-embedded-", dir=scratch) as directory:
        for pass_id, body in enumerate(bodies):
            hlsl = Path(directory) / ("pass%d-private.hlsl" % pass_id)
            hlsl.write_text(body, encoding="utf-8")
            for stage, macro in ((1, "VERTEX"), (0, "FRAGMENT")):
                spv = Path(directory) / ("pass%d-stage%d.spv" % (pass_id, stage))
                if not invoke(["glslangValidator", "-V", "-D",
                               "-DSHADER_STAGE_" + macro + "=1",
                               "-S", "vert" if stage == 1 else "frag",
                               "-e", "main", "-o", str(spv), str(hlsl)]):
                    return {"status": "embedded_stage_compilation_blocked",
                            "stage_count_validated": len(validated),
                            "failed_pass": pass_id, "failed_stage": stage,
                            "private_source_published": False}
                if (not spv.is_file() or not _physical(spv)
                        or not 20 <= spv.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1",
                                       str(spv)])):
                    return {"status": "embedded_spirv_validation_blocked",
                            "stage_count_validated": len(validated),
                            "failed_pass": pass_id, "failed_stage": stage,
                            "private_source_published": False}
                validated.append((pass_id, stage))
    return {
        "status": "original_private_candidate_embedded_four_stages_vulkan11_valid",
        "complete_embedded_original_pass_programs": len(bodies),
        "embedded_stage_variants_compiled_and_validated": len(validated),
        "original_stage_order_preserved": tuple(validated) == ORDER,
        "verified_programs_extracted_from_completed_private_ShaderLab": True,
        "unity_2021_shaderlab_import_verified": False,
        "runtime_cb0_and_material_texture_sampler_upload_verified": False,
        "original_gpu_or_android_pixels_verified": False,
        "private_source_published": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    out = args.out.absolute()
    try:
        if (not out.parent.is_dir() or not _physical(out)
                or out.exists() or out.is_relative_to(args.candidate.absolute())):
            raise ValueError("unsafe_aggregate_report_path")
        safe = compile_embedded(args.candidate, args.scratch)
        code = 0 if safe["status"] == "original_private_candidate_embedded_four_stages_vulkan11_valid" else 2
    except BaseException as exc:
        safe = {"status": "blocked_original_embedded_shaderlab_validation",
                "failure_type": type(exc).__name__, "private_source_published": False}
        code = 2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(safe, sort_keys=True) + "\n", encoding="utf-8")
    print("T2_FOAM_EMBEDDED_SHADERLAB_SAFE " + json.dumps(safe, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
