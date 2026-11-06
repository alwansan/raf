"""T2: verify original external Material Shader pointers against ZIP2 manifest.

All original Unity file names, external paths, GUIDs, shaders and asset bytes
remain in transient CI memory/staging. Only bounded numeric categories leave CI.
A unique basename candidate is NOT Unity GUID or runtime material proof.
"""
import argparse
import csv
import json
import re
import subprocess
from pathlib import Path, PurePosixPath

from scripts.t2_external_pptr_manifest_resolver import resolve_external_target
from scripts.t2_foam_original_external_pptr_graph import (
    FOAM_OWNER, FOAM_PATHID, FOAM_RAW_SHA256,
    MAX_EXTERNALS, MAX_MATERIALS, MAX_OBJECTS, external_provider_key,
)
from scripts.w1_stage_zip2_owners import PINS, ZIP2_SHA, fingerprint, safe, stage

_SHA = re.compile(r"^[0-9a-f]{64}$")
_COLUMNS = ["kind", "bytes", "sha256", "mode", "relative_path_under_Raft"]
_MANIFEST_ROWS = 366
_MANIFEST_BYTES = 7789295609
_MAX_CANDIDATE_BYTES = 256 * 1024 * 1024
_MAX_STAGED_BYTES = 384 * 1024 * 1024


def parse_original_manifest(path):
    """Strictly validate every row; reject malformed unrelated entries too."""
    path = Path(path)
    safe(path)
    if not path.is_file() or not 0 < path.stat().st_size <= 1024 * 1024:
        raise ValueError("original_manifest_missing_or_oversized")
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        if reader.fieldnames != _COLUMNS:
            raise ValueError("original_manifest_columns_drift")
        rows = list(reader)
    if len(rows) != _MANIFEST_ROWS:
        raise ValueError("original_manifest_row_count_drift")
    seen, total, result = set(), 0, []
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(_COLUMNS):
            raise ValueError("original_manifest_row_shape")
        name, sha, raw_size, kind = (
            row["relative_path_under_Raft"], row["sha256"],
            row["bytes"], row["kind"],
        )
        if (not isinstance(name, str) or not name or len(name) > 1024 or
                name.startswith("/") or "\\" in name or "\x00" in name or
                any(part in ("", ".", "..") for part in name.split("/")) or
                any(ch in name for ch in "*?[]\n\r") or
                not _SHA.fullmatch(sha or "") or
                not isinstance(raw_size, str) or
                not re.fullmatch(r"[1-9][0-9]*", raw_size) or
                kind not in ("plain", "split") or
                name in seen):
            raise ValueError("original_manifest_entry_invalid")
        seen.add(name)
        size = int(raw_size)
        if size > 16 * 1024**3:
            raise ValueError("original_manifest_file_size_unbounded")
        total += size
        result.append({"path": name, "sha256": sha, "bytes": size, "kind": kind})
    if total != _MANIFEST_BYTES:
        raise ValueError("original_manifest_total_bytes_drift")
    for name, (size, sha) in PINS.items():
        item = next((r for r in result if r["path"] == name), None)
        if item is None or (item["bytes"], item["sha256"]) != (size, sha):
            raise ValueError("original_four_owner_independent_pins_drift")
    return result


