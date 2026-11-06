"""Strict source-safe T1 WATER-001 bridge of prior real CI provenance summaries.

This does NOT authenticate GitHub job logs from JSON alone, reconstruct original
Raft shader pixels, establish Unity original-runtime kernel identity, or prove
FTZ causality. Input is an independently manually checked, redacted digest of
three pinned SUCCESS CI job markers. The only honest result is the missing link.
Never print raw evidence, private shaders, register identifiers or binary data.
"""
import argparse
import json
from pathlib import Path

MAX_BYTES = 4096
ZIP2 = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
ORIGINAL = (42220554705, "00a9157d69ba7bdbca9ba9d9cd1d8881feb1fe3f")
CANDIDATE = (42228497335, "e936ad1f96c0bb0617a7a7199c2304c5f47442ff")
UNITY = (42279949574, "93f27342d4b2c46d811c6c16a2672d9a247f346a")
PROVENANCE = "SANITIZED_PINNED_CI_LOG_EXCERPTS_UNAUTHENTICATED_AT_RUNTIME"
PAIR_LABELS = ("bitcast", "plain_multiply", "precise_multiply",
               "texture_from_bitcast", "texture_from_precise")


def _exact(obj, fields):
    if type(obj) is not dict or set(obj) != set(fields):
        raise ValueError("Unexpected redacted FFT evidence fields")
    return obj


def _ident(obj, run):
    if (type(obj["run_id"]) is not int or obj["run_id"] != run[0] or
            type(obj["commit"]) is not str or obj["commit"] != run[1]):
        raise ValueError("FFT provenance run/commit identity mismatch")


def _false(obj, *names):
    if any(obj[k] is not False for k in names):
        raise ValueError("Unproven FFT runtime or Android claim")


def _true(obj, *names):
    if any(obj[k] is not True for k in names):
        raise ValueError("Expected bounded FFT structural baseline absent")


def _safe_number(value, expected):
    if type(value) is not int or value != expected:
        raise ValueError("Unexpected FFT structural census")


def _five(value, expected):
    if (type(value) is not list or len(value) != 5 or any(
            type(x) is not int or x != expected for x in value)):
        raise ValueError("Synthetic GPU carrier signature mismatch")


def _shape(node):
    if (node["role"] != "butterfly" or
            type(node["site"]) is not int or node["site"] != 1 or
            node["coordinate"] != "x"):
        raise ValueError("Wrong original butterfly X coordinate site")


