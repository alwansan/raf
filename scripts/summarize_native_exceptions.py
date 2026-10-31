"""Aggregate exception identities/first frames from existing logs; never emit source."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
EXCEPTION = re.compile(r'^((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*(?:Exception|Error))(?::|\s|$)')
FRAME = re.compile(r'^\s*(?:at\s+)?([A-Za-z_][\w.`+<>]*(?:\.[\w`+<>]+)+)\s*\(')


def summarize(lines):
    exceptions, origins, categories = Counter(), Counter(), Counter()
    pending = None
    for raw in lines:
        line = ANSI.sub('', raw).strip('\ufeff\r\n')
        line = re.sub(r'^\d{4}-\d\d-\d\dT\S+Z\s*', '', line)
        if line.startswith(('##[', 'echo ', 'print(', 'out.write(', 'f.write(')):
            pending = None
            continue
        match = EXCEPTION.match(line)
        if match:
            pending = match[1]
            exceptions[pending] += 1
            continue
        if pending:
            frame = FRAME.match(line)
            if frame:
                origins[pending + ' @ ' + frame[1]] += 1
                pending = None
            elif line.strip():
                pending = None
        lowered = line.lower()
        for category, needle in (
            ('missing_stream', 'unable to open archive file'),
            ('shader_error', 'shader error'),
            ('missing_native_library', 'unable to load dll'),
            ('missing_script', 'the referenced script'),
            ('serialization_error', 'serialization error'),
            ('fmod_error', 'fmod error'),
            ('failed_read', 'failed to read'),
            ('error_prefixed', 'error:'),
        ):
            if needle in lowered:
                categories[category] += 1
    return {'exception_occurrences': dict(exceptions),
            'first_stack_method_occurrences': dict(origins.most_common(40)),
            'diagnostic_pattern_occurrences': dict(categories),
            'limitations': 'Log occurrences may be duplicated; not BuildReport error accounting. No raw messages, arguments, paths or source emitted.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    with args.log.open(encoding='utf-8-sig', errors='replace') as source:
        print('RAFT_NATIVE_EXCEPTION_SUMMARY ' + json.dumps(summarize(source), sort_keys=True))
