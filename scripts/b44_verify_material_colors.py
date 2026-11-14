"""B44: fail-closed original->same-export Material m_Colors fidelity check.

Complements shader-pointer lineage: identical shader links can still render
white if an exporter silently drops material color/tint SavedProperties.
Source and full per-object comparisons remain private. Published output is
aggregate integer counts only; this is not a shader/pixel/device test.
"""
from __future__ import annotations

import argparse
from functools import partial
import json
import math
from pathlib import Path, PurePosixPath
import re

UNITY_YAML_SPECIAL_FLOATS = {
    "NaN": math.nan,
    "Infinity": math.inf,
    "-Infinity": -math.inf,
}
CHANNELS = frozenset(('r', 'g', 'b', 'a'))
ENGINE = frozenset(('0000000000000000e000000000000000', '0000000000000000f000000000000000'))
MATERIAL_HEADER = re.compile(r'^--- !u!21 &(-?\d+)(?: stripped)?\s*$', re.M)
ALL_HEADER = re.compile(r'^--- !u!\d+ &-?\d+(?: stripped)?\s*$', re.M)
GUID = re.compile(r'^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*$', re.M)
FONT_COLLECTION = 'AssetRipper.Export.UnityProjects.Miscellaneous.FontAssetExportCollection'


def _number(value, *, allow_nonfinite=False):
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError('Invalid color component type')
    number = float(value)
    if not allow_nonfinite and not math.isfinite(number):
        raise ValueError('Nonfinite original or exported Material color')
    return number


def normalize_colors(entries, *, exported=False, allow_nonfinite=False):
    """Canonical per-property RGBA map from original pairs or Unity YAML maps.

    Rejects duplicates and unsupported shapes, never logs original names/values.
    """
    # Unity/AssetRipper emits exported YAML m_Colors either as a list of
    # singleton maps or as a property-name mapping, including an empty {}.
    # Original compiled source typetrees must remain arrays, not inferred maps.
    # The exported YAML loader below already rejects duplicate keys.
    if exported and isinstance(entries, dict):
        entries = list(entries.items())
    if not isinstance(entries, list):
        raise ValueError('Material m_Colors must be an array')
    result = {}
    for entry in entries:
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            key, rgba = entry
        elif isinstance(entry, dict) and set(entry) == {'m_First', 'm_Second'}:
            key, rgba = entry['m_First'], entry['m_Second']
        elif exported and isinstance(entry, dict) and len(entry) == 1:
            key, rgba = next(iter(entry.items()))
        else:
            raise ValueError('Unsupported Material color entry shape')
        if not isinstance(key, str) or not key or key in result:
            raise ValueError('Malformed or duplicated Material color slot')
        if not isinstance(rgba, dict) or set(rgba) != CHANNELS:
            raise ValueError('Malformed RGBA Material color')
        values = (rgba[channel] for channel in ("r", "g", "b", "a"))
        if exported and allow_nonfinite:
            values = (UNITY_YAML_SPECIAL_FLOATS.get(value, value) if isinstance(value, str) else value
                      for value in values)
        result[key] = tuple(_number(value, allow_nonfinite=allow_nonfinite) for value in values)
    return result


def original_colors(source_root: Path, *, selected_owners=None):
    """Only accept SHA-pinned original owner payloads, never archive labels.

    The original B44 full-provider mode remains unchanged by default. A
    bounded selection is allowed only for exact independently SHA-verified
    owners, not arbitrary caller-provided filenames or archive labels.
    """
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.b05_verify_material_texenv_bindings import B05_SMALL_OWNER_PINS

    if selected_owners is None:
        pins = SHADER_OWNERS
    else:
        names = set(selected_owners)
        if not names or not names.issubset(B05_SMALL_OWNER_PINS):
            raise ValueError('Unpinned selected Material color source')
        pins = {name:B05_SMALL_OWNER_PINS[name] for name in names}
    # Defer optional serialized-asset dependencies until after the caller's
    # requested source selection has passed the original pin allowlist.
    import UnityPy
    from scripts.w1_stage_zip2_owners import fingerprint
    result = {}
    for name, expected in pins.items():
        path = source_root / 'Raft_Data' / name
        if path.is_symlink() or not path.is_file() or fingerprint(path) != expected:
            raise ValueError('Original Material owner SHA/size mismatch')
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name != 'Material':
                continue
            props = obj.read_typetree().get('m_SavedProperties')
            if not isinstance(props, dict) or 'm_Colors' not in props:
                raise ValueError('Missing original Material color container')
            key = (name, obj.path_id)
            if key in result:
                raise ValueError('Duplicate original Material identity')
            result[key] = normalize_colors(props['m_Colors'])
    if not result:
        raise ValueError('No SHA-verified original Materials')
    return result


