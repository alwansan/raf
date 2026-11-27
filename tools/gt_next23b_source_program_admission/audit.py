"""Private NEXT23b source-slot -> actual DXBC bytes admission edge.

Caller must independently authenticate rights, immutable source owner/object,
typed class48 PathID, and obtain ParsedForm and D3D11 decompressed segments
from that same object. This module does not fetch, parse a Unity owner, grant
permission, run translators, or establish semantic/compiled-route equivalence.
All inputs and detailed witnesses stay private. Never upload them.
"""
from hashlib import sha256
import json
import re
import struct

from scripts.gt_next23b_route_provenance import (
    COUNTS, PROGRAM_REFS, derive_source_contract,
)
from scripts.probe_original_compute_containers import scan_blob
from scripts.run_original_dxbc_translation_probe import version_tokens

MAX_SEGMENT = 128 * 1024 * 1024
MAX_RECORDS = 100000
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def require(ok, category):
    if not ok:
        raise ValueError("next23b_source_bytes_" + category)


def digest(data):
    return sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("ascii")


def same(a, b):
    # Avoid Python bool == int and other cross-type dictionary equalities.
    return canonical(a) == canonical(b)


def source_identity(identity, source):
    require(type(identity) is dict and set(identity) == {
        "source_commit", "owner", "owner_sha256", "object_sha256",
        "class_id", "path_id", "platform_code",
    }, "missing_independent_identity")
    require(type(identity["source_commit"]) is str
            and HEX40.fullmatch(identity["source_commit"])
            and all(type(identity[k]) is str and HEX64.fullmatch(identity[k])
                    for k in ("owner_sha256", "object_sha256"))
            and type(identity["owner"]) is str and bool(identity["owner"])
            and type(identity["class_id"]) is int and identity["class_id"] == 48
            and type(identity["path_id"]) is int and identity["path_id"] != 0
            and -(1 << 63) <= identity["path_id"] < (1 << 63)
            and type(identity["platform_code"]) is int
            and identity["platform_code"] == 4, "invalid_independent_identity")
    require(type(source.get("source_PathID")) is int
            and source["source_PathID"] == identity["path_id"]
            and source.get("source_owner") == identity["owner"],
            "source_owner_pathid_mismatch")


def table_ranges(segments):
    # Independently rejoin the offsets, lengths and segment indices, not
    # a packet-supplied blob table or program ordinal.
    require(type(segments) in (list, tuple) and 0 < len(segments) <= 128
            and all(type(s) is bytes and 0 < len(s) <= MAX_SEGMENT
                    for s in segments), "invalid_segments")
    table = segments[0]
    require(len(table) >= 4, "truncated_table")
    count, = struct.unpack_from("<I", table)
    end = 4 + 12 * count
    require(0 < count <= MAX_RECORDS and end <= len(table), "invalid_table_count")
    ranges = []
    for index in range(count):
        offset, length, segment = struct.unpack_from("<III", table, 4 + 12 * index)
        require(segment < len(segments) and length > 0
                and offset + length <= len(segments[segment])
                and (segment != 0 or offset >= end), "invalid_entry_range")
        ranges.append((segment, offset, length))
    return ranges


def actual_program(segments, ranges, blob, stage):
    require(type(blob) is int and 0 <= blob < len(ranges), "invalid_blob_index")
    segment, offset, length = ranges[blob]
    entry = segments[segment][offset:offset + length]
    matches = scan_blob(entry)["valid_dxbc_containers"]
    require(len(matches) == 1 and matches[0]["container"] == "DXBC",
            "not_unique_dxbc")
    hit = matches[0]
    start, size = hit["offset_in_original_object"], hit["bytes"]
    code = entry[start:start + size]
    require(len(code) == size and digest(code) == hit["binary_sha256"],
            "dxbc_slice_digest_mismatch")
    versions = version_tokens(code)
    require(len(versions) == 1 and versions[0]["shader_stage_code"] == stage,
            "dxbc_stage_mismatch")
    return code, {
        "blob_index": blob, "segment_index": segment, "entry_offset": offset,
        "entry_bytes": length, "entry_sha256": digest(entry),
        "dxbc_offset_in_entry": start, "dxbc_bytes": size,
        "dxbc_sha256": digest(code),
    }


