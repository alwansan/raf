"""Stage a private Unity 2021 FFT runtime-kernel selection experiment.

20 original compiled candidates are NOT 20 proven Unity runtime kernel IDs.
This only prepares an isolated project using an *authored* .compute input.
The project and its private manifest MUST NOT be uploaded as CI artifacts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from scripts.b47_compute_kernel_contract import (
    kernel_entrypoint_profile, mask_comments_and_strings, mask_inactive_preprocessor,
)

ORIGINAL_FFT_OWNER_BYTES = 115978112
ORIGINAL_FFT_OWNER_SHA256 = "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"
ORIGINAL_FFT_OBJECT_SHA256 = "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247"
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z_0-9]{0,99}\Z")
MAX_COMPUTE_BYTES = 2_000_000


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_regular(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Required private FFT probe file missing or symlinked")
    return path


def authenticate_owner(owner):
    owner = check_regular(owner)
    if owner.stat().st_size != ORIGINAL_FFT_OWNER_BYTES or sha256_file(owner) != ORIGINAL_FFT_OWNER_SHA256:
        raise ValueError("Original FFT owner bytes/SHA256 mismatch")
    return True


def validate_private_manifest(manifest, compute_bytes):
    """Reject fabricated runtime proof, ambiguous names and selector drift."""
    if not isinstance(manifest, dict) or type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unknown private FFT probe manifest schema")
    if manifest.get("original_fft_object_sha256") != ORIGINAL_FFT_OBJECT_SHA256:
        raise ValueError("Original FFT object provenance mismatch")
    if manifest.get("candidate_provenance") != "B48_SOURCE_SELECTED_COMPILED_CANDIDATES_ONLY":
        raise ValueError("Original source-selected candidate provenance missing")
    if manifest.get("original_unity_kernel_mapping_proven") is not False:
        raise ValueError("Original runtime kernel mapping cannot be asserted before Unity evidence")
    if manifest.get("authored_compute_sha256") != hashlib.sha256(compute_bytes).hexdigest():
        raise ValueError("Authored .compute SHA256 mismatch")
    if not compute_bytes or len(compute_bytes) > MAX_COMPUTE_BYTES or b"\x00" in compute_bytes:
        raise ValueError("Authored .compute text outside bounds")
    try:
        source = compute_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Authored .compute must be UTF-8") from exc
    if not kernel_entrypoint_profile(source)["all_kernel_entrypoints_structural"]:
        raise ValueError("Authored .compute has no unambiguous bounded kernel entrypoints")
    clean = mask_inactive_preprocessor(mask_comments_and_strings(source))
    names = set(re.findall(r"(?m)^\s*#\s*pragma\s+kernel\s+([A-Za-z_]\w*)\b", clean))
    rows = manifest.get("rows")
    if not isinstance(rows, list) or len(rows) != 20:
        raise ValueError("Expected exactly 20 original compiled candidate rows")
    used = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {
            "compiled_slot", "resolution", "bank", "pass_index",
            "expected_group_x", "kernel_name", "keywords",
        }:
            raise ValueError("Private FFT row schema invalid")
        slot, r, bank, stage, x = (row[k] for k in (
            "compiled_slot", "resolution", "bank", "pass_index", "expected_group_x"))
        if any(type(k) is not int for k in (slot, r, bank, stage, x)):
            raise ValueError("FFT selector values must be integers, not bool")
        if r not in (32, 64, 128, 256, 512) or bank not in (0, 1) or stage not in (0, 1):
            raise ValueError("Unproven FFT resolution/bank/pass")
        expected_slot = ((r.bit_length() - 1) - 5) * 2 + bank * 10 + stage
        if slot != expected_slot or slot in used or x != 2 * r:
            raise ValueError("Original compiled-candidate selector or threads drift")
        used.add(slot)
        name = row["kernel_name"]
        if not isinstance(name, str) or not IDENTIFIER.fullmatch(name) or name not in names:
            raise ValueError("Named staged authored kernel absent")
        keywords = row["keywords"]
        if (not isinstance(keywords, list) or len(keywords) > 16 or
                any(not isinstance(k, str) or not IDENTIFIER.fullmatch(k) for k in keywords) or
                len(set(keywords)) != len(keywords)):
            raise ValueError("Private kernel keywords invalid")
    if used != set(range(20)):
        raise ValueError("Incomplete original compiled candidate coverage")
    return {
        "compiled_candidate_rows": len(used),
        "unique_authored_kernel_names": len(set(r["kernel_name"] for r in rows)),
        "source_only_stage": True,
        "original_unity_runtime_mapping_proven": False,
    }


def stage(compute, manifest, editor_source, project):
    """Prepare only; Unity must independently load and run the private project."""
    compute, editor_source, project = check_regular(compute), check_regular(editor_source), Path(project)
    if project.exists() or project.is_symlink():
        raise ValueError("Refusing to overwrite an existing private Unity probe project")
    if compute.suffix != ".compute" or compute.stat().st_size > MAX_COMPUTE_BYTES:
        raise ValueError("Expected bounded authored .compute")
    compute_bytes = compute.read_bytes()
    result = validate_private_manifest(manifest, compute_bytes)
    if editor_source.name != "T1FftKernelRuntimeProbe.cs":
        raise ValueError("Unexpected Unity private Editor source name")
    code = editor_source.read_text(encoding="utf-8")
    if "class T1FftKernelRuntimeProbe" not in code or "original_unity_mapping_proven=false" not in code:
        raise ValueError("Unity Editor probe lacks explicit unproven-identity guard")
    (project / "Assets/T1Private").mkdir(parents=True)
    (project / "Assets/Editor").mkdir()
    (project / "Packages").mkdir()
    (project / "ProjectSettings").mkdir()
    (project / "Assets/T1Private/FFTProbe.compute").write_bytes(compute_bytes)
    (project / "Assets/T1Private/PrivateProbeManifest.json").write_text(
        json.dumps(manifest, sort_keys=True), encoding="utf-8")
    shutil.copyfile(editor_source, project / "Assets/Editor/T1FftKernelRuntimeProbe.cs")
    (project / "Packages/manifest.json").write_text('{"dependencies":{}}\n', encoding="utf-8")
    (project / "ProjectSettings/ProjectVersion.txt").write_text(
        "m_EditorVersion: 2021.3.45f2\n", encoding="utf-8")
    return {
        **result, "staged": True, "actual_unity_import_or_execution": False,
        "android_gpu_executed": False, "original_authored_source_restored": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-owner", type=Path, required=True)
    parser.add_argument("--authored-compute", type=Path, required=True)
    parser.add_argument("--private-manifest", type=Path, required=True)
    parser.add_argument("--probe-csharp", type=Path, default=Path("android-port/Editor/T1FftKernelRuntimeProbe.cs"))
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    authenticate_owner(args.original_owner)
    private = json.loads(check_regular(args.private_manifest).read_text(encoding="utf-8"))
    result = stage(args.authored_compute, private, args.probe_csharp, args.project)
    # Never echo private authored source, kernel identifiers or keywords.
    print("RAFT_T1_UNITY_FFT_STAGE " + json.dumps(
        {"original_owner_sha256_verified": True, **result}, sort_keys=True))


if __name__ == "__main__":
    main()
