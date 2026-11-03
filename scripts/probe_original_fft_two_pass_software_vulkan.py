"""Run true two-dispatch original Raft FFT compute ping-pong on CPU Vulkan.

Read-only pinned ZIP2 owner staged by workflow, authenticated original serialized
ComputeShader, actual original DXBC and private HLSL roundtrips. No raw game
binary, HLSL, SPIR-V, image values or proprietary source emitted or committed.
Adjacent compiled slots are CANDIDATE pairs, never claimed Unity runtime indices.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)
from scripts.probe_fft_variant_table import (
    correlate_original_variant_bytecode, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
)
from scripts.probe_original_fft_resource_bindings import resource_rows
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_spirv_operation_profile import image_operation_profile
from scripts.probe_fft_spirv_formatless_repair import restore_formatless_write
from scripts.probe_original_fft_software_vulkan import (
    IMAGE_FORMATS, SCENARIOS, SELECTED_WIDTH, SELECTED_HEIGHT,
    parse_private_numeric_result, validate_requested_workload, private_command,
)

MARKER = "RAFT_A1_VULKAN_TWO_PASS "
EXTRA_FLAGS = (
    "first_pass_output_feeds_second_source",
    "same_butterfly_texture_both_passes",
    "intermediate_compute_write_read_barrier",
)


def parse_two_pass_result(output):
    if type(output) is not str or len(output) > 8192:
        raise ValueError("Two-pass Vulkan output malformed or oversized")
    lines = [line for line in output.splitlines() if line.startswith(MARKER)]
    if len(lines) != 1:
        raise ValueError("Missing/ambiguous two-pass Vulkan result")
    row = json.loads(lines[0][len(MARKER):], parse_constant=lambda _: (_ for _ in ()).throw(
        ValueError("Nonfinite private Vulkan numeric result")))
    if not isinstance(row, dict):
        raise ValueError("Two-pass numeric schema not a record")
    for key in EXTRA_FLAGS:
        if row.get(key) is not True:
            raise ValueError("Two-pass image dependency flag missing or false")
    original_keys = set(parse_private_numeric_result.__globals__["KEYS"])
    if set(row) != original_keys | set(EXTRA_FLAGS):
        raise ValueError("Unexpected two-pass Vulkan numeric schema")
    baseline = {k: row[k] for k in original_keys}
    result = parse_private_numeric_result(
        "RAFT_A1_VULKAN_DIFF " + json.dumps(baseline, sort_keys=True))
    return {**result, **{key: True for key in EXTRA_FLAGS}}


def validate_original_compiled_pairs(tree, scanned):
    correlated = correlate_original_variant_bytecode(
        tree, scanned, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT)
    resources = resource_rows(tree)
    if (correlated["authentic_compiled_variants_verified_in_original_order"]
            != EXPECTED_CONTAINERS or len(resources) != EXPECTED_CONTAINERS
            or EXPECTED_CONTAINERS != 20):
        raise ValueError("Original compiled slot order or resource contracts changed")
    for first in range(0, EXPECTED_CONTAINERS, 2):
        if (resources[first]["workgroup_xyz"] != resources[first+1]["workgroup_xyz"]
                or resources[first]["source_image_name_sha256"] !=
                   resources[first+1]["source_image_name_sha256"]
                or resources[first]["butterfly_image_name_sha256"] !=
                   resources[first+1]["butterfly_image_name_sha256"]
                or resources[first]["target_image_name_sha256"] !=
                   resources[first+1]["target_image_name_sha256"]):
            raise ValueError("Original two-pass adjacent compiled slot resource mismatch")
    return tuple((i, i+1) for i in range(0, EXPECTED_CONTAINERS, 2))


def analyze(original_root, runner):
    root = Path(original_root)
    runner = Path(runner)
    if not runner.is_file() or runner.is_symlink():
        raise ValueError("Two-pass CPU Vulkan binary missing/unsafe")
    authenticated = verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    if authenticated["authenticated_owners"] != 1:
        raise ValueError("Authentic ZIP2 FFT owner not independently verified")
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objects = [o for o in env.file.objects.values()
               if o.type.name == "ComputeShader" and int(o.path_id) == PATH_ID]
    if len(objects) != 1:
        raise ValueError("Original FFT ComputeShader missing or ambiguous")
    raw = objects[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Authentic FFT ComputeShader SHA mismatch")
    scanned = scan_blob(raw)["valid_dxbc_containers"]
    if len(scanned) != EXPECTED_CONTAINERS:
        raise ValueError("Original compiled FFT program count changed")
    pairs = validate_original_compiled_pairs(objects[0].read_typetree(), scanned)
    rows = []
    with tempfile.TemporaryDirectory(prefix="raft-a1-private-two-pass-") as work:
        temp = Path(work)
        for a,b in pairs:
            paths = [
                temp / "original_first.dxbc",temp / "original_second.dxbc",
                temp / "original_first.spv",temp / "original_second.spv",
                temp / "roundtrip_first.hlsl",temp / "roundtrip_second.hlsl",
                temp / "roundtrip_first.spv",temp / "roundtrip_second.spv",
                temp / "formatless_first.spv",temp / "formatless_second.spv",
            ]
            row = {"first_compiled_slot":a,"second_compiled_slot":b,
                   "proven_runtime_kernel_indices":False,
                   "format_comparisons":[]}
            try:
                for i,slot in enumerate((a,b)):
                    entry = scanned[slot]
                    at = entry["offset_in_original_object"]
                    binary = raw[at:at+entry["bytes"]]
                    if (len(binary) != entry["bytes"] or
                            hashlib.sha256(binary).hexdigest() != entry["binary_sha256"]):
                        raise ValueError("Private original DXBC compiled slot SHA mismatch")
                    paths[i].write_bytes(binary)
                    private_command(["vkd3d-compiler","-x","dxbc-tpf","-b",
                                     "spirv-binary","-o",str(paths[2+i]),
                                     str(paths[i])],timeout=30)
                    private_command(["spirv-val","--target-env","vulkan1.1",
                                     str(paths[2+i])],timeout=25)
                    private_command(["spirv-cross",str(paths[2+i]),"--hlsl",
                                     "--shader-model","50","--output",
                                     str(paths[4+i])],timeout=30)
                    private_command(["glslangValidator","-V","-D","-S","comp",
                                     "-e","main","-o",str(paths[6+i]),
                                     str(paths[4+i])],timeout=30)
                    private_command(["spirv-val","--target-env","vulkan1.1",
                                     str(paths[6+i])],timeout=25)
                    restored = restore_formatless_write(
                        paths[6+i].read_bytes(),
                        image_resource_contracts(paths[2+i].read_bytes()),
                        image_operation_profile(paths[2+i].read_bytes()))
                    paths[8+i].write_bytes(restored)
                    private_command(["spirv-val","--target-env","vulkan1.1",
                                     str(paths[8+i])],timeout=25)
                for fmt in IMAGE_FORMATS:
                    cases=[]
                    status="executed"
                    for seed,y_groups in SCENARIOS:
                        try:
                            roundtrip0 = paths[6] if fmt=="rgba32f" else paths[8]
                            roundtrip1 = paths[7] if fmt=="rgba32f" else paths[9]
                            output = private_command([
                                str(runner),str(paths[2]),str(roundtrip0),
                                str(paths[3]),str(roundtrip1),
                                str(SELECTED_WIDTH),str(SELECTED_HEIGHT),
                                str(seed),str(y_groups),fmt],timeout=90)
                            parsed = parse_two_pass_result(
                                output.decode("utf-8",errors="strict"))
                            validate_requested_workload(parsed,seed,y_groups,fmt)
                            cases.append({
                                "seed":seed,"groups_y":y_groups,
                                "original_written_pixels":parsed["original_written_pixels"],
                                "roundtrip_written_pixels":parsed["roundtrip_written_pixels"],
                                "write_coverage_mismatch_pixels":parsed[
                                    "write_coverage_mismatch_pixels"],
                                "nonfinite_components":parsed["nonfinite_components"],
                                "max_abs_difference":parsed["max_abs_difference"],
                                "relative_l2_difference":parsed["relative_l2_difference"],
                                "same_output_tolerance":parsed["within_selected_tolerance"],
                            })
                        except (ValueError,UnicodeError):
                            status="inconclusive"
                            break
                    row["format_comparisons"].append({
                        "vulkan_format":fmt,"status":status,
                        "cases":cases,
                    })
            except (ValueError,UnicodeError):
                row["precondition_status"]="failed_private_source_or_compiler"
            finally:
                for p in paths:p.unlink(missing_ok=True)
            rows.append(row)
    formats=[f for row in rows for f in row["format_comparisons"]]
    comparisons=[v for f in formats for v in f["cases"]]
    result={
        "original_sha256":ORIGINAL_OBJECT_SHA256,
        "original_owner_verified_bytes":EXPECTED[OWNER][0],
        "original_serialized_compiled_pairs_authored_order":len(pairs),
        "original_runtime_kernel_index_mapping_proven":False,
        "original_csharp_two_pass_source_bound":False,
        "format_program_pairs_expected":len(pairs)*len(IMAGE_FORMATS),
        "format_program_pairs_complete":sum(f["status"]=="executed" and
            len(f["cases"])==len(SCENARIOS) for f in formats),
        "two_pass_real_image_output_comparisons":len(comparisons),
        "matching_numeric_comparisons":sum(v["same_output_tolerance"] for v in comparisons),
        "mismatching_numeric_comparisons":sum(
            not v["same_output_tolerance"] for v in comparisons),
        "max_abs_difference":max((v["max_abs_difference"] for v in comparisons),default=None),
        "max_relative_l2":max((v["relative_l2_difference"] for v in comparisons),default=None),
        "original_shader_bytes_or_output_pixels_exported":False,
        "software_vulkan_not_android_or_unity":True,
        "rows":rows,
    }
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--runner",type=Path,required=True)
    args=parser.parse_args()
    report=analyze(args.source,args.runner)
    print("RAFT_A1_AUTHENTIC_FFT_TWO_PASS "+json.dumps(report,sort_keys=True))
    if (report["format_program_pairs_complete"] !=
            report["format_program_pairs_expected"] or
            report["two_pass_real_image_output_comparisons"] !=
            report["format_program_pairs_expected"]*len(SCENARIOS) or
            report["matching_numeric_comparisons"] !=
            report["two_pass_real_image_output_comparisons"]):
        raise SystemExit("Authentic FFT two-pass numerical recovery incomplete/different; keep WATER OPEN")


if __name__=="__main__":
    main()
