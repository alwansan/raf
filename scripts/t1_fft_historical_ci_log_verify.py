"""Verify pinned historical T1 FFT safe markers against *retrieved* GitHub CI logs.

This is a source-only metadata/report check, NOT signed runner attestation,
original shader numeric parity, runtime FindKernel identity, or Android proof.
All historical logs remain private temporary files; stdout is bounded flags.
"""
import argparse
import json
from pathlib import Path
import re

from scripts.t1_fft_original_phi_bridge import analyze

PINS = (
    ("original", 42220554705, 127901229510,
     "00a9157d69ba7bdbca9ba9d9cd1d8881feb1fe3f",
     "RAFT_T1_FFT_BUTTERFLY_X_WRITER_LINEAGE"),
    ("candidate", 42228497335, 127928005249,
     "e936ad1f96c0bb0617a7a7199c2304c5f47442ff",
     "RAFT_T1_FFT_HLSL_NESTED_PHI_X"),
    ("synthetic_unity", 42279949574, 128106388433,
     "93f27342d4b2c46d811c6c16a2672d9a247f346a",
     "RAFT_T1_ADDRESS_PROVENANCE_GATE"),
)
MAX_META = 256 * 1024
MAX_LOG = 2 * 1024 * 1024
MAX_MARKER = 24 * 1024
STAMP = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z"


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("Duplicate CI metadata key")
        out[key] = value
    return out


def _json(raw):
    return json.loads(raw, object_pairs_hook=_pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(
                          ValueError("Nonfinite historical CI report")))


def _load(path, max_bytes, json_data=False):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("Unsafe CI evidence path")
    with path.open("rb") as stream:
        data = stream.read(max_bytes + 1)
    if not data or len(data) > max_bytes:
        raise ValueError("Unbounded CI evidence")
    return _json(data.decode("utf-8-sig")) if json_data else data.decode("utf-8-sig")


def _validate_status(run, job, pin):
    _, run_id, job_id, sha, _ = pin
    if not isinstance(run, dict) or not isinstance(job, dict):
        raise ValueError("CI metadata not objects")
    if (type(run.get("id")) is not int or run["id"] != run_id or
            run.get("head_sha") != sha or
            run.get("status") != "completed" or
            run.get("conclusion") != "success" or
            run.get("head_branch") != "feature/android-native-port"):
        raise ValueError("Historical workflow identity/conclusion mismatch")
    if not isinstance(run.get("repository"), dict) or run["repository"].get("full_name") != "alwansan/raf":
        raise ValueError("Wrong repository")
    if (type(job.get("id")) is not int or job["id"] != job_id or
            type(job.get("run_id")) is not int or job["run_id"] != run_id or
            job.get("status") != "completed" or job.get("conclusion") != "success"):
        raise ValueError("Historical job identity/conclusion mismatch")


def _marker(log, name):
    pattern = re.compile("^" + STAMP + " " + re.escape(name) + r" (\{.*\})$")
    matches = []
    for line in log.splitlines():
        if name not in line:
            continue
        if len(line) > MAX_MARKER:
            raise ValueError("Oversized historical marker")
        found = pattern.fullmatch(line)
        if not found:
            raise ValueError("Noncanonical historical CI marker line")
        matches.append(_json(found.group(1)))
    if len(matches) != 1 or not isinstance(matches[0], dict):
        raise ValueError("Missing or nonunique historical marker")
    return matches[0]


def _require_eq(item, field, value):
    if type(item.get(field)) is not type(value) or item[field] != value:
        raise ValueError("Pinned historical CI marker differs from redacted evidence")


def _inspect_original(m, o):
    for k in ("role", "site", "coordinate", "status", "reachable_last_writer_count"):
        _require_eq(m, k, o[k])
    for k, expected in (
        ("possible_unknown_alias_write", False),
        ("possible_uninitialized_path", False),
        ("original_numeric_semantics_proven", False),
        ("complete_proof", False),
    ):
        _require_eq(m, k, expected)
    sources = m.get("possible_last_writer_component_sources")
    if type(sources) is not list or len(sources) != 1 or not isinstance(sources[0], dict):
        raise ValueError("Original writer coverage changed")
    s = sources[0]
    f = o["source_boundary"]
    for src, dst in (
        ("immediate_store_value_opcode", "immediate_store_opcode"),
        ("ssa_ops", "ssa_ops"),
        ("cast_kinds", "cast_kinds"),
        ("leaf_storage_class", "leaf_storage_class"),
        ("leaf_numeric_kind", "leaf_numeric_kind"),
        ("status", "status"),
        ("write_form", "write_form"),
    ):
        _require_eq(s, src, f[dst])


