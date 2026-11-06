"""T2: original Foam PRIVATE ShaderLab two-pass VS->FS numerical stage-I/O gate.

Unlike 4/4 independent glslang+spirv-val stage success, this checks actual
SPIRV-Cross-reflected VS outputs against PS inputs in *each* rebuilt pass.
Original ShaderLab/HLSL, SPIR-V, varying names/locations/types remain private.
No Unity importer, CB0/texture upload, frame color or Adreno claim is made.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from scripts.b20_private_foam_packet import _physical
from scripts.t2_foam_candidate_embedded_validation import (
    extract_embedded_programs, _invoke, LIMIT_BYTES,
)
from scripts.t2_foam_original_pair_compile import MAX_SPV

MAX_REFLECTION_BYTES = 1024 * 1024
MAX_INTERFACE_ROWS = 64
# Scalar/vector-only signatures. Do not treat a source struct name as a
# structural match merely because a translated name happens to be identical.
NUMERIC_TYPE = re.compile(
    r"(?:float|double|half|int|uint|bool|"
    r"(?:[biud]?vec|f16vec)[234])\Z"
)
STAGE_ORDER = ((0, 1), (0, 0), (1, 1), (1, 0))


def interface_rows(reflection, role, stage):
    """Return PRIVATE unique (location,component)->(type,array) varyings."""
    if not isinstance(reflection, dict):
        raise ValueError("SPIRV_reflection_unrecognized")
    entries = reflection.get("entryPoints")
    if (not isinstance(entries, list) or len(entries) != 1
            or not isinstance(entries[0], dict)
            or entries[0].get("mode") != stage):
        raise ValueError("original_compiled_stage_entry_mismatch")
    rows = reflection.get(role, [])
    if not isinstance(rows, list) or len(rows) > MAX_INTERFACE_ROWS:
        raise ValueError("original_compiled_interface_unbounded")
    mapped = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("malformed_compiled_varying")
        if "location" not in row:
            # SPIR-V built-ins legitimately lack a numerical Location; they
            # cannot prove user-varying cross-stage compatibility.
            if "builtin" in row:
                continue
            raise ValueError("unlocated_nonbuiltin_interface")
        loc = row["location"]
        comp = row.get("component", 0)
        ty = row.get("type")
        if (type(loc) is not int or type(comp) is not int
                or not 0 <= loc <= 1023 or not 0 <= comp <= 3
                or not isinstance(ty, str) or not NUMERIC_TYPE.fullmatch(ty)
                or "builtin" in row or "index" in row):
            raise ValueError("unsupported_compiled_varying_signature")
        arr = row.get("array", [])
        if (not isinstance(arr, list) or len(arr) > 2
                or any(type(x) is not int or not 1 <= x <= 4096 for x in arr)):
            raise ValueError("ambiguous_compiled_varying_array")
        key = (loc, comp)
        if key in mapped:
            raise ValueError("duplicate_compiled_varying_location")
        mapped[key] = (ty, tuple(arr))
    return mapped


def compare_varying_abi(vertex, fragment):
    """All PS location/type/array requirements must be produced by VS."""
    vs = interface_rows(vertex, "outputs", "vert")
    fs = interface_rows(fragment, "inputs", "frag")
    missing = sum(k not in vs for k in fs)
    wrong = sum(k in vs and vs[k] != sig for k, sig in fs.items())
    matched = len(fs) - missing - wrong
    return {
        "vertex_user_varyings": len(vs),
        "fragment_user_varyings": len(fs),
        "fragment_varyings_location_type_matched": matched,
        "fragment_varyings_missing_vertex_output": missing,
        "fragment_varyings_type_or_array_mismatch": wrong,
        "vertex_outputs_not_consumed_by_fragment": sum(k not in fs for k in vs),
        "numerical_location_type_interface_compatible": missing == 0 and wrong == 0,
        "empty_fragment_varying_interface": len(fs) == 0,
    }


def reflect_stage(path):
    """Full reflective data stay in PRIVATE memory, never stdout/log."""
    try:
        r = subprocess.run(["spirv-cross", str(path), "--reflect"],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise ValueError("private_spirv_cross_failed") from None
    if r.returncode or not 0 < len(r.stdout) <= MAX_REFLECTION_BYTES:
        raise ValueError("private_reflection_missing_or_unbounded")
    try:
        return json.loads(r.stdout)
    except (ValueError, UnicodeDecodeError):
        raise ValueError("private_reflection_json_invalid") from None


def verify_embedded_abi(candidate, scratch, *, invoke=_invoke, reflect=reflect_stage):
    candidate, scratch = Path(candidate).absolute(), Path(scratch).absolute()
    if (not candidate.is_file() or not _physical(candidate)
            or not 0 < candidate.stat().st_size <= LIMIT_BYTES
            or not scratch.is_dir() or not _physical(scratch)
            or scratch.is_relative_to(candidate)):
        raise ValueError("original_private_candidate_or_scratch_invalid")
    bodies = extract_embedded_programs(candidate.read_text(encoding="utf-8"))
    reflected = {}
    with tempfile.TemporaryDirectory(prefix="t2-foam-private-varyings-", dir=scratch) as scratch_dir:
        scratch_dir = Path(scratch_dir)
        for pass_id, program in enumerate(bodies):
            hlsl = scratch_dir / ("pass%d-private.hlsl" % pass_id)
            hlsl.write_text(program, encoding="utf-8")
            for stage_id, macro, spv_kind in ((1, "VERTEX", "vert"), (0, "FRAGMENT", "frag")):
                output = scratch_dir / ("pass%d-stage%d-private.spv" % (pass_id, stage_id))
                args = ["glslangValidator", "-V", "-D",
                        "-DSHADER_STAGE_" + macro + "=1",
                        "-S", spv_kind, "-e", "main", "-o", str(output), str(hlsl)]
                if not invoke(args):
                    return {"status": "blocked_compilation_of_embedded_original_stage",
                            "pass": pass_id, "stage_code": stage_id,
                            "private_source_published": False}
                if (not output.is_file() or not _physical(output)
                        or not 20 <= output.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1", str(output)])):
                    return {"status": "blocked_spirv_validation",
                            "pass": pass_id, "stage_code": stage_id,
                            "private_source_published": False}
                reflected[(pass_id, stage_id)] = reflect(output)
        results = [compare_varying_abi(reflected[(p, 1)], reflected[(p, 0)])
                   for p in range(2)]
    compatible = all(row["numerical_location_type_interface_compatible"] for row in results)
    return {
        "status": ("source_original_embedded_two_pass_numeric_varyings_compatible"
                   if compatible else "source_original_embedded_pass_varying_abi_mismatch"),
        "source_derived_embedded_shaders": 2,
        "compiled_stage_variants": len(reflected),
        "per_pass_user_varying_counts": results,
        "all_fragment_inputs_have_matching_vertex_outputs": compatible,
        "zero_fragment_varying_inputs_in_both_passes": all(
            x["empty_fragment_varying_interface"] for x in results
        ),
        "unity_shaderlab_actual_import_verified": False,
        "original_semantics_interpolation_and_primitive_topology_verified": False,
        "runtime_cb0_texture_sampler_or_material_upload_verified": False,
        "actual_adreno_or_device_pixels_verified": False,
        "private_source_published": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    output = args.out.absolute()
    try:
        if (not output.parent.is_dir() or not _physical(output)
                or output.exists()
                or output.is_relative_to(args.candidate.absolute())):
            raise ValueError("unsafe_numeric_report_output")
        status = verify_embedded_abi(args.candidate, args.scratch)
        # Report an authentic mismatch as a successful, safely measured
        # diagnostic. Do not hide the mismatch by claiming water readiness.
        code = 0 if status["status"].startswith("source_original_embedded_") else 2
    except BaseException as exc:
        status = {"status": "blocked_source_original_stage_io_scan",
                  "failure_type": type(exc).__name__,
                  "private_source_published": False}
        code = 2
    if output.parent.is_dir() and _physical(output) and not output.exists():
        output.write_text(json.dumps(status, sort_keys=True) + "\n", encoding="utf-8")
    print("T2_FOAM_VS_PS_IO_SAFE " + json.dumps(status, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
