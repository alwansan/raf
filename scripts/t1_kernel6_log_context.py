#!/usr/bin/env python3
"""Read-only, bounded kernel-6 log context triage. Never infer a Unity kernel name from index."""
import argparse
import hashlib
import json
import re
from collections import deque
from pathlib import Path

KERNEL6 = re.compile(r"kernel(?:\\s+index)?\\s*[:=#]?\\s*6\\b", re.I)
CONTEXT = re.compile(r"FindKernel|Dispatch|ComputeShader|ultimate_water_invalid_pass|water_fft_invalid_compute_kernel", re.I)
PASS = re.compile(r"\\b(?:Spectrum|Foam(?:\\s+Global)?|Subsurface\\s+Blur|Utility\\s+Noise)\\b", re.I)

def scan(path, session, before=8, after=8, max_hits=30):
    if not session or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", session):
        raise ValueError("explicit safe session identifier required")
    if not (0 <= before <= 100 and 0 <= after <= 100 and 1 <= max_hits <= 1000):
        raise ValueError("invalid bounded context settings")
    prior = deque(maxlen=before)
    events = []
    pending = []
    sha = hashlib.sha256()
    counts = {"kernel6_lines": 0, "water_pass_lines": 0, "findkernel_lines": 0, "dispatch_lines": 0}
    with Path(path).open("rb") as stream:
        for lineno, raw in enumerate(stream, 1):
            sha.update(raw)
            line = raw.decode("utf-8", "replace")
            if "ultimate_water_invalid_pass" in line:
                counts["water_pass_lines"] += 1
            if "FindKernel" in line:
                counts["findkernel_lines"] += 1
            if "Dispatch" in line:
                counts["dispatch_lines"] += 1
            hit = bool(KERNEL6.search(line))
            if hit:
                counts["kernel6_lines"] += 1
                if len(events) < max_hits:
                    event = {"line": lineno, "before": list(prior), "after": [],
                             "pass_tokens": sorted(set(PASS.findall(line)))}
                    events.append(event)
                    pending.append((lineno + after, event))
            # Keep only line numbers and diagnostic categories; no proprietary log payload.
            markers = []
            if KERNEL6.search(line):
                markers.append("kernel_index_6")
            for marker in ("FindKernel", "Dispatch", "ComputeShader",
                           "ultimate_water_invalid_pass", "water_fft_invalid_compute_kernel"):
                if marker.lower() in line.lower():
                    markers.append(marker)
            markers.extend("pass:" + p.lower().replace(" ", "_") for p in PASS.findall(line))
            compact = {"line": lineno, "markers": sorted(set(markers))}
            if markers:
                for end, event in pending:
                    if lineno > event["line"] and lineno <= end:
                        event["after"].append(compact)
                prior.append(compact)
            pending = [(end, event) for end, event in pending if lineno < end]
    return {"session_id": session, "source_sha256": sha.hexdigest(),
            "counts": counts, "sampled_hits": len(events), "events": events,
            "original_kernel_identity_proven": False,
            "note": "Nearby markers are not causal proof or FindKernel-to-index mapping."}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", type=Path)
    p.add_argument("--session", required=True)
    p.add_argument("--before", type=int, default=8)
    p.add_argument("--after", type=int, default=8)
    p.add_argument("--max-hits", type=int, default=30)
    args = p.parse_args()
    print(json.dumps(scan(args.log, args.session, args.before, args.after, args.max_hits),
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
