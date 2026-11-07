"""Bounded private LogRaft root classifier; never emit raw log text or identifiers.
This is heuristic Logcat text evidence, NOT a Unity FindKernel or GPU proof.
"""
import argparse
import json
import re
from pathlib import Path

STAMP = re.compile(r'(?<!\d)(\d\d-\d\d \d\d:\d\d:\d\d\.\d{3})(?!\d)')
KERNEL = re.compile(r'\b(?:invalid\s+(?:compute\s+)?kernel\s+(?:index\s*)?|kernel\s+index\s+invalid\s*[:=]?\s*)(\d{1,4})\b', re.I)
KERNEL_ALT = re.compile(r'\bkernel\s+(?:at\s+)?index\s*\(?([0-9]{1,4})\)?\s+is\s+invalid\b', re.I)
PASS = re.compile(r'\b(?:invalid\s+pass|pass\s+is\s+invalid|invalid\s+shader\s+pass|does\s+not\s+have\s+(?:a\s+)?pass)\b', re.I)
MATERIAL = {'spectrum': re.compile(r'\bspectrum\b', re.I),
            'foam_global': re.compile(r'\bfoam[ _-]+global\b', re.I)}

def classify(line):
    if len(line) > 32768:
        return None
    m = KERNEL.search(line) or KERNEL_ALT.search(line)
    if m:
        return 'kernel_index_6' if int(m.group(1)) == 6 else 'kernel_other'
    if PASS.search(line) and re.search(r'ultimate\s*water|spectrum|foam', line, re.I):
        for key, regex in MATERIAL.items():
            if regex.search(line):
                return 'pass_' + key
        return 'pass_other_water'
    return None

def scan(paths):
    if not 1 <= len(paths) <= 16:
        raise ValueError('invalid segment count')
    seen, counts, first, total = set(), {}, {}, 0
    for path in paths:
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise ValueError('missing or symlinked log segment')
        stat = path.stat()
        if stat.st_size > 500_000_000 or total + stat.st_size > 500_000_000:
            raise ValueError('log size bound exceeded')
        if (stat.st_dev, stat.st_ino) in seen:
            raise ValueError('duplicate log segment')
        seen.add((stat.st_dev, stat.st_ino))
        total += stat.st_size
        with path.open('rb') as stream:
            while True:
                # readline(limit) prevents allocating an entire malformed giant line.
                raw = stream.readline(32769)
                if not raw:
                    break
                if len(raw) > 32768:
                    # Drop the rest of this physical line: never classify its tail
                    # as an independent Logcat record.
                    while raw and not raw.endswith(b'\n'):
                        raw = stream.readline(32769)
                    continue
                line = raw.decode('utf-8', 'replace')
                kind = classify(line)
                if kind is None:
                    continue
                counts[kind] = counts.get(kind, 0) + 1
                stamp = STAMP.search(line)
                if stamp:
                    candidate = stamp.group(1)
                    if kind not in first or first[kind] is None or candidate < first[kind]:
                        first[kind] = candidate
                elif kind not in first:
                    first[kind] = None
    return {'first_by_category': first, 'root_line_counts': counts,
            'original_kernel_name_proven': False, 'findkernel_dispatch_proven': False,
            'raw_text_disclosed': False, 'input_segments': len(paths),
            'classification_scope': 'heuristic text roots; compare with pinned session-summary totals'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('segments', nargs='+', type=Path)
    args = parser.parse_args()
    print(json.dumps(scan(args.segments), sort_keys=True))

if __name__ == '__main__':
    main()
