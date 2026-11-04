"""Aggregate original Material scalar-property usage across every serialized
owner.

Purpose: ring 9 of the W2 pale-surface chain. Beyond textures, tints and
sampler settings, a rebuilt material document must also carry the original
scalar property set (``m_SavedProperties.m_Floats`` / ``m_Ints``) with the
same property-name coverage. If an exporter drops scalar properties
(e.g. ``_Cutoff``, ``_Metallic``, ``_Glossiness``, blend ``_Mode``),
surfaces lose alpha-cut transparency, metal/roughness and render-mode
behavior even when everything else is correct.

Per owner, only name-keyed integer counters are emitted (property names are
engine packaging metadata; the float/int VALUES themselves are never
published):
- material count;
- materials using zero scalars;
- ``floats_by_name`` / ``ints_by_name`` usage counters;
- explicit ``inf`` sentinel counter per name (original data uses
  non-finite sentinels), NaN hard-fails.

Identity verification and the 82-owner enumeration rule are reused from
``probe_w2_fullgame_texture_colors`` (committed-object identity via
``git show HEAD:<path>``). No object names, path IDs, float values or
payload bytes are published.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import sys
from typing import Any

from scripts.probe_w2_fullgame_texture_colors import (
    sha256_file,
    validate_owner_names,
    verify_and_hash,
)
from scripts.probe_w2_material_tint_stats import VALUE_SCANNER

SCHEMA_VERSION = 1

_FORBIDDEN_COMPONENTS = ("m_Name", "m_PathID", "m_Shader", "m_ValidKeywords", "stringTagMap")


def assert_no_float_literals(blob: str) -> None:
    """Reject any decimal float literal that could carry a payload value."""
    for match in VALUE_SCANNER.findall(blob):
        raise ValueError(f"float literal leaked into scalar-property aggregate: {match}")


def _scalar_value(value: Any) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"non-numeric scalar property value: {value!r}")
    if isinstance(value, float) and value != value:  # NaN
        raise ValueError("NaN scalar property value must fail closed")


def aggregate_owner(owner: Path) -> dict:
    import UnityPy

    env = UnityPy.load(str(owner))
    materials = 0
    materials_without_scalars = 0
    floats_by_name: collections.Counter = collections.Counter()
    ints_by_name: collections.Counter = collections.Counter()
    inf_floats_by_name: collections.Counter = collections.Counter()

    for obj in env.objects:
        if obj.type.name != "Material":
            continue
        saved = obj.read_typetree().get("m_SavedProperties")
        if not isinstance(saved, dict):
            raise ValueError(f"m_SavedProperties missing in {owner.name}")
        for key, counter in (("m_Floats", floats_by_name), ("m_Ints", ints_by_name)):
            entries = saved.get(key)
            if not isinstance(entries, list):
                raise ValueError(f"{key} missing in {owner.name}")
        used = False
        for entry in saved.get("m_Floats", []):
            if not isinstance(entry, (list, tuple)) or len(entry) != 2 or not isinstance(entry[0], str):
                raise ValueError(f"unexpected m_Floats entry shape in {owner.name}")
            _scalar_value(entry[1])
            name = entry[0]
            floats_by_name[name] += 1
            used = True
            if isinstance(entry[1], float) and entry[1] in (float("inf"), float("-inf")):
                inf_floats_by_name[name] += 1
        for entry in saved.get("m_Ints", []):
            if not isinstance(entry, (list, tuple)) or len(entry) != 2 or not isinstance(entry[0], str):
                raise ValueError(f"unexpected m_Ints entry shape in {owner.name}")
            _scalar_value(entry[1])
            ints_by_name[entry[0]] += 1
            used = True
        if not used:
            materials_without_scalars += 1
        materials += 1

    return {
        "material_count": materials,
        "materials_without_scalars": materials_without_scalars,
        "float_names": len(floats_by_name),
        "int_names": len(ints_by_name),
        "floats_by_name": dict(sorted(floats_by_name.items())),
        "ints_by_name": dict(sorted(ints_by_name.items())),
        "inf_floats_by_name": dict(sorted(inf_floats_by_name.items())),
    }


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    owners = {}
    manifest = {}
    for owner in owner_paths:
        if repo is not None:
            info = verify_and_hash(owner, repo, f"{repo_rel_prefix}/{owner.name}")
        else:
            info = {
                "sha256": sha256_file(owner),
                "byte_count": owner.stat().st_size,
                "registered_sha256": None,
                "identity_kind": "unverified-local",
            }
        manifest[owner.name] = info
        owners[owner.name] = aggregate_owner(owner)
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "owner_manifest": manifest,
        "owners": owners,
    }
    blob = json.dumps(result)
    for forbidden in _FORBIDDEN_COMPONENTS:
        if forbidden in blob:
            raise ValueError(f"forbidden output field leaked: {forbidden}")
    assert_no_float_literals(blob)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="original Raft_Data root")
    parser.add_argument("--owner", action="append", required=True, help="serialized owner file (repeatable)")
    parser.add_argument("--repo", help="optional repo worktree for identity cross-check")
    parser.add_argument(
        "--repo-rel-prefix",
        default="Raft/Raft_Data",
        help="repo-relative directory prefix of the owners (default Raft/Raft_Data)",
    )
    parser.add_argument("--out", required=True, help="aggregate JSON path")
    args = parser.parse_args(argv)
    source = Path(args.source)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    owners = []
    for name in validate_owner_names(args.owner):
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owners.append(path)
    result = probe(owners, repo, args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"aggregate_written": str(out), "no_proprietary_payload": True, "owners": len(result["owners"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
