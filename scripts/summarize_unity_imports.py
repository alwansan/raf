"""Bounded infrastructure-only import progress from existing Unity job logs."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

STAMP = re.compile(r'^\d{4}-\d\d-\d\dT\S{8,30}Z\s*')
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
ASSET = re.compile(r'(?:Start importing|Done importing|Importing)\s+((?:Assets|Packages)/.+?)\s+(?:using Guid|with |\(Guid|->)', re.I)
METHOD = re.compile(r'\b([A-Za-z_][\w.`+]*(?::{1,2}[A-Za-z_]\w*)?)\s*\(')


def summarize(lines):
    starts, completed, methods, extensions = Counter(), Counter(), Counter(), Counter()
    patterns, last_imports = {}, []
    diagnostic_headers = Counter()
    totals = Counter()
    for raw in lines:
        totals['lines'] += 1
        stamp = STAMP.match(raw.lstrip('\ufeff'))
        timestamp = stamp[0].strip() if stamp else None
        line = ANSI.sub('', STAMP.sub('', raw.lstrip('\ufeff'))).strip()
        if line.startswith(('##[', 'echo ', 'print(', 'python3 ', 'gh api ')):
            continue
        lower = line.lower()
        if line.startswith(('Assertion failed', 'Recursive Serialization', 'Error while importing',
                            'Cannot ', 'Failed to ', 'Unable to ', 'Trying to ', 'A Native ')):
            header = re.sub(r'https?://\S+', '<url>', line[:500])
            header = re.sub(r'"[^"\n]*"|\x27[^\x27\n]*\x27', '<quoted>', header)
            header = re.sub(r'0x[0-9a-fA-F]+|\b[0-9a-fA-F]{32,}\b|\b\d+\b', '<id>', header)
            diagnostic_headers[header[:240]] += 1
        for name, needle in (
            ('refresh', 'asset pipeline refresh'), ('refresh_completed', 'refresh completed'),
            ('refresh_settings', 'refresh:'), ('reload_assemblies', 'reloadassemblies'),
            ('worker_crash', 'import worker process crashed'), ('missing_script', 'referenced script'),
            ('recursive_import', 'infinite import loop'), ('refresh_restart', 'restarting refresh'),
            ('cancel', 'operation was cancel'), ('compiler_errors', 'error cs'),
        ):
            if needle in lower:
                row = patterns.setdefault(name, {'count': 0, 'first': timestamp})
                row['count'] += 1
                row['last'] = timestamp
        if 'import' not in lower:
            continue
        totals['import_pattern_lines'] += 1
        match = ASSET.search(line)
        if match:
            path = match[1]
            # Only project-relative import identities; no URLs/arguments/source.
            if '..' in path.split('/') or '\\' in path or len(path) > 400:
                totals['rejected_import_paths'] += 1
                continue
            starts[path] += 1
            extensions[Path(path).suffix.lower() or '<directory>'] += 1
            if 'artifact id:' in lower or 'done importing' in lower:
                completed[path] += 1
            last_imports.append({'path': path, 'timestamp': timestamp,
                                 'artifact_reported': 'artifact id:' in lower})
            last_imports = last_imports[-12:]
        else:
            totals['non_asset_import_lines'] += 1
        for method in METHOD.findall(line):
            if 'Import' in method or 'Refresh' in method:
                methods[method] += 1
    return {'totals': dict(totals), 'asset_import_events': sum(starts.values()),
            'distinct_import_paths': len(starts), 'artifact_or_done_events': sum(completed.values()),
            'repeated_path_events': sum(n - 1 for n in starts.values()),
            'highest_path_repeat_count': max(starts.values(), default=0),
            'most_repeated_import_paths': dict(starts.most_common(12)),
            'import_extensions': dict(extensions), 'last_imports': last_imports,
            'import_method_occurrences': dict(methods.most_common(12)), 'patterns': patterns,
            'diagnostic_headers': dict(diagnostic_headers.most_common(12)),
            'limitations': 'Infrastructure log events only, not gameplay or asset fidelity. Repeats can be legitimate; absence of matches is unknown.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('log', type=Path)
    args = parser.parse_args()
    with args.log.open(encoding='utf-8-sig', errors='replace') as source:
        report = summarize(source)
    report['log_bytes'] = args.log.stat().st_size
    print('RAFT_UNITY_IMPORT_PROGRESS ' + json.dumps(report, sort_keys=True))
