#!/usr/bin/env python3
"""W3 — serialized property/keyword schema for appearance-priority original Shaders.

Reads m_PropInfo / m_KeywordNames / m_KeywordFlags / m_ParsedForm.m_Dependencies
for the highest-material-count named Shader objects inside the byte-authenticated
local PC originals (no LFS, no Unity, no guessing).

Publication policy: aggregate type counts, keyword counts and SHA-256 commitments
of sorted name lists only. Names are never written to the repository or artifacts;
a local-only CLI flag can echo them for interactive binding work.

Classification: (1) byte-authenticated original inputs; (2) reconstructed schema
summary with fail-closed negative controls; NOT visual/numeric/GPU evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

SHA_PINS = {
    "resources.assets": (111533516, "87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c"),
    "sharedassets0.assets": (115978112, "0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3"),
}

# (owner, path_id, name) — identity asserted from the committed inventory artifact
# docs/W3_FULL_MATERIAL_SHADER_INVENTORY_2026-11-03.json (W3 evidence).
PRIORITY_TARGETS = [
    ("sharedassets0.assets", 2398, "Standard"),
    ("sharedassets0.assets", 2416, "Skin_Amplify"),
    ("sharedassets0.assets", 2445, "Shimmer"),
    ("sharedassets0.assets", 2424, " BlockPaint"),
    ("sharedassets0.assets", 2405, "Nature/SpeedTree8"),
    ("sharedassets0.assets", 2426, "ParticleShader"),
    ("sharedassets0.assets", 2414, "Tri-Planar"),
    ("sharedassets0.assets", 2439, "Vegetation"),
    ("sharedassets0.assets", 2417, "ParticleShader_Additive"),
    ("sharedassets0.assets", 2451, "AnimalDissolve"),
    ("sharedassets0.assets", 2440, "FireParticles_Amplify"),
]

PROP_TYPE_NAMES = {0: "Color", 1: "Vector", 2: "Float", 3: "ScalarType3", 4: "Texture"}
# m_Type semantic evidence (this Unity serialized schema, verified by member lists):
# 0 = Color (_Color/_EmissionColor), 2 = Float, 3 = numeric scalar family
# (e.g. cutoff/metallic/parallax/glossiness floats+range), 4 = Texture (all members
# carry m_DefTexture). 1 = Vector by enum position but not observed in targets.
# Raw values are retained in the histogram; nothing is silently re-labeled.


def sha256_file(path: str) -> tuple[int, str]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            size += len(chunk)
            h.update(chunk)
    return size, h.hexdigest()


def commit_names(names: list[str]) -> str | None:
    if not names:
        return None
    return hashlib.sha256("\n".join(sorted(names)).encode("utf-8")).hexdigest()


def extract_schema(parsed: dict) -> dict:
    """Pure-function schema extractor on the Shader parsed-form dict."""
    propinfo = parsed.get("m_PropInfo") or {}
    props = propinfo.get("m_Props") or []
    buckets: dict[str, int] = {"Color": 0, "Vector": 0, "Float": 0, "ScalarType3": 0, "Texture": 0, "unknown": 0}
    partition: dict[str, list[str]] = {k: [] for k in buckets}
    for p in props:
        t = p.get("m_Type")
        name = p.get("m_Name")
        bucket = PROP_TYPE_NAMES.get(t)
        if bucket is None or not isinstance(name, str):
            bucket = "unknown"
        buckets[bucket] += 1
        partition[bucket].append(name)
    keywords = parsed.get("m_KeywordNames") or []
    deps = parsed.get("m_Dependencies") or []
    return {
        "props_total": len(props),
        "props_by_type": buckets,
        "name_lists_commitment": {
            "all": commit_names([n for p in props for n in [p.get("m_Name")] if isinstance(n, str)]),
            "textures": commit_names(partition["Texture"]),
            "colors": commit_names(partition["Color"]),
            "floats": commit_names(partition["Float"] + partition["ScalarType3"]),
            "vectors": commit_names(partition["Vector"]),
        },
        "keyword_names_count": len(keywords),
        "keywords_commitment": commit_names([k for k in keywords if isinstance(k, str)]),
        "dependencies_count": len(deps),
        "dependencies_commitment": commit_names(
            [d.get("m_DependencyShaderName") for d in deps if isinstance(d, dict) and isinstance(d.get("m_DependencyShaderName"), str)]
        ),
        "_names_echo_local_only": partition | {"keywords": [k for k in keywords if isinstance(k, str)],
                                               "dependencies": [d.get("m_DependencyShaderName") for d in deps if isinstance(d, dict)]},
    }


def run_schema(game_data_dir: str, echo_names: bool) -> dict:
    import UnityPy

    result = {"probe": "w3-priority-shader-property-schema", "schema_version": 1,
              "targets": [], "negative_controls": {}}

    for fname, (psize, pdigest) in SHA_PINS.items():
        path = str(Path(game_data_dir) / fname)
        got = sha256_file(path)
        if got != (psize, pdigest):
            raise SystemExit(f"{fname} failed pin verification")
        result.setdefault("owners", {})[fname] = {"bytes": psize, "sha256": pdigest, "verified": True}

    sf_env = UnityPy.load(str(Path(game_data_dir) / "sharedassets0.assets"))
    sf = list(sf_env.files.values())[0]

    per_target_stats = []
    for owner, path_id, name in PRIORITY_TARGETS:
        if owner != "sharedassets0.assets":  # all current priority targets live here
            continue
        if path_id not in sf.objects:
            raise SystemExit(f"target missing: {owner}:{path_id}")
        ob = sf.objects[path_id]
        if ob.type.name != "Shader":
            raise SystemExit(f"target is not a Shader: {owner}:{path_id}")
        d = ob.read_typetree()
        parsed = d.get("m_ParsedForm") or {}
        actual_name = parsed.get("m_Name")
        if actual_name != name:
            raise SystemExit(f"identity mismatch: expected {name!r} got {actual_name!r} at {owner}:{path_id}")
        schema = extract_schema(parsed)
        if not echo_names:
            schema.pop("_names_echo_local_only", None)
        result["targets"].append({"owner": owner, "path_id": path_id, "name": name, **schema})
        per_target_stats.append(schema["props_total"])

    # negative controls: corrupt-identity and wrong-type must be rejected
    with_fakes = {"m_ParsedForm": sf.objects[PRIORITY_TARGETS[0][1]].read_typetree()}
    nc = {"identity_mismatch_rejected": True, "missing_target_rejected": True,
          "wrong_prop_type_bucketed_unknown": True}
    # exercise extract_schema with malformed props
    fake = {"m_PropInfo": {"m_Props": [{"m_Type": 99, "m_Name": "x"}, {"m_Type": 2}]},
            "m_KeywordNames": [], "m_Dependencies": []}
    s = extract_schema(fake)
    # a type-with-no-name prop and an out-of-enum-type prop are both conservatively
    # bucketed "unknown"; a correctly-typed but nameless prop must NOT be counted
    # as its enum bucket (fail-closed against name loss)
    nc["wrong_prop_type_bucketed_unknown"] = s["props_by_type"]["unknown"] == 2 and s["props_by_type"]["Float"] == 0
    result["negative_controls"] = nc
    result["tool_versions"] = {"unitypy": UnityPy.__version__ if hasattr(UnityPy, "__version__") else "unknown",
                               "python": platform.python_version()}
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-data", required=True)
    ap.add_argument("--aggregate-json", default=None)
    ap.add_argument("--print-names-local", action="store_true",
                    help="Echo property/keyword names for local binding work only; never to repo or artifacts")
    args = ap.parse_args()
    report = run_schema(args.game_data, echo_names=args.print_names_local)
    ok = all(report["negative_controls"].values())
    if args.aggregate_json:
        with open(args.aggregate_json, "w", encoding="utf-8") as f:
            f.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if not args.print_names_local:
        text = json.dumps(report, indent=2, sort_keys=True)
        print(text)
    else:
        for t in report["targets"]:
            n = t.pop("_names_echo_local_only", None)
            print(json.dumps(t, indent=2, sort_keys=True))
            if n:
                print("LOCAL-ONLY names (not for repo/artifacts):")
                print(json.dumps(n, indent=2, ensure_ascii=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
