"""Prepare and enforce a *private* SHA/physical-input-bound FFT original-vs-Unity trace pair.

Important producer boundary: original trace MUST originate from the direct
SPIR-V recorder scripts.t1_fft_original_trace_vulkan, not from an HLSL
roundtrip Vulkan trace. The original recorder's evidence sidecar binds its
actual injected-original shader, seed19 physical input dump, dispatch and trace.
The candidate Unity trace comes from T1PrivateFftInputIdentityTests in an
isolated licensed Unity2021 OpenGLCore runner. Source SHA is a file identity
declaration, NOT independent proof of Unity's compiled shader binary.

Only bounded classification and counts leave the private runner; all bytes,
SHA fields, trace record IDs and private shader names remain in scratch.
"""
import argparse
import json
import os
from pathlib import Path

from scripts.t1_fft_invocation_pair_gate import SCHEMA as PAIR_SCHEMA, MAX_METADATA_BYTES
from scripts.t1_fft_private_input_evidence import (
    BYTES, DISPATCH, input_hash, sha,
)
from scripts.t1_fft_private_invocation_pair_report import _contract
from scripts.t1_fft_private_unity_input_join import join
from scripts.t1_fft_readback_parity import read_image
from scripts.t1_fft_trace_compare import INVOCATION_SIZE, decode_invocations

EXPECTED_SITE_COUNTS = [64, 256, 64]
MAX_PRIVATE_SHADER = 512 * 1024
MIN_PRIVATE_SHADER = 20
UNITY_PREAMBLE = b"#pragma kernel main\n"