def exported_colors(project: Path, *, allow_nonfinite=False):
    """Parse only complete Material YAML documents using bounded safe YAML.

    Both embedded .asset Materials and loose .mat are included. All symlinked
    paths fail closed, and asset metadata, not filenames, identifies documents.
    """
    import yaml

    class StrictSafeLoader(yaml.SafeLoader):
        """Reject duplicate YAML keys instead of silently overwriting colors."""
        def construct_mapping(self, node, deep=False):
            result = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                try:
                    duplicate = key in result
                except TypeError:
                    raise ValueError('Unhashable YAML Material mapping key') from None
                if duplicate:
                    raise ValueError('Duplicate YAML Material mapping key')
                result[key] = self.construct_object(value_node, deep=deep)
            return result

    assets = project / 'Assets'
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError('Missing or redirected Unity Assets')
    entries = sorted(assets.rglob('*'))
    if any(p.is_symlink() for p in entries):
        raise ValueError('Symlink in exported Unity Assets')
    found = {}
    for path in entries:
        if not path.is_file() or path.suffix not in ('.mat', '.asset', '.unity', '.prefab'):
            continue
        if path.stat().st_size > 256 * 1024 * 1024:
            raise ValueError('Oversize Material YAML candidate')
        with path.open('rb') as fp:
            if not fp.read(16).lstrip(b'\xef\xbb\xbf').startswith(b'%YAML'):
                continue
        content = path.read_text(encoding='utf-8-sig')
        headers = list(ALL_HEADER.finditer(content))
        if not any(MATERIAL_HEADER.fullmatch(h.group(0)) for h in headers):
            continue
        meta = Path(str(path) + '.meta')
        if not meta.is_file() or meta.is_symlink():
            raise ValueError('Missing/redirected Material container metadata')
        guids = GUID.findall(meta.read_text(encoding='utf-8-sig'))
        if len(guids) != 1 or guids[0].lower() == '0' * 32:
            raise ValueError('Invalid Material container GUID')
        for index, header in enumerate(headers):
            match = MATERIAL_HEADER.fullmatch(header.group(0))
            if match is None:
                continue
            try:
                data = yaml.load(content[header.end():headers[index + 1].start() if index + 1 < len(headers) else len(content)], Loader=StrictSafeLoader)
            except yaml.YAMLError:
                # Parser traceback may embed proprietary Material names/values.
                raise ValueError('Malformed exported Material YAML') from None
            if not isinstance(data, dict) or not isinstance(data.get('Material'), dict):
                raise ValueError('Invalid Unity Material YAML object')
            props = data['Material'].get('m_SavedProperties')
            if not isinstance(props, dict) or 'm_Colors' not in props:
                raise ValueError('Missing exported Material color container')
            key = (int(match.group(1)), guids[0].lower())
            if key in found:
                raise ValueError('Duplicate exported Material identity')
            found[key] = normalize_colors(props['m_Colors'], exported=True,
                                          allow_nonfinite=allow_nonfinite)
    if not found:
        raise ValueError('No actual YAML Material documents')
    return found


def _source_id(value):
    if not isinstance(value, dict) or set(value) != {'owner', 'path_id'}:
        raise ValueError('Invalid original source identity')
    if not isinstance(value['owner'], str) or type(value['path_id']) is not int:
        raise ValueError('Invalid original source identity value')
    return PurePosixPath(value['owner'].replace('\\', '/')).name, value['path_id']


def _export_pointer(value):
    if not isinstance(value, dict) or set(value) != {'file_id', 'guid', 'type'}:
        raise ValueError('Invalid export pointer structure')
    if type(value['file_id']) is not int or type(value['type']) is not int or not isinstance(value['guid'], str):
        raise ValueError('Invalid export pointer types')
    if value['type'] not in (2, 3) or not value['file_id'] or not re.fullmatch('[0-9a-fA-F]{32}', value['guid']):
        raise ValueError('Invalid Material document export pointer')
    return value['file_id'], value['guid'].lower()