def resolve_unmapped_external_materials(externals, pointers, manifest):
    """Pure categorization: distinguish known four-owner names from unknowns.

    Returns private targets only to caller; caller MUST NOT serialize them.
    """
    if not isinstance(externals, list) or len(externals) > MAX_EXTERNALS or (
            not isinstance(pointers, list) or len(pointers) > MAX_MATERIALS):
        raise ValueError("external_graph_shape")
    result = {"total_external": 0, "known_four_owner": 0,
              "unmapped": 0, "unique_manifest_candidate": 0,
              "no_manifest_candidate": 0, "ambiguous_manifest_candidate": 0}
    targets = []
    for ptr in pointers:
        if (not isinstance(ptr, (tuple, list)) or len(ptr) != 2 or
                any(type(x) is not int or x < 0 for x in ptr)):
            raise ValueError("external_material_pointer_invalid")
        file_id, path_id = ptr
        if file_id == 0 or path_id == 0:
            continue
        result["total_external"] += 1
        if file_id > len(externals):
            raise ValueError("external_material_index_out_of_bounds")
        external = externals[file_id - 1]
        if (not isinstance(external, str) or
                not 0 < len(external) <= 1024 or "\x00" in external):
            raise ValueError("external_untrusted_path")
        if external_provider_key(external) is not None:
            result["known_four_owner"] += 1
            continue
        result["unmapped"] += 1
        basename = external.replace("\\", "/").rsplit("/", 1)[-1]
        candidate = resolve_external_target(basename, manifest)
        if candidate is not None:
            result["unique_manifest_candidate"] += 1
            targets.append((candidate[0], candidate[1], path_id))
        else:
            # Distinguish ambiguous vs truly absent without exporting names.
            matches = [r for r in manifest
                       if PurePosixPath(r["path"]).name.casefold() ==
                       basename.casefold()]
            category = ("ambiguous_manifest_candidate" if len(matches) > 1
                        else "no_manifest_candidate")
            result[category] += 1
    if result["unmapped"] != (result["unique_manifest_candidate"] +
                             result["no_manifest_candidate"] +
                             result["ambiguous_manifest_candidate"]):
        raise ValueError("external_graph_partition_invalid")
    return result, targets


def load_original_foam_material_edges(source):
    import UnityPy
    owner = source / FOAM_OWNER
    safe(owner)
    if not owner.is_file() or fingerprint(owner) != PINS[FOAM_OWNER]:
        raise ValueError("original_foam_owner_bytes_sha_mismatch")
    env = UnityPy.load(str(owner))
    file = env.file
    objs = list(file.objects.values())
    if len(objs) > MAX_OBJECTS or len(file.externals) > MAX_EXTERNALS:
        raise ValueError("original_foam_owner_unbounded")
    pointers, foam_raw_ok = [], False
    for obj in objs:
        if obj.type.name == "Shader" and obj.path_id == FOAM_PATHID:
            import hashlib
            foam_raw_ok = (
                hashlib.sha256(obj.get_raw_data()).hexdigest() == FOAM_RAW_SHA256
            )
        elif obj.type.name == "Material":
            if len(pointers) >= MAX_MATERIALS:
                raise ValueError("material_count_limit")
            ptr = obj.read_typetree()["m_Shader"]
            pointers.append((ptr["m_FileID"], ptr["m_PathID"]))
    if not foam_raw_ok:
        raise ValueError("original_foam_shader_object_not_authenticated")
    return [x.path for x in file.externals], pointers


def stage_and_check_targets(zip2, destination, targets, manifest):
    """Stage a bounded unique set from original pinned bytes; type-check PPtrs.

    No filenames or Unity tracebacks may appear in public output.
    """
    import UnityPy
    lookup = {r["path"]: r for r in manifest}
    unique = {}
    for name, sha, path_id in targets:
        if name not in lookup or lookup[name]["sha256"] != sha:
            raise ValueError("original_manifest_target_drift")
        unique.setdefault(name, set()).add(path_id)
    status = {"unique_target_files": len(unique), "staged_target_files": 0,
              "budget_skipped_target_files": 0, "verified_typed_Shader_PPtrs": 0,
              "verified_non_Shader_or_absent_PathID": 0,
              "target_not_readable_as_SerializedFile": 0}
    consumed = 0
    for name in sorted(unique):
        info = lookup[name]
        size = info["bytes"]
        if (size > _MAX_CANDIDATE_BYTES or
                consumed + size > _MAX_STAGED_BYTES):
            status["budget_skipped_target_files"] += 1
            continue
        # git sparse-checkout uses patterns; no path is shell-expanded.
        patterns = ["/Raft/" + name]
        if info["kind"] == "split":
            patterns.append("/Raft/" + name + "/*")
        process = subprocess.run(
            ["git", "-C", str(zip2), "sparse-checkout", "add", "--no-cone",
             *patterns],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            timeout=180, check=False,
        )
        if process.returncode != 0:
            raise ValueError("private_source_sparse_checkout_unavailable")
        target_dest = destination / name
        # stage() checks manifest exact row, full size, SHA and ordered parts.
        stage(zip2, destination, {name: (size, info["sha256"])})
        safe(target_dest)
        if fingerprint(target_dest) != (size, info["sha256"]):
            raise ValueError("private_target_byte_authentication_mismatch")
        consumed += size
        status["staged_target_files"] += 1
        try:
            target_file = UnityPy.load(str(target_dest)).file
            objs = list(target_file.objects.values())
            if len(objs) > MAX_OBJECTS:
                raise ValueError("private_target_objects_unbounded")
            shaders = {int(o.path_id) for o in objs if o.type.name == "Shader"}
        except (ValueError, RuntimeError, AttributeError, EOFError, KeyError):
            status["target_not_readable_as_SerializedFile"] += 1
            continue
        for path_id in unique[name]:
            key = ("verified_typed_Shader_PPtrs" if path_id in shaders
                   else "verified_non_Shader_or_absent_PathID")
            status[key] += 1
    status["verified_bytes_staged"] = consumed
    return status


