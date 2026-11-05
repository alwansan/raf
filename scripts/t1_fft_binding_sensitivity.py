"""T1: original FFT read-binding sensitivity under real two-pass CPU Vulkan.

Distinct question from A1's output-equivalence roundtrip: when original DXBC
compiled programs run with identical shaders, do swapping sampled input
descriptors alter the computed result? No Unity kernel-ID or visual proof.
All genuine program bytes/pixels stay in private runner temporary directories.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import tempfile

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS,
)
from scripts.probe_original_fft_two_pass_software_vulkan import (
    parse_two_pass_result, validate_original_compiled_pairs,
)
from scripts.probe_original_fft_software_vulkan import private_command

PROFILES = ("baseline", "swap_first", "swap_second")
# Restrict positive numerical inference to the verified bank0 source candidate
# pairs. Bank1 pair18 second-pass swap SIGSEGV (41938536760), and bank1
# pair10 second-pass swap fails independent same-program comparator tolerance
# (41939082498). Both negative outcomes stay documented, not hidden or
# counted as recovered kernels. This bounded probe makes no bank1 claim.
SLOTS = (0, 8)
SEED = 19
MARKER = "RAFT_T1_BINDING_FINGERPRINT "
MAX_SOURCE_BYTES = 100_000


def render_host(source: str) -> str:
    """Derive isolated runner from A1, leaving its published green tests intact.

    Exact one-time anchors fail closed on drift. The only operational change is
    which of the TWO sampled image views fills binding 0 versus binding 1.
    Original and comparator executions receive the SAME profile; neither
    original program nor output pixel is rewritten.
    """
    if not isinstance(source, str) or not 10000 <= len(source) <= MAX_SOURCE_BYTES:
        raise ValueError("Unexpected inherited A1 Vulkan harness size")
    replacements = (
        (
            '    bool canary=(argc==11 && std::string(argv[10])=="--canary");\n'
            '    require(argc==10 || canary,"Invalid two-pass synthetic canary");',
            '    std::string profile="baseline";\n'
            '    if(argc==11) {\n'
            '        const std::string flag(argv[10]);\n'
            '        if(flag=="--t1-swap-first") profile="swap_first";\n'
            '        else if(flag=="--t1-swap-second") profile="swap_second";\n'
            '    }\n'
            '    const bool canary=(argc==11 && std::string(argv[10])=="--canary");\n'
            '    require(argc==10 || canary || profile!="baseline",\n'
            '            "Invalid bounded T1 input-descriptor profile");',
        ),
        (
            '        const int textureIndex=(binding==0?passSource[set]:\n'
            '                               (binding==1?1:passTarget[set]));',
            '        const bool swap=((set<2 && profile=="swap_first") ||\n'
            '                         (set>=2 && profile=="swap_second"));\n'
            '        const int readSlot=(swap && binding<2)?1-binding:binding;\n'
            '        const int textureIndex=(readSlot==0?passSource[set]:\n'
            '                                (readSlot==1?1:passTarget[set]));',
        ),
        (
            '    uint64_t writesA=0,writesB=0,missing=0,nonFinite=0,canaryErrors=0;',
            '    uint64_t originalFingerprint=14695981039346656037ull;\n'
            '    uint64_t writesA=0,writesB=0,missing=0,nonFinite=0,canaryErrors=0;',
        ),
        (
            '            const float va=a[c],vb=b[c];',
            '            const float va=a[c],vb=b[c];\n'
            '            uint32_t bits=0;\n'
            '            std::memcpy(&bits,&va,sizeof(bits));\n'
            '            originalFingerprint^=uint64_t(bits);\n'
            '            originalFingerprint*=1099511628211ull;',
        ),
        (
            '    check(vkDeviceWaitIdle(device),"vkDeviceWaitIdle");',
            '    std::cout<<"RAFT_T1_BINDING_FINGERPRINT {\\"profile\\":\\""<<profile\n'
            '              <<"\\",\\"checksum\\":\\""<<originalFingerprint\n'
            '              <<"\\",\\"same_source_comparator\\":"<<(match?"true":"false")\n'
            '              <<"}\\n";\n'
            '    check(vkDeviceWaitIdle(device),"vkDeviceWaitIdle");',
        ),
    )
    output = source
    for old, new in replacements:
        if output.count(old) != 1:
            raise ValueError("A1 runner contract/anchor changed; no T1 transform permitted")
        output = output.replace(old, new)
    if output.count(MARKER) != 1:
        raise ValueError("T1 probe lacks unique isolated output marker")
    return output


def read_fingerprint(output: str, expected_profile: str) -> str:
    if type(output) is not str or len(output) > 8192 or expected_profile not in PROFILES:
        raise ValueError("Unbounded or unknown T1 numeric report")
    lines = [x[len(MARKER):] for x in output.splitlines() if x.startswith(MARKER)]
    if len(lines) != 1:
        raise ValueError("Missing or duplicate T1 numeric fingerprint")
    record = json.loads(lines[0], parse_constant=lambda _: (_ for _ in ()).throw(
        ValueError("Nonnumeric output")))
    if (not isinstance(record, dict)
            or set(record) != {"profile", "checksum", "same_source_comparator"}
            or record["profile"] != expected_profile
            or record["same_source_comparator"] is not True
            or not isinstance(record["checksum"], str)
            or not re.fullmatch(r"[0-9]{1,20}", record["checksum"])):
        raise ValueError("Original FFT binding probe result inconsistent")
    value = int(record["checksum"])
    if value <= 0 or value >= (1 << 64):
        raise ValueError("Invalid original output fingerprint")
    return record["checksum"]


def assess(fingerprints: dict) -> dict:
    if not isinstance(fingerprints, dict) or set(fingerprints) != set(PROFILES):
        raise ValueError("Incomplete original input binding modes")
    for mode in PROFILES:
        read_fingerprint(
            MARKER + json.dumps({"profile": mode, "checksum": fingerprints[mode],
                                 "same_source_comparator": True}), mode)
    return {
        "first_pass_input_swap_changes_original_result":
            fingerprints["baseline"] != fingerprints["swap_first"],
        "second_pass_input_swap_changes_original_result":
            fingerprints["baseline"] != fingerprints["swap_second"],
        "original_pixels_or_shader_code_published": False,
    }


def run_original(source: Path, runner: Path) -> dict:
    if not runner.is_file() or runner.is_symlink():
        raise ValueError("T1 CPU Vulkan runner unavailable")
    authenticated = verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    if authenticated["authenticated_owners"] != 1:
        raise ValueError("Original FFT owner SHA verification failed")
    import UnityPy
    env = UnityPy.load(str(source / OWNER))
    matches = [obj for obj in env.file.objects.values()
               if obj.type.name == "ComputeShader" and int(obj.path_id) == PATH_ID]
    if len(matches) != 1:
        raise ValueError("Original FFT Unity object missing or ambiguous")
    raw = matches[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original FFT object digest mismatch")
    scanned = scan_blob(raw)["valid_dxbc_containers"]
    if len(scanned) != EXPECTED_CONTAINERS:
        raise ValueError("Original compiled program inventory mismatch")
    pairs = validate_original_compiled_pairs(matches[0].read_typetree(), scanned)
    if len(pairs) != 10:
        raise ValueError("Expected 10 original two-pass candidate pairs")
    results = []
    with tempfile.TemporaryDirectory(prefix="t1-original-fft-private-") as tmp:
        temp = Path(tmp)
        for first in SLOTS:
            if pairs[first//2] != (first,first+1):
                raise ValueError("Selected original compiled program pair reordered")
            shader_paths = []
            for offset in (0, 1):
                item = scanned[first+offset]
                at = item["offset_in_original_object"]
                binary = raw[at:at+item["bytes"]]
                if (len(binary) != item["bytes"]
                        or hashlib.sha256(binary).hexdigest() != item["binary_sha256"]):
                    raise ValueError("Private original DXBC bytes do not match source")
                dxbc = temp / ("original_" + str(offset) + ".dxbc")
                spv = temp / ("original_" + str(offset) + ".spv")
                dxbc.write_bytes(binary)
                private_command(["vkd3d-compiler", "-x", "dxbc-tpf", "-b",
                                 "spirv-binary", "-o", str(spv), str(dxbc)], timeout=30)
                private_command(["spirv-val", "--target-env", "vulkan1.1",
                                 str(spv)], timeout=25)
                shader_paths.append(spv)
            fingerprints = {}
            for mode in PROFILES:
                args = ([str(runner),
                         str(shader_paths[0]), str(shader_paths[0]),
                         str(shader_paths[1]), str(shader_paths[1]),
                         "1024", "1024", str(SEED), "1", "rgba32f"] +
                        ([] if mode == "baseline" else ["--t1-" + mode.replace("_", "-")]))
                # Keep all original bytecode and image data private, even on failure.
                try:
                    output = private_command(args, timeout=110).decode("utf-8", "strict")
                except ValueError as exc:
                    raise ValueError("T1 bounded original program pair=" + str(first) +
                                     " profile=" + mode +
                                     " CPU Vulkan runner failed; no private shader data disclosed") from exc
                parsed = parse_two_pass_result(output)
                if (not parsed["within_selected_tolerance"]
                        or parsed["input_seed"] != SEED
                        or parsed["original_written_pixels"] == 0
                        or parsed["nonfinite_components"] != 0
                        or parsed["vulkan_image_format"] != "rgba32f"):
                    raise ValueError("T1 original workload incomplete: pair=" + str(first) +
                                     " profile=" + mode +
                                     " tolerance=" + str(parsed["within_selected_tolerance"]) +
                                     " nonfinite=" + str(parsed["nonfinite_components"] > 0) +
                                     " wrote=" + str(parsed["original_written_pixels"] > 0) +
                                     " seed=" + str(parsed["input_seed"] == SEED) +
                                     " format=" + str(parsed["vulkan_image_format"] == "rgba32f"))
                fingerprints[mode] = read_fingerprint(output, mode)
            assessed = assess(fingerprints)
            results.append({"first_original_compiled_candidate_slot": first,
                            **assessed})
            for p in temp.iterdir():
                p.unlink()
    first_count = sum(x["first_pass_input_swap_changes_original_result"] for x in results)
    second_count = sum(x["second_pass_input_swap_changes_original_result"] for x in results)
    return {
        "original_sha256": ORIGINAL_OBJECT_SHA256,
        "source_authentication": True,
        "examined_original_compiled_candidate_pairs": len(results),
        "numerical_two_pass_executions": len(results) * len(PROFILES),
        "original_first_input_role_sensitivity_pairs": first_count,
        "original_second_input_role_sensitivity_pairs": second_count,
        "one_or_more_input_roles_numerically_noninterchangeable":
            first_count > 0 or second_count > 0,
        "original_runtime_unity_kernel_indices_verified": False,
        "actual_unity_compute_asset_imported": False,
        "android_gpu_or_pixels_verified": False,
        "original_shader_bytes_or_pixels_published": False,
        "results": results,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--runner", required=True, type=Path)
    args = ap.parse_args()
    result = run_original(args.source, args.runner)
    print("RAFT_T1_ORIGINAL_FFT_BINDING_SENSITIVITY " + json.dumps(result, sort_keys=True))
    if not result["one_or_more_input_roles_numerically_noninterchangeable"]:
        raise SystemExit("Original FFT sampled input role sensitivity unproven; keep WATER open")


if __name__ == "__main__":
    main()
