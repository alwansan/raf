#!/usr/bin/env python3
"""GT private, *provisional* source-indexed one-ShderLab Spectrum 7pass router.

The original SHA-verified Spectrum serialized program tables use m_KeywordIndices
[] and [4] for each of 7 Passes and both VS/FS. Authenticate the actual
index-4 authored keyword spelling against the original ZIP2 and original
variant_key_sha256 in each staged private B09 packet. Assemble exactly one
7Pass ShaderLab with 2 conditional VS/FS programs per Pass.

ShaderLab pragma global/local directive semantics are UNPROVEN from the
serialized keyword flags; this is a PRIVATE compile-only candidate, NOT
original runtime selection or material/GUID/device proof.
Never publish original keyword names or shader text in CI logs/artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

from scripts.b09_spectrum_topology_contract import TARGET, PASSES, KEYWORD_NAMES, OWNER
from scripts.b09_stage_original_spectrum import _selected_original, _variant_key
from scripts.b09_translate_original_spectrum import validate_packet
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_spectrum_private_stage_buffer_isolation import isolate
from scripts.verify_targeted_lfs_compute_sources import verify_sources, EXPECTED
from scripts.w1_recover_depth_passes import stage_variants

PROGRAM = re.compile(
    r"(?ms)^([ \t]*HLSLPROGRAM[ \t]*\n)(.*?)(^[ \t]*ENDHLSL[ \t]*$)"
)
IDENT = re.compile(r"[_A-Za-z][_A-Za-z0-9]{0,127}\Z")
PRAGMAS = (
    "#pragma target 5.0",
    "#pragma vertex main",
    "#pragma fragment main",
)
MAX_BYTES=16*1024*1024


def selector(parsed, packet, *, variant_reader=stage_variants):
    """Return private keyword spelling and source-backed per-Pass on/off mapping."""
    if (type(parsed) is not dict or parsed.get("m_Name") != TARGET
            or type(parsed.get("m_KeywordNames")) is not list
            or len(parsed["m_KeywordNames"]) != KEYWORD_NAMES):
        raise ValueError("original_spectrum_keyword_author_table_unproven")
    keyword=parsed["m_KeywordNames"][4]
    if (type(keyword) is not str or not IDENT.fullmatch(keyword)
            or keyword in ("SHADER_STAGE_VERTEX", "SHADER_STAGE_FRAGMENT")
            or keyword.startswith(("GL_", "UNITY_"))):
        raise ValueError("original_spectrum_keyword_name_unsupported")
    subs=parsed.get("m_SubShaders")
    original_passes=subs[0].get("m_Passes") if type(subs) is list and len(subs)==1 and type(subs[0]) is dict else None
    packet_rows=packet.get("stages") if type(packet) is dict else None
    if (type(original_passes) is not list or len(original_passes)!=PASSES
            or type(packet_rows) is not list or len(packet_rows)!=PASSES):
        raise ValueError("original_spectrum_keyword_pass_topology_invalid")
    original=[]
    for pi in range(PASSES):
        pass_row=original_passes[pi]
        packet_row=packet_rows[pi]
        if (type(pass_row) is not dict or type(packet_row) is not dict
                or packet_row.get("pass_index")!=pi
                or type(packet_row.get("variant_pairs")) is not list
                or len(packet_row["variant_pairs"])!=2):
            raise ValueError("original_spectrum_keyword_packet_order_invalid")
        stages=[]
        for name in ("progVertex","progFragment"):
            stage_prog=pass_row.get(name)
            if type(stage_prog) is not dict:
                raise ValueError("original_spectrum_keyword_stage_missing")
            variants=variant_reader(stage_prog)
            if type(variants) is not list or len(variants)!=2:
                raise ValueError("original_spectrum_keyword_stage_variants_wrong")
            seen={}
            for bucket,ix,meta in variants:
                indices=meta.get("m_KeywordIndices") if type(meta) is dict else None
                if indices not in ([],[4]):
                    raise ValueError("original_spectrum_keyword_other_bits_unmodelled")
                on=bool(indices)
                digest=hashlib.sha256(_variant_key(meta).encode()).hexdigest()
                if on in seen:
                    raise ValueError("original_spectrum_keyword_duplicate_permutation")
                seen[on]=digest
            if set(seen)!={False,True}:
                raise ValueError("original_spectrum_keyword_both_branches_missing")
            stages.append(seen)
        if stages[0]!=stages[1]:
            raise ValueError("original_spectrum_keyword_stage_pairs_mismatch")
        packet_map={}
        for j,pair in enumerate(packet_row["variant_pairs"]):
            if (type(pair) is not dict or pair.get("pair_index")!=j
                    or type(pair.get("variant_key_sha256")) is not str):
                raise ValueError("original_spectrum_keyword_packet_pair_invalid")
            digest=pair["variant_key_sha256"]
            branches=[on for on in (False,True) if stages[0][on]==digest]
            if len(branches)!=1 or branches[0] in packet_map:
                raise ValueError("original_spectrum_keyword_hash_and_slot_drift")
            packet_map[branches[0]]=j
        if set(packet_map)!={False,True}:
            raise ValueError("original_spectrum_keyword_packet_incomplete")
        original.append(packet_map)
    return keyword, original


def _sections(shader):
    if (type(shader) is not str or not 0<len(shader.encode("utf-8"))<=MAX_BYTES
            or "\x00" in shader or "//DummyShaderTextExporter" in shader):
        raise ValueError("private_Spectrum_shaderlab_not_real")
    matches=list(PROGRAM.finditer(shader))
    coverage=pass_coverage(shader)
    if (len(matches)!=PASSES or coverage.get("subshader_pass_counts")!=[PASSES]
            or coverage.get("passes_with_complete_program")!=PASSES
            or coverage.get("pass_braces_balanced") is not True):
        raise ValueError("private_Spectrum_exact_seven_program_blocks_required")
    headers=[]
    bodies=[]
    trailers=[]
    pos=0
    for match in matches:
        headers.append(shader[pos:match.start()])
        body=match.group(2)
        nonempty=[x.strip() for x in body.splitlines() if x.strip()]
        if (len(nonempty)<5 or tuple(nonempty[:3])!=PRAGMAS
                or any(x.startswith("#pragma") for x in nonempty[3:])):
            raise ValueError("private_Spectrum_program_pragma_mismatch")
        first=body.find("#pragma fragment main")
        first=body.find("\n",first)
        if first<0:
            raise ValueError("private_Spectrum_program_body_empty")
        bodies.append(body[first+1:].strip()+"\n")
        trailers.append(match.group(3))
        pos=match.end()
    headers.append(shader[pos:])
    return headers,bodies,trailers


def compose(parsed, packet, first, second, *, isolator=isolate,
            variant_reader=stage_variants):
    keyword, maps=selector(parsed,packet,variant_reader=variant_reader)
    isolated=[]
    for candidate in (first,second):
        changed, proof=isolator(candidate)
        if (type(proof) is not dict
                or proof.get("private_original_HLSL_register_annotations_identical") is not True
                or proof.get("other_private_ShaderLab_text_bytewise_reversible") is not True):
            raise ValueError("private_Spectrum_stage_alias_guard_unproven")
        isolated.append(changed)
    header0,bodies0,ends0=_sections(isolated[0])
    header1,bodies1,ends1=_sections(isolated[1])
    if header0!=header1 or ends0!=ends1:
        raise ValueError("private_Spectrum_source_envelopes_not_equal")
    parts=[]
    for pi in range(PASSES):
        on=maps[pi][True]
        off=maps[pi][False]
        source_by_pair=[bodies0[pi],bodies1[pi]]
        body=(
            "\n".join(PRAGMAS)+"\n"+
            "#pragma multi_compile __ "+keyword+"\n"+
            "#if defined("+keyword+")\n"+
            source_by_pair[on]+
            "#else\n"+
            source_by_pair[off]+
            "#endif\n"
        )
        parts.extend([header0[pi],"HLSLPROGRAM\n",body,ends0[pi]])
    parts.append(header0[-1])
    shader="".join(parts)
    cover=pass_coverage(shader)
    if (not 0<len(shader.encode("utf-8"))<=MAX_BYTES
            or cover.get("pass_count")!=PASSES
            or cover.get("subshader_pass_counts")!=[PASSES]
            or cover.get("passes_with_complete_program")!=PASSES
            or cover.get("all_subshaders_programmed") is not True
            or shader.count("#pragma multi_compile __ "+keyword)!=PASSES):
        raise ValueError("private_Spectrum_one_seven_pass_keyword_router_incomplete")
    return shader,{
        "schema":1,
        "status":"PRIVATE_SPECTRUM_ORIGINAL_KEYWORD_INDEX4_SEVEN_PASS_ROUTED_SHADERLAB_CANDIDATE",
        "source_original_pass_count":PASSES,
        "source_original_keyword_index":4,
        "source_original_keyword_variants_per_pass":2,
        "source_program_variant_stage_references":28,
        "source_original_keyword_index_name_authenticated":True,
        "source_original_VS_FS_pair_hashes_authenticated":True,
        "private_seven_program_keyword_pragmas":7,
        "original_shader_keyword_flags_pragma_scope_proven":False,
        "original_material_keyword_runtime_selection_parity_proven":False,
        "original_Material_sampler_CB0_RT_GUID_binding_proven":False,
        "original_game_ShaderLab_modified":False,
        "Unity_Android_2021_import_or_GPU_proven":False,
        "original_Adreno_pixel_parity_proven":False,
        "original_keyword_names_or_ShaderLab_published":False,
    }


def write_private(source:Path, packet_dir:Path, packet_report:Path,
                  private_dir:Path, out:Path, *, original_reader=_selected_original):
    source,packet_dir,packet_report,private_dir,out=(
        Path(p).absolute() for p in
        (source,packet_dir,packet_report,private_dir,out))
    if (not source.is_dir() or not packet_dir.is_dir()
            or not packet_report.is_file() or not private_dir.is_dir()
            or out.exists() or out.is_symlink()
            or out.parent.is_relative_to(private_dir)
            or any(p.is_symlink() for p in
                   (source,packet_dir,packet_report,private_dir,out.parent))):
        raise ValueError("private_Spectrum_keyword_router_paths_invalid")
    verify_sources(source,expected={OWNER:EXPECTED[OWNER]})
    _,_,tree,attest=original_reader(source)
    if (attest.get("authenticated_original_passes")!=PASSES
            or attest.get("authenticated_variant_stage_programs")!=28):
        raise ValueError("Spectrum_original_SHA_shader_identity_missing")
    packet=json.loads(packet_report.read_text(encoding="utf-8"))
    validate_packet(packet_dir,packet)
    original=private_dir/"original-spectrum-7pass-variant-0.shader"
    alt=private_dir/"original-spectrum-7pass-variant-1.shader"
    target=private_dir/"spectrum-keyword-index4-router-private.shader"
    if (target.exists() or target.is_symlink()
            or not original.is_file() or original.is_symlink()
            or not alt.is_file() or alt.is_symlink()):
        raise ValueError("private_Spectrum_router_source_unavailable_or_target_exists")
    shader,report=compose(tree["m_ParsedForm"],packet,
                          original.read_text(encoding="utf-8"),
                          alt.read_text(encoding="utf-8"))
    try:
        with target.open("x", encoding="utf-8") as stream:
            stream.write(shader)
        out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    except BaseException:
        target.unlink(missing_ok=True)
        out.unlink(missing_ok=True)
        raise
    print("GT_SPECTRUM_SOURCE_KEYWORD_ROUTER_PRIVATE_SAFE "+json.dumps(report,sort_keys=True))
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("source","packet-dir","packet-report","private-dir","out"):
        p.add_argument("--"+name,type=Path,required=True)
    x=p.parse_args()
    try:
        result=write_private(x.source,x.packet_dir,x.packet_report,x.private_dir,x.out)
    except BaseException as exc:
        result={"status":"INCONCLUSIVE", "safe_error_type":type(exc).__name__,
                "original_game_ShaderLab_modified":False,
                "Unity_Android_2021_import_or_GPU_proven":False}
        print("GT_SPECTRUM_SOURCE_KEYWORD_ROUTER_PRIVATE_SAFE "+json.dumps(result,sort_keys=True))
        return 2
    return 0


if __name__=="__main__":
    raise SystemExit(main())
