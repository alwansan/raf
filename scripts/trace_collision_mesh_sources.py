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

import UnityPy

from scripts.audit_mesh_stream_dependencies import classify_stream_range, is_pointer

COLLIDER = re.compile(r'Mesh asset path "Assets/Mesh/([^"\\/]+)\.asset"')


def failing_meshes(log: str) -> Counter:
    return Counter(COLLIDER.findall(log))


def scan_original_headers(root: Path, wanted: set[str]) -> tuple[dict, dict]:
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


def summary(failures: Counter, matches: dict, metadata: dict) -> dict:
    if not failures:
        raise ValueError("No collider-failure mesh paths found in the log")
    matched = {name: matches[name] for name in failures if matches.get(name)}
    missing = set(failures) - set(matched)
    return {
        "failure_log_lines": sum(failures.values()),
        "distinct_failed_names": len(failures),
        "matched_distinct_names": len(matched),
        "unmatched_distinct_names": len(missing),
        "ambiguous_names": sum(len(items) > 1 for items in matched.values()),
        "matched_stream_status": dict(Counter(row["stream_status"] for items in matched.values() for row in items)),
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
    args = parser.parse_args()
    failures = failing_meshes(args.log.read_text(encoding="utf-8", errors="replace"))
    matches, metadata = scan_original_headers(args.root, set(failures))
    result = summary(failures, matches, metadata)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print("RAFT_COLLIDER_ORIGINAL_HEADER_COVERAGE " + json.dumps(result, sort_keys=True))