def compare(trace: dict, original: dict, actual: dict) -> dict:
    """Count exact mismatches, including absent/extra slots (without values)."""
    if trace.get('schema_version') != 1 or not isinstance(trace.get('export_instance'), str) or not re.fullmatch(r'[0-9a-f]{32}', trace['export_instance']):
        raise ValueError('Missing authenticated same-instance export trace')
    if not isinstance(trace.get('objects'), list):
        raise ValueError('Invalid export trace object list')
    covered_sources = set()
    expected = {}
    skipped_engine = 0
    skipped_font = 0
    for row in trace['objects']:
        if row.get('class_id') != 21:
            continue
        src = _source_id(row['source'])
        if src not in original or src in covered_sources:
            raise ValueError('Unverified/duplicate source Material identity')
        covered_sources.add(src)
        ref = row['export']
        if not isinstance(ref, dict) or set(ref) != {'file_id', 'guid', 'type'}:
            raise ValueError('Invalid traced export pointer')
        if (isinstance(ref['guid'], str) and ref['guid'].lower() in ENGINE and
                ref['type'] == 0 and row['exportable'] is False):
            skipped_engine += 1
            continue
        if row.get('collection_type') == FONT_COLLECTION:
            skipped_font += 1
            continue
        pointer = _export_pointer(ref)
        if pointer in expected:
            raise ValueError('Multiple original Materials share one exported document')
        expected[pointer] = original[src]
    if covered_sources != set(original):
        raise ValueError('Original source Material missing in same-instance export trace')
    if not expected or set(expected) != set(actual):
        raise ValueError('Actual exported Material identities differ from the trace')

    compared_slots = absent_slots = unexpected_slots = changed_rgba = 0
    material_mismatches = 0
    material_nonidentity = 0
    nonfinite_channels = nonfinite_drift = 0
    for key, before in expected.items():
        after = actual[key]
        if not isinstance(after, dict):
            raise ValueError('Invalid exported Material color map')
        missing = before.keys() - after.keys()
        extra = after.keys() - before.keys()
        absent_slots += len(missing)
        unexpected_slots += len(extra)
        mismatch = bool(missing or extra)
        for slot in before.keys() & after.keys():
            compared_slots += 1
            rgba_original, rgba_exported = before[slot], after[slot]
            if len(rgba_original) != 4 or len(rgba_exported) != 4:
                raise ValueError('Invalid RGBA width')
            changed = False
            for original_channel, exported_channel in zip(rgba_original, rgba_exported):
                if math.isfinite(original_channel) and math.isfinite(exported_channel):
                    changed |= not math.isclose(original_channel, exported_channel,
                                                rel_tol=2e-6, abs_tol=2e-5)
                else:
                    nonfinite_channels += 1
                    equivalent = (original_channel == exported_channel or
                                  (math.isnan(original_channel) and math.isnan(exported_channel)))
                    nonfinite_drift += not equivalent
                    changed |= not equivalent
            if changed:
                changed_rgba += 1
                mismatch = True
        if any(any(abs(c - 1.0) > 1e-6 for c in rgba) for rgba in before.values()):
            material_nonidentity += 1
        if mismatch:
            material_mismatches += 1
    report = {
        'schema_version': 1,
        'source_materials_verified': len(original),
        'yaml_materials_compared': len(expected),
        'engine_material_redirects_excluded': skipped_engine,
        'font_importer_materials_excluded': skipped_font,
        'materials_with_original_nonidentity_colors': material_nonidentity,
        'color_slots_compared': compared_slots,
        'missing_color_slots': absent_slots,
        'unexpected_color_slots': unexpected_slots,
        'changed_color_values': changed_rgba,
        'nonfinite_channels_compared': nonfinite_channels,
        'nonfinite_channel_drift': nonfinite_drift,
        'mismatched_materials': material_mismatches,
        'original_material_color_values_preserved': material_mismatches == 0,
        'shader_program_or_device_fidelity_verified': False,
    }
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--source', type=Path, required=True)
    ap.add_argument('--private-export-trace', type=Path, required=True)
    ap.add_argument('--project', type=Path, required=True)
    ap.add_argument('--zip2-manifest', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.resolve().is_relative_to(args.project.resolve()):
        raise ValueError('Report destination is inside original project')
    if args.zip2_manifest is None:
        source = original_colors(args.source)
    else:
        from scripts.gt_full_original_export_texenvs import original
        source = original(args.source, args.zip2_manifest, property_name='m_Colors',
                          normalize=partial(normalize_colors, allow_nonfinite=True))
    actual = exported_colors(args.project, allow_nonfinite=args.zip2_manifest is not None)
    report = compare(json.loads(args.private_export_trace.read_text(encoding='utf-8')), source, actual)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print('RAFT_B44_MATERIAL_COLOR_LINEAGE ' + json.dumps(report, sort_keys=True))
    if not report['original_material_color_values_preserved']:
        raise SystemExit('Original Material color properties do not match same-instance export')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
