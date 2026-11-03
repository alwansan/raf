"""Recover actual graphics programs privately from authenticated Unity Shader blobs.

No reconstructed program or original name is logged/uploaded. All segments are
decoded, unlike first-segment-only text exporters. This is a recovery experiment,
not a Unity ShaderLab installer or proof of image/numerical equivalence.
"""
import argparse
from collections import Counter
import gc
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources
from scripts.probe_original_compute_containers import scan_blob
from scripts.run_original_dxbc_translation_probe import version_tokens

OWNERS = {name: EXPECTED[name] for name in ('resources.assets', 'sharedassets0.assets')}
MAX_SEGMENT = 128 * 1024 * 1024
MAX_RECORDS = 100000


def records(segments):
    """Unity >=2019.3 entry: offset, length, segment index (little endian).

    Offsets are relative to the referenced decompressed segment, not always
    segment zero. Keep every entry's exact byte range; never concatenate segments.
    """
    if not segments or any(not isinstance(s, bytes) or len(s) > MAX_SEGMENT for s in segments):
        raise ValueError('Missing or over-budget shader segments')
    table = segments[0]
    if len(table) < 4:
        raise ValueError('Truncated shader program table')
    count = struct.unpack_from('<I', table)[0]
    table_end = 4 + 12 * count
    if count > MAX_RECORDS or table_end > len(table):
        raise ValueError('Unbounded shader program table')
    result = []
    for index in range(count):
        offset, length, segment = struct.unpack_from('<III', table, 4 + index * 12)
        if segment >= len(segments) or length == 0 or offset + length > len(segments[segment]):
            raise ValueError('Invalid shader program segment/range')
        if segment == 0 and offset < table_end:
            raise ValueError('Shader program overlaps entry table')
        result.append((segment, segments[segment][offset:offset + length]))
    return result


def decoded_platforms(tree):
    from UnityPy.helpers import CompressionHelper
    blob = bytes(tree['compressedBlob'])
    platforms = tree['platforms']
    offsets, compressed, decoded = (tree[k] for k in ('offsets', 'compressedLengths', 'decompressedLengths'))
    if not (len(platforms) == len(offsets) == len(compressed) == len(decoded)):
        raise ValueError('Shader platform arrays disagree')
    for platform, starts, sizes, lengths in zip(platforms, offsets, compressed, decoded):
        if not isinstance(starts, list):
            starts, sizes, lengths = [starts], [sizes], [lengths]
        if not (len(starts) == len(sizes) == len(lengths)) or len(starts) > 128:
            raise ValueError('Shader segment arrays disagree')
        segments = []
        for start, size, length in zip(starts, sizes, lengths):
            if min(start, size, length) < 0 or not 0 < length <= MAX_SEGMENT or start + size > len(blob):
                raise ValueError('Shader compression range exceeds bounds')
            segment = CompressionHelper.decompress_lz4(blob[start:start + size], length)
            if len(segment) != length:
                raise ValueError('Shader segment decompressed size mismatch')
            segments.append(segment)
        yield int(platform), segments


def command(argv):
    try:
        return subprocess.run(argv, capture_output=True, timeout=30, check=False).returncode == 0
    except subprocess.TimeoutExpired:
        return False


def translate(dxbc, stage, directory):
    src, spv, hlsl, roundtrip = (directory / n for n in ('source.dxbc', 'original.spv', 'private.hlsl', 'roundtrip.spv'))
    for path in (src, spv, hlsl, roundtrip):
        path.unlink(missing_ok=True)
    src.write_bytes(dxbc)
    result = {'dxbc_sha256': hashlib.sha256(dxbc).hexdigest(), 'bytes': len(dxbc),
              'stage': stage, 'vulkan11_valid': False, 'hlsl_recovered': False,
              'roundtrip_vulkan11_valid': False, 'numeric_or_visual_equivalence': False}
    if not command(['vkd3d-compiler', '-x', 'dxbc-tpf', '-b', 'spirv-binary', '-o', str(spv), str(src)]):
        return result
    result['vulkan11_valid'] = command(['spirv-val', '--target-env', 'vulkan1.1', str(spv)])
    if not result['vulkan11_valid']:
        return result
    if not command(['spirv-cross', str(spv), '--hlsl', '--shader-model', '50', '--output', str(hlsl)]):
        return result
    if not hlsl.is_file() or not 0 < hlsl.stat().st_size <= 1024 * 1024:
        return result
    result['hlsl_recovered'] = True
    result['hlsl_sha256'] = hashlib.sha256(hlsl.read_bytes()).hexdigest()
    suffix = {0: 'frag', 1: 'vert'}[stage]
    if command(['glslangValidator', '-V', '-D', '-S', suffix, '-e', 'main', '-o', str(roundtrip), str(hlsl)]):
        result['roundtrip_vulkan11_valid'] = command(['spirv-val', '--target-env', 'vulkan1.1', str(roundtrip)])
    return result


