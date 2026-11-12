"""Pair Android Raft FFT events by logger session and bounded hook sequence."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

PREFIX = "t1_original_fft_dispatch."
EVENTS = {"before", "returned", "threw"}


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
        if not isinstance(operation, str) or not operation.startswith(PREFIX):
            continue
        event = operation[len(PREFIX):]
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
                argument = int(fields["numeric_kernel_argument"])
                present = fields["shader_present"].lower()
                if present not in ("true", "false"):
                    raise ValueError
                value = (argument, present == "true")
            else:
                expected = "managed_dispatch_threw" if event == "threw" else "managed_dispatch_call_returned"
                if fields[expected] != "true":
                    raise ValueError
                value = True
        except (KeyError, ValueError):
            counts["malformed_trace_events"] += 1
            continue
        observed = calls[(session, sequence)]
        if event in observed:
            if observed[event] != value:
                observed["conflict"] = True
            counts["duplicate_events"] += 1
        observed[event] = value
    by_argument = defaultdict(Counter)
    for observed in calls.values():
        if "conflict" in observed or {"returned", "threw"} <= observed.keys():
            counts["conflicting_calls"] += 1
        elif "before" not in observed:
            counts["terminal_without_before"] += 1
        else:
            argument, present = observed["before"]
            outcome = ("threw" if "threw" in observed else
                       "returned" if "returned" in observed else "no_terminal")
            by_argument[argument][outcome] += 1
            by_argument[argument]["shader_missing"] += not present
    return {"trace_sessions": len({session for session, _ in calls}),
            "trace_counts": dict(counts), "numeric_arguments": dict(by_argument),
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
