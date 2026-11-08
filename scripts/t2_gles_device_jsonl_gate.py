"""Fail-closed, source-free T2 mini GLES JSONL evidence consistency gate.

Checks a single exported per-case stream, not summary PASS and not Raft water.
Never prints raw device log details or identifiers.
"""
import json
import re
import sys
from pathlib import Path

CASES = {"CASE01", "CASE02", "CASE03", "CASE04"}
EVENTS = {"startup", "gl_context", "surface", "case_start", "gl_observed",
          "shared_auto_result", "export", "activity", "user_result"}
MAX_BYTES = 128 * 1024
MAX_LINES = 128


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def verify(lines, expected_case):
    if expected_case not in CASES:
        raise ValueError("unsupported_case")
    if not 1 <= len(lines) <= MAX_LINES:
        raise ValueError("invalid_line_count")
    parsed = []
    for line in lines:
        if not line.strip() or len(line.encode("utf-8")) > 4096:
            raise ValueError("unsafe_line")
        obj = json.loads(line, object_pairs_hook=no_duplicates,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        if type(obj) is not dict or set(obj) != {
            "unix_ms", "elapsed_ms", "worker", "package", "version",
            "session", "case", "event", "detail"
        }:
            raise ValueError("unexpected_record_shape")
        if (obj["worker"] != "T2" or
                obj["event"] not in EVENTS or
                type(obj["unix_ms"]) is not int or type(obj["elapsed_ms"]) is not int or
                obj["unix_ms"] < 0 or obj["elapsed_ms"] < 0 or
                not isinstance(obj["detail"], str) or len(obj["detail"]) > 1200 or
                not isinstance(obj["session"], str) or
                not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[0-9]{3,12}", obj["session"]) or
                not isinstance(obj["package"], str) or
                not re.fullmatch(r"[A-Za-z0-9_.]{3,120}", obj["package"]) or
                not isinstance(obj["version"], str) or len(obj["version"]) > 24 or
                obj["case"] not in (None, expected_case)):
            raise ValueError("unsafe_or_mixed_record")
        parsed.append(obj)
    if (len({r["session"] for r in parsed}) != 1 or
            len({r["package"] for r in parsed}) != 1 or
            len({r["version"] for r in parsed}) != 1):
        raise ValueError("mixed_sessions")
    if any(b["elapsed_ms"] < a["elapsed_ms"] or b["unix_ms"] < a["unix_ms"]
           for a, b in zip(parsed, parsed[1:])):
        raise ValueError("nonmonotonic_elapsed_time")
    def one(event):
        found = [i for i, row in enumerate(parsed) if row["event"] == event]
        if len(found) != 1:
            raise ValueError("missing_or_duplicate_" + event)
        return found[0]
    ctx, start, observed, auto = map(one, ("gl_context", "case_start", "gl_observed", "shared_auto_result"))
    if not ctx < start < observed < auto:
        raise ValueError("invalid_event_order")
    if any(parsed[i]["case"] != expected_case for i in (start, observed, auto)):
        raise ValueError("wrong_case")
    detail = parsed[observed]["detail"]
    if not detail.startswith("OK ") or detail != parsed[auto]["detail"]:
        raise ValueError("failed_or_mismatched_observation")
    # An OK prefix is not sufficient: require the expected probe's characteristic
    # measurement. This is still only a syntactic gate, never pixel authenticity.
    markers = {
        "CASE01": ("renderer=", "version=", "maxTexture="),
        "CASE02": ("2-pass RGBA8 FBO", "sourceLeft=", "sourceRight=",
                   "finalBaseline=", "finalContrast=", "tolerance=2"),
        "CASE03": ("rejects unattached FBO:", "0x8cd7"),
        "CASE04": ("compile rejected invalid fragment shader",),
    }
    if any(token not in detail for token in markers[expected_case]):
        raise ValueError("missing_expected_probe_measurement")
    return {"case": expected_case, "synthetic_gles_log_consistent": True,
            "original_raft_water_verified": False}


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        raise SystemExit("usage: python -m scripts.t2_gles_device_jsonl_gate CASE01 path.jsonl")
    case, name = args
    path = Path(name)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_BYTES:
        raise ValueError("unsafe_log_file")
    result = verify(path.read_text(encoding="utf-8").splitlines(), case)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