def analyze(payload):
    root = _exact(payload, ("schema_version", "provenance",
                            "original", "candidate", "synthetic_unity"))
    _safe_number(root["schema_version"], 1)
    if root["provenance"] != PROVENANCE:
        raise ValueError("Original CI redaction provenance missing")
    o = _exact(root["original"], (
        "run_id", "commit", "zip2_pin", "role", "site", "coordinate",
        "status", "reachable_last_writer_count", "source_boundary",
        "no_unknown_alias_write", "no_uninitialized_path",
        "original_numeric_semantics_proven", "authored_unity_runtime_mapping_proven"))
    c = _exact(root["candidate"], (
        "run_id", "commit", "zip2_pin", "role", "site", "coordinate",
        "status", "top_phi_kind", "top_selected_component", "phi_expansions",
        "cycle_boundaries", "structural_phi_backedges", "incoming_count",
        "first_noncyclic_boundary", "second_boundary",
        "selected_runtime_predecessor_proven", "original_vs_unity_numeric_parity_proven"))
    u = _exact(root["synthetic_unity"], (
        "run_id", "commit", "engine", "backend", "site_count", "threads",
        "positive_controls_all_zero", "computed_mismatches",
        "computed_zero_signatures", "buffered_mismatches",
        "buffered_zero_signatures", "sourcefree_only",
        "original_shader_executed", "android_adreno_proven"))
    _ident(o, ORIGINAL)
    _ident(c, CANDIDATE)
    _ident(u, UNITY)
    if o["zip2_pin"] != ZIP2 or c["zip2_pin"] != ZIP2:
        raise ValueError("Original and candidate ZIP2 source pin drift")
    _shape(o)
    _shape(c)
    if (o["status"] != "bounded_last_write_component_lineage" or
            c["status"] != "bounded_nested_phi_component_provenance"):
        raise ValueError("Original or candidate analysis not at expected structural boundary")
    _safe_number(o["reachable_last_writer_count"], 1)
    _true(o, "no_unknown_alias_write", "no_uninitialized_path")
    _false(o, "original_numeric_semantics_proven", "authored_unity_runtime_mapping_proven")
    source = _exact(o["source_boundary"], (
        "immediate_store_opcode", "ssa_ops", "cast_kinds",
        "leaf_storage_class", "leaf_numeric_kind", "status", "write_form"))
    if (source["immediate_store_opcode"] != "OpVectorShuffle" or
            source["ssa_ops"] != ["OpVectorShuffle", "OpBitcast", "OpVectorShuffle", "OpLoad"] or
            source["cast_kinds"] != ["sint32_bits_to_float32"] or
            source["leaf_storage_class"] != "Input" or
            source["leaf_numeric_kind"] != "sint32_vector" or
            source["status"] != "memory_load_boundary" or
            source["write_form"] != "whole"):
        raise ValueError("Original FFT signed Input bitcarrier path not established")
    if c["top_phi_kind"] != "float32_vector" or c["top_selected_component"] != "x":
        raise ValueError("Candidate selected X Phi type not verified")
    for k, n in (("phi_expansions", 1), ("cycle_boundaries", 1),
                 ("structural_phi_backedges", 1), ("incoming_count", 2)):
        _safe_number(c[k], n)
    leaf = _exact(c["first_noncyclic_boundary"], (
        "leaf_storage_class", "leaf_numeric_kind", "status", "has_bitcast"))
    if (leaf["leaf_storage_class"] != "Private" or
            leaf["leaf_numeric_kind"] != "uint32_vector" or
            leaf["status"] != "memory_load_boundary"):
        raise ValueError("Candidate noncyclic Phi branch origin unverified")
    _true(leaf, "has_bitcast")
    if c["second_boundary"] != "loop_carried_or_cyclic_phi":
        raise ValueError("Candidate Phi backedge category not established")
    _false(c, "selected_runtime_predecessor_proven",
           "original_vs_unity_numeric_parity_proven")
    if u["engine"] != "2021.3.45f2" or u["backend"] != "OpenGLCore":
        raise ValueError("Synthetic Unity GPU backend mismatch")
    _safe_number(u["site_count"], 16)
    _safe_number(u["threads"], 64)
    _true(u, "positive_controls_all_zero", "sourcefree_only")
    _false(u, "original_shader_executed", "android_adreno_proven")
    _five(u["computed_mismatches"], 63)
    _five(u["computed_zero_signatures"], 63)
    _five(u["buffered_mismatches"], 0)
    _five(u["buffered_zero_signatures"], 0)

    # This is a safe *structural context* bridge, not a numeric/causal proof:
    # the translated Private load might itself be fed by original Input.
    return {
        "status": "original_input_bitcast_vs_translated_private_loop_phi_gap",
        "original_source_boundary": "sint32_input_vector_bitcast_to_float32",
        "candidate_source_boundary": "uint32_private_vector_through_float32_loop_phi",
        "candidate_runtime_phi_branch_known": False,
        "synthetic_computed_carrier_zero_signature_lanes_per_path": 63,
        "synthetic_buffered_carrier_zero_signature_lanes_per_path": 0,
        "synthetic_path_names": list(PAIR_LABELS),
        "original_and_candidate_appear_in_distinct_bounded_static_shapes": True,
        "original_candidate_numeric_parity_in_Unity_proven": False,
        "translation_is_cause_of_water_failure_proven": False,
        "float32_FTZ_causality_proven": False,
        "original_runtime_kernel_mapping_proven": False,
        "android_adreno_water_proven": False,
        "source_report_authenticated_by_this_gate": False,
        "source_zip2_sha_attested_by_external_CI_only": True,
        "safe_next_step": "private_sha_pinned_same_input_original_vulkan_vs_unity_candidate_invocation_key_trace",
        "raw_shader_pixel_hashes_or_ids_exported": False,
    }


def _no_duplicates(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError("Duplicate FFT original provenance field")
        obj[key] = value
    return obj


def read(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Unsafe FFT evidence file")
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if not 0 < len(data) <= MAX_BYTES:
        raise ValueError("Unbounded FFT evidence report")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=_no_duplicates,
                          parse_constant=lambda _: (_ for _ in ()).throw(
                              ValueError("Nonfinite FFT evidence")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed FFT original provenance report") from None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = analyze(read(args.evidence))
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        parser.exit(2, "RAFT_T1_FFT_ORIGINAL_PHI_BRIDGE invalid_or_unverified_safe_evidence=true\n")
    print("RAFT_T1_FFT_ORIGINAL_PHI_BRIDGE " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
