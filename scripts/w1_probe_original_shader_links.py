"""Preserve original Shader object identity and inspect duplicate program keys.

All original object names, owner/pathIDs and Material edges stay private. Export
GUIDs cannot be reconstructed: the pinned exporter uses UnityGuid.NewGuid().
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath

from scripts.w1_verify_engine_export import digest, exact_table
from scripts.w1_stage_zip2_owners import fingerprint


def resolve_pointer(owner, external_names, pointer):
    if set(pointer) != {'m_FileID', 'm_PathID'}:
        raise ValueError('Unexpected original Shader PPtr schema')
    file_id, path_id = pointer['m_FileID'], pointer['m_PathID']
    if type(file_id) is not int or type(path_id) is not int or file_id < 0:
        raise ValueError('Invalid original Shader PPtr values')
    if path_id == 0:
        return None
    if file_id == 0:
        return owner, path_id
    if file_id > len(external_names):
        raise ValueError('Original external Shader file index outside table')
    # FileID is ONE based. Never open a path supplied by a serialized object;
    # normalized basenames are only looked up in the authenticated owner map.
    external = external_names[file_id - 1]
    if not isinstance(external, str) or not external or '\x00' in external:
        raise ValueError('Invalid original external owner name')
    name = PurePosixPath(external.replace('\\', '/')).name
    if not name or name in ('.', '..'):
        raise ValueError('Missing original external owner identity')
    return name, path_id


def duplicate_groups(shaders):
    groups = defaultdict(list)
    for identity, row in shaders.items():
        groups[row['key']].append((identity, row))
    result = []
    for key, members in groups.items():
        if len(members) < 2:
            continue
        program_hashes = {row['program_set_sha256'] for _, row in members}
        parsed_hashes = {row['parsed_form_sha256'] for _, row in members}
        result.append({'key_digest': digest(key), 'original_objects': len(members),
                       'distinct_serialized_payloads': len({row['payload_sha256'] for _, row in members}),
                       'distinct_parsed_forms': len(parsed_hashes),
                       'distinct_decompressed_program_sets': len(program_hashes),
                       'byte_identical_parsed_forms_and_programs': len(program_hashes) == len(parsed_hashes) == 1,
                       'member_fingerprints': sorted([
                           {'object_identity_digest': digest(identity),
                            'payload_sha256': row['payload_sha256'],
                            'parsed_form_sha256': row['parsed_form_sha256'],
                            'program_set_sha256': row['program_set_sha256']}
                           for identity, row in members], key=lambda x: x['object_identity_digest'])})
    return sorted(result, key=lambda x: x['key_digest'])


def link_materials(materials, shaders, table):
    counts = Counter()
    engine_refs = Counter()
    per_object = Counter()
    known_owners = {identity[0] for identity in shaders}
    for owner, external, pointer in materials:
        counts['original_material_objects'] += 1
        target = resolve_pointer(owner, external, pointer)
        if target is None:
            counts['null_shader_refs'] += 1
            continue
        row = shaders.get(target)
        if row is None:
            counts['shader_refs_outside_authenticated_shader_objects'] += 1
            if target[0] in known_owners:
                counts['shader_refs_to_known_owner_missing_shader_object'] += 1
            elif target[0].lower() in ('unity_builtin_extra', 'unity default resources', 'unity_default_resources'):
                counts['shader_refs_to_engine_resource_owner_not_loaded'] += 1
            elif target[0].lower() in {name.lower() for name in known_owners}:
                # Observe a case mismatch; do not silently change resolver semantics.
                counts['shader_refs_with_owner_case_mismatch'] += 1
            else:
                counts['shader_refs_to_other_owner_not_loaded'] += 1
            continue
        per_object[target] += 1
        choices = table.get(row['key'], [])
        if len(choices) > 1:
            raise ValueError('Ambiguous original material engine shader key')
        if choices:
            engine_refs[choices[0]] += 1
            counts['original_material_refs_to_engine_keys'] += 1
        else:
            counts['original_material_refs_to_custom_shader_objects'] += 1
    return dict(counts), engine_refs, per_object


def probe(source, database, reader, out):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS, ORIGINAL_SHADER_OBJECTS
    from scripts.w1_recover_graphics_programs import decoded_platforms
    table = exact_table(json.loads(database.read_text()), json.loads(reader.read_text()))
    shaders = {}
    materials = []
    owners = {}
    # Load all shader identities before resolving cross-file Material references.
    # Process one owner at a time; only the small summaries/PPtrs remain resident.
    pending = []
    for owner, pin in SHADER_OWNERS.items():
        path = source / 'Raft_Data' / owner
        if path.is_symlink() or fingerprint(path) != pin:
            raise ValueError('Original shader owner changed')
        env = UnityPy.load(str(path))
        for obj in env.objects:
            if obj.type.name not in ('Shader', 'Material'):
                continue
            tree = obj.read_typetree()
            if obj.type.name == 'Shader':
                parsed = tree['m_ParsedForm']
                key = (parsed['m_Name'], tuple(p['m_Name'] for p in parsed['m_PropInfo']['m_Props']))
                identity = (owner, obj.path_id)
                if identity in shaders:
                    raise ValueError('Duplicate original object identity')
                shaders[identity] = {'key': key, 'payload_sha256': hashlib.sha256(obj.get_raw_data()).hexdigest(),
                                     'parsed_form_sha256': digest(parsed)}
                # Decompression is required only for repeated key groups. Keep
                # private compressed trees briefly, then release each unique one.
                pending.append((identity, tree))
            else:
                external = [item.path for item in obj.assets_file.externals]
                materials.append((owner, external, tree['m_Shader']))
        owners[owner] = pin[1]
    if len(shaders) != ORIGINAL_SHADER_OBJECTS:
        raise ValueError('Full165 original Shader objects not covered')
    multiplicity = Counter(row['key'] for row in shaders.values())
    for identity, tree in pending:
        if multiplicity[shaders[identity]['key']] > 1:
            platform_rows = []
            for platform, segments in decoded_platforms(tree):
                platform_rows.append([platform, [hashlib.sha256(segment).hexdigest() for segment in segments]])
            if not platform_rows:
                raise ValueError('Duplicate original shader has no platform program data')
            shaders[identity]['program_set_sha256'] = digest(platform_rows)
    pending.clear()
    counts, engine_refs, object_refs = link_materials(materials, shaders, table)
    duplicates = duplicate_groups(shaders)
    result = {'schema_version': 1, 'original_owner_count': len(owners),
              'original_verified_bytes': sum(p[0] for p in SHADER_OWNERS.values()),
              'original_shader_objects': len(shaders), **counts,
              'repeated_key_groups': duplicates,
              'material_refs_to_duplicate_shader_objects': [
                  {'key_digest': digest(key), 'source_object_reference_counts': sorted(
                      object_refs[identity] for identity, row in shaders.items() if row['key'] == key)}
                  for key in sorted(multiplicity) if multiplicity[key] > 1],
              'original_engine_pointer_histogram': [
                  {'engine_kind': kind, 'file_id': number, 'references': n}
                  for (kind, number), n in sorted(engine_refs.items())],
              'source_graph_complete_within_selected_owners': not (
                  counts.get('null_shader_refs', 0) or counts.get('shader_refs_outside_authenticated_shader_objects', 0)),
              'actual_export_guid_associations_verified': False,
              'original_material_assignments_preserved_in_export': False,
              'export_guid_is_deterministic': False,
              'shader_objects_merged_or_changed': 0,
              'production_gates_changed': False, 'unity_or_device_executed': False}
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_ORIGINAL_SHADER_OBJECT_LINKS ' + json.dumps(result, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--private-database', type=Path, required=True)
    p.add_argument('--reader-summary', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.out.resolve().is_relative_to(a.source.resolve()):
        raise ValueError('Aggregate output must be outside original source')
    probe(a.source, a.private_database, a.reader_summary, a.out)


if __name__ == '__main__':
    main()
