"""Independently check an already-authorized NEXT23b metadata packet.

No asset reader, source acquisition, or Unity execution. A successful check
establishes packet consistency, not authenticity of the input, keyword scope,
program equivalence, or runtime material selection. Private names stay private.
"""
from collections import Counter
from hashlib import sha256
import json

from scripts.gt_runtime_keyword_contract import keyword_set

COUNTS = (512, 4, 128, 512)
PROGRAM_REFS = frozenset(f"program-{i:03d}" for i in range(134))
MODES = {name.upper(): name for name in (
    "Normal", "Always", "ForwardBase", "ForwardAdd", "Deferred", "ShadowCaster")}
# Only the currently supported, provisional composer normalization. This is
# not a statement that Unity supplies these macros at actual runtime.
FIXED = {"ForwardBase": "DIRECTIONAL", "ShadowCaster": "UNITY_PASS_SHADOWCASTER"}


def _require(ok, reason):
    if not ok:
        raise ValueError("next23b_provenance_" + reason)


def _int(value, lower=0, upper=None):
    return type(value) is int and value >= lower and (upper is None or value < upper)


def _mode(state):
    _require(type(state) is dict, "missing_render_state")
    table = state.get("m_Tags")
    tags = table.get("tags") if type(table) is dict else None
    _require(type(tags) is list, "missing_pass_tags")
    found = []
    for pair in tags:
        _require(type(pair) in (list, tuple) and len(pair) == 2
                 and all(type(s) is str for s in pair), "malformed_pass_tag")
        if pair[0].upper() == "LIGHTMODE":
            found.append(MODES.get(pair[1].upper()))
    _require(len(found) <= 1 and (not found or found[0] not in (None, "Normal")),
             "ambiguous_or_unknown_lightmode")
    return found[0] if found else "Untagged"


def _rows(program, expected):
    _require(type(program) is dict, "missing_stage_table")
    legacy = program.get("m_SubPrograms", [])
    player = program.get("m_PlayerSubPrograms", [])
    _require(type(legacy) is list and type(player) is list
             and all(type(bucket) is list for bucket in player), "malformed_stage_table")
    _require(not (legacy and any(player)), "ambiguous_stage_table")
    rows = ({(None, i): item for i, item in enumerate(legacy)} if legacy else
            {(b, i): item for b, bucket in enumerate(player) for i, item in enumerate(bucket)})
    _require(len(rows) == expected and all(type(row) is dict for row in rows.values()),
             "stage_population_drift")
    return rows


def _indices(row, size):
    _require(type(row) is dict, "invalid_stage_metadata")
    for lane in ("m_GlobalKeywordIndices", "m_LocalKeywordIndices"):
        _require(type(row.get(lane, [])) is list and not row.get(lane, []), "separate_scope_unproved")
    ids = row.get("m_KeywordIndices")
    _require(type(ids) is list and all(_int(i, upper=size) for i in ids)
             and len(set(ids)) == len(ids), "invalid_keyword_indices")
    _require(_int(row.get("m_BlobIndex")), "invalid_blob_index")
    return tuple(ids)