def private_file(path: Path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Missing or unsafe private FFT producer")
    return path


def safe_trace(path: Path):
    path = private_file(path)
    return read_image(path, INVOCATION_SIZE)


def safe_image(path: Path):
    return read_image(private_file(path), BYTES)


def _stage_images(path: Path):
    path = Path(path)
    if path.is_symlink() or not path.is_dir():
        raise ValueError("Unsafe private FFT input root")
    a = private_file(path / "source.rgba32f")
    b = private_file(path / "butterfly.rgba32f")
    if a.samefile(b):
        raise ValueError("Private FFT input roles alias")
    source, butterfly = safe_image(a), safe_image(b)
    if source == butterfly:
        raise ValueError("Private source and butterfly data indistinguishable")
    return (a, b), (source, butterfly)


def _trace_sites(raw):
    return [len(site) for site in decode_invocations(raw)]


def make_manifest(original_evidence, original_trace, unity_trace,
                  vulkan_input_dir, unity_input_dir, unity_shader):
    """Return private metadata, never returned unredacted to logs."""
    evidence = _contract(private_file(original_evidence), "original_spirv")
    original_path, unity_path = private_file(original_trace), private_file(unity_trace)
    if original_path.samefile(unity_path):
        raise ValueError("Original SPIR-V and Unity trace are aliased")
    original, unity = safe_trace(original_path), safe_trace(unity_path)
    if sha(original) != evidence["trace_sha256"]:
        raise ValueError("Private ORIGINAL keyed trace SHA differs from directly injected SPIR-V sidecar")
    for rows in (evidence["records_by_site"], _trace_sites(original), _trace_sites(unity)):
        if rows != EXPECTED_SITE_COUNTS:
            raise ValueError("Private original/Unity keyed invocation coverage invalid")

    (v_paths, v_bytes), (u_paths, u_bytes) = (
        _stage_images(vulkan_input_dir), _stage_images(unity_input_dir))
    for a, b in zip(v_paths, u_paths):
        if a.samefile(b):
            raise ValueError("Private original/Unity inputs are linked across backends")
    if v_bytes != u_bytes:
        raise ValueError("Original and Unity physical FFT input bytes differ")
    digest = input_hash(*v_bytes)
    if digest != evidence["input_sha256"]:
        raise ValueError("Original SPIR-V independently captured input differs from Vulkan fixture")
    from scripts.t1_fft_private_unity_input_join import _identity
    _identity(Path(unity_input_dir) / "input_identity.rgba32f")

    shader = private_file(unity_shader)
    if shader.stat().st_size < MIN_PRIVATE_SHADER or shader.stat().st_size > MAX_PRIVATE_SHADER:
        raise ValueError("Private Unity trace shader source absent or oversized")
    with shader.open("rb") as stream:
        code = stream.read(MAX_PRIVATE_SHADER + 1)
    if not code.startswith(UNITY_PREAMBLE) or b"SV_DispatchThreadID" not in code:
        raise ValueError("Unity trace program was not generated from expected keyed compute entry")
    dispatch_sha = sha(json.dumps(DISPATCH, sort_keys=True).encode("ascii"))
    if evidence["dispatch_sha256"] != dispatch_sha:
        raise ValueError("Private original SPIR-V dispatch configuration not canonical")
    return {
        "schema": PAIR_SCHEMA,
        "expected_records_by_site": list(EXPECTED_SITE_COUNTS),
        "reference": {
            "role": "original_spirv",
            "shader_sha256": evidence["shader_sha256"],
            "trace_sha256": evidence["trace_sha256"],
            "input_sha256": digest,
            "dispatch_sha256": dispatch_sha,
        },
        "candidate": {
            "role": "unity_compute_spirv",  # declaration, NOT compiled binary attestation
            "shader_sha256": sha(code),
            "trace_sha256": sha(unity),
            "input_sha256": digest,
            "dispatch_sha256": dispatch_sha,
        },
    }


def save_and_join(out, original_evidence, original_trace, unity_trace,
                  vulkan_input_dir, unity_input_dir, unity_shader):
    out = Path(out)
    if out.is_symlink() or out.exists() or not out.parent.is_dir() or out.parent.is_symlink():
        raise ValueError("Private FFT paired manifest target unsafe or occupied")
    meta = make_manifest(original_evidence, original_trace, unity_trace,
                         vulkan_input_dir, unity_input_dir, unity_shader)
    encoded = (json.dumps(meta, sort_keys=True) + "\n").encode("ascii")
    if len(encoded) > MAX_METADATA_BYTES:
        raise ValueError("Private FFT paired manifest length outside expected bound")
    fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as dest:
            dest.write(encoded)
        # Existing independent join must independently re-read the actual
        # reference/Unity physical images, both trace SHAs, role/copy-GPU
        # identity, invocation keys and fixed dispatch SHA before publishing.
        report = join(out, original_trace, unity_trace,
                      vulkan_input_dir, unity_input_dir)
    except BaseException:
        out.unlink(missing_ok=True)
        raise
    return {
        "status": "private_actual_original_spirv_vs_unity_declared_keyed_input_join",
        "actual_direct_original_spirv_trace_source_declared_by_private_producer": True,
        "actual_physical_input_pairs_sha_bound_to_original_private_sidecar": True,
        "actual_gpu_copy_input_report_required": True,
        "original_and_unity_keyed_trace_site_coverage": list(EXPECTED_SITE_COUNTS),
        "unity_gpu_shader_compiled_binary_attested_independently": False,
        "source_authenticity_verified_by_manifest_alone": False,
        "original_runtime_findkernel_mapping_proven": False,
        "android_adreno_water_proven": False,
        "diagnostics": report["diagnostics"],
        "private_shaders_pixels_ids_sha_values_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-evidence", required=True, type=Path)
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--unity", required=True, type=Path)
    p.add_argument("--vulkan-input-dir", required=True, type=Path)
    p.add_argument("--unity-input-dir", required=True, type=Path)
    p.add_argument("--unity-shader", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    a = p.parse_args()
    try:
        result = save_and_join(
            a.manifest, a.original_evidence, a.original, a.unity,
            a.vulkan_input_dir, a.unity_input_dir, a.unity_shader)
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
        p.exit(2, "RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN invalid_or_unproven_evidence=true\n")
    # Differing coordinates are a legitimate diagnostic; do not suppress
    # the report or fail only because the original/candidate differ.
    print("RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
