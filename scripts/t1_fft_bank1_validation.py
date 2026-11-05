"""T1 bank1 original FFT Vulkan validation: bounded failure classification only.

Runs the *same* pinned original shader program twice (as original/comparator)
with Khronos validation enabled. Historical bank1 failures are never converted
to positive shader/Unity evidence. Private shader bytes and driver text stay
inside the ephemeral runner; reports contain sanitized counters only.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from scripts.probe_original_fft_two_pass_software_vulkan import (
    parse_two_pass_result, validate_original_compiled_pairs,
)
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

CASES = ((10, "baseline"), (10, "swap_second"), (18, "baseline"),
         (18, "swap_second"))
MAX_CAPTURE = 131072
MAX_SECONDS = 120


def classify_process(returncode, stdout, stderr, *, timed_out=False):
    """No driver messages, pixel arrays, shader names or program bytes escape."""
    if not isinstance(stdout, bytes) or not isinstance(stderr, bytes):
        raise ValueError("Require binary bounded temporary captures")
    if len(stdout) > MAX_CAPTURE or len(stderr) > MAX_CAPTURE:
        raise ValueError("Unbounded driver report: do not disclose contents")
    text = stderr.decode("utf-8", "replace")
    # Only counts, not private driver trace or VUID/identifier text.
    errors = len(re.findall(r"Validation Error:", text, flags=re.I))
    warnings = len(re.findall(r"Validation Warning:", text, flags=re.I))
    vuids = len(re.findall(r"\bVUID-[A-Za-z0-9_-]+", text))
    layer_missing = "VK_ERROR_LAYER_NOT_PRESENT" in text
    if timed_out:
        kind = "timeout"
    elif returncode == -11 or returncode == 139:
        kind = "segmentation_fault"
    elif returncode != 0:
        kind = "nonzero"
    else:
        kind = "exit_zero"
    record = {"outcome": kind, "validation_error_markers": errors,
              "validation_warning_markers": warnings, "vuid_markers": vuids,
              "layer_missing": layer_missing, "numeric_report_valid": False,
              "same_source_comparator": None,
              "within_selected_tolerance": None,
              "original_written_pixels_nonzero": None,
              "nonfinite_components_zero": None}
    if returncode == 0 and not timed_out:
        output = stdout.decode("utf-8", "replace")
        try:
            parsed = parse_two_pass_result(output)
        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            pass
        else:
            record.update({
                "numeric_report_valid": True,
                "same_source_comparator": bool(parsed["within_selected_tolerance"]),
                "within_selected_tolerance": bool(parsed["within_selected_tolerance"]),
                "original_written_pixels_nonzero": parsed["original_written_pixels"] > 0,
                "nonfinite_components_zero": parsed["nonfinite_components"] == 0,
            })
    return record


def run_host(args, env):
    if not Path(args[0]).is_file() or Path(args[0]).is_symlink():
        raise ValueError("Original FFT runner not a regular file")
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            result = subprocess.run(
                args, env=env, stdout=stdout, stderr=stderr, timeout=MAX_SECONDS,
                check=False,
            )
            timed_out = False
            rc = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            rc = -1
        stdout.seek(0, os.SEEK_END)
        out_size = stdout.tell()
        stderr.seek(0, os.SEEK_END)
        err_size = stderr.tell()
        if max(out_size, err_size) > MAX_CAPTURE:
            raise ValueError("Oversized original FFT driver output")
        stdout.seek(0)
        stderr.seek(0)
        return classify_process(rc, stdout.read(), stderr.read(),
                                timed_out=timed_out)


def verify_validator_available():
    # Verify loader visibility of the layer separately. Requested activation
    # does not by itself prove the layer is actually available.
    result = subprocess.run(["vulkaninfo", "--summary"], capture_output=True,
                            check=False, timeout=30)
    if result.returncode != 0 or b"VK_LAYER_KHRONOS_validation" not in result.stdout + result.stderr:
        raise ValueError("Required Khronos Vulkan validation layer unavailable")


def inspect(source, runner):
    verify_validator_available()
    authenticated = verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    if authenticated["authenticated_owners"] != 1:
        raise ValueError("Original owner SHA check failed")
    import UnityPy
    env = UnityPy.load(str(source / OWNER))
    objects = [o for o in env.file.objects.values()
               if o.type.name == "ComputeShader" and int(o.path_id) == PATH_ID]
    if len(objects) != 1:
        raise ValueError("Original FFT ComputeShader ambiguous")
    raw = objects[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original FFT object fingerprint mismatch")
    scanned = scan_blob(raw)["valid_dxbc_containers"]
    if len(scanned) != EXPECTED_CONTAINERS:
        raise ValueError("Original compiled program count mismatch")
    pairs = validate_original_compiled_pairs(objects[0].read_typetree(), scanned)
    out = []
    with tempfile.TemporaryDirectory(prefix="t1-original-bank1-validation-") as tmp:
        temp = Path(tmp)
        for first in (10, 18):
            if pairs[first // 2] != (first, first + 1):
                raise ValueError("Original bank1 pair was reordered")
            shaders = []
            for offset in (0, 1):
                entry = scanned[first + offset]
                start = entry["offset_in_original_object"]
                blob = raw[start:start + entry["bytes"]]
                if len(blob) != entry["bytes"] or hashlib.sha256(blob).hexdigest() != entry["binary_sha256"]:
                    raise ValueError("Original DXBC slot SHA mismatch")
                dxbc = temp / ("original_" + str(offset) + ".dxbc")
                spirv = temp / ("original_" + str(offset) + ".spv")
                dxbc.write_bytes(blob)
                private_command(["vkd3d-compiler", "-x", "dxbc-tpf", "-b",
                                 "spirv-binary", "-o", str(spirv), str(dxbc)], timeout=35)
                private_command(["spirv-val", "--target-env", "vulkan1.1",
                                 str(spirv)], timeout=25)
                shaders.append(spirv)
            for pair, mode in CASES:
                if pair != first:
                    continue
                argv = ([str(runner), str(shaders[0]), str(shaders[0]),
                         str(shaders[1]), str(shaders[1]), "1024", "1024",
                         "19", "1", "rgba32f"] +
                        ([] if mode == "baseline" else ["--t1-swap-second"]))
                attempt_env = dict(os.environ)
                attempt_env["VK_INSTANCE_LAYERS"] = "VK_LAYER_KHRONOS_validation"
                observation = run_host(argv, attempt_env)
                if observation["layer_missing"]:
                    raise ValueError("Validation layer failed to load")
                out.append({"original_compiled_pair_first_slot": pair,
                            "descriptor_profile": mode, **observation})
            for p in temp.iterdir():
                p.unlink()
    if len(out) != len(CASES):
        raise ValueError("Bank1 failure isolation incomplete")
    return {"authenticated_original_owner": True,
            "original_compute_object_sha256": ORIGINAL_OBJECT_SHA256,
            "khronos_layer_requested_and_listed": True,
            "attempts": out, "attempted_original_compiled_pairs": 2,
            "host_exit_zero_cases": sum(case["outcome"] == "exit_zero" for case in out),
            "segmentation_fault_cases": sum(case["outcome"] == "segmentation_fault" for case in out),
            "original_runtime_unity_kernel_indices_verified": False,
            "native_unity_or_android_rendering_verified": False,
            "bank1_numeric_success_claimed": False,
            "private_shader_bytes_pixels_or_driver_text_published": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--runner", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_T1_BANK1_VALIDATION " + json.dumps(
        inspect(args.source, args.runner), sort_keys=True))


if __name__ == "__main__":
    main()
