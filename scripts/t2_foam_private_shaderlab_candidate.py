"""T2: authentic Foam authored Properties and private two-pass ShaderLab only.

No Unity import, runtime CB0 aliases, material upload or Android pixels claimed.
Source-derived ShaderLab never printed or copied outside private CI scratch.
"""
import argparse
import json
import math
from pathlib import Path
import re

from scripts.b20_private_foam_packet import _physical, ORIGINAL_STATE_BYTES
from scripts.b20_private_foam_packet import ORIGINAL_STAGE_SHA, ORIGINAL_OBJECT_SHA256
from scripts.b24_original_foam_stage_translation import OWNER, OBJECT_ID, validate_stage
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_recover_depth_passes import linked_program
from scripts.run_original_dxbc_translation_probe import version_tokens
from scripts.w1_stage_zip2_owners import PINS, fingerprint
import hashlib
from scripts.b24_original_foam_stage_translation import TARGET
from scripts.b45_blur_properties import PROPERTY_FIELDS, TEXTURE_DIMENSIONS, DEFAULT_TEXTURE_NAMES
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.t2_foam_original_pair_compile import _exact_manifest
from scripts.t2_foam_member_abi import original_source_tree
from scripts.w1_depth_shaderlab import number, quoted, stage_body, tags

IDENT = re.compile(r"[_A-Za-z][_A-Za-z0-9]{0,127}\Z")
MAX_SHADERLAB_BYTES = 4 * 1024 * 1024



ORIGINAL_STAGE_KEYS = ((0,1),(0,0),(1,1),(1,0))
SUPPORTED_ORIGINAL_SHADER_MODELS = {(4,0),(4,1),(5,0),(5,1)}


def source_derived_pass_targets(source):
    """Pin four original DXBC stage SHA and read actual shader profile tokens.

    No proprietary DXBC stage, token or compiled program name leaves scratch.
    A mixed-model original pass is not silently widened to an invented target.
    """
    import UnityPy
    owner=Path(source).absolute()/OWNER
    if not _physical(owner) or not owner.is_file() or fingerprint(owner)!=PINS[OWNER]:
        raise ValueError("DXBC_original_owner_SHA_mismatch")
    env=UnityPy.load(str(owner))
    matches=[o for o in env.file.objects.values()
             if o.type.name=="Shader" and int(o.path_id)==OBJECT_ID]
    if len(matches)!=1 or hashlib.sha256(matches[0].get_raw_data()).hexdigest()!=ORIGINAL_OBJECT_SHA256:
        raise ValueError("DXBC_original_Foam_object_mismatch")
    tree=matches[0].read_typetree()
    parsed=tree.get("m_ParsedForm")
    if not isinstance(parsed,dict) or parsed.get("m_Name")!=TARGET:
        raise ValueError("DXBC_original_Shader_name_mismatch")
    platforms=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(platforms)!=1:
        raise ValueError("DXBC_original_platform_table_ambiguous")
    version_by_stage={}
    ps=parsed["m_SubShaders"][0]["m_Passes"]
    for pi,sc in ORIGINAL_STAGE_KEYS:
        program=ps[pi]["progVertex" if sc==1 else "progFragment"]
        metadata,_=validate_stage(program,sc,{"original_pass":pi})
        dxbc,_=linked_program(metadata,platforms[0],sc)
        if hashlib.sha256(dxbc).hexdigest()!=ORIGINAL_STAGE_SHA[(pi,sc)]:
            raise ValueError("original_stage_DXBC_SHA_mismatch")
        versions=version_tokens(dxbc)
        if len(versions)!=1 or versions[0].get("shader_stage_code")!=sc:
            raise ValueError("original_stage_model_mismatch")
        major_minor=versions[0].get("shader_model")
        if (not isinstance(major_minor,list) or len(major_minor)!=2
                or any(type(v) is not int for v in major_minor)
                or tuple(major_minor) not in SUPPORTED_ORIGINAL_SHADER_MODELS):
            raise ValueError("unsupported_original_stage_shader_model")
        version_by_stage[(pi,sc)]=tuple(major_minor)
    return select_exact_pass_models(version_by_stage)


def select_exact_pass_models(stage_models):
    if not isinstance(stage_models,dict) or set(stage_models)!=set(ORIGINAL_STAGE_KEYS):
        raise ValueError("original_stage_model_table_incomplete")
    result=[]
    for pi in range(2):
        v,p=stage_models[(pi,1)],stage_models[(pi,0)]
        if (type(v) is not tuple or type(p) is not tuple
                or v not in SUPPORTED_ORIGINAL_SHADER_MODELS
                or p not in SUPPORTED_ORIGINAL_SHADER_MODELS or v!=p):
            raise ValueError("original_pass_compiled_stage_models_differ_or_unsupported")
        result.append("%d.%d" % v)
    return tuple(result)


