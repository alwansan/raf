"""Install authentic seven-pass FFT Utilities at its same-export original GUID.

Original SHA-owned Shader48 identity, source recovery, Unity compilation and
independently decoded bundle receipts are separate requirements. Only the one
trace-resolved dummy shader changes. No static Material usage count is inferred.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

from scripts.b45_install_original_blur import _atomic_replace_bytes, check_safe_ancestors
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_fft_utilities_restore import TARGET, STATUS as SOURCE_STATUS
from scripts.gt_install_original_particle108 import read_bounded, traced_shader, MAX_SHADER
from scripts.gt_original_921_all_variants import enumerate_all
from scripts.gt_original_921_keyword_routes import keyword_routes
from scripts.gt_fft_utilities_restore import validate_routes
from scripts.gt_fft_receipt_contract import require_same_decoded_receipt
from scripts.gt_next23b_unity_receipt import strict_json, read_snapshot, MAX_BUNDLE_BYTES, MAX_RECEIPT_BYTES
from scripts.gt_verify_921_shader_bundle import inspect_fft_original_bytes
from scripts.restore_builtin_shaders import exported_shader_identity
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_stage_zip2_owners import PINS, fingerprint

STATUS='GT_FFT_UTILITIES_AUTHENTIC_SAME_EXPORT_GUID_INSTALLED_NO_APK'


def source_identity(original):
    """Return private exact owner/PathID only after both independent owner SHAs."""
    import UnityPy
    original=check_safe_ancestors(original)
    owners=('resources.assets','sharedassets0.assets')
    for owner in owners:
        path=check_safe_ancestors(original/owner)
        if fingerprint(path)!=PINS['Raft_Data/'+owner]:
            raise ValueError('fft_install_original_owner_SHA_mismatch')
    matches=[]
    for owner in owners:
        for obj in UnityPy.load(str(original/owner)).objects:
            if obj.type.name!='Shader':continue
            tree=obj.read_typetree()
            if tree.get('m_ParsedForm',{}).get('m_Name')==TARGET:
                matches.append(((owner,obj.path_id),tree))
    if len(matches)!=1:
        raise ValueError('fft_install_original_source_identity_ambiguous')
    key,tree=matches[0]
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(tables)!=1:
        raise ValueError('fft_install_original_D3D11_table_ambiguous')
    parsed = tree["m_ParsedForm"]
    pairs, orphans, passes, _ = enumerate_all(parsed, tables[0], variants=stage_variants,
        permutation=variant_key, linker=linked_program, topology=(7,7,0,12))
    routes, _ = keyword_routes(parsed, pairs, orphans, passes)
    validate_routes(routes)
    if (len(parsed["m_SubShaders"]) != 1
            or len(parsed["m_SubShaders"][0]["m_Passes"]) != 7
            or any(type(p.get("m_Type")) is not int or p["m_Type"] != 0
                   for p in parsed["m_SubShaders"][0]["m_Passes"])):
        raise ValueError("fft_install_original_normal_passes_required")
    return key


def verify_receipts(candidate, source_raw, unity_raw, bundle_receipt_raw, bundle_bytes, decoder):
    # Re-run the independent decoder on the exact private bundle at install.
    # Never accept an old JSON-only receipt or fabricate a validation result.
    source, unity, claimed = map(strict_json, (source_raw, unity_raw, bundle_receipt_raw))
    actual = inspect_fft_original_bytes(candidate, source_raw, unity_raw, bundle_bytes, decoder)
    require_same_decoded_receipt(actual, claimed)
    return source, unity, claimed


def snapshot(project):
    """Private complete project file commitments, including non-Assets files."""
    paths=list(project.rglob('*'))
    if len(paths)>250000 or any(path.is_symlink() for path in paths):
        raise ValueError('fft_install_unsafe_or_oversized_export_tree')
    result={}
    for path in paths:
        if path.is_file():result[str(path.relative_to(project))]=fingerprint(path)
        elif not path.is_dir():raise ValueError('fft_install_nonregular_export_entry')
    return result


def install(project, trace, source_key, candidate, source_raw, unity_raw, bundle_receipt_raw, backup, *, bundle_bytes, smolv_decoder):
    project,backup=map(check_safe_ancestors,(project,backup))
    if backup.exists() or backup.is_relative_to(project) or not backup.parent.is_dir():
        raise ValueError('fft_install_fresh_external_private_backup_required')
    source, unity, bundle = verify_receipts(candidate, source_raw, unity_raw,
        bundle_receipt_raw, bundle_bytes, smolv_decoder)
    target,meta=traced_shader(project/'Assets',trace,source_key)
    previous=read_bounded(target,MAX_SHADER)
    metadata=read_bounded(meta,65536)
    if exported_shader_identity(previous.decode('utf-8-sig'))!=TARGET:
        raise ValueError('fft_install_traced_export_lookup_name_mismatch')
    # Bundle receipts ordinarily contain no export GUID. If a caller attaches
    # a binding, it must agree with the independently trace-resolved .meta.
    guid_rows=re.findall(rb'(?m)^guid: *([0-9a-fA-F]{32}) *\r?$',metadata)
    if len(guid_rows)!=1:raise ValueError('fft_install_ambiguous_original_meta_GUID')
    for receipt in (source,unity,bundle):
        for field in ('export_guid','original_export_guid','guid'):
            if field in receipt and receipt[field]!=guid_rows[0].decode().lower():
                raise ValueError('fft_install_receipt_export_GUID_mismatch')
    if previous!=candidate and b'DummyShaderTextExporter' not in previous:
        raise ValueError('fft_install_traced_export_is_not_dummy')
    before=snapshot(project)
    backup.mkdir(mode=0o700)
    (backup/'original.shader').write_bytes(previous)
    (backup/'original.shader.meta').write_bytes(metadata)
    (backup/'original-private-project-commitments.json').write_text(json.dumps(before,sort_keys=True))
    if ((backup/'original.shader').read_bytes()!=previous
            or (backup/'original.shader.meta').read_bytes()!=metadata
            or target.read_bytes()!=previous or meta.read_bytes()!=metadata):
        raise ValueError('fft_install_backup_or_preinstall_source_drift')
    try:
        _atomic_replace_bytes(target,candidate,'.gt-fft-utilities-')
        after=snapshot(project)
        expected=dict(before)
        expected[str(target.relative_to(project))]=(len(candidate),sha256(candidate).hexdigest())
        if after!=expected or meta.read_bytes()!=metadata:
            raise ValueError('fft_install_unrelated_export_or_GUID_drift')
    except BaseException:
        _atomic_replace_bytes(target,previous,'.gt-fft-utilities-rollback-')
        raise
    return dict(status=STATUS,original_export_guid_preserved=True,
        original_meta_bytes_preserved=True,unrelated_project_files_byte_identical=True,
        original_source_identity_trace_matched=True,installed_passes=7,
        decoded_Vulkan_vertex_fragment_routes=[1]*7,
        actual_bundle_revalidated_at_install=True,
        bundle_sha256=bundle['bundle_sha256'], unity_receipt_sha256=bundle['unity_receipt_sha256'],
        original_static_Material_usage_count_inferred=False,
        original_source_names_GUIDs_PathIDs_or_program_bytes_published=False,
        game_Player_or_APK_created=False,Android_device_pixels_proven=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original','project','trace','candidate','source-receipt',
                 'unity-receipt','bundle-receipt','bundle','smolv-decoder','backup','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    project=check_safe_ancestors(args.project)
    external=(args.original,args.trace,args.candidate,args.source_receipt,
              args.unity_receipt,args.bundle_receipt,args.bundle,args.smolv_decoder,args.backup,args.out)
    if any(check_safe_ancestors(path).is_relative_to(project) for path in external):
        raise ValueError('fft_install_private_input_or_output_inside_export')
    if (args.backup.resolve().is_relative_to(args.original.resolve())
            or args.out.exists() or args.out.resolve().is_relative_to(args.original.resolve())
            or args.out.resolve().is_relative_to(args.backup.resolve())):
        raise ValueError('fft_install_unsafe_public_receipt')
    key=source_identity(args.original)
    result=install(project,json.loads(read_bounded(args.trace,40000000)),key,
        read_bounded(args.candidate,MAX_SHADER),
        read_snapshot(args.source_receipt, MAX_RECEIPT_BYTES),
        read_snapshot(args.unity_receipt, MAX_RECEIPT_BYTES),
        read_snapshot(args.bundle_receipt, MAX_RECEIPT_BYTES), args.backup,
        bundle_bytes=read_snapshot(args.bundle, MAX_BUNDLE_BYTES), smolv_decoder=args.smolv_decoder)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('GT_FFT_UTILITIES_SAME_EXPORT_INSTALL_SAFE '+json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