def recover(root, output):
    verify_sources(root, expected=OWNERS)
    import UnityPy
    counts = Counter()
    stages = Counter()
    samples = []
    sampled_categories = Counter()
    with tempfile.TemporaryDirectory(prefix='w1-private-graphics-') as folder:
        private = Path(folder)
        for owner in OWNERS:
            env = UnityPy.load(str(root / owner))
            for obj in env.file.objects.values():
                if obj.type.name != 'Shader':
                    continue
                counts['shader_objects'] += 1
                raw = obj.get_raw_data()
                object_sha = hashlib.sha256(raw).hexdigest()
                tree = obj.read_typetree()
                parsed = tree.get('m_ParsedForm', {})
                name = parsed.get('m_Name', tree.get('m_Name', ''))
                category = ('water' if any(t in name.lower() for t in ('water', 'foam')) else
                            'effect' if any(t in name.lower() for t in ('particle', 'fire', 'smoke')) else 'other')
                passes = sum(len(s.get('m_Passes', [])) for s in parsed.get('m_SubShaders', []))
                counts['original_passes'] += passes
                counts['category_' + category] += 1
                seen_stages = set()
                for platform, segments in decoded_platforms(tree):
                    counts['platform_tables'] += 1
                    counts['compressed_segments'] += len(segments)
                    entries = records(segments)
                    counts['program_entries'] += len(entries)
                    for segment, entry in entries:
                        counts['entries_in_nonzero_segment'] += int(segment != 0)
                        containers = scan_blob(entry)['valid_dxbc_containers']
                        for row in containers:
                            start, size = row['offset_in_original_object'], row['bytes']
                            dxbc = entry[start:start + size]
                            versions = version_tokens(dxbc)
                            if len(versions) != 1:
                                raise ValueError('Ambiguous original graphics DXBC stage')
                            stage = versions[0]['shader_stage_code']
                            stages[str(stage)] += 1
                            # A bounded first vertex+fragment per chosen object. More
                            # variants/passes still require explicit recovery/linkage.
                            if stage not in (0, 1) or stage in seen_stages or sampled_categories[category] >= 4:
                                continue
                            seen_stages.add(stage)
                            result = translate(dxbc, stage, private)
                            result.update(owner=owner, path_id=int(obj.path_id), object_sha256=object_sha,
                                          category=category, original_pass_count=passes,
                                          platform_code=platform, segment_index=segment)
                            samples.append(result)
                            sampled_categories[category] += 1
                del tree, raw
            del env
            gc.collect()
    report = {'source_sha': __import__('os').environ.get('GITHUB_SHA'),
              'authenticated_owners': OWNERS, 'counts': dict(counts),
              'original_dxbc_stage_counts': dict(stages), 'samples': samples,
              'private_programs_published': False, 'unity_shaderlab_installed': False,
              'material_guid_or_texture_changed': False, 'gpu_or_phone_executed': False,
              'all_variants_or_pass_bindings_recovered': False}
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    print('RAFT_W1_GRAPHICS_RECOVERY ' + json.dumps(report, sort_keys=True))
    if not samples or not any(s['hlsl_recovered'] for s in samples):
        raise ValueError('No original graphics HLSL program recovered')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    recover(args.source, args.out)
