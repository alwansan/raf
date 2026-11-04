"""Game-wide UI-scaler census (count level) freeing A2's DISPLAY-003 traversal.

Counts MonoBehaviour instantiations of A2's published display-settings script
identities (``CanvasScaler``, ``Settings``, ``GraphicsSettingsBox``,
``ControlsSettingsBox``) across every serialized owner, resolving cross-file
script references through each owner's externals into the build-wide script
registry in ``globalgamemanagers.assets``.

This intentionally stays *below* A2's reserved lane: no Settings-panel to
Canvas pointer-path traversal, no display-value decoding, no panel patching.
The only per-behaviour payload-adjacent datum published is the **byte-length
of the raw serialized record** (a length histogram), which tells A2 how many
instantiations his pinned record-shape work applies to before he runs it.

Identity of every owner is verified against its committed Git object
(``git show HEAD:<path>``) via
``probe_w2_fullgame_texture_colors.verify_and_hash``. Nothing is published
but counters, histogram keys (byte lengths) and script-class-name keys that
are already published engine metadata on A2's gate.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import re
import sys

from scripts.probe_w2_fullgame_texture_colors import sha256_file, verify_and_hash

SCHEMA_VERSION = 1

TARGET_CLASSES = ("CanvasScaler", "Settings", "GraphicsSettingsBox", "ControlsSettingsBox")
SCRIPT_HOST = "globalgamemanagers.assets"

_FORBIDDEN = ("m_PathID", "m_GameObject", "scaleFactor", "referenceResolution")

_FORBIDDEN_LEAKS_SUBSTRINGS = _FORBIDDEN


def owner_name_ok(name: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_\-.]+\.assets", name)
                or re.fullmatch(r"level[0-9]+", name))


def build_script_registry(env) -> tuple[dict, int]:
    """{pathID: class name} for every MonoScript in the script-host owner."""
    registry: dict[int, str] = {}
    undecodable = 0
    for obj in env.objects:
        if str(obj.type.name) != "MonoScript":
            continue
        try:
            tree = obj.read_typetree(check_read=False) or {}
        except Exception:
            undecodable += 1
            continue
        name = tree.get("m_ClassName")
        registry[obj.path_id] = name if isinstance(name, str) else "?"
    return registry, undecodable


def external_paths(env) -> list[str]:
    """Ordered externals of a single-file environment (fileID = index + 1)."""
    file = getattr(env, "file", None)
    externals = getattr(file, "externals", None) or []
    paths = []
    for ext in externals:
        path = getattr(ext, "path", None) or getattr(ext, "name", "")
        paths.append(str(path))
    return paths


def record_byte_length(obj) -> int:
    try:
        raw = obj.get_raw_data()
    except Exception:
        return -1
    if not isinstance(raw, bytes):
        return -1
    return len(raw)


def scan_owner(env, registry: dict) -> dict:
    targets = set(TARGET_CLASSES)
    counts = collections.Counter()
    histograms = {c: collections.Counter() for c in TARGET_CLASSES}
    external_refs = collections.Counter()
    behaviours = 0
    undecodable_behaviours = 0
    raw_unavailable = 0
    paths = external_paths(env)
    for obj in env.objects:
        if str(obj.type.name) != "MonoBehaviour":
            continue
        behaviours += 1
        try:
            tree = obj.read_typetree(check_read=False) or {}
        except Exception:
            undecodable_behaviours += 1
            continue
        script = tree.get("m_Script")
        if not isinstance(script, dict):
            counts["<no-script-pptr>"] += 1
            continue
        file_id = script.get("m_FileID")
        path_id = script.get("m_PathID")
        class_name = None
        if not isinstance(file_id, int) or not isinstance(path_id, int):
            counts["<malformed-script-pptr>"] += 1
            continue
        if file_id == 0:
            class_name = registry.get(path_id)
            external_refs["same-file"] += 1
        else:
            ext = paths[file_id - 1] if 1 <= file_id <= len(paths) else "<out-of-range>"
            if ext == SCRIPT_HOST:
                class_name = registry.get(path_id)
            external_refs[f"external:{ext}"] += 1
        if class_name in targets:
            counts[class_name] += 1
            length = record_byte_length(obj)
            if length < 0:
                raw_unavailable += 1
            else:
                histograms[class_name][length] += 1
    return {
        "behaviours": behaviours,
        "targetCounts": {c: counts.get(c, 0) for c in TARGET_CLASSES},
        "scriptReferenceBuckets": dict(sorted(external_refs.items())),
        "recordByteLengthHistograms": {c: dict(sorted(h.items())) for c, h in histograms.items()},
        "undecodable_behaviours": undecodable_behaviours,
        "raw_unavailable_target_behaviours": raw_unavailable,
        "otherPptrBuckets": {k: v for k, v in counts.items() if k.startswith("<")},
    }


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    import UnityPy

    def verify(owner: Path) -> dict:
        if repo is not None:
            return verify_and_hash(owner, repo, f"{repo_rel_prefix}/{owner.name}")
        return {"sha256": sha256_file(owner), "byte_count": owner.stat().st_size,
                "registered_sha256": None, "identity_kind": "unverified-local"}

    host = next((p for p in owner_paths if p.name == SCRIPT_HOST), None)
    if host is None:
        raise ValueError(f"script host owner missing from the census: {SCRIPT_HOST}")
    envs: dict[str, object] = {}
    registry, registry_undecodable = build_script_registry(UnityPy.load(str(host)))
    if len(registry) == 0:
        raise ValueError("script host parses to an empty MonoScript registry")

    owners = {}
    for owner in owner_paths:
        if owner.name == SCRIPT_HOST:
            env = envs.get(owner.name)
            if env is None:
                env = UnityPy.load(str(owner))
                envs[owner.name] = env
            info = verify(owner)
        else:
            env = UnityPy.load(str(owner))
            info = verify(owner)
        owners[owner.name] = {**info, **scan_owner(env, registry)}

    total_targets = collections.Counter()
    for data in owners.values():
        for cls, n in data["targetCounts"].items():
            total_targets[cls] += n
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "lane_boundary": "below A2's reserved DISPLAY-003 traversal: counts + record byte-length histograms only",
        "script_host": SCRIPT_HOST,
        "script_host_registry_size": len(registry),
        "script_host_undecodable": registry_undecodable,
        "gameWideTargetTotals": {c: total_targets.get(c, 0) for c in TARGET_CLASSES},
        "owners": owners,
    }
    blob = json.dumps(result)
    for forbidden in _FORBIDDEN_LEAKS_SUBSTRINGS:
        if forbidden in blob:
            raise ValueError(f"forbidden output key leaked: {forbidden}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="original Raft_Data root")
    parser.add_argument("--owner", action="append", required=True, help="serialized owner (repeatable)")
    parser.add_argument("--repo", help="repo worktree for identity cross-check")
    parser.add_argument("--repo-rel-prefix", default="Raft/Raft_Data")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    owners = []
    for name in args.owner:
        if not owner_name_ok(name):
            raise ValueError(f"unsafe owner name: {name}")
        path = Path(args.source) / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owners.append(path)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    result = probe(owners, repo, args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    totals = result["gameWideTargetTotals"]
    print(json.dumps({"aggregate_written": str(out), "owners": len(result["owners"]),
                      "behaviours_scanned": sum(o["behaviours"] for o in result["owners"].values()),
                      "gameWideTargetTotals": totals,
                      "no_proprietary_payload": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
