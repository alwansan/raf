"""Fail-closed, read-only commitment to a local AssetRipper shader export.

This does NOT authenticate that a supplied directory is the full original export.
The only public outputs are numeric counts, hashes, and explicit limited verdicts.
No original shader sources or file paths are emitted.
"""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from scripts.restore_builtin_shaders import archive_sources, exported_shader_identity


class ScopeError(ValueError):
    """A local scope check failed; no candidate is authorized."""


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def _check_expected_counts(actual, expected_shaders, expected_computes):
    # An unpaired expected value does not establish same-stage count consistency.
    if (expected_shaders is None) != (expected_computes is None):
        raise ScopeError("incomplete_expected_counts")
    if expected_shaders is not None:
        if expected_shaders < 0 or expected_shaders != actual["shader_files"]:
            raise ScopeError("reported_shader_count_mismatch")
        if expected_computes < 0 or expected_computes != actual["compute_files"]:
            raise ScopeError("reported_compute_count_mismatch")


def _shader_meta_guid(meta_bytes):
    # Unity .meta GUIDs identify shader references across projects. Never emit them.
    lines = [line for line in meta_bytes.splitlines() if line.strip().startswith(b"guid:")]
    if len(lines) != 1:
        raise ScopeError("invalid_shader_meta_guid")
    match = re.fullmatch(rb"guid:[ \t]*([0-9a-fA-F]{32})[ \t]*", lines[0])
    if match is None:
        raise ScopeError("invalid_shader_meta_guid")
    return match.group(1).lower()


def snapshot(project):
    project = Path(project)
    # A leaf can be ordinary while an ancestor redirects to a different export.
    absolute_project = Path(os.path.abspath(project))
    if any(parent.is_symlink() for parent in (absolute_project, *absolute_project.parents)):
        raise ScopeError("symlinked_project_ancestor")
    if project.is_symlink() or not project.is_dir():
        raise ScopeError("unsafe_project_root")
    assets = project / "Assets"
    if assets.is_symlink() or not assets.is_dir():
        raise ScopeError("missing_or_unsafe_assets_root")

    # Do not silently omit any redirect inside the candidate tree.
    entries = []
    seen_guids = set()
    for path in assets.rglob("*"):
        if path.is_symlink():
            raise ScopeError("redirected_asset_entry")
        if not path.is_file():
            continue
        if path.name.endswith((".shader.meta", ".compute.meta")):
            companion = path.with_name(path.name[:-5])
            if companion.is_symlink() or not companion.is_file():
                raise ScopeError("orphan_shader_meta")
        if path.suffix not in (".shader", ".compute"):
            continue
        meta = path.with_name(path.name + ".meta")
        if meta.is_symlink() or not meta.is_file():
            raise ScopeError("missing_or_unsafe_shader_meta")
        guid = _shader_meta_guid(meta.read_bytes())
        if guid in seen_guids:
            raise ScopeError("duplicate_shader_meta_guid")
        seen_guids.add(guid)
        rel = path.relative_to(assets).as_posix()
        entries.append({
            "path_digest_sha256": _digest(rel.encode("utf-8")),
            "kind": path.suffix[1:],
            "source_sha256": _digest(path.read_bytes()),
            "meta_sha256": _digest(meta.read_bytes()),
        })

    if not entries:
        raise ScopeError("empty_shader_export_inventory")
    entries.sort(key=lambda record: (record["path_digest_sha256"], record["kind"]))
    shaders = sum(record["kind"] == "shader" for record in entries)
    computes = sum(record["kind"] == "compute" for record in entries)
    return {
        "schema_version": 1,
        "scope": "local_snapshot_not_authenticated_complete_export",
        "shader_files": shaders,
        "compute_files": computes,
        "entries": entries,
        "entries_sha256": _digest(_canonical(entries)),
        "original_export_provenance_verified": False,
    }


def verify(project, manifest, expected_shaders=None, expected_computes=None):
    """Verify local snapshot bytes/counts only; never certify full-export origin."""
    actual = snapshot(project)
    if not isinstance(manifest, dict) or set(manifest) != set(actual):
        raise ScopeError("invalid_manifest_shape")
    if manifest != actual:
        raise ScopeError("snapshot_scope_or_content_mismatch")
    _check_expected_counts(actual, expected_shaders, expected_computes)
    return {
        "schema_version": 1,
        "local_snapshot_bytes_unchanged": True,
        "reported_counts_consistent": expected_shaders is not None and expected_computes is not None,
        "shader_files": actual["shader_files"],
        "compute_files": actual["compute_files"],
        "inventory_sha256": actual["entries_sha256"],
        "original_export_provenance_verified": False,
        "built_in_identity_matches_verified": False,
        "ready_for_build": False,
    }



