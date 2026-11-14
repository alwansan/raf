"""Compose one private, source-derived FFT compute candidate with explicit routes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from scripts.probe_directx_shader_bridge import inspect
from scripts.probe_original_fft_software_vulkan import private_command
from scripts.t1_stage_original_fft_compute_candidates import (
    stage_original_candidates, validate_import_candidate_manifest,
)
from scripts.probe_original_fft_resource_bindings import resource_rows
from scripts.probe_authentic_fft_dxbc_translation import OWNER, PATH_ID
from scripts.verify_export_lineage import identity, pointer

# Original managed SetTexture names, checked against the serialized ABI.
RESOURCE_NAMES = {
    't0': ('source_image_name_sha256', '_SourceTex'),
    't1': ('butterfly_image_name_sha256', '_ButterflyTex'),
    'u0': ('target_image_name_sha256', '_TargetTex'),
}
DECLARATIONS = {
    't0': 'Texture2D<float4> t0 : register(t0);',
    't1': 'Texture2D<float4> t1 : register(t1);',
    'u0': 'RWTexture2D<float4> u0 : register(u2);',
}


def entry(index):
    return f'RaftFftSlot{index:02d}'


def exported_fft(assets, trace):
    if trace.get("schema_version") != 1 or not re.fullmatch(
        r"[a-f0-9]{32}", trace.get("export_instance", "")
    ):
        raise ValueError("invalid_original_fft_export_trace")
    matches = [row for row in trace["objects"] if row["class_id"] == 72
               and identity(row["source"]) == (OWNER, PATH_ID)]
    if len(matches) != 1 or not matches[0]["exportable"]:
        raise ValueError("original_fft_export_trace_missing")
    file_id, guid, kind = pointer(matches[0]["export"])
    if file_id != 7200000 or kind != "2":
        raise ValueError("original_fft_export_type")
    pattern = re.compile(r"(?m)^guid: " + re.escape(guid) + r"$")
    matches = [path for path in assets.rglob("*.asset.meta")
               if pattern.search(path.read_text(encoding="utf-8-sig"))]
    if len(matches) != 1:
        raise ValueError("original_fft_export_meta_missing")
    asset = matches[0].with_suffix("")
    if asset.is_symlink() or matches[0].is_symlink():
        raise ValueError("original_fft_export_unsafe_asset")
    with asset.open(encoding="utf-8-sig") as stream:
        if not any(line.rstrip() == "--- !u!72 &7200000" for line in stream):
            raise ValueError("original_fft_export_class")
    return asset, guid


def install_fft(project, trace, shader, backup):
    project = project.resolve()
    backup = backup.resolve()
    if backup.is_relative_to(project) or not backup.is_dir():
        raise ValueError("original_fft_backup_must_be_outside_project")
    old, guid = exported_fft(project / "Assets", trace)
    old_meta = old.with_suffix(".asset.meta")
    destination = old.with_suffix(".compute")
    destination_meta = destination.with_suffix(".compute.meta")
    saved = backup / old.relative_to(project)
    saved_meta = saved.with_suffix(".asset.meta")
    paths = (destination, destination_meta, saved, saved_meta)
    if any(path.exists() or path.is_symlink() for path in paths):
        raise ValueError("original_fft_install_path_conflict")
    source = shader.read_text(encoding="utf-8")
    expected = [(entry(i), str(i)) for i in range(20)]
    if re.findall(r"(?m)^#pragma kernel (\w+) RAFT_FFT_SLOT=(\d+)$", source) != expected:
        raise ValueError("original_fft_install_kernel_order")
    saved.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(old, saved)
    shutil.copy2(old_meta, saved_meta)
    created = []
    try:
        with destination.open("x", encoding="utf-8") as output:
            created.append(destination)
            output.write(source)
        with destination_meta.open("x", encoding="utf-8") as output:
            created.append(destination_meta)
            output.write(
                f"fileFormatVersion: 2\nguid: {guid}\nComputeShaderImporter:\n"
                "  externalObjects: {}\n  currentAPIMask: 4\n  userData:\n"
                "  assetBundleName:\n  assetBundleVariant:\n"
            )
        old.unlink()
        old_meta.unlink()
    except BaseException:
        if not old.exists():
            shutil.copy2(saved, old)
        if not old_meta.exists():
            shutil.copy2(saved_meta, old_meta)
        for path in created:
            path.unlink(missing_ok=True)
        raise
    return {"original_fft_guid_preserved": True, "ordered_routes_installed": len(expected)}


def route(candidate, row):
    index = row['compiled_slot']
    for token, (role, original_name) in RESOURCE_NAMES.items():
        declaration = DECLARATIONS[token]
        if (hashlib.sha256(original_name.encode()).hexdigest() != row[role]
                or candidate.count(declaration) != 1):
            raise ValueError('Original FFT resource binding contract mismatch')
        candidate = re.sub(
            rf'\b{token}\b(?!\s*\)\s*;)', original_name, candidate
        )
        # The numeric register token is untouched. vkd3d assigned u2 to
        # the translated original u0 to keep the Vulkan descriptor distinct.
        expected = declaration.replace(f' {token} :', f' {original_name} :')
        if expected not in candidate:
            raise ValueError('FFT HLSL resource identifier replacement failed')
    header = '#pragma kernel main\n'
    if not candidate.startswith(header) or candidate.count('void main(') != 1:
        raise ValueError('Unexpected translated FFT entrypoint')
    body = candidate[len(header):].replace('void main(', f'void {entry(index)}(')
    return f'#if RAFT_FFT_SLOT == {index}\n{body}#endif\n'


def stage(original_data, destination):
    import UnityPy

    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir():
        raise ValueError('Choose a new destination inside private scratch')
    with tempfile.TemporaryDirectory(prefix='.fft-indexed-', dir=destination.parent) as folder:
        root = Path(folder)
        source = root / 'unified'
        stage_original_candidates(original_data, source)
        assets = source / 'Assets/T1OriginalDerived'
        manifest = json.loads((assets / 'PrivateCandidates.json').read_text())
        validate_import_candidate_manifest(manifest, source)
        env = UnityPy.load(str(original_data / OWNER))
        records = resource_rows(env.file.objects[PATH_ID].read_typetree())
        header = ''.join(f'#pragma kernel {entry(i)} RAFT_FFT_SLOT={i}\n' for i in range(len(records)))
        bodies = []
        for candidate, record in zip(manifest['rows'], records, strict=True):
            if candidate['compiled_slot'] != record['compiled_slot']:
                raise ValueError('FFT source candidate and resource ABI order differ')
            bodies.append(route((source / candidate['compute_asset']).read_text(), record))
        shader = source / 'Assets/DX11 FFT.compute'
        shader.write_text(header + '\n' + ''.join(bodies), encoding='utf-8')
        module = root / 'slot.spv'
        reference = root / 'reference.spv'
        for candidate, record in zip(manifest['rows'], records, strict=True):
            index = record['compiled_slot']
            private_command(['glslangValidator', '-V', '-D', f'-DRAFT_FFT_SLOT={index}',
                             '-S', 'comp', '-e', entry(index), '-o', str(module), str(shader)])
            private_command(['spirv-val', '--target-env', 'vulkan1.1', str(module)])
            if inspect(module.read_bytes())['declared_local_workgroup_sizes'] != [record['workgroup_xyz']]:
                raise ValueError('FFT routed candidate changed workgroup')
            private_command(['glslangValidator', '-V', '-D', '-S', 'comp',
                             '--source-entrypoint', 'main', '-e', entry(index),
                             '-o', str(reference), str(source / candidate['compute_asset'])])
            for binary in (module, reference):
                private_command(['spirv-opt', '--strip-debug', str(binary), '-o', str(binary)])
            if module.read_bytes() != reference.read_bytes():
                raise ValueError('FFT binding or route altered executable SPIR-V')
        for path in assets.iterdir():
            path.unlink()
        assets.rmdir()
        if destination.exists() or destination.is_symlink():
            raise ValueError('Private FFT destination appeared during staging')
        source.rename(destination)
    return {'source_candidate_routes': len(records), 'all_routed_stages_valid_vulkan11': True,
            'executable_spirv_matches_independent_candidates': len(records),
            'original_resource_names_rebound': len(RESOURCE_NAMES),
            'actual_unity_registration_verified': False, 'android_gpu_verified': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original-data', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--install-project', type=Path)
    parser.add_argument('--private-export-trace', type=Path)
    parser.add_argument('--backup', type=Path)
    args = parser.parse_args()
    install_args = (args.install_project, args.private_export_trace, args.backup)
    if any(install_args) and not all(install_args):
        parser.error("FFT installation requires an export project, its trace, and an external backup")
    report = stage(args.original_data, args.project)
    if args.install_project:
        trace = json.loads(args.private_export_trace.read_text(encoding="utf-8"))
        report.update(install_fft(args.install_project, trace,
                                  args.project / "Assets/DX11 FFT.compute", args.backup))
    print('GT_INDEXED_FFT_CANDIDATE ' + json.dumps(report, sort_keys=True))
