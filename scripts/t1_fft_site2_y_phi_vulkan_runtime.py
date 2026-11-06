"""Private real Mesa CPU Vulkan path-count test for FFT third-butterfly Y Phi.

Source provider: exact SHA-pinned ZIP2 owner and original compiled FFT slots0/1.
Compare two physically independent Vulkan executions using identical host code
and seed19 physical source/butterfly inputs:
  A original0 / HLSL50-glslang untagged0 / original1 / original1
  B original0 / HLSL50-glslang PRIVATE Phi-tagged0 / original1 / original1
The tagged candidate alone uses a 128-u32 zeroed set0/binding3 SSBO. Reports
safe histogram/bitwise output-invariance only; all original shader, HLSL,
SPIR-V, runtime counter bytes and pixel buffers remain ephemeral.

Not Unity/OpenGLCore, original authored FindKernel or Android Adreno. Counter
execution on Mesa software Vulkan does not establish per-invocation edge
selection for a distinct Unity compiled backend.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS)
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_original_fft_two_pass_software_vulkan import validate_original_compiled_pairs
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.t1_fft_pass0_vulkan_trace import trace_host
from scripts.t1_fft_private_input_evidence import BYTES
from scripts.t1_fft_readback_parity import read_image, compare_pass
from scripts.t1_fft_site2_y_hlsl_pair import stage_original_dxbc
from scripts.t1_fft_site2_y_phi_path_tag import instrument, COUNTER_U32
from scripts.t1_fft_vulkan_roundtrip_isolation import WIDTH, HEIGHT

ORIGINAL_PIN = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
OWNER_DIGEST = "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"
EXPECTED_DISPATCH = (1, 1, 1)
COUNTER_BYTES = COUNTER_U32 * 4
MAX_LOOP_COUNT = 4096
COUNTERS = struct.Struct("<128I")
INPUTS = ("t1-source-input.rgba32f", "t1-butterfly-input.rgba32f")
OUTPUTS = ("original0.rgba32f", "original1.rgba32f",
           "roundtrip0.rgba32f", "roundtrip1.rgba32f")


def counter_profile(unmodified, tagged):
    """Reject forged controls and report no individual thread/path values."""
    if type(unmodified) is not bytes or type(tagged) is not bytes:
        raise ValueError("Counter payloads must be direct runtime bytes")
    if len(unmodified) != COUNTER_BYTES or len(tagged) != COUNTER_BYTES:
        raise ValueError("Private counter byte count mismatch")
    if any(COUNTERS.unpack(unmodified)):
        raise ValueError("Untagged shader unexpectedly modified counter buffer")
    words = COUNTERS.unpack(tagged)
    entry, loop = words[::2], words[1::2]
    if any(n > MAX_LOOP_COUNT for n in words):
        raise ValueError("Phi loop counter unbounded")
    hits = lambda x: {"zero": sum(v == 0 for v in x),
                      "one": sum(v == 1 for v in x),
                      "multiple": sum(v > 1 for v in x)}
    return {
        "status": "real_CPU_Vulkan_original_derived_fft_phi_path_counter_profile",
        "zeroed_untagged_buffer_verified": True,
        "counter_slots": 64,
        "entry_execution_hists": hits(entry),
        "loop_backedge_execution_hists": hits(loop),
        "threads_with_both_entry_and_loop_edges": sum(a > 0 and b > 0 for a, b in zip(entry, loop)),
        "threads_with_only_entry_edge": sum(a > 0 and b == 0 for a, b in zip(entry, loop)),
        "threads_with_no_entry_but_loop_edge": sum(a == 0 and b > 0 for a, b in zip(entry, loop)),
        "total_entry_edge_visits": sum(entry),
        "total_loop_backedge_visits": sum(loop),
        "all_invocations_have_entry_edge": all(n > 0 for n in entry),
        "any_loop_backedge_observed": any(n > 0 for n in loop),
        "counter_bytes_or_invocation_keys_exported": False,
        "actual_shader_choice_at_site2_fetch_proven": False,
        "actual_Unity_compiled_shader_execution_proven": False,
        "android_Adreno_water_proven": False,
    }


def readback_pair(plain_dir, tagged_dir):
    """Require physical input bytes and original controls stable across runs."""
    left, right = Path(plain_dir), Path(tagged_dir)
    if left.is_symlink() or right.is_symlink() or not left.is_dir() or not right.is_dir():
        raise ValueError("Unsafe original/counter Vulkan output root")
    if left.samefile(right):
        raise ValueError("Untagged/tagged experiment directories alias")
    for name in (*INPUTS, OUTPUTS[0], OUTPUTS[1]):
        a, b = (read_image(root / name, BYTES) for root in (left, right))
        if a != b:
            raise ValueError("Vulkan physical input or original-control output changed")
    candidates = {}
    for i, name in enumerate(OUTPUTS[2:]):
        original, tagged = (read_image(root / name, BYTES) for root in (left, right))
        check = compare_pass(original, tagged)
        candidates["pass" + str(i)] = {
            "original_untagged_to_tagged_readback_byte_identical": original == tagged,
            "compared_written_pixels": check["compared_written_pixels"],
            "write_coverage_mismatch_pixels": check["write_coverage_mismatch_pixels"],
            "nonfinite_pixels": check["nonfinite_pixels"],
            "outside_tolerance_pixels": check["outside_tolerance_pixels"],
            "within_tolerance": check["match"],
        }
    return {
        "two_physical_runs_with_byte_identical_inputs": True,
        "original_control_pixels_byte_identical": True,
        "tagging_did_not_change_candidate_outputs_bitwise":
            all(x["original_untagged_to_tagged_readback_byte_identical"]
                for x in candidates.values()),
        "tagging_did_not_change_candidate_outputs_within_tolerance":
            all(x["within_tolerance"] for x in candidates.values()),
        "candidate_output_parity_by_pass": candidates,
        "private_pixels_or_input_sha_values_exported": False,
    }


def original_slot_pair(root):
    # Stage slot0 with the already provenance-proven original SHA gate.
    slot0 = stage_original_dxbc(root)
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Invalid original FFT owner directory")
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    hits = [v for v in env.file.objects.values()
            if v.type.name == "ComputeShader" and int(v.path_id) == PATH_ID]
    if len(hits) != 1:
        raise ValueError("Private original FFT object identity changed")
    obj = hits[0]
    raw = obj.get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Private source object SHA mismatch")
    slots = scan_blob(raw)["valid_dxbc_containers"]
    if len(slots) != EXPECTED_CONTAINERS or len(
            validate_original_compiled_pairs(obj.read_typetree(), slots)) != 10:
        raise ValueError("Original FFT compiled slot pair ABI mismatch")
    second = slots[1]
    start, size = second["offset_in_original_object"], second["bytes"]
    if (type(start) is not int or type(size) is not int or start < 0
            or not 36 <= size <= 1024*1024 or start + size > len(raw)):
        raise ValueError("Original FFT slot1 bounds changed")
    slot1 = raw[start:start+size]
    if hashlib.sha256(slot1).hexdigest() != second["binary_sha256"]:
        raise ValueError("Original FFT slot1 DXBC SHA mismatch")
    return slot0, slot1


def run_private(command, cwd, timeout=110):
    result = subprocess.run(command, cwd=cwd, capture_output=True,
                            timeout=timeout, check=False)
    if result.returncode != 0:
        # NEVER include shader driver stderr/raw output, SSA ids or values.
        raise ValueError("Private CPU Vulkan build or execution unavailable")


def inspect(original_data, host_path):
    host_path = Path(host_path)
    if host_path.is_symlink() or not host_path.is_file() or not 2048 <= host_path.stat().st_size <= 128*1024:
        raise ValueError("Original Vulkan host file absent or unsafe")
    slot0, slot1 = original_slot_pair(original_data)
    with tempfile.TemporaryDirectory(prefix="t1-private-fft-phi-runtime-") as dirname:
        root = Path(dirname)
        dx0, dx1, spv0, spv1, hlsl, derived, tagged_src, tagged = [
            root / filename for filename in ("slot0.dxbc", "slot1.dxbc",
              "slot0.spv", "slot1.spv", "private.hlsl", "derived.spv",
              "tagged.spvasm", "tagged.spv")]
        dx0.write_bytes(slot0); dx1.write_bytes(slot1)
        for inp, out in ((dx0, spv0), (dx1, spv1)):
            private_command(["vkd3d-compiler", "-x", "dxbc-tpf",
                             "-b", "spirv-binary", "-o", str(out), str(inp)], timeout=30)
            private_command(["spirv-val", "--target-env", "vulkan1.1", str(out)], timeout=25)
        private_command(["spirv-cross", str(spv0), "--hlsl", "--shader-model", "50",
                         "--output", str(hlsl)], timeout=30)
        if hlsl.is_symlink() or not 20 <= hlsl.stat().st_size <= 512*1024:
            raise ValueError("Private HLSL translation invalid")
        private_command(["glslangValidator", "-V", "-D", "-S", "comp", "-e", "main",
                         "-o", str(derived), str(hlsl)], timeout=30)
        private_command(["spirv-val", "--target-env", "vulkan1.1", str(derived)], timeout=25)
        dis = subprocess.run(["spirv-dis", "--raw-id", str(derived)],
                             capture_output=True, text=True, timeout=25, check=True)
        if not 40 <= len(dis.stdout) <= 4*1024*1024:
            raise ValueError("Private derived assembly unbounded")
        tagged_text, tag_schema = instrument(dis.stdout)
        tagged_src.write_text(tagged_text, encoding="utf-8")
        private_command(["spirv-as", "--target-env", "vulkan1.1", "-o",
                         str(tagged), str(tagged_src)], timeout=30)
        private_command(["spirv-val", "--target-env", "vulkan1.1", str(tagged)], timeout=30)

        host = trace_host(host_path.read_text(encoding="utf-8"),
                          COUNTER_BYTES, capture_inputs=True)
        target = root / "private_cpu_host.cpp"
        binary = root / "private_cpu_host"
        target.write_text(host, encoding="utf-8")
        run_private(["g++", "-std=c++17", "-O2", str(target),
                     "-lvulkan", "-o", str(binary)], root, timeout=65)
        candidates = [derived, tagged]
        directories = [root / "plain", root / "tagged"]
        for path, selected in zip(directories, candidates):
            path.mkdir(mode=0o700)
            run_private([str(binary), str(spv0), str(selected), str(spv1),
                         str(spv1), str(WIDTH), str(HEIGHT), "19", "1",
                         "rgba32f"], path, timeout=110)
        raw0, raw1 = (read_image(p / "trace.bin", COUNTER_BYTES)
                      for p in directories)
        counts = counter_profile(raw0, raw1)
        parity = readback_pair(*directories)
    return {
        "status": "source_sha_original_fft_site2_Y_phi_real_cpu_vulkan_counter_and_invariance",
        "original_sha_source_verified": True,
        "original_compiled_slots0_and1_verified": True,
        "direct_original_and_original_derived_spirv_validated": True,
        "private_phi_counter_spirv_validated": True,
        "source_pin_full_commit": ORIGINAL_PIN,
        "original_owner_sha_verified": True,
        "fixture": "original_seed19_1024x32_single_groupY_RGBA32F",
        "backend": "software_CPU_Vulkan_not_Unity",
        "private_gpu_driver_and_dispatch_completed": True,
        **counts, **parity,
        "game_original_authored_kernel_mapping_proven": False,
        "original_direct_vs_derived_numeric_parity_proven": False,
        "android_adreno_water_proven": False,
        "private_shader_pixels_and_full_counter_buffers_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-data", required=True, type=Path)
    p.add_argument("--vulkan-host", type=Path, default=Path("scripts/a1_fft_two_pass_vulkan.cpp"))
    args = p.parse_args()
    try:
        report = inspect(args.original_data, args.vulkan_host)
    except (OSError, ValueError, TypeError, KeyError, IndexError,
            UnicodeError, subprocess.SubprocessError):
        p.exit(2, "RAFT_T1_SITE2Y_PHI_CPU_VULKAN source_counter_or_output_evidence_unverified=true\n")
    print("RAFT_T1_SITE2Y_PHI_CPU_VULKAN " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
