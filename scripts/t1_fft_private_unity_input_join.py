"""Join *actual private input bytes* and Unity CopyInput evidence to FFT trace taxonomy.

Unlike an unsigned manifest's equal SHA strings, this checks physical
Vulkan/Unity input files byte-for-byte and binds those bytes to the declared
paired trace SHA. It accepts only the separate Unity 2021 OpenGLCore CopyInput
GPU test's bounded zero-mismatch report (an execution claim, not a signed
attestation). All raw game data stay inside a private runner.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.t1_fft_invocation_pair_gate import _read_manifest
from scripts.t1_fft_private_input_evidence import BYTES, DISPATCH, input_hash, sha
from scripts.t1_fft_private_unity_ftz_diagnostic import classify
from scripts.t1_fft_readback_parity import read_image

BACKEND = b"OpenGLCore"
MAX_IDENTITY = 64
IDENTITY_NAME = "input_identity.rgba32f"


def _private_file(path: Path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Missing, linked or unsafe private evidence file")
    return path


def _read_actual(path: Path) -> bytes:
    # read_image is bounded to BYTES+1 and fails if incomplete or oversized.
    return read_image(_private_file(path), BYTES)


def _identity(path: Path) -> None:
    path = _private_file(path)
    with path.open("rb") as stream:
        content = stream.read(MAX_IDENTITY + 1)
    if not 0 < len(content) <= MAX_IDENTITY:
        raise ValueError("Unity CopyInput report missing or too large")
    # C# File.WriteAllLines output, no whitespace or private free-text.
    if content not in (
        BACKEND + b"\n0\n0\n",
        BACKEND + b"\r\n0\r\n0\r\n",
    ):
        raise ValueError("Unity OpenGLCore CopyInput zero-mismatch report absent")


def join(manifest, original, unity, vulkan_input_dir, unity_input_dir):
    manifest = _private_file(Path(manifest))
    original = _private_file(Path(original))
    unity = _private_file(Path(unity))
    a_root = Path(vulkan_input_dir)
    b_root = Path(unity_input_dir)
    if a_root.is_symlink() or b_root.is_symlink() or not a_root.is_dir() or not b_root.is_dir():
        raise ValueError("Input roots must be real private directories")

    metadata = _read_manifest(manifest)
    # Existing classifier does strict role, independent capture byte SHA and
    # per-site invocation-key validation before any public result.
    report = classify(manifest, original, unity)
    stage_bytes = []
    for root in (a_root, b_root):
        source = _private_file(root / "source.rgba32f")
        butterfly = _private_file(root / "butterfly.rgba32f")
        if source.samefile(butterfly):
            raise ValueError("Source and butterfly files are aliased")
        stage_bytes.append((_read_actual(source), _read_actual(butterfly)))
    for first, second in zip(stage_bytes[0], stage_bytes[1]):
        if first != second:
            raise ValueError("Physical Vulkan/Unity image inputs differ")
    for name, inputs in (("reference", stage_bytes[0]),
                         ("candidate", stage_bytes[1])):
        if input_hash(*inputs) != metadata[name]["input_sha256"]:
            raise ValueError("Declared input SHA does not bind actual input images")
    dispatch_hash = sha(json.dumps(DISPATCH, sort_keys=True).encode("ascii"))
    for name in ("reference", "candidate"):
        if metadata[name]["dispatch_sha256"] != dispatch_hash:
            raise ValueError("Declared dispatch differs from pinned FFT fixture")
    _identity(b_root / IDENTITY_NAME)
    return {
        **report,
        "actual_both_capture_input_blob_pairs_byte_identical": True,
        "actual_input_bytes_match_paired_manifest_sha": True,
        "exact_pinned_1024x32_seed19_dispatch_declaration_match": True,
        "reported_unity_openglcore_gpu_copyinput_zero_mismatch": True,
        "unity_copyinput_claim_is_not_signed_hardware_attestation": True,
        "unity_compute_shader_or_backend_independently_proven": False,
        "original_author_runtime_kernel_mapping_proven": False,
        "android_adreno_water_proven": False,
        "private_input_bytes_hashes_or_pixels_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--unity", type=Path, required=True)
    p.add_argument("--vulkan-input-dir", type=Path, required=True)
    p.add_argument("--unity-input-dir", type=Path, required=True)
    a = p.parse_args()
    try:
        result = join(a.manifest, a.original, a.unity,
                      a.vulkan_input_dir, a.unity_input_dir)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        p.exit(2, "RAFT_T1_ACTUAL_INPUT_JOIN invalid_private_input_or_gpu_identity=true\n")
    print("RAFT_T1_ACTUAL_INPUT_JOIN " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
