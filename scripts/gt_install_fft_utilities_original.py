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
    enumerate_all(tree['m_ParsedForm'],tables[0],variants=stage_variants,
        permutation=variant_key,linker=linked_program,topology=(7,7,0,12))
    return key


def require(receipt, expected):
    if type(receipt) is not dict or any(type(receipt.get(key)) is not type(value)
            or receipt[key]!=value for key,value in expected.items()):
        raise ValueError('fft_install_source_Unity_or_decoded_bundle_proof_missing')


def verify_receipts(candidate, source, unity, bundle):
    digest=sha256(candidate).hexdigest()
    require(source,dict(status=SOURCE_STATUS,candidate_shader_sha256=digest,
        original_SHA_owned_serialized_files=2,original_passes=7,original_keyword_pairs=7,
        original_orphan_stages=0,original_distinct_D3D11_programs=12,
        original_stages_roundtrip_validated=12,named_ShaderLab_entrypoints_compiled=14))
    require(unity,dict(unityVersion='2021.3.45f2',candidateSha256=digest,
        passCount=7,registeredKeywordVariants=1,errors=0,androidVulkanOnly=True,
        privateBundleCompiled=True,gamePlayerBuilt=False,devicePixelsProven=False))
    require(bundle,dict(candidate_sha256=digest,compiled_program_table_verified=True,
        vertex_and_fragment_entrypoints_verified=True,vulkan_platform_only=True,
        engine_keywords_verified=False,vertex_routes_by_pass=[1]*7,fragment_routes_by_pass=[1]*7))
    if any(type(value) is not int for field in ('vertex_routes_by_pass','fragment_routes_by_pass')
           for value in bundle[field]):
        raise ValueError('fft_install_decoded_route_counts_must_be_integers')
    text=candidate.decode('utf-8')
    coverage=pass_coverage(text)
    if (exported_shader_identity(text)!=TARGET or 'DummyShaderTextExporter' in text
            or coverage['subshader_pass_counts']!=[7]
            or coverage['passes_with_complete_program']!=7
            or coverage['pass_braces_balanced'] is not True
            or re.search(r'(?m)^\s*#pragma\s+(?:multi_compile|shader_feature)',text)):
        raise ValueError('fft_install_authentic_seven_pass_empty_keyword_candidate_required')


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


def install(project, trace, source_key, candidate, source, unity, bundle, backup):
    project,backup=map(check_safe_ancestors,(project,backup))
    if backup.exists() or backup.is_relative_to(project) or not backup.parent.is_dir():
        raise ValueError('fft_install_fresh_external_private_backup_required')
    verify_receipts(candidate,source,unity,bundle)
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
        original_static_Material_usage_count_inferred=False,
        original_source_names_GUIDs_PathIDs_or_program_bytes_published=False,
        game_Player_or_APK_created=False,Android_device_pixels_proven=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('original','project','trace','candidate','source-receipt',
                 'unity-receipt','bundle-receipt','backup','out'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    project=check_safe_ancestors(args.project)
    external=(args.original,args.trace,args.candidate,args.source_receipt,
              args.unity_receipt,args.bundle_receipt,args.backup,args.out)
    if any(check_safe_ancestors(path).is_relative_to(project) for path in external):
        raise ValueError('fft_install_private_input_or_output_inside_export')
    if (args.backup.resolve().is_relative_to(args.original.resolve())
            or args.out.exists() or args.out.resolve().is_relative_to(args.original.resolve())
            or args.out.resolve().is_relative_to(args.backup.resolve())):
        raise ValueError('fft_install_unsafe_public_receipt')
    key=source_identity(args.original)
    result=install(project,json.loads(read_bounded(args.trace,40000000)),key,
        read_bounded(args.candidate,MAX_SHADER),
        json.loads(read_bounded(args.source_receipt,65536)),
        json.loads(read_bounded(args.unity_receipt,65536)),
        json.loads(read_bounded(args.bundle_receipt,65536)),args.backup)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('GT_FFT_UTILITIES_SAME_EXPORT_INSTALL_SAFE '+json.dumps(result,sort_keys=True))

if __name__=='__main__':main()
