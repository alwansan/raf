"""Strict source-only gate for two *instrumented* Foam runtime RT observations.

Opaque tokens must originate from the SAME live Unity capture, not static IL.
A matching token is evidence only for that capture, never for Android pixels.
"""
import json

FIELDS = {"schema", "capture_id", "source_commit", "frame", "pass0", "pass1"}
PASS_FIELDS = {"destination", "source"}
MAX_BYTES = 8192


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def check(raw):
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise ValueError("invalid_size")
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (UnicodeError, RecursionError, ValueError) as exc:
        raise ValueError("invalid_json") from exc
    if type(doc) is not dict or set(doc) != FIELDS or doc["schema"] != "t2-foam-runtime-rt-v1":
        raise ValueError("invalid_schema")
    capture = doc["capture_id"]
    if type(capture) is not str or not (8 <= len(capture) <= 64) or not all(
            c.isascii() and (c.isalnum() or c in "-_") for c in capture):
        raise ValueError("invalid_capture")
    sha = doc["source_commit"]
    if type(sha) is not str or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("invalid_sha")
    if type(doc["frame"]) is not int or not (0 <= doc["frame"] <= 2**31-1):
        raise ValueError("invalid_frame")
    for name in ("pass0", "pass1"):
        row = doc[name]
        if type(row) is not dict or set(row) != PASS_FIELDS:
            raise ValueError("invalid_pass")
        for key in PASS_FIELDS:
            token = row[key]
            if type(token) is not str or not (8 <= len(token) <= 64) or not all(
                    c.isascii() and (c.isalnum() or c in "-_") for c in token):
                raise ValueError("invalid_token")
    return {
        "schema": "t2-foam-runtime-rt-result-v1",
        "capture_id": capture,
        "source_commit": sha,
        "frame": doc["frame"],
        "pass0_destination_equals_pass1_source": doc["pass0"]["destination"] == doc["pass1"]["source"],
        "runtime_identity_evidence": "CAPTURE_TOKEN_MATCH" if doc["pass0"]["destination"] == doc["pass1"]["source"] else "CAPTURE_TOKEN_MISMATCH",
        "original_foam_runtime_provenance_verified": False,
        "android_pixels_verified": False,
        "note": "Tokens require trusted instrumentation and same-frame resource lifetime; this parser does not authenticate their origin.",
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m scripts.t2_foam_runtime_rt_pair_gate safe_capture.json")
    try:
        with open(sys.argv[1], "rb") as f:
            result = check(f.read(MAX_BYTES + 1))
    except (OSError, ValueError) as exc:
        print("REJECTED: " + type(exc).__name__, file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(result, sort_keys=True))
