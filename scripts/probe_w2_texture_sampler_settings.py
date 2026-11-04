"""Aggregate original Texture2D sampler settings across every serialized owner.

Purpose: a further ring of the W2 pale-surface/color-loss chain, beyond color
space: if a port rebuilds texture assets and drops the original sampler
settings (wrap U/V/W, filter mode, anisotropic filtering, mip bias, stripped
mipmaps), surfaces lose their texture handling even when the sRGB/linear
split and color tints are correct — water and tiling surfaces show seams,
smearing or aliasing.

Per owner, only integer counters/enums are emitted:
- texture count;
- wrap U/V/W split and filter-mode split (Unity enums, packaging metadata);
- aniso level split (0..16);
- mip bias zero/non-zero and mips-stripped zero/non-zero counters
  (no float mip-bias values are published).

Fail-closed: enum values outside the engine ranges (wrap/filter 0..3,
aniso 0..16), non-integer enums, or non-finite mip bias hard-fail. Identity
verification is imported from ``probe_w2_fullgame_texture_colors`` — the
registered side always comes from ``git show HEAD:<path>`` (committed object),
stable regardless of LFS hydration state. Output is aggregate-only: no
object names, path IDs, float values or payload bytes.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import math
import sys

from scripts.probe_w2_fullgame_texture_colors import (
    sha256_file,
    validate_owner_names,
    verify_and_hash,
)

SCHEMA_VERSION = 1

WRAP_RANGE = range(0, 4)
FILTER_RANGE = range(0, 4)
ANISO_RANGE = range(0, 17)


def aggregate_owner(owner: Path) -> dict:
    import UnityPy

    env = UnityPy.load(str(owner))
    textures = 0
    wrap_u = collections.Counter()
    wrap_v = collections.Counter()
    wrap_w = collections.Counter()
    filter_mode = collections.Counter()
    aniso = collections.Counter()
    mipbias = {"zero": 0, "nonzero": 0}
    mips_stripped = {"zero": 0, "stripped": 0}

    for obj in env.objects:
        if obj.type.name != "Texture2D":
            continue
        tree = obj.read_typetree()
        settings = tree.get("m_TextureSettings")
        if not isinstance(settings, dict):
            raise ValueError(f"m_TextureSettings missing in {owner.name}")
        for counter, key, allowed in (
            (wrap_u, "m_WrapU", WRAP_RANGE),
            (wrap_v, "m_WrapV", WRAP_RANGE),
            (wrap_w, "m_WrapW", WRAP_RANGE),
            (filter_mode, "m_FilterMode", FILTER_RANGE),
        ):
            value = settings.get(key)
            if not isinstance(value, int) or isinstance(value, bool) or value not in allowed:
                raise ValueError(f"{key} outside engine enum in {owner.name}: {value!r}")
            counter[int(value)] += 1
        level = settings.get("m_Aniso")
        if not isinstance(level, int) or isinstance(level, bool) or level not in ANISO_RANGE:
            raise ValueError(f"m_Aniso outside engine range in {owner.name}: {level!r}")
        aniso[int(level)] += 1
        bias = settings.get("m_MipBias")
        if not isinstance(bias, (int, float)) or isinstance(bias, bool) or not math.isfinite(bias):
            raise ValueError(f"m_MipBias non-finite in {owner.name}: {bias!r}")
        mipbias["nonzero" if bias != 0 else "zero"] += 1
        stripped = tree.get("m_MipsStripped", 0)
        if not isinstance(stripped, int) or isinstance(stripped, bool) or stripped < 0:
            raise ValueError(f"m_MipsStripped invalid in {owner.name}: {stripped!r}")
        mips_stripped["stripped" if stripped > 0 else "zero"] += 1
        textures += 1

    return {
        "texture_count": textures,
        "wrap_u": dict(sorted(wrap_u.items())),
        "wrap_v": dict(sorted(wrap_v.items())),
        "wrap_w": dict(sorted(wrap_w.items())),
        "filter_mode": dict(sorted(filter_mode.items())),
        "aniso": dict(sorted(aniso.items())),
        "mipbias_nonzero": mipbias["nonzero"],
        "mips_stripped": mips_stripped["stripped"],
    }


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    owners = {}
    manifest = {}
    for owner in owner_paths:
        if repo is not None:
            repo_rel = f"{repo_rel_prefix}/{owner.name}"
            info = verify_and_hash(owner, repo, repo_rel)
        else:
            digest = sha256_file(owner)
            info = {
                "sha256": digest,
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
    for forbidden in ("m_Name", "m_PathID", "m_Shader", "m_ValidKeywords", "MipBias"):
        if forbidden in blob:
            raise ValueError(f"forbidden output field leaked: {forbidden}")
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
    owners = []
    for name in validate_owner_names(args.owner):
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owners.append(path)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    result = probe(owners, repo, args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"aggregate_written": str(out), "no_proprietary_payload": True, "owners": len(result["owners"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
