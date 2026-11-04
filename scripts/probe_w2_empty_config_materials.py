"""Empty-config (base-variant) material census — the W2 counters lane for
W3's *announced but unclaimed* option "the 22 empty-config Standard
materials base-variant audit", taken under the owner's explicit take-over
directive for paused/standby peers (W3 stands by awaiting a peer-announced
lane; a heads-up message goes with this delivery).

Grounded definition (W3's per-material keyword report): **empty-config =
``m_ValidKeywords`` is an empty list** — for `Standard`, those materials
render with the base keyword configuration. W3 established the count
(22/674 Standard references); this probe validates it at the committed
HEAD and adds the W2 counters lane around it:

- shader identity resolved via ``m_ParsedForm.m_Name`` (the top-level
  ``m_Name`` is serialized empty in this build — the resolution sink this
  lane documents), with same-file and normalized-external resolution,
- per-shader-name histogram of empty vs configured keyword sets,
- for the Standard empty-config subset: owner distribution,
  m_CustomRenderQueue / m_LightmapFlags histograms, instancing and
  double-sided-GI booleans, m_InvalidKeywords sizes,
  **texture-emptiness split** (all nine Standard slots null = pure default
  vs some bound), all as counters,
- serialized record byte-length histogram (empty vs configured) as the
  shape invariant that lets a loader distinguish them without content.

Counters, booleans, byte-lengths and published shader-name identities only
— no material names, no path IDs, no property values, no colors. Owners
identity-verified against commit HEAD via ``verify_and_hash``.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import sys

from scripts.probe_w2_fullgame_texture_colors import sha256_file, verify_and_hash
from scripts.probe_w2_ui_scaler_census import owner_name_ok

SCHEMA_VERSION = 1
TRUE_FLAG = 1
FALSE_FLAG = 0

_FORBIDDEN = ("m_Texture", "m_Color", "m_Scale", "m_Offset", "m_ParsedForm",
              "m_Floats", "m_TexEnvs")


def _read(obj) -> dict:
    try:
        tree = obj.read_typetree(check_read=False) or {}
    except Exception:
        tree = {}
    return tree if isinstance(tree, dict) else {}


def _shader_identity(tree: dict) -> str:
    if not isinstance(tree, dict):
        return ""
    pf = tree.get("m_ParsedForm")
    if isinstance(pf, dict):
        name = pf.get("m_Name")
        if isinstance(name, str) and name:
            return name
    name = tree.get("m_Name")
    return name if isinstance(name, str) and name else ""


def build_indexes(owner_name: str, env) -> dict:
    """Owner-only shader-name index; hierarchy-free and cheap."""
    index: dict[int, str] = {}
    for obj in env.objects:
        if str(obj.type.name) == "Shader":
            name = _shader_identity(_read(obj))
            index[obj.path_id] = name or "<unnamed-shader>"
    return index


def external_paths(env) -> list[str]:
    file = getattr(env, "file", None)
    out = []
    for ext in getattr(file, "externals", None) or []:
        path = str(getattr(ext, "path", None) or getattr(ext, "name", ""))
        out.append(path.split("/")[-1])
    return out


def resolve_shader(owner_name: str, pptr, indexes: dict, paths: list[str]) -> str:
    if not isinstance(pptr, dict):
        return "<no-shader-pptr>"
    file_id, path_id = pptr.get("m_FileID"), pptr.get("m_PathID")
    if not isinstance(file_id, int) or not isinstance(path_id, int):
        return "<malformed-shader-pptr>"
    if file_id == 0:
        return indexes.get(owner_name, {}).get(path_id, "<unresolvable-same-file>")
    raw_ext = paths[file_id - 1] if 1 <= file_id <= len(paths) else None
    if raw_ext is None:
        return "<out-of-range>"
    ext = str(raw_ext).split("/")[-1]
    ext_index = indexes.get(ext)
    if ext_index is None:
        return "<unresolvable-external>"
    name = ext_index.get(path_id, "<missing-shader-path>")
    return name


def classify_materials(owner_name: str, env, indexes: dict) -> dict:
    paths = external_paths(env)
    out = {
        "materials": 0,
        "standardReferences": 0,
        "standardBaseVariant": 0,
        "baseVariantOwners": collections.Counter(),
        "baseVariantRenderQueueHistogram": collections.Counter(),
        "baseVariantLightmapFlagsHistogram": collections.Counter(),
        "baseVariantInstancingHistogram": collections.Counter(),
        "baseVariantDoubleSidedGIHistogram": collections.Counter(),
        "baseVariantInvalidKeywordSizes": collections.Counter(),
        "baseVariantTextureEmptinessSplit": collections.Counter(),
        "baseVariantRecordByteLengthHistogram": collections.Counter(),
        "configuredRecordByteLengthHistogram": collections.Counter(),
        "shaderNameHistogram": collections.Counter(),
        "keywordEmptyByShaderName": collections.Counter(),
        "unresolvableShaderRefs": 0,
    }
    for obj in env.objects:
        if str(obj.type.name) != "Material":
            continue
        tree = _read(obj)
        if not tree:
            continue
        out["materials"] += 1
        shader = resolve_shader(owner_name, tree.get("m_Shader"), indexes, paths)
        out["shaderNameHistogram"][shader] += 1
        if shader == "Standard":
            out["standardReferences"] += 1
        valid = tree.get("m_ValidKeywords")
        kw_empty = isinstance(valid, list) and len(valid) == 0
        if kw_empty:
            out["keywordEmptyByShaderName"][shader] += 1
        try:
            raw_len = len(obj.get_raw_data())
        except Exception:
            raw_len = -1
        is_base = kw_empty and shader == "Standard"
        if is_base:
            out["standardBaseVariant"] += 1
            out["baseVariantOwners"][owner_name] += 1
            queue = tree.get("m_CustomRenderQueue")
            if isinstance(queue, int):
                out["baseVariantRenderQueueHistogram"][queue] += 1
            lightmap = tree.get("m_LightmapFlags")
            if isinstance(lightmap, int):
                out["baseVariantLightmapFlagsHistogram"][lightmap] += 1
            out["baseVariantInstancingHistogram"][
                TRUE_FLAG if tree.get("m_EnableInstancingVariants") else FALSE_FLAG] += 1
            out["baseVariantDoubleSidedGIHistogram"][
                TRUE_FLAG if tree.get("m_DoubleSidedGI") else FALSE_FLAG] += 1
            invalid = tree.get("m_InvalidKeywords")
            out["baseVariantInvalidKeywordSizes"][
                len(invalid) if isinstance(invalid, list) else -1] += 1
            sp = tree.get("m_SavedProperties")
            tex_envs = sp.get("m_TexEnvs") if isinstance(sp, dict) else None
            if isinstance(tex_envs, list) and tex_envs:
                all_null = all(
                    not (isinstance(v, dict)
                         and (v.get("m_Texture") or {}).get("m_PathID"))
                    for _, v in tex_envs)
                out["baseVariantTextureEmptinessSplit"]["all-slots-null" if all_null
                                                        else "some-bound"] += 1
            else:
                out["baseVariantTextureEmptinessSplit"]["no-slot-entries"] += 1
            if raw_len >= 0:
                out["baseVariantRecordByteLengthHistogram"].update({raw_len: 1})
        elif raw_len >= 0:
            out["configuredRecordByteLengthHistogram"].update({raw_len: 1})
        if shader.startswith("<unresolvable"):
            out["unresolvableShaderRefs"] += 1
    return {k: (dict(v) if isinstance(v, collections.Counter) else v)
            for k, v in out.items()}


def probe(owner_paths: list[Path], repo: Path | None, repo_rel_prefix: str) -> dict:
    import UnityPy

    def verify(owner: Path) -> dict:
        if repo is not None:
            return verify_and_hash(owner, repo, f"{repo_rel_prefix}/{owner.name}")
        return {"sha256": sha256_file(owner), "byte_count": owner.stat().st_size,
                "registered_sha256": None, "identity_kind": "unverified-local"}

    # pass 1: shader-name indexes for every owner
    indexes: dict[str, dict] = {}
    for owner in owner_paths:
        indexes[owner.name] = build_indexes(owner.name, UnityPy.load(str(owner)))
    # pass 2: material classification (fresh loads keep memory bounded)
    owners = {}
    for owner in owner_paths:
        info = verify(owner)
        env = UnityPy.load(str(owner))
        scan = classify_materials(owner.name, env, indexes)
        owners[owner.name] = {**info, **scan}

    def merge(key: str) -> dict:
        merged = collections.Counter()
        for data in owners.values():
            merged.update(data.get(key, {}))
        return dict(merged)

    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "lane": "W2 counters lane of W3's announced-unclaimed option 'the 22 empty-config Standard materials base-variant audit' (owner-authorized takeover of standby-peer work)",
        "definition": {"empty-config": "m_ValidKeywords is an empty list (W3's per-material keyword report bases the 22/674 Standard base-variant notion on exactly this)"},
        "gameWide": {
            "materials": sum(merge("shaderNameHistogram").values()),
            "standardReferences": merge("shaderNameHistogram").get("Standard", 0),
            "keywordEmptyByShaderName": merge("keywordEmptyByShaderName"),
            "standardBaseVariant": sum(d["standardBaseVariant"] for d in owners.values()),
            "baseVariantOwners": merge("baseVariantOwners"),
            "baseVariantRenderQueueHistogram": merge("baseVariantRenderQueueHistogram"),
            "baseVariantLightmapFlagsHistogram": merge("baseVariantLightmapFlagsHistogram"),
            "baseVariantInstancingHistogram": merge("baseVariantInstancingHistogram"),
            "baseVariantDoubleSidedGIHistogram": merge("baseVariantDoubleSidedGIHistogram"),
            "baseVariantInvalidKeywordSizes": merge("baseVariantInvalidKeywordSizes"),
            "baseVariantTextureEmptinessSplit": merge("baseVariantTextureEmptinessSplit"),
            "recordByteLengthHistogram": {
                "baseVariant": merge("baseVariantRecordByteLengthHistogram"),
                "configured": merge("configuredRecordByteLengthHistogram"),
            },
            "unresolvableShaderRefs": sum(d["unresolvableShaderRefs"] for d in owners.values()),
        },
        "owners": owners,
    }
    blob = json.dumps(result, )
    for forbidden in _FORBIDDEN:
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
    owner_files = []
    for name in args.owner:
        if not owner_name_ok(name):
            raise ValueError(f"unsafe owner name: {name}")
        path = Path(args.source) / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"missing or unsafe owner: {name}")
        owner_files.append(path)
    repo = Path(args.repo) if args.repo else None
    if repo is not None and not repo.is_dir():
        raise ValueError(f"repo worktree missing: {repo}")
    result = probe(owner_files, repo, args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    gw = result["gameWide"]
    print(json.dumps({"aggregate_written": str(out),
                      "materials": gw["materials"],
                      "standardReferences": gw["standardReferences"],
                      "standardBaseVariant": gw["standardBaseVariant"],
                      "no_proprietary_payload": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