def _inspect_candidate(m, c):
    for k in ("role", "site", "coordinate", "status", "top_phi_kind",
              "top_selected_component", "phi_expansions", "cycle_boundaries",
              "structural_phi_backedges"):
        _require_eq(m, k, c[k])
    _require_eq(m, "selected_runtime_predecessor_proven", False)
    _require_eq(m, "actual_original_vs_unity_numeric_parity_proven", False)
    chain = m.get("chain")
    if not isinstance(chain, dict):
        raise ValueError("Candidate phi chain missing")
    for key, expected in (
        ("incoming_count", c["incoming_count"]),
        ("status", "phi_merge"), ("value_kind", "float32_vector"),
        ("selected_component", "x"),
    ):
        _require_eq(chain, key, expected)
    inc = chain.get("incoming")
    if type(inc) is not list or len(inc) != 2 or not all(isinstance(v, dict) for v in inc):
        raise ValueError("Candidate phi incoming graph missing")
    _require_eq(inc[0], "predecessor_in_structural_cfg_cycle", False)
    _require_eq(inc[1], "predecessor_in_structural_cfg_cycle", True)
    cur = inc[0].get("source")
    seen_bitcast = False
    for _ in range(24):
        if not isinstance(cur, dict):
            raise ValueError("Candidate noncyclic chain invalid")
        seen_bitcast |= cur.get("opcode") == "OpBitcast"
        if isinstance(cur.get("detail"), dict):
            detail = cur["detail"]
            for k in ("leaf_storage_class", "leaf_numeric_kind", "status"):
                _require_eq(detail, k, c["first_noncyclic_boundary"][k])
            if not seen_bitcast:
                raise ValueError("Candidate phi bitcast not on selected source path")
            break
        cur = cur.get("source")
    else:
        raise ValueError("Candidate phi noncyclic bound not reached")
    cur = inc[1].get("source")
    for _ in range(24):
        if not isinstance(cur, dict):
            raise ValueError("Candidate cyclic source invalid")
        if cur.get("status") == c["second_boundary"]:
            break
        cur = cur.get("source")
    else:
        raise ValueError("Candidate phi cycle not confirmed")


def _inspect_unity(m, u):
    _require_eq(m, "positive_controls_passed", u["positive_controls_all_zero"])
    _require_eq(m, "original_raft_shader_compiled_or_compared", u["original_shader_executed"])
    _require_eq(m, "android_adreno_water_proven", u["android_adreno_proven"])
    _require_eq(m, "sourcefree_unity_nunit_exact_case_passed", True)
    _require_eq(m, "synthetic_gpu_invocations_expected", u["threads"])
    _require_eq(m, "synthetic_gpu_words_expected", u["threads"] * u["site_count"])
    for src, dst in (
        ("computed_address_category_mismatches", "computed_mismatches"),
        ("computed_zero_signatures", "computed_zero_signatures"),
        ("buffered_address_category_mismatches", "buffered_mismatches"),
        ("buffered_zero_signatures", "buffered_zero_signatures"),
    ):
        _require_eq(m, src, u[dst])
    _require_eq(m, "zero_signature_is_float_FTZ_causality", False)


def verify(evidence, entries):
    analyze(evidence)  # fail closed on curated report's complete safe schema
    if set(entries) != set(x[0] for x in PINS):
        raise ValueError("Incomplete historical run manifest")
    for pin in PINS:
        name, _, _, _, marker = pin
        run, job, log = entries[name]
        _validate_status(run, job, pin)
        x = _marker(log, marker)
        if name == "original":
            _inspect_original(x, evidence[name])
        elif name == "candidate":
            _inspect_candidate(x, evidence[name])
        else:
            _inspect_unity(x, evidence[name])
    return {
        "status": "historical_three_pinned_ci_log_markers_match_curated_evidence",
        "pinned_successful_runs_and_jobs_checked": 3,
        "unique_historical_safe_markers_checked": 3,
        "retrieved_gitHub_CI_job_logs_match_curated_safe_report": True,
        "offline_fixture_alone_is_authenticated": False,
        "CI_logs_are_signed_runtime_attestation": False,
        "shader_original_vs_Unity_numeric_parity_proven": False,
        "original_runtime_kernel_identity_proven": False,
        "FTZ_cause_of_water_proven": False,
        "android_adreno_water_proven": False,
        "raw_logs_original_shader_or_pixels_exported": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--evidence", type=Path, required=True)
    for name, _, _, _, _ in PINS:
        for kind in ("run", "job", "log"):
            p.add_argument(f"--{name}-{kind}", type=Path, required=True)
    args = p.parse_args()
    try:
        evidence = _load(args.evidence, 4096, json_data=True)
        entries = {
            name: tuple(_load(getattr(args, f"{name}_{kind}"),
                              MAX_LOG if kind == "log" else MAX_META,
                              json_data=kind != "log")
                        for kind in ("run", "job", "log"))
            for name, _, _, _, _ in PINS
        }
        report = verify(evidence, entries)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError):
        p.exit(2, "RAFT_T1_FFT_HISTORICAL_CI_LOG invalid_or_untrusted_private_evidence=true\n")
    print("RAFT_T1_FFT_HISTORICAL_CI_LOG " + json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
