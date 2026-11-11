"""Fail-closed lifetime-order audit for instrumented Foam RenderTexture events.

This is not Unity provenance or pixel validation. Producer must be independently trusted.
"""
import json
MAX_BYTES = 65536
FIELDS = {"schema", "capture_id", "source_commit", "frame", "events"}
KINDS = {"allocate", "pass0_write", "pass1_read", "release"}

def pairs_unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result

def token_ok(value):
    return type(value) is str and 8 <= len(value) <= 64 and all(
        c.isascii() and (c.isalnum() or c in "-_") for c in value)

def check(raw):
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        raise ValueError("invalid_size")
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs_unique,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ValueError("invalid_json") from exc
    if type(doc) is not dict or set(doc) != FIELDS or doc["schema"] != "t2-foam-rt-lifetime-v1":
        raise ValueError("invalid_schema")
    if not token_ok(doc["capture_id"]):
        raise ValueError("invalid_capture")
    sha = doc["source_commit"]
    if type(sha) is not str or len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("invalid_sha")
    if type(doc["frame"]) is not int or not 0 <= doc["frame"] < 2**31:
        raise ValueError("invalid_frame")
    events = doc["events"]
    if type(events) is not list or not 4 <= len(events) <= 256:
        raise ValueError("invalid_events")
    states, joined, previous = {}, [], -1
    for event in events:
        if type(event) is not dict or set(event) != {"seq", "kind", "token"}:
            raise ValueError("invalid_event")
        seq, kind, token = event["seq"], event["kind"], event["token"]
        if type(seq) is not int or not previous < seq < 2**31:
            raise ValueError("invalid_sequence")
        previous = seq
        if type(kind) is not str or kind not in KINDS or not token_ok(token):
            raise ValueError("invalid_event_value")
        prior = states.get(token)
        if kind == "allocate":
            if prior is not None:
                raise ValueError("reused_token")
            states[token] = "allocated"
        elif kind == "pass0_write":
            if prior != "allocated":
                raise ValueError("write_without_allocation")
            states[token] = "written"
        elif kind == "pass1_read":
            if prior != "written":
                raise ValueError("read_without_live_write")
            states[token] = "read"
            joined.append(token)
        else:
            if prior not in ("allocated", "written", "read"):
                raise ValueError("invalid_release")
            states[token] = "released"
    if len(joined) != 1 or states[joined[0]] != "released":
        raise ValueError("missing_unique_completed_pair")
    return {"schema": "t2-foam-rt-lifetime-result-v1",
            "capture_id": doc["capture_id"], "source_commit": sha,
            "frame": doc["frame"], "lifetime_order_evidence": "CAPTURE_ORDER_CONSISTENT",
            "original_foam_runtime_provenance_verified": False,
            "android_pixels_verified": False,
            "note": "Capture order only; no producer authentication or Unity object proof."}

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m scripts.t2_foam_rt_lifetime_gate capture.json")
    try:
        with open(sys.argv[1], "rb") as handle:
            result = check(handle.read(MAX_BYTES + 1))
    except (OSError, ValueError) as exc:
        print("REJECTED: " + type(exc).__name__, file=sys.stderr)
        raise SystemExit(2)
    print(json.dumps(result, sort_keys=True))