def properties_shape(parsed):
    """Return safe schema category only, never original strings or numbers."""
    props = parsed.get("m_PropInfo", {}).get("m_Props") if isinstance(parsed,dict) else None
    if not isinstance(props,list) or len(props)!=2 or not all(isinstance(p,dict) for p in props):
        raise ValueError("authored_property_shape_missing")
    codes=[p.get("m_Type") for p in props]
    if any(type(t) is not int or not 0<=t<=5 for t in codes):
        raise ValueError("authored_property_type_invalid")
    return {
        "authored_properties":2,
        "authored_texture_properties":codes.count(4),
        "nontexture_property_type_code":next((t for t in codes if t!=4),None),
        "any_property_flags_nonzero":any(p.get("m_Flags")!=0 for p in props),
        "any_property_attributes":any(p.get("m_Attributes")!=[] for p in props),
        "private_property_names_or_values_published":False,
    }


def serialize_properties(parsed):
    shape=properties_shape(parsed)
    if shape["authored_texture_properties"]!=1:
        raise ValueError("not_exact_one_original_texture")
    used=set()
    lines=["Properties {"]
    for prop in parsed["m_PropInfo"]["m_Props"]:
        if set(prop)!=PROPERTY_FIELDS:
            raise ValueError("unknown_original_property_fields")
        name,description=prop["m_Name"],prop["m_Description"]
        if (not isinstance(name,str) or not IDENT.fullmatch(name) or name in used
                or not isinstance(description,str) or len(description)>1024
                or any(ch in description for ch in "\r\n\x00")):
            raise ValueError("malformed_or_duplicate_property")
        used.add(name)
        if type(prop["m_Flags"]) is not int or prop["m_Flags"]!=0 or prop["m_Attributes"]!=[]:
            raise ValueError("unsupported_original_property_flags_or_attrs")
        values=[prop.get("m_DefValue[%d]"%i) for i in range(4)]
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
            raise ValueError("nonfinite_original_default")
        tex=prop["m_DefTexture"]
        if (not isinstance(tex,dict) or set(tex)!={"m_DefaultName","m_TexDim"}
                or type(tex["m_TexDim"]) is not int
                or not isinstance(tex["m_DefaultName"],str)):
            raise ValueError("unhandled_original_texture_metadata")
        typ=prop["m_Type"]
        start=name+" ("+quoted(description)+", "
        if typ==4:
            if (any(v!=0 for v in values)
                    or tex["m_TexDim"] not in TEXTURE_DIMENSIONS
                    or tex["m_DefaultName"] not in DEFAULT_TEXTURE_NAMES):
                raise ValueError("unhandled_original_texture_default")
            line=(start+TEXTURE_DIMENSIONS[tex["m_TexDim"]]+") = "
                  +quoted(tex["m_DefaultName"])+" {}")
        else:
            if tex["m_DefaultName"]!="" or tex["m_TexDim"] not in (0,1):
                raise ValueError("unexpected_nontexture_default")
            if typ in (0,1):
                kind="Color" if typ==0 else "Vector"
                line=start+kind+") = ("+",".join(number(v) for v in values)+")"
            elif typ==2:
                if any(v!=0 for v in values[1:]):
                    raise ValueError("float_extra_numeric_default")
                line=start+"Float) = "+number(values[0])
            elif typ==3:
                if values[3]!=0 or not values[1]<=values[0]<=values[2]:
                    raise ValueError("range_default_outside_bounds")
                line=(start+"Range("+number(values[1])+","+number(values[2])
                      +")) = "+number(values[0]))
            else:
                raise ValueError("unsupported_original_numeric_type")
        lines.append(line)
    lines.append("}")
    return "\n".join(lines),shape


