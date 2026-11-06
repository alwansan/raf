"""Private-only T1 Unity FFT replay stage and original-derived candidate binding.

Run AFTER the direct-original SPIR-V versus Unity paired invocation gate.
Checks physical source identity, generated candidate manifests and the existing
Unity NUnit's final 'complete' stage. A stage file is UNSIGNED and can be stale
or forged: this does not attest the compiled Unity shader, authored runtime
kernel, same-device numeric parity or Android device pixels. Nothing private
may appear in the printed report or on error.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from scripts.t1_fft_invocation_pair_gate import _read_manifest, _json_no_duplicates
from scripts.t1_fft_private_unity_input_join import _identity
from scripts.t1_fft_readback_parity import read_image
from scripts.t1_fft_trace_compare import INVOCATION_SIZE

ORIGINAL_OBJECT_SHA256 = "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247"
MAX_RESOURCES_BYTES = 8192
MAX_CANDIDATE_BYTES = 512 * 1024
MAX_STAGE_BYTES = 32
ASSET_PREAMBLE = b"#pragma kernel main\n"
HEX = re.compile(r"[0-9a-f]{64}\Z")
PROPERTY = re.compile(r"[A-Za-z_][A-Za-z_0-9]{0,119}\Z")
MANIFEST_FIELDS = {
    "schema_version", "original_fft_object_sha256", "selected_compiled_slots",
    "resources", "original_authored_resource_names_proven",
    "original_runtime_kernel_mapping_proven", "unity_gpu_dispatch_executed",
    "android_device_proven",
}
ROW_FIELDS = {
    "compiled_slot", "candidate_sha256", "expected_group_x",
    "source_property", "butterfly_property", "output_property",
}


def _safe_file(path, max_bytes):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Missing, linked or unsafe private Unity file")
    with path.open("rb") as stream:
        blob = stream.read(max_bytes + 1)
    if not 0 < len(blob) <= max_bytes:
        raise ValueError("Invalid private Unity file bounds")
    return blob


def _physical_sha(path, max_bytes):
    return hashlib.sha256(_safe_file(path, max_bytes)).hexdigest()


def check(project, private_pair_manifest):
    root = Path(project)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Private Unity root must be an existing directory")
    # A private C# test stage marker is NOT a signed execution certificate.
    if _safe_file(root / "T1ReplayStage.txt", MAX_STAGE_BYTES) != b"complete":
        raise ValueError("Private Unity FFT test did not reach complete")
    private_pair_manifest = Path(private_pair_manifest)
    if private_pair_manifest.is_symlink():
        raise ValueError("Private pair metadata symlink")
    pair = _read_manifest(private_pair_manifest)
    if pair["candidate"]["role"] != "unity_compute_spirv" or pair["expected_records_by_site"] != [64, 256, 64]:
        raise ValueError("Private paired candidate did not reach expected Unity role/coverage")
    asset_dir = root / "Assets/T1OriginalDerived"
    if asset_dir.is_symlink() or not asset_dir.is_dir():
        raise ValueError("Unsafe original-derived asset directory")
    sidecar = _safe_file(asset_dir / "PrivateGpuResources.json", MAX_RESOURCES_BYTES)
    obj = json.loads(sidecar.decode("utf-8"), object_pairs_hook=_json_no_duplicates,
                     parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite private field")))
    if not isinstance(obj, dict) or set(obj) != MANIFEST_FIELDS:
        raise ValueError("Bad private GPU resource sidecar")
    if (type(obj["schema_version"]) is not int or obj["schema_version"] != 1 or
            obj["original_fft_object_sha256"] != ORIGINAL_OBJECT_SHA256 or
            obj["selected_compiled_slots"] != [0, 1]):
        raise ValueError("Unknown original FFT candidate source or slot variant")
    for k in ("original_authored_resource_names_proven",
              "original_runtime_kernel_mapping_proven",
              "unity_gpu_dispatch_executed", "android_device_proven"):
        if obj[k] is not False:
            raise ValueError("Original-derived sidecar falsely promotes unproven outcome")
    resources = obj["resources"]
    if not isinstance(resources, list) or len(resources) != 2:
        raise ValueError("Original-derived first two candidate rows missing")
    candidate_paths = []
    for n, row in enumerate(resources):
        if not isinstance(row, dict) or set(row) != ROW_FIELDS:
            raise ValueError("Unsafe candidate row")
        if (type(row["compiled_slot"]) is not int or row["compiled_slot"] != n or
                type(row["expected_group_x"]) is not int or row["expected_group_x"] != 64 or
                not isinstance(row["candidate_sha256"], str) or
                not HEX.fullmatch(row["candidate_sha256"])):
            raise ValueError("Original translated FFT candidate row drift")
        names = [row[x] for x in ("source_property", "butterfly_property", "output_property")]
        if any(not isinstance(x, str) or not PROPERTY.fullmatch(x) for x in names) or len(set(names)) != 3:
            raise ValueError("Private candidate roles missing, malformed or aliased")
        path = asset_dir / ("FFT_Candidate_%02d.compute" % n)
        if _physical_sha(path, MAX_CANDIDATE_BYTES) != row["candidate_sha256"]:
            raise ValueError("Original-derived candidate source bytes changed")
        if not _safe_file(path, MAX_CANDIDATE_BYTES).startswith(ASSET_PREAMBLE):
            raise ValueError("Original-derived candidate kernel preamble missing")
        candidate_paths.append(path)
    if candidate_paths[0].samefile(candidate_paths[1]):
        raise ValueError("Candidate slots share the same physical file")

    trace_shader = root / "Assets/T1TracePass0.compute"
    trace_path = root / "T1UnityCapture/trace.bin"
    if trace_shader.samefile(candidate_paths[0]) or trace_shader.samefile(candidate_paths[1]):
        raise ValueError("Injected trace shader aliases a candidate")
    if _physical_sha(trace_shader, MAX_CANDIDATE_BYTES) != pair["candidate"]["shader_sha256"]:
        raise ValueError("Injected Unity trace shader does not match paired SHA")
    if _physical_sha(trace_path, INVOCATION_SIZE) != pair["candidate"]["trace_sha256"]:
        raise ValueError("Real Unity trace does not match paired SHA")
    # Strict byte length (no oversized/truncated trace) and source-only producer
    # fingerprint of claimed physical copy input, not signed runtime output.
    read_image(trace_path, INVOCATION_SIZE)
    if (root / "T1UnityCapture").is_symlink():
        raise ValueError("Private Unity output directory symlink")
    _identity(root / "T1UnityCapture/input_identity.rgba32f")
    return {
        "status": "private_original_derived_unity_fft_producer_stage_and_candidate_hashes_checked",
        "private_unity_producer_complete_stage_file_verified": True,
        "original_derived_candidate_slots_physically_sha_bound": 2,
        "private_unity_trace_shader_and_output_physically_sha_bound": True,
        "reported_unity_copyinput_identity_required": True,
        "unity_compiler_shader_binary_independently_attested": False,
        "unity_nunit_stage_file_is_signed_attestation": False,
        "actual_original_vs_unity_numeric_parity_proven_here": False,
        "original_authored_runtime_findkernel_proven": False,
        "android_adreno_water_proven": False,
        "private_candidate_symbols_shas_pixels_or_trace_bytes_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--pair-manifest", required=True, type=Path)
    a = p.parse_args()
    try:
        result = check(a.project, a.pair_manifest)
    except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
        p.exit(2, "RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER invalid_or_unattested_private_stage=true\n")
    print("RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