def run(zip2, source, destination):
    zip2, source, destination = map(lambda p: Path(p).absolute(),
                                    (zip2, source, destination))
    safe(zip2)
    safe(source)
    safe(destination)
    if source.is_relative_to(zip2) or destination.is_relative_to(zip2):
        raise ValueError("original_source_and_scratch_must_be_separate")
    actual = subprocess.check_output(
        ["git", "-C", str(zip2), "rev-parse", "HEAD"],
        text=True, stderr=subprocess.DEVNULL, timeout=15,
    ).strip()
    if actual != ZIP2_SHA:
        raise ValueError("original_provider_revision_not_pinned")
    manifest = parse_original_manifest(zip2 / "RAFT_FILE_MANIFEST.tsv")
    externals, pointers = load_original_foam_material_edges(source)
    counts, targets = resolve_unmapped_external_materials(
        externals, pointers, manifest,
    )
    if counts["total_external"] != 7 or counts["known_four_owner"] != 5 or (
            counts["unmapped"] != 2):
        raise ValueError("original_four_owner_external_baseline_drift")
    staged = stage_and_check_targets(zip2, destination, targets, manifest)
    return {
        "status": "source_original_external_PPtr_manifest_verified",
        "original_zip2_commit_authenticated": True,
        "original_manifest_366_rows_bytes_authenticated": True,
        "original_sharedassets0_SHA_authenticated": True,
        "original_Foam_Shader_object_SHA_authenticated": True,
        "original_material_count": len(pointers),
        **counts, **staged,
        "basename_candidate_is_verified_Unity_GUID": False,
        "verified_typed_target_is_proven_runtime_material": False,
        "original_Foam_CB0_upload_verified": False,
        "Android_Adreno_water_pixels_verified": False,
        "private_path_GUID_shader_or_raw_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip2", type=Path, required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--destination", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    stage_name = "source_input"
    try:
        out = args.out.absolute()
        safe(out)
        if (out.exists() or not out.parent.is_dir() or
                out.is_relative_to(args.source.absolute()) or
                out.is_relative_to(args.zip2.absolute())):
            raise ValueError("unsafe_public_output")
        stage_name = "private_original_manifest_and_typecheck"
        report = run(args.zip2, args.source, args.destination)
        stage_name = "safe_count_only_report"
        out.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        print("T2_ORIGINAL_MANIFEST_PPTR_SAFE " + json.dumps(report, sort_keys=True))
        return 0
    except BaseException:
        # Never print exception messages, Unity source paths, private names,
        # UnityPy traces, subprocess stderr or any original byte fragments.
        print("T2_ORIGINAL_MANIFEST_PPTR_SAFE " + json.dumps({
            "status": "blocked", "safe_phase": stage_name,
            "private_source_disclosed": False,
        }, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
