#!/usr/bin/env python3
"""GT: authenticate original Spectrum keyword flag bytes in SHA-pinned ZIP2.

No keyword spelling, original shader/Material program, or source payload is
written to a report or CI logs. This is a structural source probe only.
Byte values are NOT interpreted as global/local scope without a version-
specific verified mapping and runtime keyword-space test.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.b09_spectrum_topology_contract import TARGET, KEYWORD_NAMES, OWNER, PASSES
from scripts.b09_stage_original_spectrum import _selected_original
from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources


def inspect_flags(parsed: dict) -> dict:
    if type(parsed) is not dict or parsed.get("m_Name") != TARGET:
        raise ValueError("original_spectrum_identity_mismatch")
    names = parsed.get("m_KeywordNames")
    flags = parsed.get("m_KeywordFlags")
    if type(names) is not list or len(names) != KEYWORD_NAMES:
        raise ValueError("original_keyword_name_table_incomplete")
    if any(type(x) is not str or not x or len(x) > 128 for x in names):
        raise ValueError("original_keyword_name_row_invalid")
    if len(set(names)) != KEYWORD_NAMES:
        raise ValueError("original_keyword_name_index_ambiguous")
    if isinstance(flags, (bytes, bytearray)):
        flags = list(flags)
    if type(flags) is not list or len(flags) != KEYWORD_NAMES:
        raise ValueError("original_keyword_flags_missing_or_wrong_length")
    if any(type(x) is not int or not 0 <= x <= 255 for x in flags):
        raise ValueError("original_keyword_flag_outside_uint8")
    subs = parsed.get("m_SubShaders")
    if (type(subs) is not list or len(subs) != 1
            or type(subs[0]) is not dict
            or type(subs[0].get("m_Passes")) is not list
            or len(subs[0]["m_Passes"]) != PASSES):
        raise ValueError("original_spectrum_pass_structure_changed")
    # A numeric-only commitment to the flag table; never disclose the names.
    return {
        "status": "SOURCE_AUTHENTIC_SPECTRUM_INDEX4_FLAG_BYTES_OBSERVED",
        "original_keyword_names_count": KEYWORD_NAMES,
        "original_keyword_flags_count": len(flags),
        "original_keyword_index": 4,
        "original_keyword_index4_flag_byte": flags[4],
        "original_keyword_flags_distinct_byte_values": len(set(flags)),
        "original_keyword_flag_bytes_sha256": hashlib.sha256(bytes(flags)).hexdigest(),
        "original_passes": PASSES,
        "original_keyword_name_or_program_published": False,
        "original_flag_byte_to_global_local_semantics_proven": False,
        "original_material_keyword_selection_proven": False,
        "original_game_modified": False,
        "unity_or_adreno_pixels_verified": False,
    }


def verify_original(source: Path, repo: Path, out: Path, *, original_reader=_selected_original):
    source, repo, out = (Path(x).absolute() for x in (source, repo, out))
    if (not source.is_dir() or not repo.is_dir() or not out.parent.is_dir()
            or out.exists() or out.is_symlink()
            or any(p.is_symlink() for p in (source, repo, out.parent))
            or source.is_relative_to(repo) or out.is_relative_to(repo)
            or out.is_relative_to(source)):
        raise ValueError("source_or_report_path_unsafe")
    verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    path_id, _obj_sha, tree, original_proof = original_reader(source)
    if (path_id != 2432
            or original_proof.get("authenticated_original_passes") != PASSES
            or original_proof.get("authenticated_variant_stage_programs") != 28):
        raise ValueError("source_original_B09_attestation_unproven")
    result = inspect_flags(tree.get("m_ParsedForm"))
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify_original(args.source, args.repo, args.out)
    except BaseException as exc:
        print("GT_SPECTRUM_ORIGINAL_KEYWORD_FLAGS_SAFE " + json.dumps({
            "status": "INCONCLUSIVE",
            "error_type": type(exc).__name__,
            "original_flag_byte_to_global_local_semantics_proven": False,
            "original_game_modified": False,
            "unity_or_adreno_pixels_verified": False
        }, sort_keys=True))
        return 2
    print("GT_SPECTRUM_ORIGINAL_KEYWORD_FLAGS_SAFE " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