def derive_source_contract(source):
    """Rejoin exact stage metadata using original table slots, not route order."""
    _require(type(source) is dict, "invalid_source_packet")
    parsed = source.get("original_shader_ParsedForm_full_private")
    _require(type(parsed) is dict, "missing_parsed_form")
    names, flags = parsed.get("m_KeywordNames"), parsed.get("m_KeywordFlags")
    _require(type(names) is list and 0 < len(names) <= 256, "invalid_keyword_table")
    keyword_set(names)
    _require(type(flags) is list and len(flags) == len(names)
             and all(_int(flag, upper=256) for flag in flags), "invalid_keyword_flags")
    subs = parsed.get("m_SubShaders")
    _require(type(subs) is list and len(subs) == 1 and type(subs[0]) is dict,
             "subshader_population_drift")
    passes = subs[0].get("m_Passes")
    copies, pairs = source.get("original_passes"), source.get("paired")
    _require(type(passes) is list and len(passes) == len(COUNTS)
             and type(copies) is list and len(copies) == len(COUNTS)
             and type(pairs) is list and len(pairs) == sum(COUNTS)
             and source.get("unpaired") == [], "pass_or_pair_population_drift")
    grouped = [[] for _ in COUNTS]
    for pair in pairs:
        _require(type(pair) is dict and type(pair.get("subshader")) is int
                 and pair["subshader"] == 0 and _int(pair.get("pass"), upper=len(COUNTS)),
                 "invalid_pair_owner")
        grouped[pair["pass"]].append(pair)
    expected = []
    all_refs = {"vs": set(), "fs": set()}
    flag_counts = Counter()
    for p, (original, copy, count, group) in enumerate(zip(passes, copies, COUNTS, grouped)):
        _require(type(original) is dict and type(original.get("m_Type")) is int
                 and original["m_Type"] == 0 and type(copy) is dict, "non_normal_serialized_pass")
        _require(type(copy.get("subshader")) is int and copy["subshader"] == 0
                 and type(copy.get("pass")) is int and copy["pass"] == p
                 and type(copy.get("matched_pairs")) is int and copy["matched_pairs"] == count
                 and all(type(copy.get(key)) is int and copy[key] == 0
                         for key in ("unmatched_vertex", "unmatched_fragment"))
                 and len(group) == count, "pass_copy_population_drift")
        mode = _mode(original.get("m_State"))
        _require(copy.get("original_state") == original.get("m_State"), "copied_pass_state_drift")
        tables = {}
        for stage, field, copied in (("vs", "progVertex", "original_vertex_program"),
                                      ("fs", "progFragment", "original_fragment_program")):
            program = original.get(field)
            _require(copy.get(copied) == program, "copied_stage_table_drift")
            tables[stage] = _rows(program, count)
        used = {stage: set() for stage in tables}
        raw_keys = []
        for pair in group:
            stages = []
            for stage in tables:
                row = pair.get(stage)
                _require(type(row) is dict and _int(row.get("bucket_ordinal"))
                         and (row.get("player_bucket") is None or _int(row.get("player_bucket"))),
                         "invalid_pair_stage_slot")
                slot = (row.get("player_bucket"), row["bucket_ordinal"])
                _require(slot in tables[stage] and slot not in used[stage], "duplicate_or_missing_stage_slot")
                metadata = tables[stage][slot]
                _require(row.get("original_variant_metadata") == metadata, "copied_variant_metadata_drift")
                ids = _indices(metadata, len(names))
                ref = row.get("program_ref")
                _require(type(ref) is str and ref in PROGRAM_REFS,
                         "invalid_program_reference")
                all_refs[stage].add(ref)
                used[stage].add(slot)
                stages.append((slot[0], metadata.get("m_ShaderHardwareTier"), ids))
            _require(stages[0] == stages[1], "vertex_fragment_permutation_drift")
            raw_keys.append(frozenset(names[i] for i in stages[0][2]))
        _require(all(used[s] == set(tables[s]) for s in tables), "incomplete_stage_slot_coverage")
        _require(len(set(raw_keys)) == count, "ambiguous_keyword_permutation")
        universe = set().union(*raw_keys)
        flag_counts.update(flags[i] for i, name in enumerate(names) if name in universe)
        fixed = FIXED.get(mode)
        if fixed in universe:
            _require(all(fixed in key for key in raw_keys), "nonconstant_fixed_keyword")
            keys = {key - {fixed} for key in raw_keys}
        else:
            keys = set(raw_keys)
        _require(len(keys) == count and len(keys) == 1 << len(set().union(*keys)),
                 "independent_toggle_lattice_unproved")
        expected.append({"passType": "Normal" if mode in ("Always", "Untagged") else mode,
                         "variants": [{"keywords": sorted(key)} for key in sorted(keys, key=lambda x: sorted(x))]})
    _require(not all_refs["vs"] & all_refs["fs"] and len(all_refs["vs"] | all_refs["fs"]) == 134,
             "distinct_stage_reference_population_drift")
    return {"passes": expected}, {
        "source_packet_consistency_verified": True,
        "source_routes_by_pass": list(COUNTS),
        "paired_source_stage_slots_checked": 2 * sum(COUNTS),
        "used_flag_byte_counts_across_passes": {str(k): v for k, v in sorted(flag_counts.items())},
        "original_keyword_scope_verified": False,
        "original_runtime_keyword_selection_verified": False,
    }


