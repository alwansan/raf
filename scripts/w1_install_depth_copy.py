"""Install the pinned W1 reconstruction into its traced AssetRipper shader."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from scripts.restore_builtin_shaders import exported_shader_identity, _require_safe_asset_path
from scripts.verify_export_lineage import identity, pointer
from scripts.w1_audit_export_material_shaders import ENGINE
from scripts.w1_recover_depth_passes import SOURCE_IDENTITY, TARGET

WRAPPER_SHA256 = '0a7e11f750cac17ecc25cb7179c0a29850d6fb91fa983618f12e6bd8782ed1ea'


def traced_guid(trace):
    if trace.is_symlink() or not trace.is_file() or trace.stat().st_size > 32 * 1024 * 1024:
        raise ValueError('Missing or unsafe same-instance shader trace')
    document = json.loads(trace.read_text(encoding='utf-8'))
    if (not isinstance(document, dict)
            or document.get('schema_version') != 1
            or not re.fullmatch(r'[0-9a-f]{32}', document.get('export_instance', ''))
            or not isinstance(document.get('objects'), list)):
        raise ValueError('Invalid same-instance shader trace')
    shaders = [row for row in document['objects'] if row.get('class_id') == 48]
    targets = [row for row in shaders
               if identity(row['source']) == SOURCE_IDENTITY]
    if len(targets) != 1 or targets[0].get('exportable') is not True:
        raise ValueError('Expected one original Depth Copy shader trace')
    file_id, guid, kind = pointer(targets[0]['export'])
    if file_id <= 0 or guid in ENGINE or guid == '0' * 32 or kind not in ('2', '3'):
        raise ValueError('Invalid original Depth Copy export pointer')
    if sum(pointer(row['export'])[1] == guid for row in shaders) != 1:
        raise ValueError('Ambiguous original Depth Copy export GUID')
    return guid


def install(project, shader, backup, trace):
    project = project.absolute()
    if any(p.is_symlink() for p in (project, *project.parents)):
        raise ValueError('Unsafe project ancestor')
    assets = project / 'Assets'
    _require_safe_asset_path(assets, assets)
    if shader.is_symlink():
        raise ValueError('Unsafe reconstruction input')
    content = shader.read_bytes()
    if hashlib.sha256(content).hexdigest() != WRAPPER_SHA256:
        raise ValueError('Reconstruction fingerprint mismatch')
    if exported_shader_identity(content.decode()) != TARGET:
        raise ValueError('Reconstruction identity mismatch')
    guid = traced_guid(trace)
    targets = []
    for path in assets.rglob('*.shader'):
        _require_safe_asset_path(assets, path)
        if exported_shader_identity(path.read_text(encoding='utf-8-sig')) == TARGET:
            targets.append(path)
    if len(targets) != 1:
        raise ValueError('Expected exactly one exported target identity')
    target = targets[0]
    meta = Path(str(target) + '.meta')
    _require_safe_asset_path(assets, meta)
    metadata = meta.read_bytes()
    guid_fields = [line for line in metadata.splitlines() if line.startswith(b'guid:')]
    if (len(guid_fields) != 1 or
            re.fullmatch(rb'guid:[ \t]*([0-9a-fA-F]{32})[ \t]*', guid_fields[0]) is None or
            guid_fields[0].split(b':', 1)[1].strip().lower() != guid.encode('ascii')):
        raise ValueError('Exported target metadata does not match the traced source GUID')
    original = target.read_bytes()
    backup = backup.absolute()
    if backup.resolve().is_relative_to(project.resolve()) or any(p.is_symlink() for p in (backup, *backup.parents)):
        raise ValueError('Backup must be external and nonredirected')
    backup.mkdir(parents=True, exist_ok=False)
    try:
        (backup / 'original.shader').write_bytes(original)
        (backup / 'original.shader.meta').write_bytes(metadata)
    except BaseException:
        shutil.rmtree(backup)
        raise
    changed = False
    try:
        # Fail if another stage changed the selected export after preflight.
        _require_safe_asset_path(assets, target)
        if target.read_bytes() != original or meta.read_bytes() != metadata:
            raise ValueError('Export changed before installation')
        changed = True
        target.write_bytes(content)
        if target.read_bytes() != content or meta.read_bytes() != metadata:
            raise ValueError('Installed source or metadata mismatch')
    except BaseException:
        # Keep the complete external backup for diagnosis/retry.
        if changed:
            target.write_bytes(original)
        raise
    return {'installed_targets': 1, 'exported_meta_unchanged': True,
            'target_path_sha256': hashlib.sha256(str(target.relative_to(assets)).encode()).hexdigest(),
            'original_export_shader_sha256': hashlib.sha256(original).hexdigest(),
            'meta_sha256': hashlib.sha256(metadata).hexdigest(),
            'reconstruction_sha256': WRAPPER_SHA256,
            'source_shader_guid_matches_same_instance_trace': True,
            'unity_binding_or_phone_acceptance': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--private-shader', type=Path, required=True)
    parser.add_argument('--backup', type=Path, required=True)
    parser.add_argument('--trace', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = install(args.project, args.private_shader, args.backup, args.trace)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_DEPTH_INSTALL ' + json.dumps(result, sort_keys=True))
