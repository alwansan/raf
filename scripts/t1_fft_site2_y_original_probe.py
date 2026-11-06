"""SHA-authenticated original ZIP2 first FFT slot into a private, bounded CFG report."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from scripts.probe_authentic_fft_dxbc_translation import (
    OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256, EXPECTED_CONTAINERS)
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_original_fft_two_pass_software_vulkan import validate_original_compiled_pairs
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.t1_fft_site2_y_cfg import analyze

def inspect(original_data):
    root = Path(original_data)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Original owner directory unsafe")
    auth = verify_sources(root, expected={OWNER: EXPECTED[OWNER]})
    if auth["authenticated_owners"] != 1:
        raise ValueError("Original owner SHA/bytes invalid")
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    matches = [x for x in env.file.objects.values()
               if x.type.name == "ComputeShader" and int(x.path_id) == PATH_ID]
    if len(matches) != 1:
        raise ValueError("Original ComputeShader identity unavailable")
    raw = matches[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original ComputeShader object SHA mismatch")
    slots = scan_blob(raw)["valid_dxbc_containers"]
    if len(slots) != EXPECTED_CONTAINERS:
        raise ValueError("Original compiled FFT inventory changed")
    if len(validate_original_compiled_pairs(matches[0].read_typetree(), slots)) != 10:
        raise ValueError("Original compiled pair resources/order drift")
    rec = slots[0]
    start, size = rec["offset_in_original_object"], rec["bytes"]
    if not (type(start) is int and type(size) is int
            and start >= 0 and 36 <= size <= 1024 * 1024
            and start + size <= len(raw)):
        raise ValueError("Original DXBC slot out of range")
    dxbc = raw[start:start+size]
    if hashlib.sha256(dxbc).hexdigest() != rec["binary_sha256"]:
        raise ValueError("DXBC source digest drift")
    with tempfile.TemporaryDirectory(prefix="t1-site2-y-private-") as tmp:
        d = Path(tmp)
        path_in, spv = d / "original.dxbc", d / "original.spv"
        path_in.write_bytes(dxbc)
        private_command(["vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                         "-o", str(spv), str(path_in)], timeout=30)
        private_command(["spirv-val", "--target-env", "vulkan1.1", str(spv)], timeout=25)
        dis = subprocess.run(["spirv-dis", "--raw-id", str(spv)],
                             capture_output=True, text=True, check=True, timeout=20)
        report = analyze(dis.stdout)
    if report["site"] != 2 or report["role"] != "butterfly":
        raise ValueError("Third original ImageFetch is not butterfly")
    return {
        "status": "sha_verified_original_fft_slot0_site2_y_may_path_provenance",
        "original_owner_and_compute_object_sha_verified": True,
        "original_dxbc_slot_digest_verified": True,
        "original_compiled_pair_order_verified": True,
        "vkd3d_spirv_validated": True,
        "original_shader_or_pixels_published": False,
        "authored_unity_runtime_kernel_proven": False,
        "unity_gpu_or_android_test_proven": False,
        "site2_y": report,
    }

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-data", type=Path, required=True)
    args = p.parse_args()
    try:
        report = inspect(args.original_data)
    except (OSError, ValueError, TypeError, KeyError, IndexError,
            subprocess.SubprocessError):
        p.exit(2, "RAFT_T1_PRIVATE_SITE2Y original_data_or_spirv_unverified=true\n")
    print("RAFT_T1_PRIVATE_SITE2Y " + json.dumps(report, sort_keys=True))

if __name__ == "__main__":
    main()