def assemble(parsed,stages,states,pass_targets):
    if not isinstance(parsed,dict) or parsed.get("m_Name")!=TARGET:
        raise ValueError("wrong_original_foam_identity")
    if (not isinstance(stages,dict)
            or set(stages)!={(0,1),(0,0),(1,1),(1,0)}
            or not isinstance(states,list) or len(states)!=2
            or any(not isinstance(x,str) or not x.strip() for x in [*stages.values(),*states])):
        raise ValueError("four_original_stages_two_states_required")
    if (not isinstance(pass_targets,tuple) or len(pass_targets)!=2
            or any((type(x) is not str or x not in
                    {"4.0","4.1","5.0","5.1"}) for x in pass_targets)):
        raise ValueError("missing_original_DXBC_shader_models")
    properties,shape=serialize_properties(parsed)
    subs=parsed.get("m_SubShaders")
    if (not isinstance(subs,list) or len(subs)!=1 or not isinstance(subs[0],dict)
            or not isinstance(subs[0].get("m_Passes"),list)
            or len(subs[0]["m_Passes"])!=2
            or any(p.get("m_Type")!=0 for p in subs[0]["m_Passes"])):
        raise ValueError("unsupported_original_pass_topology")
    sub=subs[0]
    lod=sub.get("m_LOD")
    if type(lod) is not int or not 0<=lod<=10000:
        raise ValueError("invalid_original_lod")
    lines=["Shader "+quoted(TARGET)+" {",properties,"SubShader {",
           "LOD "+str(lod),tags(sub["m_Tags"])]
    for pi in range(2):
        lines.extend(["Pass {",states[pi],"HLSLPROGRAM",
                      "#pragma target "+pass_targets[pi], "#pragma vertex main",
                      "#pragma fragment main",
                      stage_body(stages[(pi,1)],stages[(pi,0)]),
                      "ENDHLSL","}"])
    lines.append("}")
    for field,directive in (("m_FallbackName","Fallback"),("m_CustomEditorName","CustomEditor")):
        if parsed.get(field):
            lines.append(directive+" "+quoted(parsed[field]))
    lines.append("}")
    candidate="\n".join(lines)+"\n"
    if len(candidate.encode("utf-8"))>MAX_SHADERLAB_BYTES:
        raise ValueError("private_shaderlab_size_budget")
    coverage=pass_coverage(candidate)
    if (coverage["subshader_pass_counts"]!=[2]
            or coverage["passes_with_complete_program"]!=2
            or not coverage["all_subshaders_programmed"]):
        raise ValueError("private_candidate_invalid_pass_contract")
    return candidate,shape


def authenticate_and_stage(source,packet,manifest,dest):
    source,packet,manifest,dest=[Path(x).absolute() for x in (source,packet,manifest,dest)]
    if (not source.is_dir() or not _physical(source)
            or not _physical(packet) or not _physical(manifest)
            or not dest.parent.is_dir() or not _physical(dest) or dest.exists()
            or dest.is_relative_to(source) or dest.is_relative_to(packet)
            or dest.is_relative_to(Path.cwd())):
        raise ValueError("original_or_private_path_invalid")
    stages=_exact_manifest(packet,manifest)
    parsed=original_source_tree(source) # exact pinned owner+shader raw SHA
    states=[]
    for pi in range(2):
        f=packet/("foam-pass-%02d-state.txt"%pi)
        if not _physical(f) or not f.is_file() or f.stat().st_size!=ORIGINAL_STATE_BYTES:
            raise ValueError("original_pass_state_missing")
        states.append(f.read_text(encoding="utf-8"))
    pass_targets=source_derived_pass_targets(source)
    candidate,shape=assemble(parsed,stages,states,pass_targets)
    dest.write_text(candidate,encoding="utf-8")
    return {
        "status":"original_private_foam_two_pass_shaderlab_structural_candidate",
        **shape,
        "original_passes":2,"original_program_stages":4,
        "private_candidate_bytes":len(candidate.encode("utf-8")),
        "original_DXBC_stage_model_SHA_verified":True,
        "shaderlab_target_derived_per_pass_not_guessed":True,
        "original_stage_models_verified":4,
        "authentic_pass_states":2,
        "complete_structural_passes":2,
        "shaderlab_unity_import_verified":False,
        "original_cb0_name_or_data_upload_verified":False,
        "original_material_sampler_upload_verified":False,
        "original_numeric_or_device_pixels_verified":False,
        "private_shaderlab_published":False,
    }


def main():
    ap=argparse.ArgumentParser()
    for name in ("source","packet","manifest","private_dest","out"):
        ap.add_argument("--"+name.replace("_","-"),required=True,type=Path)
    a=ap.parse_args()
    out=a.out.absolute()
    try:
        if (not out.parent.is_dir() or not _physical(out) or out.exists()
                or out.is_relative_to(a.source.absolute())
                or out.is_relative_to(a.packet.absolute())):
            raise ValueError("unsafe_aggregate_report")
        report=authenticate_and_stage(a.source,a.packet,a.manifest,a.private_dest)
        code=0
    except BaseException as exc:
        report={"status":"blocked_private_foam_shaderlab",
                "failure_type":type(exc).__name__,
                "shaderlab_unity_import_verified":False,
                "private_shaderlab_published":False}
        # Safe bounded schema only; never original identifiers or literals.
        try:
            report.update(properties_shape(original_source_tree(a.source.absolute())))
        except BaseException:
            pass
        code=2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(report,sort_keys=True)+"\n",encoding="utf-8")
    print("T2_FOAM_PRIVATE_SHADERLAB_SAFE "+json.dumps(report,sort_keys=True))
    return code


if __name__=="__main__":
    raise SystemExit(main())
