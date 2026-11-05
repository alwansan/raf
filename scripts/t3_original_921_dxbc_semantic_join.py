#!/usr/bin/env python3
"""T3: true compiled DXBC VS->PS semantic/mask coverage for 921-use Shader48.

Private semantic strings remain in ephemeral memory. The public result contains
only allow-listed aggregate counts, never original shader bytes/names/IDs.
No correspondence to SPIR-V Location, interpolation, ShaderLab, or pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import struct

from scripts import t3_original_921_vf_component_bridge as prior
from scripts import t3_original_top_shader_fourpass_translation as fourpass
from scripts.t3_dxbc_signature_contract import summarize_signature

MAX_DXBC_BYTES = 4 * 1024 * 1024
MAX_CHUNKS = 128
MAX_RECORDS = 256
INPUT_CHUNKS = {b"ISGN": 24, b"ISG1": 32}
OUTPUT_CHUNKS = {b"OSGN": 24, b"OSG5": 28, b"OSG1": 32}
SUPPORTED = {**INPUT_CHUNKS, **OUTPUT_CHUNKS}
COUNTER_FIELDS = (
    "original_programs_read", "original_input_records",
    "original_output_records", "original_user_fragment_inputs",
    "original_user_vertex_outputs", "original_matched_semantic_records",
    "original_unmatched_fragment_semantic_records",
    "original_unmatched_fragment_component_lanes",
    "original_matched_semantic_missing_output_component_lanes",
    "original_matched_semantic_type_mismatches",
    "original_unused_vertex_semantic_records",
    "original_input_system_value_records", "original_output_system_value_records",
    "original_fragment_input_mask_components",
    "original_vertex_output_mask_components",
    "original_semantic_header_isgn", "original_semantic_header_isg1",
    "original_semantic_header_osgn", "original_semantic_header_osg5",
    "original_semantic_header_osg1",
    "original_vertex_register_components",
    "original_fragment_register_components",
)


def _u32(data: bytes, at: int) -> int:
    if at < 0 or at + 4 > len(data):
        raise ValueError("truncated_DXBC_signature_field")
    return struct.unpack_from("<I", data, at)[0]


def _chunks(data: bytes):
    if (type(data) is not bytes or not 32 <= len(data) <= MAX_DXBC_BYTES
            or data[:4] != b"DXBC" or _u32(data, 20) != 1
            or _u32(data, 24) != len(data)):
        raise ValueError("untrusted_private_DXBC_container_header")
    count = _u32(data, 28)
    if count == 0 or count > MAX_CHUNKS or 32 + 4 * count > len(data):
        raise ValueError("out_of_bounds_original_DXBC_chunk_table")
    offsets = [_u32(data, 32 + 4 * i) for i in range(count)]
    ranges, chunks = [], {}
    table_end = 32 + count * 4
    for off in offsets:
        if off % 4 or off < table_end or off + 8 > len(data):
            raise ValueError("invalid_original_DXBC_chunk_offset")
        size = _u32(data, off + 4)
        end = off + 8 + size
        if end > len(data) or end <= off + 8:
            raise ValueError("invalid_original_DXBC_chunk_size")
        if any(off < hi and end > lo for lo, hi in ranges):
            raise ValueError("overlapping_original_DXBC_chunks")
        ranges.append((off, end))
        tag = data[off:off + 4]
        if tag in chunks:
            raise ValueError("duplicate_original_DXBC_chunk_tag")
        chunks[tag] = data[off + 8:end]
    if not (b"SHDR" in chunks or b"SHEX" in chunks):
        raise ValueError("original_DXBC_missing_bytecode_chunk")
    return chunks


def _signature(tag: bytes, payload: bytes):
    width = SUPPORTED[tag]
    if len(payload) < 8:
        raise ValueError("truncated_original_signature_header")
    count, header_size = struct.unpack_from("<II", payload, 0)
    if (count > MAX_RECORDS or header_size < 8 or header_size % 4 or
            header_size > len(payload) or
            count * width > len(payload) - header_size):
        raise ValueError("out_of_bounds_original_signature_records")
    names_start = header_size + count * width
    rows = []
    seen = set()
    for i in range(count):
        fields = struct.unpack_from("<" + "I" * (width // 4), payload,
                                    header_size + i * width)
        has_stream = width >= 28
        stream = fields[0] if has_stream else 0
        shifted = 1 if has_stream else 0
        name_off, sem_index, system_value, component_type, reg, mask_word = (
            fields[shifted:shifted + 6])
        min_precision = fields[-1] if width == 32 else 0
        if stream != 0 or min_precision > 16:
            raise ValueError("unsupported_original_signature_stream_or_precision")
        if not names_start <= name_off < len(payload):
            raise ValueError("out_of_bounds_original_signature_semantic_offset")
        end = payload.find(b"\x00", name_off)
        if not name_off < end <= min(len(payload) - 1, name_off + 64):
            raise ValueError("unterminated_or_overlong_original_signature_semantic")
        try:
            semantic = payload[name_off:end].decode("ascii").upper()
        except UnicodeError:
            raise ValueError("non_ascii_original_signature_semantic") from None
        if not semantic[0].isalpha() and semantic[0] != "_":
            raise ValueError("invalid_original_signature_semantic_initial")
        if not all(c.isalnum() or c == "_" for c in semantic):
            raise ValueError("invalid_original_signature_semantic_alphabet")
        mask = mask_word & 0xff
        used_mask = (mask_word >> 8) & 0xff
        if (sem_index > 4095 or system_value > 64 or component_type not in (1, 2, 3)
                or mask == 0 or mask > 15 or used_mask > 15
                or mask_word >> 16
                or (reg > 4095 and not (system_value and reg == 0xffffffff))):
            raise ValueError("invalid_original_signature_mask_register_or_type")
        key = (semantic, sem_index)
        if key in seen:
            raise ValueError("duplicate_original_signature_semantic")
        seen.add(key)
        rows.append({
            "semantic": semantic, "index": sem_index, "system_value": system_value,
            "type": component_type, "register": reg, "mask": mask,
            "used_mask": used_mask, "stream": stream,
        })
    return rows


def read_original_dxbc_signatures(code: bytes):
    """Private object: never include this return value in reports/artifacts."""
    chunks = _chunks(code)
    result = {}
    for side, tags in (("input", INPUT_CHUNKS), ("output", OUTPUT_CHUNKS)):
        selected = [t for t in tags if t in chunks]
        if len(selected) != 1:
            raise ValueError("missing_or_ambiguous_original_DXBC_signature_side")
        tag = selected[0]
        result[side] = _signature(tag, chunks[tag])
        result[side + "_tag"] = tag.decode("ascii")
    return result


def _user_map(rows):
    return {(r["semantic"], r["index"]): r for r in rows if not r["system_value"]}


def compare_original_vf(vertex: dict, fragment: dict):
    """Join *original* declared DXBC names+semantic indices privately."""
    if not (type(vertex) is dict and type(fragment) is dict):
        raise ValueError("invalid_original_DXBC_pair")
    vo, fi = vertex["output"], fragment["input"]
    # Source-free scheduled T3 contract validates register/component occupancy.
    def contract(rows, kind):
        usable = [
            {"kind": kind, "register": r["register"], "mask": r["mask"],
             "system_value": False}
            for r in rows if not r["system_value"]
        ]
        return summarize_signature(usable)[kind]
    vcontract = contract(vo, "output")
    fcontract = contract(fi, "input")
    vm, fm = _user_map(vo), _user_map(fi)
    if len(vm) != sum(not x["system_value"] for x in vo):
        raise ValueError("duplicate_vertex_user_semantic")
    if len(fm) != sum(not x["system_value"] for x in fi):
        raise ValueError("duplicate_fragment_user_semantic")
    missing = set(fm) - set(vm)
    paired = set(fm) & set(vm)
    result = Counter({
        "original_programs_read": 2,
        "original_input_records": len(vertex["input"]) + len(fragment["input"]),
        "original_output_records": len(vertex["output"]) + len(fragment["output"]),
        "original_user_fragment_inputs": len(fm),
        "original_user_vertex_outputs": len(vm),
        "original_matched_semantic_records": len(paired),
        "original_unmatched_fragment_semantic_records": len(missing),
        "original_unmatched_fragment_component_lanes":
            sum(fm[key]["mask"].bit_count() for key in missing),
        "original_matched_semantic_missing_output_component_lanes":
            sum((fm[key]["mask"] & ~vm[key]["mask"]).bit_count() for key in paired),
        "original_matched_semantic_type_mismatches":
            sum(fm[key]["type"] != vm[key]["type"] for key in paired),
        "original_unused_vertex_semantic_records": len(set(vm) - set(fm)),
        "original_input_system_value_records":
            sum(bool(x["system_value"]) for x in vertex["input"] + fragment["input"]),
        "original_output_system_value_records":
            sum(bool(x["system_value"]) for x in vertex["output"] + fragment["output"]),
        "original_fragment_input_mask_components":
            sum(x["mask"].bit_count() for x in fi if not x["system_value"]),
        "original_vertex_output_mask_components":
            sum(x["mask"].bit_count() for x in vo if not x["system_value"]),
        "original_vertex_register_components": vcontract["components"],
        "original_fragment_register_components": fcontract["components"],
    })
    for side in (vertex, fragment):
        for category in ("input", "output"):
            code = side[category + "_tag"].lower()
            result["original_semantic_header_" + code] += 1
    if set(result) - set(COUNTER_FIELDS):
        raise ValueError("unapproved_private_DXBC_semantic_aggregate_shape")
    return {key: int(result[key]) for key in COUNTER_FIELDS}


def classify_original_fourpass(pairs):
    if (type(pairs) is not list or len(pairs) != 4 or
            any(type(p) is not tuple or len(p) != 2 or
                any(type(code) is not bytes or not code for code in p)
                for p in pairs)):
        raise ValueError("not_exact_four_original_DXBC_pass_pairs")
    counts = Counter()
    for v, f in pairs:
        a = read_original_dxbc_signatures(v)
        b = read_original_dxbc_signatures(f)
        row = compare_original_vf(a, b)
        for k in COUNTER_FIELDS:
            counts[k] += row[k]
    if counts["original_programs_read"] != 8:
        raise ValueError("partial_original_DXBC_semantic_extraction")
    return {
        "schema_version": 1,
        "status": "ORIGINAL_921_FOURPASS_DXBC_SEMANTIC_MASK_JOIN_MEASURED",
        "source": "SHA_pinned_original_Unity_D3D11_921_use_Shader48",
        "original_pass_pairs": 4,
        "counts": {k: int(counts[k]) for k in COUNTER_FIELDS},
        "original_DXBC_compiled_semantic_identity_checked": True,
        "original_to_SPIRV_semantic_Location_mapping_verified": False,
        "interpolation_or_ShaderLab_verified": False,
        "Unity_Vulkan_Adreno_pixels_verified": False,
        "private_semantic_names_or_bytecode_published": False,
        "game_assets_changed": False,
    }


def probe(original: Path, manifest: Path):
    # Reuse prior actual six-scene/four-owner SHA source authentication and
    # source original top-921 selector without re-translating known good stages.
    original_counts = {}
    graph = prior.original.load_original(original, manifest,
                                         private_slot_counts=original_counts)
    owner, obj_id = prior.feasibility.selected_high_use(original_counts, graph)
    path = original / "Raft_Data" / owner
    if path.is_symlink() or prior.fingerprint(path) != prior.SHADER_OWNERS[owner]:
        raise ValueError("original_Shader48_owner_SHA_changed")
    import UnityPy
    objects = [o for o in UnityPy.load(str(path)).file.objects.values()
               if o.path_id == obj_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("original_selected_Shader48_identity_drift")
    tree = objects[0].read_typetree()
    platforms = [prior.records(segments) for p, segments in prior.decoded_platforms(tree)
                 if p == 4]
    if len(platforms) != 1:
        raise ValueError("original_D3D11_shader_platform_not_unique")
    parsed, table = tree["m_ParsedForm"], platforms[0]
    baseline = prior.feasibility.summarize(parsed, table)
    if (baseline["original_source_Shader48_pass_count"] != fourpass.SOURCE_NORMAL_PASSES or
        baseline["non_normal_passes_not_stage_linked"] != 0 or
        baseline["matched_vertex_fragment_permutation_pairs"] != fourpass.SOURCE_TOTAL_MATCHED_VARIANTS or
        baseline["unmatched_vertex_permutations"] != fourpass.SOURCE_UNMATCHED_VERTEX or
        baseline["unmatched_fragment_permutations"] != fourpass.SOURCE_UNMATCHED_FRAGMENT):
        raise ValueError("original_921_DXBC_pass_baseline_changed")
    report = classify_original_fourpass(fourpass.exact_pass_samples(parsed, table))
    report.update({
        "original_scenes_SHA_verified": 6, "original_serialized_owners_SHA_verified": 4,
        "original_renderer_material_slot_uses": 921,
        "source_exact_linked_variants_total": fourpass.SOURCE_TOTAL_MATCHED_VARIANTS,
        "source_unmatched_vertex_variants_untranslated": fourpass.SOURCE_UNMATCHED_VERTEX,
    })
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
        a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_original_DXBC_semantic_report_destination")
    try:
        result = probe(a.original, a.manifest)
    except Exception as err:
        result = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "failure_type": type(err).__name__,
                  "private_semantic_names_or_bytecode_published": False,
                  "Unity_Vulkan_Adreno_pixels_verified": False}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")
    print("T3_ORIGINAL_DXBC_SEMANTIC_JOIN " + json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "ORIGINAL_921_FOURPASS_DXBC_SEMANTIC_MASK_JOIN_MEASURED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
