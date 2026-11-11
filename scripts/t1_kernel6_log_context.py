#!/usr/bin/env python3
"""Read-only, bounded kernel-6 log context triage. Never infer a Unity kernel name from index."""
import argparse
import hashlib
import json
import re
from collections import deque
from pathlib import Path

KERNEL6 = re.compile(r"\bkernel(?:\s+index)?\s*(?:[:=#]\s*6(?![\w.])|\(\s*6\s*\)|6(?![\w.]))", re.I)
KERNEL_ERROR = re.compile(r"\b(?:invalid|error|failed|failure|exception|out.of.range|missing)\b|\b(?:not\s+found|cannot\s+find|could\s+not\s+find)\b|water_fft_invalid_compute_kernel", re.I)
CONTEXT = re.compile(r"FindKernel|Dispatch|ComputeShader|ultimate_water_invalid_pass|water_fft_invalid_compute_kernel", re.I)
PASS = re.compile(r"\b(?:Spectrum|Foam(?:\s+Global)?|Subsurface\s+Blur|Utility\s+Noise)\b", re.I)

def scan(path, session, before=8, after=8, max_hits=30, errors_only=False):
    if not session or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", session):
        raise ValueError("explicit safe session identifier required")
    if not (0 <= before <= 100 and 0 <= after <= 100 and 1 <= max_hits <= 1000):
        raise ValueError("invalid bounded context settings")
    prior = deque(maxlen=before)
    events = []
    pending = []
    sha = hashlib.sha256()
    counts = {"kernel6_lines": 0, "kernel6_error_lines": 0, "kernel6_nonerror_mentions": 0, "water_pass_lines": 0, "findkernel_lines": 0, "dispatch_lines": 0}
    with Path(path).open("rb") as stream:
        for lineno, raw in enumerate(stream, 1):
            sha.update(raw)
            line = raw.decode("utf-8", "replace")
            if "ultimate_water_invalid_pass" in line.lower():
                counts["water_pass_lines"] += 1
            if "findkernel" in line.lower():
                counts["findkernel_lines"] += 1
            if "dispatch" in line.lower():
                counts["dispatch_lines"] += 1
            hit = bool(KERNEL6.search(line))
            if hit:
                counts["kernel6_lines"] += 1
                if KERNEL_ERROR.search(line):
                    counts["kernel6_error_lines"] += 1
                else:
                    counts["kernel6_nonerror_mentions"] += 1
                if len(events) < max_hits and (not errors_only or KERNEL_ERROR.search(line)):
                    event = {"line": lineno, "before": [item for item in prior if item["markers"]], "after": [],
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
            # Physical-line proximity: non-diagnostic lines must also age the
            # look-behind window. Emit only diagnostic markers, never raw text.
            for end, event in pending:
                if markers and lineno > event["line"] and lineno <= end:
                    event["after"].append(compact)
            prior.append(compact)
            pending = [(end, event) for end, event in pending if lineno < end]
    return {"session_id": session, "source_sha256": sha.hexdigest(),
            "counts": counts, "sampled_hits": len(events), "sample_errors_only": bool(errors_only), "events": events,
            "original_kernel_identity_proven": False,
            "note": "kernel6_lines includes mentions, not only errors; error_lines requires an error word on the same line. Nearby markers are not causal proof or FindKernel-to-index mapping."}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("log", type=Path)
    p.add_argument("--session", required=True)
    p.add_argument("--before", type=int, default=8)
    p.add_argument("--after", type=int, default=8)
    p.add_argument("--max-hits", type=int, default=30)
    p.add_argument("--errors-only", action="store_true", help="Sample only kernel-6 lines with same-line error markers")
    args = p.parse_args()
    print(json.dumps(scan(args.log, args.session, args.before, args.after, args.max_hits, args.errors_only),
                     ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