def audit_same_stage_builtin_identities(project, archive_path, expected_shaders, expected_computes):
    """Compare exact SHA-pinned Unity vendor identities on one stable local scope.

    This MUST run on the exported project before restoration, not on a different
    sample or on overwritten shader sources. An operator-supplied scope is not
    independently authenticated as the original full AssetRipper export.
    """
    if expected_shaders is None or expected_computes is None:
        raise ScopeError("stage_requires_paired_expected_counts")
    before = snapshot(project)
    _check_expected_counts(before, expected_shaders, expected_computes)
    archive = Path(archive_path)
    if archive.is_symlink() or not archive.is_file() or archive.stat().st_size > 2 * 1024 * 1024:
        raise ScopeError("invalid_builtin_archive")
    try:
        vendor, _, _ = archive_sources(archive.read_bytes())
    except (ValueError, OSError, KeyError, UnicodeError, EOFError, RuntimeError):
        raise ScopeError("unauthenticated_builtin_archive") from None
    parsed = 0
    matched = 0
    unmatched = 0
    seen_matches = set()
    for path in (Path(project) / "Assets").rglob("*.shader"):
        if path.is_symlink() or not path.is_file():
            raise ScopeError("redirected_asset_entry")
        try:
            identity = exported_shader_identity(path.read_bytes().decode("utf-8-sig"))
        except UnicodeError:
            raise ScopeError("invalid_shader_source_encoding") from None
        except ValueError:
            raise ScopeError("ambiguous_shaderlab_declarations") from None
        if identity is None:
            continue
        parsed += 1
        if identity in vendor:
            if identity in seen_matches:
                raise ScopeError("duplicate_builtin_export_identity")
            seen_matches.add(identity)
            matched += 1
        else:
            unmatched += 1
    after = snapshot(project)
    if before != after:
        raise ScopeError("stage_changed_during_identity_audit")
    return {
        "schema_version": 1,
        "status": "SCOPED_DIAGNOSTIC_ONLY",
        "shader_files": before["shader_files"],
        "compute_files": before["compute_files"],
        "parseable_shaderlab_headers": parsed,
        "unparseable_shaderlab_headers": before["shader_files"] - parsed,
        "builtin_identity_matches": matched,
        "nonbuiltin_headers": unmatched,
        "authenticated_builtin_archive_identities": len(vendor),
        "paired_expected_counts_equal": True,
        "same_scope_bytes_unchanged_during_audit": True,
        "scope_inventory_sha256": before["entries_sha256"],
        "original_export_provenance_verified": False,
        "original_gpu_shader_execution_verified": False,
        "ready_for_build": False,
    }

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--write-local-snapshot", type=Path)
    g.add_argument("--verify-local-snapshot", type=Path)
    g.add_argument("--audit-stage-builtin-archive", type=Path)
    p.add_argument("--expected-shaders", type=int)
    p.add_argument("--expected-computes", type=int)
    args = p.parse_args(argv)
    try:
        if args.audit_stage_builtin_archive:
            result = audit_same_stage_builtin_identities(
                args.project, args.audit_stage_builtin_archive,
                args.expected_shaders, args.expected_computes)
        elif args.write_local_snapshot:
            record = snapshot(args.project)
            _check_expected_counts(record, args.expected_shaders, args.expected_computes)
            if args.write_local_snapshot.is_symlink() or args.write_local_snapshot.exists():
                raise ScopeError("snapshot_output_already_exists")
            # Local operator chooses output path; never publish full raw tree.
            with args.write_local_snapshot.open("x", encoding="utf-8") as out:
                json.dump(record, out, sort_keys=True, indent=2)
                out.write("\n")
            result = {"local_snapshot_created": True,
                      "reported_counts_consistent": args.expected_shaders is not None,
                      "shader_files": record["shader_files"],
                      "compute_files": record["compute_files"],
                      "inventory_sha256": record["entries_sha256"],
                      "original_export_provenance_verified": False}
        else:
            with args.verify_local_snapshot.open(encoding="utf-8") as inp:
                record = json.load(inp)
            result = verify(args.project, record, args.expected_shaders, args.expected_computes)
        print("RAFT_A11_SHADER_EXPORT_SCOPE " + json.dumps(result, sort_keys=True))
    except (ScopeError, ValueError, OSError, json.JSONDecodeError) as exc:
        # Error codes only; never include paths, names, or raw shader source.
        code = str(exc) if isinstance(exc, ScopeError) else "invalid_input"
        print("RAFT_A11_SHADER_EXPORT_SCOPE " + json.dumps({
            "status": "REJECTED", "error_code": code,
            "original_export_provenance_verified": False,
            "ready_for_build": False,
        }, sort_keys=True))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
