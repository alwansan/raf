#!/usr/bin/env python3
"""Correlate Unity collider mesh import errors to original serialized Mesh headers.

Read-only; does not open mesh stream payloads, execute game code or publish assets.
Matches are structural clues, not proof that a restored .resS fixes a collider.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

try:
    from scripts.audit_mesh_stream_dependencies import classify_stream_range, is_pointer
except ModuleNotFoundError:
    from audit_mesh_stream_dependencies import classify_stream_range, is_pointer

COLLIDER = re.compile(r'Mesh asset path "Assets/Mesh/([^"\\/]+)\.asset"')


def failing_meshes(log: str) -> Counter:
    return Counter(COLLIDER.findall(log))


def scan_original_headers(root: Path, wanted: set[str]) -> tuple[dict, dict]:
    import UnityPy
    matches: dict[str, list[dict]] = defaultdict(list)
    errors: Counter = Counter()
    skipped: list[str] = []
    for file in sorted(root.glob("sharedassets*.assets")) + sorted(root.glob("resources.assets")):
        if is_pointer(file):
            skipped.append(file.name)
            continue
        try:
            environment = UnityPy.load(str(file))
            for item in environment.objects:
                if getattr(item.type, "name", "") != "Mesh":
                    continue
                try:
                    tree = item.read_typetree()
                    name = str(tree.get("m_Name", ""))
                    if name not in wanted:
                        continue
                    stream = tree.get("m_StreamData") or {}
                    reference = str(stream.get("path") or stream.get("m_Path") or "")
                    offset = int(stream.get("offset") if stream.get("offset") is not None else stream.get("m_Offset", 0))
                    size = int(stream.get("size") if stream.get("size") is not None else stream.get("m_Size", 0))
                    matches[name].append({
                        "source": file.name,
                        "original_path_id": item.path_id,
                        "stream_file": Path(reference.replace("\\", "/")).name if reference else "",
                        "stream_status": classify_stream_range(root, reference, offset, size) if reference and size else "inline-or-empty",
                        "stream_offset": offset,
                        "stream_size": size,
                    })
                except Exception as exc:
                    errors["mesh:" + type(exc).__name__] += 1
        except Exception as exc:
            errors["load:" + type(exc).__name__] += 1
    return dict(matches), {"skipped_lfs_header_files": skipped, "parse_errors": dict(errors)}


def recovery_ranges(root: Path, failures: Counter, matches: dict) -> dict:
    """Private exact range ledger; no payload reads and no download instructions.

    Keep ambiguous name matches visible. Merge overlaps for byte accounting only;
    the whole LFS object still has to be obtained and verified before use.
    """
    providers = defaultdict(list)
    rejected = Counter()
    for name in sorted(failures):
        for row in matches.get(name, []):
            stream = row.get("stream_file", "")
            if row.get("stream_status") != "lfs-pointer":
                continue
            if not stream or Path(stream).name != stream or "\\" in stream or ":" in stream:
                rejected["unsafe-provider"] += 1
                continue
            pointer = root / stream
            if not pointer.is_file() or not is_pointer(pointer):
                rejected["missing-pointer"] += 1
                continue
            payload = pointer.read_text(encoding="ascii")
            oid = re.search(r"(?m)^oid sha256:([0-9a-f]{64})$", payload)
            declared = re.search(r"(?m)^size (\d+)$", payload)
            if not oid or not declared:
                rejected["invalid-pointer"] += 1
                continue
            offset, size = row.get("stream_offset"), row.get("stream_size")
            if (type(offset) is not int or type(size) is not int or offset < 0 or
                    size <= 0 or offset + size > int(declared.group(1))):
                rejected["invalid-declared-range"] += 1
                continue
            providers[stream].append(dict(row, mesh_name=name,
                ambiguous_name=len(matches[name]) > 1, lfs_sha256=oid.group(1),
                lfs_declared_bytes=int(declared.group(1))))
    result = []
    for stream, rows in sorted(providers.items()):
        intervals = []
        for start, end in sorted((r["stream_offset"], r["stream_offset"] + r["stream_size"]) for r in rows):
            if intervals and start <= intervals[-1][1]:
                intervals[-1][1] = max(intervals[-1][1], end)
            else:
                intervals.append([start, end])
        result.append({"stream": stream, "lfs_sha256": rows[0]["lfs_sha256"],
                       "lfs_declared_bytes": rows[0]["lfs_declared_bytes"],
                       "distinct_names": len({r["mesh_name"] for r in rows}),
                       "unique_mesh_range_bytes": sum(end-start for start, end in intervals),
                       "merged_range_count": len(intervals), "meshes": rows})
    return {"providers": result, "rejected_rows": dict(rejected)}


def summary(failures: Counter, matches: dict, metadata: dict, root: Path | None = None) -> dict:
    if not failures:
        raise ValueError("No collider-failure mesh paths found in the log")
    matched = {name: matches[name] for name in failures if matches.get(name)}
    missing = set(failures) - set(matched)
    sources: dict[str, set[str]] = defaultdict(set)
    for name, rows in matched.items():
        for row in rows:
            stream = row.get("stream_file")
            if row["stream_status"] == "lfs-pointer" and stream:
                sources[stream].add(name)
    priorities = []
    for stream, names in sources.items():
        advertised = None
        if root is not None:
            pointer = root / stream
            if pointer.is_file() and is_pointer(pointer):
                match = re.search(r"(?m)^size (\d+)$", pointer.read_text(encoding="ascii"))
                if match:
                    advertised = int(match.group(1))
        priorities.append({
            "stream": stream,
            "lfs_declared_bytes": advertised,
            "matching_distinct_collider_names": len(names),
            "matching_collider_error_lines": sum(failures[name] for name in names),
            "distinct_names_per_100_MiB": round(len(names) * 104857600 / advertised, 3)
            if advertised else None
        })
    priorities.sort(key=lambda row: (
        -(row["distinct_names_per_100_MiB"] or 0),
        -row["matching_distinct_collider_names"], row["stream"]))
    return {
        "failure_log_lines": sum(failures.values()),
        "distinct_failed_names": len(failures),
        "matched_distinct_names": len(matched),
        "unmatched_distinct_names": len(missing),
        "ambiguous_names": sum(len(items) > 1 for items in matched.values()),
        "matched_stream_status": dict(Counter(row["stream_status"] for items in matched.values() for row in items)),
        "stream_lfs_priorities": priorities,
        "matched_original_sources": dict(Counter(row["source"] for items in matched.values() for row in items)),
        "skipped_lfs_original_header_count": len(metadata["skipped_lfs_header_files"]),
        "source_parse_errors": metadata["parse_errors"],
        "caveat": "Header-only exact name lookup on source files present without LFS. An unmatched name is not proof of missing game data; a source header may itself be an LFS pointer.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--details-out", type=Path, help="Private per-object range ledger; never printed")
    args = parser.parse_args()
    failures = failing_meshes(args.log.read_text(encoding="utf-8", errors="replace"))
    matches, metadata = scan_original_headers(args.root, set(failures))
    result = summary(failures, matches, metadata, args.root)
    nonfinite = failing_meshes("\n".join(line for line in args.log.read_text(
        encoding="utf-8", errors="replace").splitlines() if "contains a non-finite value" in line))
    ledger = recovery_ranges(args.root, nonfinite, matches)
    result["nonfinite_distinct_names"] = len(nonfinite)
    result["nonfinite_range_rejections"] = ledger["rejected_rows"]
    result["nonfinite_stream_ranges"] = [{k: v for k, v in provider.items()
        if k not in ("meshes", "lfs_sha256")} for provider in ledger["providers"]]
    if args.details_out:
        args.details_out.parent.mkdir(parents=True, exist_ok=True)
        args.details_out.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf8")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print("RAFT_COLLIDER_ORIGINAL_HEADER_COVERAGE " + json.dumps(result, sort_keys=True))

