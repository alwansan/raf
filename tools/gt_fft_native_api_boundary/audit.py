#!/usr/bin/env python3
"""Strict, read-only native logger observation audit. No original runtime proof.

T1FftDirectDispatchTrace uses independent binding/dispatch call counters (16
each). PersistentDiagnosticLog supplies a different global counter and thread.
Only structural observations from one persisted segment are admitted here.
No original assets, game code, device access, or Unity invocation is needed.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

MAX_BYTES = 4 * 1024 * 1024
PREFIX = "t1_original_fft_"
SOURCE = "8aa32937d423"
FAMILIES = ("bind", "dispatch")
PHASES = ("before", "returned", "threw")
OPS = {PREFIX + f + "." + p: (f, p) for f in FAMILIES for p in PHASES}
ENVELOPE = {"utc", "session", "sequence", "thread", "area", "operation", "detail"}
BIND_BEFORE = {"sequence", "site", "pass", "shader_present", "shader_name_sha256",
               "shader_instance_session_local", "frame", "source_sha_prefix"}
DISPATCH_BEFORE = {"sequence", "source_sha_prefix", "original_findkernel_callsite_present",
    "shader_instance_session_local", "shader_present", "original_exponent",
    "inferred_bank_only", "pass_offset", "numeric_kernel_argument", "group_xyz",
    "unity_compute_supported", "frame", "realtime_s", "original_runtime_mapping", "gpu_result"}
RETURN = {"sequence", "managed_dispatch_call_returned", "unity_error_callback_may_follow",
          "gpu_result", "water_rendering"}
THROW = {"sequence", "managed_dispatch_threw", "exception_kind", "original_runtime_mapping",
         "gpu_result", "water_rendering"}
BIND_TERMINAL = {"sequence", "gpu_result"}


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def integer(raw, lo=-(1 << 31), hi=(1 << 31)-1):
    need(isinstance(raw, str) and re.fullmatch(r"-?(0|[1-9][0-9]*)", raw)
         and len(raw) <= 11, "noncanonical_detail_integer")
    n = int(raw)
    need(str(n) == raw and lo <= n <= hi, "detail_integer_range")
    return n


def exact_int(v, lo, hi):
    return type(v) is int and lo <= v <= hi


def unique(pairs):
    out = {}
    for k,v in pairs:
        need(k not in out, "duplicate_json_key")
        out[k] = v
    return out


def fields(raw):
    need(isinstance(raw,str) and 0 < len(raw) <= 4096, "invalid_detail")
    result = {}
    for part in raw.split(";"):
        k, sep, v = part.strip().partition("=")
        need(sep and k and v and k not in result and
             re.fullmatch(r"[a-z][a-z0-9_]*",k), "invalid_or_duplicate_detail_field")
        result[k] = v
    return result


def boolean(raw):
    need(raw in ("True", "False"), "invalid_csharp_boolean")
    return raw == "True"


def i32(n):
    return ((n + (1 << 31)) % (1 << 32)) - (1 << 31)


def before(family, d):
    common = BIND_BEFORE if family == "bind" else DISPATCH_BEFORE
    need(set(d) == common and d["source_sha_prefix"] == SOURCE, "before_schema_or_source_marker")
    present = boolean(d["shader_present"])
    instance = integer(d["shader_instance_session_local"])
    need((instance != 0) == present, "shader_presence_identity_mismatch")
    out = {"present": present, "instance": instance, "frame": integer(d["frame"],0)}
    if family == "bind":
        site = integer(d["site"],0,5)
        pass_ = integer(d["pass"],0,1)
        digest = d["shader_name_sha256"]
        need(pass_ == site // 3, "binding_site_pass_mismatch")
        need(digest == "unavailable" or (present and re.fullmatch(r"[0-9a-f]{64}",digest)),
             "binding_shader_digest_schema")
        out.update(site=site, pass_=pass_, digest=digest)
    else:
        need(d["original_findkernel_callsite_present"] == "false" and
             d["original_runtime_mapping"] == d["gpu_result"] == "unverified",
             "dispatch_source_or_proof_marker")
        exp = integer(d["original_exponent"])
        pass_ = integer(d["pass_offset"],0,1)
        arg = integer(d["numeric_kernel_argument"])
        groups = tuple(integer(x) for x in d["group_xyz"].split(","))
        need(len(groups) == 3, "dispatch_group_schema")
        delta = i32(arg - i32((i32(exp-5) << 1) + pass_))
        inferred = ("source_bank0_candidate" if delta == 0 else
                    "source_bank1_candidate" if delta == 10 else "outside_source_bank_candidates")
        need(d["inferred_bank_only"] == inferred, "inferred_bank_marker_mismatch")
        need(re.fullmatch(r"[0-9]{1,12}\.[0-9]{3}",d["realtime_s"]), "realtime_schema")
        supported = boolean(d["unity_compute_supported"])
        out.update(pass_=pass_, arg=arg, exp=exp, bank=inferred, groups=groups,
                   supported=supported)
    return out


def terminal(family, phase, d):
    if family == "bind":
        need(set(d)==BIND_TERMINAL and d["gpu_result"]=="unverified","binding_terminal_schema")
    elif phase == "returned":
        need(set(d)==RETURN and d["managed_dispatch_call_returned"]=="true" and
             d["unity_error_callback_may_follow"]=="true" and
             d["gpu_result"]==d["water_rendering"]=="unverified","dispatch_return_schema")
    else:
        need(set(d)==THROW and d["managed_dispatch_threw"]=="true" and
             d["exception_kind"] in {"argument","invalid_operation","null_reference","other"} and
             d["original_runtime_mapping"]==d["gpu_result"]==d["water_rendering"]=="unverified",
             "dispatch_throw_schema")


def scan(rows):
    session = None
    last_global = None
    global_ids = set()
    events = []
    calls = {}
    overflow = False
    other_unsequenced = False
    global_gaps = 0
    for row in rows:
        need(type(row) is dict, "row_schema")
        op = row.get("operation")
        # A legacy targeted event must not disappear as an unrelated line.
        need(row.get("event") not in OPS, "legacy_fft_envelope_not_supported")
        relevant = op in OPS
        if row.get("area")=="logging" and op=="queue_overflow":
            need(exact_int(row.get("dropped"),1,(1<<63)-1),"overflow_schema")
            overflow = True
            continue
        if not relevant and not ENVELOPE <= row.keys():
            other_unsequenced = True
            continue
        need(set(row)==ENVELOPE and exact_int(row["sequence"],1,(1<<63)-1)
             and exact_int(row["thread"],1,(1<<31)-1) and isinstance(row["session"],str)
             and 0<len(row["session"])<=256 and not any(ord(c)<32 for c in row["session"]),
             "persisted_envelope_schema")
        if session is None:
            session = row["session"]
        need(row["session"]==session,"mixed_logger_sessions")
        seq = row["sequence"]
        need(last_global is None or seq>last_global,"duplicate_or_reversed_global_sequence")
        if last_global is not None and seq!=last_global+1:
            global_gaps += 1
        last_global = seq
        global_ids.add(seq)
        if not relevant:
            continue
        need(row["area"]=="water","fft_logger_area")
        family, phase = OPS[op]
        d = fields(row["detail"])
        local = integer(d.get("sequence"),1,16)
        key = family,local
        call = calls.setdefault(key,{})
        e = {"family":family,"phase":phase,"local":local,"global":seq,"thread":row["thread"]}
        if phase=="before":
            need("before" not in call,"duplicate_call_start")
            e.update(before(family,d))
            call["before"] = e
        else:
            terminal(family,phase,d)
            need("terminal" not in call,"duplicate_or_conflicting_call_terminal")
            call["terminal"] = e
        events.append(e)
    counters = Counter()
    valid = {}
    first = None
    for key,c in calls.items():
        family,_ = key
        b,t = c.get("before"),c.get("terminal")
        if b is None:
            counters[family+"_orphan_terminal"] += 1
        elif t is None:
            counters[family+"_unresolved"] += 1
        elif t["global"]<=b["global"] or t["thread"]!=b["thread"]:
            counters[family+"_invalid_pair"] += 1
        else:
            valid[key] = (b,t)
            counters[family+"_"+t["phase"]] += 1
            if t["phase"]=="threw" and (first is None or t["global"]<first["global"]):
                first = t
    # A strict observed source-order window is NOT an invocation token or
    # binding-to-program proof. Any missing records, overflow, overlap, changed
    # frame/shader/thread, or source-site ordering blocks this narrow evidence.
    windows = []
    for i in range(0,len(events)-7):
        batch = events[i:i+8]
        if [(e["family"],e["phase"]) for e in batch[:6]] != [
            ("bind","before"),("bind","returned")]*3:
            continue
        if [(e["family"],e["phase"]) for e in batch[6:]] not in [
            [("dispatch","before"),("dispatch","returned")],
            [("dispatch","before"),("dispatch","threw")]]:
            continue
        if any(valid.get((batch[j]["family"],batch[j]["local"]))!=(batch[j],batch[j+1])
               for j in (0,2,4,6)):
            continue
        b0,b1,b2,dispatch = (batch[j] for j in (0,2,4,6))
        starts = (b0,b1,b2,dispatch)
        p = dispatch["pass_"]
        if [e["site"] for e in starts[:3]] != list(range(p*3,p*3+3)):
            continue
        if [e["local"] for e in starts[:3]] != list(range(b0["local"],b0["local"]+3)):
            continue
        if len({e["thread"] for e in batch})!=1 or len({(e["instance"],e["frame"],e["present"]) for e in starts})!=1:
            continue
        if not dispatch["present"] or len({e["digest"] for e in starts[:3]})!=1:
            continue
        lo,hi = batch[0]["global"],batch[-1]["global"]
        if overflow or other_unsequenced or global_gaps:
            continue
        if sum(lo<=x<=hi for x in global_ids)!=hi-lo+1:
            continue
        windows.append({"pass_offset":p,"numeric_arg_is_6":dispatch["arg"]==6,
            "candidate_256_bank0_pass0": dispatch["arg"]==6 and dispatch["exp"]==8 and p==0
                 and dispatch["bank"]=="source_bank0_candidate" and dispatch["groups"]==(1,256,1)
                 and dispatch["supported"],
            "terminal":batch[-1]["phase"]})
    # Report only bounded counts and categories, not private session identifiers,
    # timestamps, original shader names, hashes, raw arguments, or instance IDs.
    return {
        "status":"SCOPED_NATIVE_API_OBSERVATIONS_ONLY",
        "observed_fft_events":len(events),
        "api_calls":{f:{k:counters[f+"_"+k] for k in
                     ("returned","threw","orphan_terminal","unresolved","invalid_pair")} for f in FAMILIES},
        "first_observed_paired_synchronous_throw_api": None if first is None else
            ("SetTexture" if first["family"]=="bind" else "Dispatch"),
        "global_sequence_gaps":global_gaps,"queue_overflow_seen":overflow,
        "unsequenced_non_fft_rows_seen":other_unsequenced,
        "binding_counter_budget_reached":any(k==("bind",16) for k in calls),
        "dispatch_counter_budget_reached":any(k==("dispatch",16) for k in calls),
        "source_order_compatible_windows":len(windows),
        "windows_ending_dispatch_throw":sum(w["terminal"]=="threw" for w in windows),
        "numeric_6_source_compatible_windows":sum(w["candidate_256_bank0_pass0"] for w in windows),
        "runtime_invocation_identity_proven":False,
        "actual_first_unity_failure_proven":False,
        "original_bank_measured":False,
        "original_runtime_kernel_mapping_proven":False,
        "gpu_execution_proven":False,"water_rendering_proven":False,
    }


def read(path):
    p = Path(path)
    need(p.is_file() and not p.is_symlink() and p.stat().st_size<=MAX_BYTES,"bounded_regular_log_required")
    raw = p.read_bytes()
    need(len(raw)<=MAX_BYTES,"bounded_regular_log_required")
    return scan(json.loads(line,object_pairs_hook=unique) for line in raw.decode("utf-8").splitlines() if line.strip())


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jsonl",type=Path)
    print(json.dumps(read(parser.parse_args().jsonl),sort_keys=True))
