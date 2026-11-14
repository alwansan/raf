#!/usr/bin/env python3
"""SHA-original Particle108: stage FOUR private per-keyword ShaderLab compile candidates.

These are FOUR ISOLATED compile-only variants, NOT a keyword-selectable Unity
runtime shader or a safe replacement for the game's GUID/Material. No private
ShaderLab/HLSL, original names, DXBC, registers or source identifiers leave
the runner scratch. Do not publish this output or upload its directory.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil

from scripts import t3_original_particle108_spirv_translation as original
from scripts.t3_original_particle_shader_state import inspect_parsed
from scripts import t3_particle108_source_propstate as source_state
from scripts import t3_particle108_shaderlab_property_parity as props
from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.run_original_dxbc_translation_probe import version_tokens
from scripts.w1_depth_shaderlab import quoted, tags, render_state, stage_body
from scripts.w1_recover_graphics_programs import translate, decoded_platforms, records
from scripts.w1_stage_zip2_owners import fingerprint

STATUS="T3_ORIGINAL_PARTICLE108_FOUR_PRIVATE_SHADERLAB_STRUCTURAL_VARIANTS"
MODELS=frozenset({(4,0),(4,1),(5,0),(5,1)})
MAX_HLSL=1024*1024
MAX_CANDIDATE=4*1024*1024
FAIL=frozenset({"T3_VARIANT_SOURCE_INVALID","T3_VARIANT_MODEL_UNSUPPORTED",
                "T3_VARIANT_TRANSLATION_MISSING","T3_VARIANT_PRIVATE_IO_UNSAFE",
                "T3_VARIANT_STRUCTURE_INVALID","T3_VARIANT_PROPERTY_MISMATCH",
                "T3_VARIANT_ORIGINAL_IDENTITY_INVALID"})


def source_models(vs:bytes,fs:bytes):
    """Require two genuine graphics stages; don't invent the target shader model."""
    versions=[]
    for data,stage in ((vs,1),(fs,0)):
        if type(data) is not bytes or not 36<=len(data)<=original.MAX_PRIVATE_STAGE_BYTES:
            raise ValueError("T3_VARIANT_SOURCE_INVALID")
        rows=version_tokens(data)
        if type(rows) is not list or len(rows)!=1 or rows[0].get("shader_stage_code")!=stage:
            raise ValueError("T3_VARIANT_MODEL_UNSUPPORTED")
        model=rows[0].get("shader_model")
        if (type(model) is not list or len(model)!=2 or
            any(type(v) is not int for v in model) or tuple(model) not in MODELS):
            raise ValueError("T3_VARIANT_MODEL_UNSUPPORTED")
        versions.append(tuple(model))
    # Different original VS/PS SM versions need explicit Unity compile study.
    if versions[0]!=versions[1]:
        raise ValueError("T3_VARIANT_MODEL_UNSUPPORTED")
    return versions[0]