def verify(source, *, identity, parsed, segments, program_files):
    """Rejoin an independently obtained source snapshot to the old private packet.

    program_files is an exact ref -> source.dxbc bytes map from separately read
    immutable private translation folders. identity and parsed/segments MUST
    come from the independently authenticated source reader, not the packet.
    Return (private_witness, safe_counts). The former must not leave that reader.
    No translated-stage validation or runtime/module/installation claim is made.
    """
    require(type(source) is dict, "invalid_packet")
    source_identity(identity, source)
    require(type(parsed) is dict
            and same(parsed, source.get("original_shader_ParsedForm_full_private")),
            "independent_parsed_form_mismatch")
    derive_source_contract(source)
    require(type(program_files) is dict and set(program_files) == PROGRAM_REFS
            and all(type(b) is bytes and 0 < len(b) <= 16 * 1024 * 1024
                    for b in program_files.values()), "incomplete_program_files")
    ranges = table_ranges(segments)
    passes = parsed["m_SubShaders"][0]["m_Passes"]
    names = parsed["m_KeywordNames"]
    by_ref, by_code, cache, witnesses = {}, {}, {}, []
    for pair in source["paired"]:
        p = pair["pass"]
        for lane, field, stage in (("vs", "progVertex", 1), ("fs", "progFragment", 0)):
            row = pair[lane]
            bucket, ordinal = row.get("player_bucket"), row["bucket_ordinal"]
            table = passes[p][field]
            meta = (table["m_SubPrograms"][ordinal] if bucket is None
                    else table["m_PlayerSubPrograms"][bucket][ordinal])
            require(same(row["original_variant_metadata"], meta), "independent_slot_metadata_mismatch")
            blob = meta["m_BlobIndex"]
            key = (blob, stage)
            if key not in cache:
                cache[key] = actual_program(segments, ranges, blob, stage)
            code, record = cache[key]
            meta_sha = digest(canonical(meta))
            origin = {
                "blob_index": blob, "segment_index": record["segment_index"],
                "metadata_sha256": meta_sha, "entry_sha256": record["entry_sha256"],
            }
            require(same(row.get("original_D3D11_link"), origin), "packet_entry_link_mismatch")
            ref = row["program_ref"]
            require(program_files[ref] == code, "program_ref_dxbc_bytes_mismatch")
            ident = (stage, record["dxbc_sha256"])
            require(by_ref.setdefault(ref, ident) == ident
                    and by_code.setdefault(ident, ref) == ref, "non_bijective_program_identity")
            witnesses.append({
                "subshader": 0, "pass": p, "stage": stage, "player_bucket": bucket,
                "bucket_ordinal": ordinal, "hardware_tier": meta.get("m_ShaderHardwareTier"),
                "keyword_indices": list(meta["m_KeywordIndices"]),
                "keywords": [names[i] for i in meta["m_KeywordIndices"]],
                "metadata_sha256": meta_sha, "program_ref": ref, **record,
            })
    require(len(witnesses) == 2 * sum(COUNTS) and len(by_ref) == len(by_code) == 134
            and set(by_ref) == PROGRAM_REFS, "identity_population_drift")
    # Private commitment includes raw keyword names, exact owner identity and
    # full slot->entry->DXBC mapping; never publish the witness or its digests.
    private = {
        "source_identity": dict(identity), "parsed_form_sha256": digest(canonical(parsed)),
        "keyword_flags": list(parsed["m_KeywordFlags"]),
        "slots": sorted(witnesses, key=lambda r: (
            r["pass"], r["stage"], -1 if r["player_bucket"] is None else r["player_bucket"],
            r["bucket_ordinal"])),
    }
    safe = {
        "status": "PASS_INPUT_SOURCE_SLOT_TO_DXBC_BYTE_JOIN_ONLY",
        "routes_by_pass": list(COUNTS), "stage_slots_byte_joined": len(witnesses),
        "distinct_stage_programs_byte_joined": len(by_code),
        "distinct_blob_stage_links": len(cache),
        "authorization_verified_by_this_tool": False,
        "owner_and_object_bytes_authenticated_by_this_tool": False,
        "translated_stage_equivalence_verified": False,
        "compiled_route_program_identity_verified": False,
        "same_export_census_verified": False,
        "production_install_allowed": False,
    }
    return private, safe
