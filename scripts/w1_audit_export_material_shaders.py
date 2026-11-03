"""Read-only, aggregate Material->Shader PPtr inventory of the real Unity export.

Internal engine IDs are classified, never accepted as authenticated programs by
this diagnostic. No names, paths, source, materials or GUIDs enter the report.
This is deliberately separate from the strict shader and water readiness gates.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

HEADER = re.compile(r'^--- !u!(\d+) &-?\d+(?: stripped)?\s*$', re.M)
SHADER = re.compile(r'^  m_Shader:\s*\{([^{}\r\n]*)\}\s*$', re.M)
GUID = re.compile(r'^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*$', re.M)
ENGINE = {'0000000000000000e000000000000000': 'default',
          '0000000000000000f000000000000000': 'extra'}


def pptr(body):
    fields = {}
    for part in body.split(','):
        pair = part.strip().split(':', 1)
        if len(pair) != 2 or pair[0] in fields:
            raise ValueError('Malformed or duplicate PPtr field')
        fields[pair[0]] = pair[1].strip()
    if not set(fields) <= {'fileID', 'guid', 'type'} or 'fileID' not in fields:
        raise ValueError('Unexpected PPtr fields')
    if not re.fullmatch(r'-?\d+', fields['fileID']):
        raise ValueError('Malformed fileID')
    if 'guid' in fields and not re.fullmatch('[0-9a-fA-F]{32}', fields['guid']):
        raise ValueError('Malformed GUID')
    if 'type' in fields and not re.fullmatch(r'\d+', fields['type']):
        raise ValueError('Malformed reference type')
    return int(fields['fileID']), fields.get('guid', '').lower(), fields.get('type')


def inventory(project):
    assets = Path(project) / 'Assets'
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError('Missing or unsafe Assets')
    errors = Counter()
    counts = Counter()
    shader_guids = Counter()
    internal = Counter()
    # Reject redirected parents before traversing or reading their contents.
    entries = sorted(assets.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise ValueError('Symlink in exported Assets')
    for path in entries:
        if path.suffix != '.shader' or not path.is_file():
            continue
        counts['shader_files'] += 1
        meta = Path(str(path) + '.meta')
        if not meta.is_file():
            errors['shader_missing_meta'] += 1
            continue
        guids = GUID.findall(meta.read_text(encoding='utf-8-sig'))
        if len(guids) != 1 or guids[0].lower() == '0' * 32:
            errors['shader_invalid_meta_guid'] += 1
            continue
        shader_guids[guids[0].lower()] += 1
    errors['duplicate_shader_guids'] = sum(n - 1 for n in shader_guids.values() if n > 1)
    for path in entries:
        if not path.is_file() or path.suffix not in {'.mat', '.asset', '.unity', '.prefab'}:
            continue
        if path.stat().st_size > 256 * 1024 * 1024:
            errors['oversize_yaml_candidate'] += 1
            continue
        with path.open('rb') as stream:
            prefix = stream.read(16)
        if not prefix.lstrip(b'\xef\xbb\xbf').startswith(b'%YAML'):
            if path.suffix == '.mat':
                errors['non_yaml_material_file'] += 1
            continue
        text = path.read_text(encoding='utf-8-sig')
        headers = list(HEADER.finditer(text))
        in_file = 0
        for i, header in enumerate(headers):
            if header[1] != '21':
                continue
            in_file += 1
            counts['material_documents'] += 1
            end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
            body = text[header.end():end]
            refs = SHADER.findall(body)
            field_count = len(re.findall(r'^  m_Shader:', body, re.M))
            if len(refs) != 1 or field_count != 1:
                errors['missing_or_ambiguous_shader_field'] += 1
                continue
            try:
                file_id, guid, kind = pptr(refs[0])
            except ValueError:
                errors['malformed_shader_pptr'] += 1
                continue
            if file_id == 0:
                errors['null_shader_reference'] += 1
            elif guid in ENGINE and kind == '0':
                counts['internal_engine_references'] += 1
                internal[(ENGINE[guid], file_id)] += 1
            elif guid and kind == '3' and shader_guids[guid] == 1 and file_id == 4800000:
                counts['resolved_exported_shader_references'] += 1
            else:
                errors['unresolved_or_unsupported_shader_reference'] += 1
        if path.suffix == '.mat' and not in_file:
            errors['material_file_without_material_document'] += 1
    if not counts['material_documents']:
        errors['no_material_documents'] += 1
    return {
        'schema_version': 1,
        'purpose': 'read-only exported material shader reference inventory',
        'counts': dict(sorted(counts.items())),
        'errors': {k: v for k, v in sorted(errors.items()) if v},
        'internal_pointer_histogram': [
            {'engine_kind': k, 'file_id': n, 'references': v}
            for (k, n), v in sorted(internal.items())],
        'reference_inventory_complete': not any(errors.values()),
        'internal_pointer_authenticity_verified': False,
        'original_material_associations_verified': False,
        'unity_or_device_execution': False,
        'changes_to_project': 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.resolve().is_relative_to(args.project.resolve()):
        raise ValueError('Report must be outside original export')
    report = inventory(args.project)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('RAFT_W1_EXPORT_SHADER_REFERENCES ' + json.dumps(report, sort_keys=True))
    if not report['reference_inventory_complete']:
        raise SystemExit('Export reference inventory found unresolved or unsupported references')


if __name__ == '__main__':
    main()