def assemble(parsed:dict,vertex:str,fragment:str,model:tuple, *, candle16=False):
    """Make one *isolated* ShaderLab candidate without claiming keyword routing."""
    if (type(parsed) is not dict or type(model) is not tuple or model not in MODELS
        or any(type(code) is not str or not 0<len(code.encode("utf-8"))<=MAX_HLSL
               or "\x00" in code or "HLSLPROGRAM" in code or "ENDHLSL" in code
               or "//DummyShaderTextExporter" in code or "// No subprograms found" in code
               or not re.search(r"\bmain\s*\(",code) for code in (vertex,fragment))):
        raise ValueError("T3_VARIANT_SOURCE_INVALID")
    # Source-state authenticates original normal Pass, selective RGB mask,
    # exact authored property schema and no dynamic state guessed.
    if candle16:
        inspect_parsed(parsed)
    else:
        _,shape=source_state.source_fragment(parsed)
    subs=parsed["m_SubShaders"]
    sub=subs[0]
    render_pass=sub["m_Passes"][0]
    properties,property_shape=source_state.serialize_properties(parsed,allow_hidden_and_toggle=candle16)
    if candle16:
        shape=property_shape
    try:
        state=render_state(render_pass["m_State"],allow_selective_color_mask=True)
        shader_name=quoted(parsed["m_Name"])
        sub_tags=tags(sub["m_Tags"])
    except (KeyError,TypeError,ValueError):
        raise ValueError("T3_VARIANT_SOURCE_INVALID") from None
    if "ColorMask RGB" not in state:
        raise ValueError("T3_VARIANT_SOURCE_INVALID")
    # spirv-cross --hlsl --shader-model 50 produced HLSL, so HLSL target 5.0
    # is a compiler *candidate*, not a claim of original SM target fidelity.
    lines=["Shader "+shader_name+" {",properties,"SubShader {",
           "LOD "+str(sub["m_LOD"]),sub_tags,"Pass {",state,
           "HLSLPROGRAM","#pragma target 5.0",
           "#pragma vertex main","#pragma fragment main",
           stage_body(vertex,fragment),"ENDHLSL","}","}"]
    for field,word in (("m_FallbackName","Fallback"),
                       ("m_CustomEditorName","CustomEditor")):
        if parsed.get(field):
            lines.append(word+" "+quoted(parsed[field]))
    lines.append("}")
    candidate="\n".join(lines)+"\n"
    if len(candidate.encode("utf-8"))>MAX_CANDIDATE:
        raise ValueError("T3_VARIANT_SOURCE_INVALID")
    coverage=pass_coverage(candidate)
    if (coverage.get("pass_count")!=1 or
        coverage.get("passes_with_complete_program")!=1 or
        coverage.get("subshader_pass_counts")!=[1] or
        coverage.get("subshader_programmed_pass_counts")!=[1] or
        coverage.get("all_subshaders_programmed") is not True or
        coverage.get("pass_braces_balanced") is not True):
        raise ValueError("T3_VARIANT_STRUCTURE_INVALID")
    parity=props.compare(properties,candidate)
    if (parity.get("original_authored_property_names_types_exact") is not True or
        parity.get("original_authored_property_defaults_semantically_equal") is not True):
        raise ValueError("T3_VARIANT_PROPERTY_MISMATCH")
    return candidate,shape


def evaluate(pairs,parsed,private_dir:Path,*,translator=translate,
             model_reader=source_models):
    """Eight original stages -> 4 scratch-only shader texts, count-only report."""
    if (type(pairs) is not list or len(pairs)!=4 or
        not isinstance(private_dir,Path) or not private_dir.is_dir()
        or private_dir.is_symlink() or any(type(p) is not tuple or len(p)!=2
        for p in pairs)):
        raise ValueError("T3_VARIANT_PRIVATE_IO_UNSAFE")
    totals=Counter()
    shape=None
    for n,(vs,fs) in enumerate(pairs):
        model=model_reader(vs,fs)
        paths={}
        for stage,data in ((1,vs),(0,fs)):
            folder=private_dir/("keyword-%d-stage-%d"%(n,stage))
            folder.mkdir(exist_ok=False)
            result=translator(data,stage,folder)
            # A recovered text file alone is not an accepted graphics stage:
            # require an attested Vulkan 1.1 roundtrip and exact stage identity.
            # bool is a subclass of int in Python, so reject True as vertex=1.
            if (type(result) is not dict or result.get("vulkan11_valid") is not True
                or result.get("hlsl_recovered") is not True
                or result.get("roundtrip_vulkan11_valid") is not True
                or type(result.get("stage")) is not int
                or result["stage"] != stage):
                raise ValueError("T3_VARIANT_TRANSLATION_MISSING")
            hlsl=folder/"private.hlsl"
            if (hlsl.is_symlink() or not hlsl.is_file()
                or not 0<hlsl.stat().st_size<=MAX_HLSL):
                raise ValueError("T3_VARIANT_TRANSLATION_MISSING")
            paths[stage]=hlsl.read_text(encoding="utf-8")
            totals["genuine_original_DXBC_stages_translated"]+=1
            totals["recovered_HLSL_stages"]+=1
            totals["separately_validated_HLSL_roundtrip_stages"]+=(
                result.get("roundtrip_vulkan11_valid") is True)
        candidate,shape=assemble(parsed,paths[1],paths[0],model)
        variant=private_dir/("keyword-%d-private.shader"%n)
        if variant.exists() or variant.is_symlink():
            raise ValueError("T3_VARIANT_PRIVATE_IO_UNSAFE")
        variant.write_text(candidate,encoding="utf-8")
        totals["private_complete_one_pass_ShaderLab_candidates"]+=1
        totals["private_property_default_parity_passes"]+=1
    if (totals["genuine_original_DXBC_stages_translated"]!=8 or
        totals["separately_validated_HLSL_roundtrip_stages"]!=8 or
        totals["private_complete_one_pass_ShaderLab_candidates"]!=4):
        raise ValueError("T3_VARIANT_STRUCTURE_INVALID")
    return {"schema_version":1,"status":STATUS,
            "source_authenticated_keyword_pairs":4,
            "original_authored_property_count":shape["original_authored_property_count"],
            "original_authored_texture_property_count":shape["original_authored_texture_property_count"],
            "counts":dict(sorted(totals.items())),
            "per_variant_ShaderLab_structural_candidates_created":True,
            "four_keywords_selectable_in_one_runtime_shader":False,
            "source_keyword_routing_or_original_descriptors_preserved":False,
            "Unity_ShaderLab_import_or_GPU_compile_proven":False,
            "original_Material_texture_resource_bindings_equivalent":False,
            "original_Android_pixels_or_emitter_verified":False,
            "original_name_program_HLSL_DXBC_SPV_GUID_or_private_values_published":False}


