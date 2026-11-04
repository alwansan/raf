"""Aggregate the serialized stage/variant/constant-buffer topology of the
UltimateWater shaders that still fail the strict water gate.

Purpose: completes the read-only topology hand-off from W4's water-gate
diagnosis (Spectrum needs variant recovery + CB binding; Foam needs CB
binding). The only client-owned outputs so far describe pass counts and
stage byte-sizes; this probe extracts the full *serialized binding tables*
of the two unclaimed shaders:

- per pass and per stage (vertex/fragment): subprogram variant count and
  the per-variant keyword-index tuple (keyword *indices* only — never the
  keyword strings), program-blob index, GPU program type and shader
  requirement mask;
- the complete ``m_CommonParameters`` constant-buffer table: name index,
  byte size, partial-CB flag, parameter counts (vector/matrix/struct/buffer),
  plus the binding table (name index, slot index, array size);
- the pass-to-blob reuse map (which passes share vertex payloads).

Fail-closed: the probe re-derives W4's documented topology (Spectrum:
1 subshader, 7 passes, 2 stage variants each, second variant carrying one
keyword index; Foam: 1 subshader, 2 passes, single variant; Depth Copy:
subshader 0 with 6 passes, all single-variant) and hard-fails on any
deviation. Identity of the single LFS owner (``sharedassets0.assets``) is
verified against its committed-object SHA via ``git show HEAD:<path>``.

Publishable: numeric indices, sizes and counters only — no keyword strings,
no shader source, no property strings, no payload bytes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

from scripts.probe_w2_fullgame_texture_colors import verify_and_hash, validate_owner_names

SCHEMA_VERSION = 1

OWNER = "sharedassets0.assets"

STAGES = ("progVertex", "progFragment")

EXPECTED = {
    "Spectrum-graph": {
        "passes": 7,
        "variants_per_stage": 2,
        "variant_keyword_tuples": [(), (4,)],
        "common_buffers_per_vertex": [3, 3, 3, 3, 2, 3, 3],
        "common_buffers_per_fragment": [1] * 7,
        "fragment_blob_sequence": [5, 6, 7, 8, 9, 10, 11, 12, 16, 17, 18, 19, 20, 21],
        "vertex_blob_sequence": [1, 2, 1, 2, 1, 2, 1, 2, 14, 15, 1, 2, 1, 2],
        "keyword_name_count": 5,
    },
    "Foam-graph": {
        "passes": 2,
        "variants_per_stage": 1,
        "variant_keyword_tuples": [()],
        "common_buffers_per_vertex": [3, 3],
        "common_buffers_per_fragment": [1, 1],
        "vertex_blob_sequence": [1, 4],
        "fragment_blob_sequence": [3, 5],
        "keyword_name_count": 4,
    },
    "DepthCopy-graph": {
        "passes": 6,
        "variants_per_stage": 1,
        "variant_keyword_tuples": [()],
        "common_buffers_per_vertex": [0] * 6,
        "common_buffers_per_fragment": [0] * 6,
        "vertex_blob_sequence": [1] * 6,
        "fragment_blob_sequence": [2, 3, 4, 5, 6, 7],
        "keyword_name_count": 4,
    },
}

POINTER_RE = re.compile(r"oid sha256:([0-9a-f]{64})")


def _common_buffers(prog: dict) -> list[dict]:
    common = prog.get("m_CommonParameters") or {}
    buffers = []
    for cb in common.get("m_ConstantBuffers", []):
        buffers.append(
            {
                "nameIndex": cb["m_NameIndex"],
                "size": cb["m_Size"],
                "partial": bool(cb["m_IsPartialCB"]),
                "vectorParams": len(cb["m_VectorParams"]),
                "matrixParams": len(cb["m_MatrixParams"]),
                "structParams": len(cb["m_StructParams"]),
                "bufferParams": len(cb.get("m_BufferParams", [])),
            }
        )
    return buffers


def _bindings(prog: dict) -> list[dict]:
    common = prog.get("m_CommonParameters") or {}
    return [
        {"nameIndex": b["m_NameIndex"], "slotIndex": b["m_Index"], "arraySize": b["m_ArraySize"]}
        for b in common.get("m_ConstantBufferBindings", [])
    ]


def _variants(prog: dict) -> list[dict]:
    variants = []
    for bucket in prog.get("m_PlayerSubPrograms", []):
        for sub in bucket:
            variants.append(
                {
                    "keywordIndices": list(sub.get("m_KeywordIndices", [])),
                    "blobIndex": sub["m_BlobIndex"],
                    "gpuProgramType": sub["m_GpuProgramType"],
                    "requirements": sub["m_ShaderRequirements"],
                }
            )
    return sorted(variants, key=lambda v: (tuple(v["keywordIndices"]), v["blobIndex"]))


def extract_shader(objects_by_path_id: dict[int, object], path_id: int, gate: str) -> dict:
    if path_id not in objects_by_path_id:
        raise ValueError(f"{gate}: object {path_id} missing from {OWNER}")
    tree = objects_by_path_id[path_id].read_typetree()
    parsed = tree["m_ParsedForm"]
    subshaders = parsed["m_SubShaders"]
    if len(subshaders) == 0:
        raise ValueError(f"{gate}: no subshaders")
    passes = subshaders[0]["m_Passes"]
    keyword_names_count = len(parsed["m_KeywordNames"])
    stages_out = {}
    for stage in STAGES:
        per_pass = []
        for i, p in enumerate(passes):
            prog = p.get(stage)
            if not isinstance(prog, dict) or not prog:
                raise ValueError(f"{gate}: pass {i} missing/stale {stage}")
            variants = _variants(prog)
            if len(variants) != EXPECTED[gate]["variants_per_stage"]:
                raise ValueError(
                    f"{gate}: pass {i} {stage} variant count {len(variants)} "
                    f"!= documented {EXPECTED[gate]['variants_per_stage']}"
                )
            if [tuple(v["keywordIndices"]) for v in variants] != [
                tuple(t) for t in EXPECTED[gate]["variant_keyword_tuples"]
            ]:
                raise ValueError(f"{gate}: pass {i} {stage} keyword-index shapes deviate (fail closed)")
            buffers = _common_buffers(prog)
            bindings = _bindings(prog)
            expected_count_key = (
                "common_buffers_per_vertex" if stage == "progVertex" else "common_buffers_per_fragment"
            )
            expected_counts = EXPECTED[gate].get(expected_count_key)
            if expected_counts is not None and len(buffers) != expected_counts[i]:
                raise ValueError(
                    f"{gate}: pass {i} {stage} common-buffer count {len(buffers)} != {expected_counts[i]}"
                )
            if len(bindings) != len(buffers) or any(
                b["nameIndex"] != buffers[j]["nameIndex"] for j, b in enumerate(bindings)
            ):
                raise ValueError(
                    f"{gate}: pass {i} {stage} binding table does not match the CB table (fail closed)"
                )
            if any(b["arraySize"] != 1 for b in bindings) or any(b["slotIndex"] < 0 for b in bindings):
                raise ValueError(f"{gate}: pass {i} {stage} malformed binding entry")
            per_pass.append(
                {
                    "passIndex": i,
                    "variants": variants,
                    "commonBuffers": buffers,
                    "constantBufferBindings": bindings,
                }
            )
        blob_seq = [v["blobIndex"] for entry_p in per_pass for v in entry_p["variants"]]
        expected_key = (
            "vertex_blob_sequence" if stage == "progVertex" else "fragment_blob_sequence"
        )
        if EXPECTED[gate].get(expected_key) is not None and blob_seq != EXPECTED[gate][expected_key]:
            raise ValueError(
                f"{gate}: {stage} blob-order sequence deviates from the documented topology"
            )
        stages_out[stage] = per_pass
    return {
        "gate": gate,
        "subshaderCount": len(subshaders),
        "passCount": len(passes),
        "keywordNameCount": keyword_names_count,
        "stages": stages_out,
    }


def probe(source: Path, repo: Path, repo_rel_prefix: str) -> dict:
    import UnityPy

    owner_path = source / OWNER
    if owner_path.is_symlink() or not owner_path.is_file():
        raise ValueError(f"missing owner: {owner_path}")
    verify_and_hash(owner_path, repo, f"{repo_rel_prefix}/{OWNER}")
    env = UnityPy.load(str(owner_path))
    objects_by_path_id = {obj.path_id: obj for obj in env.objects}
    gates = {"Spectrum-graph": 2432, "Foam-graph": 2420, "DepthCopy-graph": 2407}
    result = {
        "schema_version": SCHEMA_VERSION,
        "aggregate_only": True,
        "no_proprietary_payload": True,
        "owner": OWNER,
        "gates": {},
    }
    for gate, path_id in gates.items():
        result["gates"][gate] = extract_shader(objects_by_path_id, path_id, gate)
    blob = json.dumps(result)
    for forbidden in ("m_Name", "m_PathID", "m_Shader", "stringTagMap", "m_KeywordNames", "m_ValidKeywords"):
        if forbidden in blob:
            raise ValueError(f"forbidden output key leaked: {forbidden}")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source", required=True, help="original Raft_Data root")
    parser.add_argument("--repo", required=True, help="repo worktree for identity cross-check")
    parser.add_argument("--out", required=True, help="aggregate JSON output path")
    parser.add_argument("--repo-rel-prefix", default="Raft/Raft_Data")
    args = parser.parse_args(argv)
    result = probe(Path(args.source), Path(args.repo), args.repo_rel_prefix.strip("/"))
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"aggregate_written": str(out), "gates": sorted(result["gates"]), "no_proprietary_payload": True}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