def _manifest_sets(packet):
    _require(type(packet) is dict and type(packet.get("passes")) is list
             and len(packet["passes"]) == len(COUNTS), "invalid_engine_manifest")
    result = []
    for row, count in zip(packet["passes"], COUNTS):
        _require(type(row) is dict and type(row.get("variants")) is list
                 and len(row["variants"]) == count, "engine_route_population_drift")
        keys = []
        for variant in row["variants"]:
            _require(type(variant) is dict and type(variant.get("keywords")) is list,
                     "invalid_engine_route")
            keys.append(keyword_set(variant["keywords"]))
        _require(len(set(keys)) == count, "engine_route_collision")
        result.append((row.get("passType"), set(keys)))
    return result


def bind_candidate_route_manifest(source_bytes, shader_bytes, packet):
    """Compare original packet and generated manifest; commit both byte streams."""
    _require(type(source_bytes) is bytes and 0 < len(source_bytes) <= 128 * 1024 * 1024
             and type(shader_bytes) is bytes and 0 < len(shader_bytes) <= 128 * 1024 * 1024,
             "invalid_private_input_bytes")
    expected, report = derive_source_contract(json.loads(source_bytes))
    _require(_manifest_sets(packet) == _manifest_sets(expected), "engine_manifest_source_mismatch")
    return dict(passes=packet["passes"], schema_version=2,
                source_manifest_sha256=sha256(source_bytes).hexdigest(),
                candidate_sha256=sha256(shader_bytes).hexdigest()), report


def verify_candidate_route_manifest(source_bytes, shader_bytes, packet):
    sealed, report = bind_candidate_route_manifest(source_bytes, shader_bytes, packet)
    _require(type(packet.get("schema_version")) is int and packet["schema_version"] == 2
             and all(packet.get(key) == sealed[key] for key in ("source_manifest_sha256", "candidate_sha256")),
             "candidate_or_source_commitment_mismatch")
    return report


def verify_bundle_metadata(source_bytes, parsed, packet):
    """Compare raw pass tags and used flag bytes, without guessing semantics."""
    source = json.loads(source_bytes)["original_shader_ParsedForm_full_private"]
    _require(type(parsed) is dict, "invalid_bundle_parsed_form")
    names, flags = parsed.get("m_KeywordNames"), parsed.get("m_KeywordFlags")
    if isinstance(flags, (bytes, bytearray)):
        flags = list(flags)
    _require(type(names) is list and type(flags) is list and len(names) == len(flags)
             and all(_int(flag, upper=256) for flag in flags), "invalid_bundle_keyword_flags")
    keyword_set(names)
    actual = dict(zip(names, flags))
    expected = dict(zip(source["m_KeywordNames"], source["m_KeywordFlags"]))
    required = set().union(*(keys for _, routes in _manifest_sets(packet) for keys in routes))
    _require(required <= expected.keys() and required <= actual.keys()
             and all(expected[name] == actual[name] for name in required),
             "bundle_keyword_flag_byte_mismatch")
    subs = parsed.get("m_SubShaders")
    _require(type(subs) is list and len(subs) == 1 and type(subs[0]) is dict,
             "bundle_subshader_population_drift")
    passes = subs[0].get("m_Passes")
    _require(type(passes) is list and len(passes) == len(COUNTS), "bundle_pass_population_drift")
    for original, candidate in zip(source["m_SubShaders"][0]["m_Passes"], passes):
        _require(type(candidate) is dict and type(candidate.get("m_Type")) is int
                 and candidate["m_Type"] == 0
                 and _mode(original.get("m_State")) == _mode(candidate.get("m_State")),
                 "bundle_pass_lightmode_mismatch")
    return {"bundle_serialized_pass_tags_matched": len(COUNTS),
            "bundle_used_keyword_flag_bytes_matched": len(required),
            "original_keyword_scope_verified": False,
            "original_runtime_keyword_selection_verified": False}