def probe(source:Path,manifest:Path,private_dir:Path):
    if any(shutil.which(bin) is None for bin in original.TOOLS):
        raise ValueError("T3_VARIANT_TRANSLATION_MISSING")
    chosen={}
    census=impact.load_original(source,manifest,private_particle_slot_counts=chosen)
    owner,pid=identity.select(chosen,census)
    path=source/"Raft_Data"/owner
    if (path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]):
        raise ValueError("T3_VARIANT_ORIGINAL_IDENTITY_INVALID")
    import UnityPy
    objs=[o for o in UnityPy.load(str(path)).file.objects.values() if o.path_id==pid]
    if len(objs)!=1 or objs[0].type.name!="Shader":
        raise ValueError("T3_VARIANT_ORIGINAL_IDENTITY_INVALID")
    tree=objs[0].read_typetree()
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(tables)!=1:
        raise ValueError("T3_VARIANT_ORIGINAL_IDENTITY_INVALID")
    parsed=tree["m_ParsedForm"]
    check=identity.inspect(parsed,tables[0])
    if (check.get("status")!=identity.STATUS or
        check.get("matched_vertex_fragment_permutation_pairs")!=4 or
        check.get("original_D3D11_program_table_records")!=16):
        raise ValueError("T3_VARIANT_ORIGINAL_IDENTITY_INVALID")
    _,p=source_state.serialize_properties(parsed)
    if (p["original_authored_property_count"]!=13 or
        p["original_authored_texture_property_count"]!=2):
        raise ValueError("T3_VARIANT_ORIGINAL_IDENTITY_INVALID")
    pairs=original.exact_four_pairs(parsed,tables[0])
    return evaluate(pairs,parsed,private_dir)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for arg in ("source","manifest","private-dir","out"):
        parser.add_argument("--"+arg,required=True,type=Path)
    a=parser.parse_args(argv)
    # Keep generated ShaderLab away from repository and private original files;
    # output only the safe summary. CI provides RUNNER_TEMP scratch as parent.
    if (a.private_dir.exists() or a.private_dir.is_symlink() or
        not a.private_dir.parent.is_dir() or a.private_dir.parent.is_symlink()
        or a.private_dir.resolve().is_relative_to(a.source.resolve()) or
        a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.source.resolve()) or
        a.out.resolve().is_relative_to(a.private_dir.resolve())):
        raise ValueError("T3_VARIANT_PRIVATE_IO_UNSAFE")
    a.private_dir.mkdir()
    try:
        report=probe(a.source,a.manifest,a.private_dir)
    except Exception as exc:
        literal=str(exc) if type(exc) is ValueError else ""
        report={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_code":literal if literal in FAIL else "T3_VARIANT_UNCLASSIFIED_FAILURE",
                "failure_type":type(exc).__name__,
                "Unity_ShaderLab_import_or_GPU_compile_proven":False,
                "original_name_program_HLSL_DXBC_SPV_GUID_or_private_values_published":False}
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("T3_PRIVATE_SHADERLAB_VARIANTS_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
