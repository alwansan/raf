"""Compare authentic FFT compute SPIR-V vs its HLSL roundtrip on CPU Vulkan.

Only deterministic RGBA32Float input images are exercised. Original DXBC,
temporary SPIR-V/HLSL, actual shader names, output pixel arrays and raw tool
diagnostics remain inside TemporaryDirectory and are never emitted or uploaded.
Vulkan lavapipe execution is neither an Android GPU test nor a Unity water fix.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)

MARKER = "RAFT_A1_VULKAN_DIFF "
KEYS = (
    "cpu_software_vulkan", "rgba32f_linear_only",
    "extent_width", "extent_height", "original_written_pixels",
    "roundtrip_written_pixels", "write_coverage_mismatch_pixels",
    "nonfinite_components", "max_abs_difference",
    "relative_l2_difference", "within_selected_tolerance",
    "synthetic_canary_verified", "unity_gpu_or_android_device_verified",
)
SELECTED_WIDTH = 1024
SELECTED_HEIGHT = 1024


def parse_private_numeric_result(output):
    if type(output) is not str or len(output) > 8192:
        raise ValueError("Missing or oversized private Vulkan result")
    lines = [line for line in output.splitlines() if line.startswith(MARKER)]
    if len(lines) != 1:
        raise ValueError("Ambiguous private Vulkan result")
    report = json.loads(lines[0][len(MARKER):], parse_constant=lambda _: (_ for _ in ()).throw(
        ValueError("Nonfinite private Vulkan JSON value")))
    if type(report) is not dict or set(report) != set(KEYS):
        raise ValueError("Unexpected Vulkan result schema")
    for flag in ("cpu_software_vulkan", "rgba32f_linear_only",
                 "within_selected_tolerance", "synthetic_canary_verified",
                 "unity_gpu_or_android_device_verified"):
        if type(report[flag]) is not bool:
            raise ValueError("Invalid Vulkan boolean")
    if (not report["cpu_software_vulkan"] or not report["rgba32f_linear_only"]
            or report["unity_gpu_or_android_device_verified"]):
        raise ValueError("Unsupported or false Vulkan platform claim")
    for field in ("extent_width", "extent_height", "original_written_pixels",
                  "roundtrip_written_pixels", "write_coverage_mismatch_pixels",
                  "nonfinite_components"):
        if type(report[field]) is not int or report[field] < 0:
            raise ValueError("Invalid Vulkan pixel census")
    if (report["extent_width"] not in (8, SELECTED_WIDTH)
            or report["extent_height"] not in (1, SELECTED_HEIGHT)):
        raise ValueError("Unexpected Vulkan extent")
    pixels = report["extent_width"] * report["extent_height"]
    if (not 0 < report["original_written_pixels"] <= pixels
            or not 0 < report["roundtrip_written_pixels"] <= pixels
            or report["write_coverage_mismatch_pixels"] > pixels):
        raise ValueError("Missing or impossible Vulkan image writes")
    for field in ("max_abs_difference", "relative_l2_difference"):
        number = report[field]
        if type(number) not in (int, float) or not math.isfinite(number) or number < 0:
            raise ValueError("Invalid Vulkan numeric metric")
    if report["within_selected_tolerance"] and (
            report["write_coverage_mismatch_pixels"] != 0 or
            report["nonfinite_components"] != 0 or
            report["max_abs_difference"] > 1e-4 or
            report["relative_l2_difference"] > 1e-5):
        raise ValueError("Inconsistent declared Vulkan tolerance")
    return report


def private_command(command, timeout=35):
    """No stderr or private file contents from compiler may escape to reports."""
    try:
        process = subprocess.run(command, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout,
                                 check=False)
    except (OSError, subprocess.TimeoutExpired) as ex:
        raise ValueError("Private shader tool unavailable or timed out") from ex
    if process.returncode != 0:
        raise ValueError("Private shader tool failed with returncode " +
                         str(process.returncode))
    return process.stdout


def analyze(root, runner):
    if not runner.is_file() or runner.is_symlink():
        raise ValueError("Private Vulkan runner missing or unsafe")
    auth = verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    if auth["authenticated_owners"] != 1:
        raise ValueError("Original source was not SHA-authenticated")
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objs = [obj for obj in env.file.objects.values()
            if obj.type.name == "ComputeShader" and int(obj.path_id) == PATH_ID]
    if len(objs) != 1:
        raise ValueError("Authentic original FFT ComputeShader unavailable")
    raw = objs[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("FFT object SHA256 changed")
    original_programs = scan_blob(raw)["valid_dxbc_containers"]
    if len(original_programs) != EXPECTED_CONTAINERS:
        raise ValueError("Authentic FFT program count changed")
    rows = []
    with tempfile.TemporaryDirectory(prefix="raft-private-a1-fft-vulkan-") as directory:
        temp = Path(directory)
        for i, item in enumerate(original_programs):
            position = item["offset_in_original_object"]
            binary = raw[position:position + item["bytes"]]
            if len(binary) != item["bytes"] or hashlib.sha256(binary).hexdigest() != item["binary_sha256"]:
                raise ValueError("Private DXBC source SHA mismatch")
            source = temp / "private_original.dxbc"
            translated = temp / "private_original.spv"
            hlsl = temp / "private_roundtrip.hlsl"
            recompiled = temp / "private_roundtrip.spv"
            source.write_bytes(binary)
            row = {"compiled_program_slot_not_unity_kernel_index": i,
                   "status": "not_executed", "numerical_equivalence_proven": False,
                   "android_gpu_executed": False}
            try:
                private_command(["vkd3d-compiler", "-x", "dxbc-tpf", "-b",
                                 "spirv-binary", "-o", str(translated),
                                 str(source)], timeout=30)
                private_command(["spirv-val", "--target-env", "vulkan1.1",
                                 str(translated)], timeout=20)
                private_command(["spirv-cross", str(translated), "--hlsl",
                                 "--shader-model", "50", "--output", str(hlsl)],
                                timeout=30)
                private_command(["glslangValidator", "-V", "-D", "-S", "comp",
                                 "-e", "main", "-o", str(recompiled), str(hlsl)],
                                timeout=30)
                private_command(["spirv-val", "--target-env", "vulkan1.1",
                                 str(recompiled)], timeout=20)
                output = private_command([str(runner), str(translated),
                                          str(recompiled), str(SELECTED_WIDTH),
                                          str(SELECTED_HEIGHT)], timeout=90)
                parsed = parse_private_numeric_result(output.decode("utf-8", errors="strict"))
                row.update({"status": "executed_on_cpu_vulkan",
                            "same_rgba32f_workload_tolerance": parsed["within_selected_tolerance"],
                            "original_written_pixels": parsed["original_written_pixels"],
                            "roundtrip_written_pixels": parsed["roundtrip_written_pixels"],
                            "coverage_mismatch_pixels": parsed["write_coverage_mismatch_pixels"],
                            "nonfinite_components": parsed["nonfinite_components"],
                            "max_abs_difference": parsed["max_abs_difference"],
                            "relative_l2_difference": parsed["relative_l2_difference"]})
            except (UnicodeError, ValueError) as exc:
                # Never emit original shaders, filename paths, GLSL text or tool stderr.
                row.update({"status": "inconclusive_execution_or_translation",
                            "failure_category": ("invalid_executor_result" if
                                "Vulkan" in str(exc) else "private_tool_or_pipeline")})
            rows.append(row)
            for p in (source, translated, hlsl, recompiled):
                p.unlink(missing_ok=True)
    executed = [row for row in rows if row["status"] == "executed_on_cpu_vulkan"]
    return {
        "authenticated_original_object_sha256": ORIGINAL_OBJECT_SHA256,
        "original_lfs_owner_count": 1,
        "original_source_bytes_verified": EXPECTED[OWNER][0],
        "compiled_programs_checked": len(rows),
        "software_vulkan_executed_pairs": len(executed),
        "software_vulkan_inconclusive_pairs": len(rows)-len(executed),
        "equal_within_single_rgba32f_workload": sum(
            r["same_rgba32f_workload_tolerance"] for r in executed),
        "different_within_single_rgba32f_workload": sum(
            not r["same_rgba32f_workload_tolerance"] for r in executed),
        "software_vulkan_is_adreno_or_unity_proof": False,
        "other_original_formats_or_all_inputs_proven": False,
        "original_private_shader_bytes_exported": False,
        "programs": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--runner", required=True, type=Path)
    args = parser.parse_args()
    result = analyze(args.source, args.runner)
    print("RAFT_A1_AUTHENTIC_FFT_SOFTWARE_VK " + json.dumps(result, sort_keys=True))
    if result["software_vulkan_executed_pairs"] == 0:
        raise SystemExit("No authentic FFT software Vulkan program executed; test inconclusive")


if __name__ == "__main__":
    main()
