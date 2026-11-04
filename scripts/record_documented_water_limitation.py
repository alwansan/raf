"""Allow an explicitly acknowledged experimental water limitation, or fail.

This never weakens the authentic water gate. The strict inspector still runs
first; a trial may continue ONLY when the explicit build request enumerates
exactly the conditions that are currently unmet. Any new, missing or stale
condition fails here exactly like the strict gate. No kernel is fabricated and
`authentic_water_kernel_identity_verified` is never toggled.
"""
import argparse
import json
from pathlib import Path
import re

from scripts.verify_water_render_contract import inspect, native_ready

MAX_ACKNOWLEDGED = 32
MAX_CONDITION_CHARS = 300
MAX_REQUEST_BYTES = 64 * 1024
CONDITION = re.compile(r'[a-z_]+(:[^\r\n]{1,%d})?' % MAX_CONDITION_CHARS)


def unmet_conditions(report):
    contracts = report.get('shader_contracts')
    if not isinstance(contracts, dict) or set(contracts) == set() or len(contracts) > 64:
        raise ValueError('Water report lacks bounded shader contracts')
    unmet = []
    for name in sorted(contracts):
        if not isinstance(name, str) or len(name) > MAX_CONDITION_CHARS:
            raise ValueError('Water report contains an invalid shader identity')
        if not contracts[name].get('contract_satisfied'):
            unmet.append('shader_pass_contract:' + name)
    if not report.get('water_compute_source_candidate_present'):
        unmet.append('water_compute_source_candidate')
    if not report.get('authentic_water_kernel_identity_verified'):
        unmet.append('authentic_water_kernel_identity')
    if len(unmet) > MAX_ACKNOWLEDGED:
        raise ValueError('Water report contains too many unmet conditions')
    return unmet


def check(project, request, out=None):
    project = Path(project)
    if project.is_symlink() or not project.is_dir():
        raise ValueError('Unsafe or missing reconstructed project')
    report = inspect(project)
    if native_ready(report):
        print('RAFT_WATER_CONTRACT strict=pass')
        return {'status': 'satisfied', 'unmet_conditions': []}
    unmet = unmet_conditions(report)
    if not unmet:
        # The report is not ready but names no unmet condition: refuse rather
        # than fabricating a limitation record.
        raise ValueError('Water report is incomplete but lists no unmet condition')
    request = Path(request)
    if request.is_symlink() or not request.is_file():
        raise ValueError('Documented limitation needs an explicit nonredirected build request')
    if request.stat().st_size > MAX_REQUEST_BYTES:
        raise ValueError('Build request exceeds the bounded documented-limitation size')
    payload = json.loads(request.read_text(encoding='utf-8'))
    acknowledged = payload.get('documented_water_limitations')
    if not isinstance(acknowledged, list) or len(acknowledged) > MAX_ACKNOWLEDGED:
        raise ValueError('Build request does not document an explicit water limitation list')
    if any(not isinstance(item, str) or CONDITION.fullmatch(item) is None for item in acknowledged):
        raise ValueError('Build request limitation entries are malformed')
    if len(set(acknowledged)) != len(acknowledged):
        raise ValueError('Build request limitation entries are duplicated')
    observed = sorted(set(unmet))
    if sorted(acknowledged) != observed:
        raise ValueError('Documented water limitations do not exactly match the live unmet conditions')
    record = {
        'schema_version': 1,
        'experimental': True,
        'strict_water_gate': 'not_passed',
        'documented_by_request': payload.get('request_id'),
        'unmet_conditions': observed,
        'shader_contracts': {
            name: report['shader_contracts'][name] for name in sorted(report['shader_contracts'])
        },
        'water_compute_source_candidate_present': bool(
            report.get('water_compute_source_candidate_present')),
        'water_named_compute_sources_with_kernels': report.get(
            'water_named_compute_sources_with_kernels'),
        'authentic_water_kernel_identity_verified': False,
        'device_execution_verified': False,
        'modified_source': bool(report.get('modified_source')),
    }
    if out is not None:
        out = Path(out)
        if out.is_symlink() or out.exists():
            raise ValueError('Limitation record destination already exists or is redirected')
        out.write_text(json.dumps(record, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    print('RAFT_EXPERIMENTAL_WATER_LIMITATION ' + json.dumps(record, sort_keys=True))
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    check(args.project, args.request, args.out)


if __name__ == '__main__':
    main()
