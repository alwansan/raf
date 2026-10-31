"""Restore scene-owned ScriptableObjects exported as invalid cross-scene .asset files.

Only unique, single-scene ownership is accepted. No field or object is dropped.
Original files/metas are backed up outside the Unity project before installation.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil

HEADER = re.compile(r'^--- !u!(\d+) &(-?\d+)(?: stripped)?[^\n]*\n', re.M)
POINTER = re.compile(r'\{[^{}\n]*\bfileID:\s*-?\d+[^{}\n]*\}')
GUID = re.compile(r'\bguid:\s*([0-9a-fA-F]{32})\b')
FILEID = re.compile(r'\bfileID:\s*(-?\d+)\b')


def references(text):
    for match in POINTER.finditer(text):
        guid = GUID.search(match[0])
        yield match, int(FILEID.search(match[0])[1]), guid[1].lower() if guid else None


def documents(text):
    headers = list(HEADER.finditer(text))
    result = {}
    for index, match in enumerate(headers):
        key = int(match[2])
        if key in result:
            raise ValueError('Duplicate local object ID')
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        result[key] = (int(match[1]), text[match.end():end])
    return result


def fingerprint(doc, owner, reverse):
    kind, body = doc
    def replace(match):
        local = int(FILEID.search(match[0])[1])
        guid = GUID.search(match[0])
        target = (guid[1].lower() if guid else owner, local)
        target = reverse.get(target, target)
        return '<PPtr:' + repr(target) + '>' if local else '<PPtr:null>'
    body = POINTER.sub(replace, body).rstrip('\n')
    return hashlib.sha256((str(kind) + '\n' + body).encode()).hexdigest()


def plan(project):
    project = Path(project).resolve()
    assets = project / 'Assets'
    rows, paths = {}, {}
    for path in sorted(assets.rglob('*')):
        if not path.is_file() or path.suffix == '.meta':
            continue
        if path.is_symlink():
            raise ValueError('Symlink inside project')
        # Shader/texture/source payloads are not deserialized as YAML here.
        with path.open('rb') as stream:
            if not stream.read(32).lstrip(b'\xef\xbb\xbf').startswith(b'%YAML'):
                continue
        text = path.read_bytes().decode('utf-8-sig')
        meta = Path(str(path) + '.meta')
        if not meta.is_file():
            raise ValueError('Serialized YAML asset lacks original meta')
        match = re.search(r'^guid:\s*([0-9a-fA-F]{32})\s*$', meta.read_text(), re.M)
        if not match or match[1].lower() in rows:
            raise ValueError('Missing or duplicate serialized asset GUID')
        guid = match[1].lower()
        row = {'path': path, 'meta': meta, 'text': text, 'docs': documents(text), 'guid': guid}
        rows[guid] = row
        paths[path] = guid
    scenes = {guid: row for guid, row in rows.items() if row['path'].suffix == '.unity'}
    owners = {}
    # Cross-file pointers into an actual scene object are illegal in persistent
    # standalone assets; scene-asset pointers absent from the object table stay external.
    for guid, row in rows.items():
        if guid in scenes:
            continue
        target_scenes = set()
        for _, fileid, target in references(row['text']):
            if fileid and target in scenes and fileid in scenes[target]['docs']:
                target_scenes.add(target)
        if len(target_scenes) > 1:
            raise ValueError('Asset references multiple scenes: ' + str(row['path'].relative_to(project)))
        if target_scenes:
            owners[guid] = next(iter(target_scenes))
    # A persistent asset cannot continue pointing into a relocated scene object.
    changed = True
    while changed:
        changed = False
        for guid, row in rows.items():
            needed = {owners[target] for _, fileid, target in references(row['text'])
                      if fileid and target in owners}
            if guid in owners:
                needed.add(owners[guid])
            if guid in scenes:
                if needed - {guid}:
                    raise ValueError('Another scene references scene-owned data: ' + str(row['path'].relative_to(project)))
            elif needed:
                if len(needed) != 1:
                    raise ValueError('Indirect scene ownership conflict: ' + str(row['path'].relative_to(project)))
                owner = next(iter(needed))
                if guid not in owners:
                    owners[guid] = owner
                    changed = True
    mapping = {}
    used = {g: set(r['docs']) for g, r in scenes.items()}
    for guid, owner in sorted(owners.items()):
        row = rows[guid]
        relative = row['path'].relative_to(assets)
        if row['path'].suffix != '.asset' or len(row['docs']) != 1 or next(iter(row['docs'].values()))[0] != 114:
            raise ValueError('Scene-bound source is not a single ScriptableObject YAML asset: ' + str(relative))
        if any(part.lower() in ('resources', 'streamingassets', 'editor') for part in relative.parts[:-1]):
            raise ValueError('Cannot relocate resource/editor path without runtime lookup proof: ' + str(relative))
        oldid = next(iter(row['docs']))
        # Preserve original local ID when available. On collisions allocate a
        # deterministic local alias, representing the SAME object and fields.
        newid = oldid
        if newid in used[owner]:
            newid = -int(hashlib.sha256((guid + ':' + str(oldid)).encode()).hexdigest()[:15], 16) - 1
        if not newid or newid in used[owner]:
            raise ValueError('Scene-local identity collision')
        used[owner].add(newid)
        mapping[(guid, oldid)] = (owner, newid)
    reverse = {target: source for source, target in mapping.items()}
    for row in rows.values():
        non_pointers = POINTER.sub('', row['text']).lower()
        if any(guid in non_pointers for guid in owners):
            raise ValueError('Non-PPtr GUID consumer requires inspection')
    edits, rewritten = {}, [0]
    def rewrite(text, current_guid):
        def replace(match):
            fileid = int(FILEID.search(match[0])[1])
            gm = GUID.search(match[0])
            target_guid = gm[1].lower() if gm else current_guid
            if fileid and target_guid in owners and (target_guid, fileid) not in mapping:
                raise ValueError('Reference to an absent object in relocated asset')
            target = mapping.get((target_guid, fileid), (target_guid, fileid))
            if target[0] == current_guid and fileid and (gm or (target_guid, fileid) in mapping):
                if target[1] not in used.get(current_guid, set()):
                    raise ValueError('Target local object absent')
                rewritten[0] += 1
                return '{fileID: ' + str(target[1]) + '}'
            if target != (target_guid, fileid):
                raise ValueError('Unexpected external consumer of scene-owned object')
            return match[0]
        return POINTER.sub(replace, text)
    for guid, row in rows.items():
        if guid in owners:
            continue
        updated = rewrite(row['text'], guid)
        if guid in scenes:
            for source, owner in sorted(owners.items()):
                if owner != guid:
                    continue
                sourceid = next(iter(rows[source]['docs']))
                _, newid = mapping[(source, sourceid)]
                kind, body = rows[source]['docs'][sourceid]
                # Original local self references must resolve within the moved object.
                for _, local, external in references(body):
                    if local and external is None and local != sourceid:
                        raise ValueError('Unresolved local reference in standalone source')
                body = POINTER.sub(lambda m: '{fileID: ' + str(newid) + '}'
                    if not GUID.search(m[0]) and int(FILEID.search(m[0])[1]) == sourceid else m[0], body)
                updated = updated.rstrip('\n') + '\n--- !u!' + str(kind) + ' &' + str(newid) + '\n' + rewrite(body, guid)
        if updated != row['text']:
            edits[row['path']] = updated
    # Compare EVERY serialized object by original logical identity. This protects
    # arbitrary original fields and unrelated objects, not just pointer counts.
    before, after = {}, {}
    for guid, row in rows.items():
        for local, doc in row['docs'].items():
            before[(guid, local)] = fingerprint(doc, guid, {})
        if guid in owners:
            continue
        text = edits.get(row['path'], row['text'])
        for local, doc in documents(text).items():
            key = reverse.get((guid, local), (guid, local))
            if key in after:
                raise ValueError('Relocated object duplicated')
            after[key] = fingerprint(doc, guid, reverse)
    if before != after:
        raise ValueError('Original object field or logical reference fingerprint changed')
    # Any non-YAML consumer may encode a GUID and cannot be silently ignored.
    for path in assets.rglob('*') if owners else ():
        if not path.is_file() or path.suffix == '.meta' or path in paths:
            continue
        with path.open('rb') as source:
            tail = b''
            while chunk := source.read(1024 * 1024):
                payload = (tail + chunk).lower()
                if any(g.encode() in payload for g in owners):
                    raise ValueError('Non-YAML consumer of relocated object requires inspection')
                tail = payload[-64:]
    report = {'scene_bound_assets': len(owners), 'owner_scenes': len(set(owners.values())),
              'serialized_objects_before': len(before), 'serialized_objects_after': len(after),
              'logical_object_fingerprints_unchanged': True, 'rewritten_pointers': rewritten[0],
              'modified_scene_files': len(edits), 'source_meta_bytes_preserved': None,
              'applied': False, 'installed_object_fingerprints_verified': False}
    return {'project': project, 'edits': edits, 'relocated': [rows[g] for g in sorted(owners)],
            'remaining': {g: r for g, r in rows.items() if g not in owners},
            'expected_objects': before, 'reverse': reverse,
            'meta_hashes': {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in assets.rglob('*.meta')},
            'report': report}


def apply(result, backup):
    project, backup = result['project'], Path(backup).resolve()
    if backup == project or project in backup.parents or backup.exists():
        raise ValueError('Backup must be a new directory outside the Unity project')
    originals = set(result['edits'])
    for row in result['relocated']:
        originals.update((row['path'], row['meta']))
    backup.mkdir(parents=True)
    for path in originals:
        target = backup / path.relative_to(project)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        if path.read_bytes() != target.read_bytes():
            raise ValueError('Backup verification failed before writes')
    try:
        for path, text in result['edits'].items():
            path.write_bytes(text.encode())
        for row in result['relocated']:
            row['path'].unlink()
            row['meta'].unlink()
        disk = {}
        for guid, row in result['remaining'].items():
            for local, doc in documents(row['path'].read_bytes().decode('utf-8-sig')).items():
                key = result['reverse'].get((guid, local), (guid, local))
                if key in disk:
                    raise ValueError('Duplicate installed logical object')
                disk[key] = fingerprint(doc, guid, result['reverse'])
        if disk != result['expected_objects']:
            raise ValueError('Installed object fingerprint validation failed')
        relocated_metas = {r['meta'] for r in result['relocated']}
        for path, expected in result['meta_hashes'].items():
            actual = backup / path.relative_to(project) if path in relocated_metas else path
            if hashlib.sha256(actual.read_bytes()).hexdigest() != expected:
                raise ValueError('Original meta bytes changed')
    except BaseException:
        for path in originals:
            shutil.copyfile(backup / path.relative_to(project), path)
        raise
    result['report'].update(applied=True, source_meta_bytes_preserved=True,
                            installed_object_fingerprints_verified=True)
    return result['report']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--backup-dir', type=Path)
    args = parser.parse_args()
    result = plan(args.project)
    if args.apply:
        if not args.backup_dir:
            parser.error('--backup-dir is required for --apply')
        apply(result, args.backup_dir)
    print('RAFT_SCENE_BOUND_ASSET_REEMBED ' + json.dumps(result['report'], sort_keys=True))
