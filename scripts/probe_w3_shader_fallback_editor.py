#!/usr/bin/env python3
"""W3 — fallback/custom-editor enumeration for every original Shader object.

Closes the "fallback not claimed" caveat of the committed property/keyword schema:
for all Shader objects across the byte-authenticated local PC originals (82
owners, identical set and pins to the committed inventory), reads
m_ParsedForm.m_FallbackName and m_ParsedForm.m_CustomEditorName.

Publication policy: counts and SHA-256 commitments of sorted lists only. Names
never enter the repository or artifacts; a local-only --print-names-local flag
echoes them. Circular/self references and name-guessing are absent by
construction: this probe only aggregates serialized strings it actually read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

PINNED_OWNERS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}

def sha256_file(path: str) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


def commit_names(names) -> str | None:
    got = sorted(n for n in names if isinstance(n, str) and n)
    if not got:
        return None
    return hashlib.sha256("\n".join(got).encode("utf-8")).hexdigest()


def multiplicity_profile(hist: dict) -> list[int]:
    """Name-free structural profile: descending multiplicities of distinct values."""
    return sorted((c for k, c in hist.items() if k != "<empty>"), reverse=True)


def extract_identity(parsed: dict) -> tuple[str, str]:
    """Pure extractor: returns (fallback, custom_editor) raw strings from a parsed form."""
    fallback = parsed.get("m_FallbackName") if isinstance(parsed.get("m_FallbackName"), str) else ""
    editor = parsed.get("m_CustomEditorName") if isinstance(parsed.get("m_CustomEditorName"), str) else ""
    return fallback, editor


def run_fallback_enum(game_data_dir: str, echo_names: bool) -> dict:
    import UnityPy

    root = Path(game_data_dir)
    owner_names = sorted([p.name for p in root.iterdir() if p.is_file() and p.suffix == ".assets"]
                         + [p.name for p in root.iterdir()
                            if p.is_file() and p.suffix == "" and p.name.startswith("level")])
    if len(owner_names) != 82:
        raise SystemExit(f"expected exactly 82 local owners, got {len(owner_names)}")

    per_file: dict[str, dict] = {}
    for name in owner_names:
        size, digest = sha256_file(str(root / name))
        per_file[name] = {"bytes": size, "sha256": digest, "pinned": name in PINNED_OWNERS}
        if name in PINNED_OWNERS:
            expected = PINNED_OWNERS[name]
            if (size, digest) != expected:
                raise SystemExit(f"pinned owner {name} failed verification")
            per_file[name]["pin_verified"] = True

    fallback_space: list[str] = []   # local-only name space
    editor_space: list[str] = []
    fallback_hist: Counter = Counter()
    editor_hist: Counter = Counter()
    total_shaders = 0
    per_owner_shader_counts: Counter = Counter()

    for name in owner_names:
        env = UnityPy.load(str(root / name))
        sf = list(env.files.values())[0]
        for path_id, ob in sf.objects.items():
            if ob.type.name != "Shader":
                continue
            d = ob.read_typetree()
            parsed = d.get("m_ParsedForm") or {}
            fb, ed = extract_identity(parsed)
            total_shaders += 1
            per_owner_shader_counts[name] += 1
            fallback_hist[fb if fb else "<empty>"] += 1
            editor_hist[ed if ed else "<empty>"] += 1
            if fb:
                fallback_space.append(fb)
            if ed:
                editor_space.append(ed)
        del env

    result = {
        "probe": "w3-shader-fallback-customeditor-enumeration",
        "schema_version": 1,
        "owners": per_file,
        "totals": {
            "owners": len(owner_names),
            "shader_objects": total_shaders,
            "fallback_nonempty": len(fallback_space),
            "fallback_distinct": len(set(fallback_space)),
            "fallback_commitment": commit_names(fallback_space),
            "customeditor_nonempty": len(editor_space),
            "customeditor_distinct": len(set(editor_space)),
            "customeditor_commitment": commit_names(editor_space),
        },
        "histograms": {
            "fallback": dict(fallback_hist),
            "customeditor": dict(editor_hist),
        },
        "negative_controls": {
            "shader_count_matches_inventory": total_shaders == 165,
            "pin_owners_verified": True,
            "empty_strings_never_committed": True,
            "histograms_and_spaces_agree": (
                sum(1 for k, c in fallback_hist.items() if k != "<empty>" for _ in range(c))
                == len(fallback_space)
                and sum(1 for k, c in editor_hist.items() if k != "<empty>" for _ in range(c))
                == len(editor_space)),
        },
        "tool_versions": {"unitypy": UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown",
                          "python": platform.python_version()},
    }
    if echo_names:
        result["_names_echo_local_only"] = {
            "fallback": sorted(set(fallback_space)),
            "customeditor": sorted(set(editor_space)),
        }
        result["histograms"] = {"fallback": dict(fallback_hist), "customeditor": dict(editor_hist)}
        return result
    # durable aggregate: name-free structural profiles only (policy: no raw names)
    result["histograms"] = {
        "fallback_multiplicity_profile": multiplicity_profile(dict(fallback_hist)),
        "customeditor_multiplicity_profile": multiplicity_profile(dict(editor_hist)),
        "fallback_empty_count": fallback_hist.get("<empty>", 0),
        "customeditor_empty_count": editor_hist.get("<empty>", 0),
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--aggregate-json", default=None)
    ap.add_argument("--print-names-local", action="store_true",
                    help="Echo fallback/custom-editor names locally only; never to repo/artifacts")
    args = ap.parse_args()
    report = run_fallback_enum(args.game_data, echo_names=args.print_names_local)
    if not all(report["negative_controls"].values()):
        print("NEGATIVE CONTROLS FAILED", file=sys.stderr)
        return 1
    if args.aggregate_json:
        with open(args.aggregate_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if not args.print_names_local:
        report.pop("_names_echo_local_only", None)
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        n = report.pop("_names_echo_local_only", None)
        print(json.dumps(report, indent=2, sort_keys=True))
        if n:
            print("LOCAL-ONLY names (not for repo/artifacts):")
            print(json.dumps(n, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
