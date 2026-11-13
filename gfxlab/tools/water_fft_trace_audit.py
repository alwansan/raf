"""Pair Android Raft FFT events by logger session and bounded hook sequence."""
import argparse
from collections import Counter, defaultdict
import json
import re
from pathlib import Path

PREFIXES = {"t1_original_fft_dispatch": "dispatch", "t1_original_fft_bind": "binding"}
EVENTS = {"before", "returned", "threw"}
ORIGINAL_FFT_NAME_SHA256 = "60c1b5ee2352bd6e303aa5fc68c88f61031cf21234f524d54ec02334a8e142d1"
RECEIVER_FIELDS = {"shader_present", "shader_name_sha256", "shader_instance_session_local"}


def binding_receiver(fields):
    if not RECEIVER_FIELDS.intersection(fields):
        return None
    present = fields["shader_present"].lower()
    digest = fields["shader_name_sha256"]
    instance = int(fields["shader_instance_session_local"])
    if present == "false" and digest == "unavailable" and instance == 0:
        return ("missing", instance)
    if present != "true" or instance == 0:
        raise ValueError("Invalid binding receiver")
    if digest == "unavailable":
        return ("name_unavailable", instance)
    if not re.fullmatch(r"[a-f0-9]{64}", digest):
        raise ValueError("Invalid binding receiver name digest")
    return ("original_name_match" if digest == ORIGINAL_FFT_NAME_SHA256 else "other_name", instance)


def audit(lines):
    calls = defaultdict(dict)
    counts = Counter()
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            counts["unreadable_lines"] += 1
            continue
        if not isinstance(row, dict) or row.get("area") != "water":
            continue
        operation = row.get("operation")
        if not isinstance(operation, str):
            continue
        prefix, _, event = operation.partition(".")
        kind = PREFIXES.get(prefix)
        if kind is None:
            continue
        session, detail = row.get("session"), row.get("detail")
        if event not in EVENTS or not isinstance(session, str) or not session or not isinstance(detail, str):
            counts["malformed_trace_events"] += 1
            continue
        fields = dict(field.strip().split("=", 1) for field in detail.split(";") if "=" in field)
        try:
            sequence = int(fields["sequence"])
            if not 1 <= sequence <= 16:
                raise ValueError
            if event == "before":
                if fields["source_sha_prefix"] != "8aa32937d423":
                    raise ValueError
                if kind == "binding":
                    site, pass_index = int(fields["site"]), int(fields["pass"])
                    if not 0 <= site < 6 or pass_index != site // 3:
                        raise ValueError
                    value = (site, binding_receiver(fields))
                else:
                    argument = int(fields["numeric_kernel_argument"])
                    present = fields["shader_present"].lower()
                    if present not in ("true", "false"):
                        raise ValueError
                    value = (argument, present == "true")
            elif kind == "binding":
                if fields["gpu_result"] != "unverified":
                    raise ValueError
                value = True
            else:
                expected = "managed_dispatch_threw" if event == "threw" else "managed_dispatch_call_returned"
                if fields[expected] != "true":
                    raise ValueError
                value = True
        except (KeyError, ValueError):
            counts["malformed_trace_events"] += 1
            continue
        observed = calls[(session, kind, sequence)]
        if event in observed:
            if observed[event] != value:
                observed["conflict"] = True
            counts["duplicate_events"] += 1
        observed[event] = value
    by_argument = defaultdict(Counter)
    by_binding_site = defaultdict(Counter)
    receiver_outcomes = defaultdict(Counter)
    receiver_instances = defaultdict(set)
    for (session, kind, _), observed in calls.items():
        if "conflict" in observed or {"returned", "threw"} <= observed.keys():
            counts["conflicting_calls"] += 1
        elif "before" not in observed:
            counts["terminal_without_before"] += 1
        else:
            outcome = ("threw" if "threw" in observed else
                       "returned" if "returned" in observed else "no_terminal")
            if kind == "binding":
                site, receiver = observed["before"]
                by_binding_site[site][outcome] += 1
                if receiver is not None:
                    identity, instance = receiver
                    receiver_outcomes[identity][outcome] += 1
                    if instance:
                        receiver_instances[identity].add((session, instance))
            else:
                argument, present = observed["before"]
                by_argument[argument][outcome] += 1
                by_argument[argument]["shader_missing"] += not present
    return {"trace_sessions": len({session for session, _, _ in calls}),
            "trace_counts": dict(counts), "numeric_arguments": dict(by_argument),
            "binding_sites": dict(by_binding_site),
            "binding_receiver_outcomes": dict(receiver_outcomes),
            "binding_receiver_session_instances": {k: len(v) for k, v in receiver_instances.items()},
            "gpu_result_verified": False, "runtime_kernel_registration_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path, nargs="+")
    args = parser.parse_args()

    def lines():
        for path in args.logs:
            with path.open(encoding="utf-8-sig") as log:
                yield from log

    print(json.dumps(audit(lines()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
