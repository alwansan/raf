#!/usr/bin/env python3
"""T3: reconstruct original Particle108 Shader48 private Property/Pass state fragment.

This deliberately DOES NOT emit a runnable ShaderLab program. Four authentic
VS/FS keyword variants and their semantic contract are a separate task.
Proprietary ShaderLab, names, property values and IDs stay only in ephemeral CI.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import re

from scripts.b45_blur_properties import PROPERTY_FIELDS, TEXTURE_DIMENSIONS, DEFAULT_TEXTURE_NAMES
from scripts.w1_depth_shaderlab import quoted, number, tags, render_state
from scripts.t3_original_particle_shader_state import inspect_parsed

STATUS = "T3_SHA_ORIGINAL_PARTICLE108_PRIVATE_PROPERTY_PASS_FRAGMENT"
IDENT = re.compile(r"[_A-Za-z][_A-Za-z0-9]{0,127}\Z")
MAX_PROPS = 128
MAX_BYTES = 2*1024*1024
CATEGORIES = frozenset((
    "PROPERTY_TABLE_SCHEMA", "PROPERTY_COUNT", "PROPERTY_FIELD_SCHEMA",
    "PROPERTY_NAME", "PROPERTY_DUPLICATE", "PROPERTY_DESCRIPTION",
    "PROPERTY_FLAGS_OR_ATTRIBUTES", "PROPERTY_DEFAULT_NUMERIC",
    "PROPERTY_TEXTURE_SCHEMA", "PROPERTY_TEXTURE_DEFAULT",
    "PROPERTY_NON_TEXTURE_DEFAULT", "PROPERTY_RANGE",
    "PROPERTY_TYPE_UNSUPPORTED", "SUBSHADER_TOPOLOGY", "SOURCE_STATE",
    "PRIVATE_SHADERLAB_SIZE",
))

class PrivateContractError(ValueError):
    def __init__(self, category):
        if category not in CATEGORIES:
            raise ValueError("unknown_private_particle_contract_category")
        self.category = category
        super().__init__("private_source_particle_" + category)

def require(test, category):
    if not test:
        raise PrivateContractError(category)

def serialize_properties(parsed, *, allow_hidden_and_toggle=False):
    """Return only private text + public-safe type counts; never log source values."""
    info = parsed.get("m_PropInfo") if type(parsed) is dict else None
    require(type(info) is dict and type(info.get("m_Props")) is list,
            "PROPERTY_TABLE_SCHEMA")
    props = info["m_Props"]
    require(len(props)<=MAX_PROPS, "PROPERTY_COUNT")
    names = set()
    family = Counter()
    lines = ["Properties {"]
    for prop in props:
        require(type(prop) is dict and set(prop)==PROPERTY_FIELDS,
                "PROPERTY_FIELD_SCHEMA")
        name, description = prop["m_Name"], prop["m_Description"]
        require(type(name) is str and IDENT.fullmatch(name) is not None,
                "PROPERTY_NAME")
        require(name not in names, "PROPERTY_DUPLICATE")
        names.add(name)
        require(type(description) is str and len(description)<=1024
                and not any(c in description for c in "\r\n\0"),
                "PROPERTY_DESCRIPTION")
        flags = prop["m_Flags"]
        attributes = prop["m_Attributes"]
        require(type(flags) is int and type(attributes) is list and
                ((flags == 0 and not attributes) or
                 (allow_hidden_and_toggle and flags in (0, 1) and attributes in ([], ["Toggle"]))),
                "PROPERTY_FLAGS_OR_ATTRIBUTES")
        typ=prop["m_Type"]
        require(type(typ) is int and typ in (0,1,2,3,4),
                "PROPERTY_TYPE_UNSUPPORTED")
        values=[prop["m_DefValue[%d]"%i] for i in range(4)]
        require(all(type(v) in (int,float) and math.isfinite(v)
                    for v in values), "PROPERTY_DEFAULT_NUMERIC")
        tex=prop["m_DefTexture"]
        require(type(tex) is dict and set(tex)=={"m_DefaultName","m_TexDim"}
                and type(tex["m_TexDim"]) is int
                and type(tex["m_DefaultName"]) is str,
                "PROPERTY_TEXTURE_SCHEMA")
        label=name+" ("+quoted(description)+", "
        if typ==4:
            require(all(x==0 for x in values), "PROPERTY_DEFAULT_NUMERIC")
            require(tex["m_TexDim"] in TEXTURE_DIMENSIONS and
                    tex["m_DefaultName"] in DEFAULT_TEXTURE_NAMES,
                    "PROPERTY_TEXTURE_DEFAULT")
            line=(label+TEXTURE_DIMENSIONS[tex["m_TexDim"]]+") = "
                  +quoted(tex["m_DefaultName"])+" {}")
            family["textures"]+=1
        else:
            require(tex["m_DefaultName"]=="" and tex["m_TexDim"] in (0,1),
                    "PROPERTY_NON_TEXTURE_DEFAULT")
            if typ in (0,1):
                category="Color" if typ==0 else "Vector"
                line=(label+category+") = ("+
                      ",".join(number(x) for x in values)+")")
                family["colors" if typ==0 else "vectors"]+=1
            elif typ==2:
                require(all(x==0 for x in values[1:]),
                        "PROPERTY_DEFAULT_NUMERIC")
                line=label+"Float) = "+number(values[0])
                family["floats"]+=1
            else:
                require(values[3]==0 and values[1]<=values[0]<=values[2],
                        "PROPERTY_RANGE")
                line=(label+"Range("+number(values[1])+","+
                      number(values[2])+")) = "+number(values[0]))
                family["ranges"]+=1
        require(not attributes or typ == 2, "PROPERTY_FLAGS_OR_ATTRIBUTES")
        prefix = ("[HideInInspector] " if flags == 1 else "") + ("[Toggle] " if attributes else "")
        lines.append(prefix + line)
    lines.append("}")
    return "\n".join(lines), {
        "original_authored_property_count":len(props),
        "original_authored_texture_property_count":family["textures"],
        "original_authored_color_property_count":family["colors"],
        "original_authored_vector_property_count":family["vectors"],
        "original_authored_float_property_count":family["floats"],
        "original_authored_range_property_count":family["ranges"],
    }

def source_fragment(parsed):
    profile=inspect_parsed(parsed)
    require(profile.get("source_108_particle_shader_original_normal_Pass") is True
            and profile.get("original_pass_color_mask_shaderlab_channels")=="RGB"
            and profile.get("original_pass_opt_in_selective_colormask_translator_accepted") is True,
            "SOURCE_STATE")
    subs=parsed["m_SubShaders"]
    sub=subs[0]
    require(type(sub.get("m_LOD")) is int and 0<=sub["m_LOD"]<=10000
            and type(sub.get("m_Tags")) is dict
            and type(sub.get("m_Passes")) is list and len(sub["m_Passes"])==1,
            "SUBSHADER_TOPOLOGY")
    props,counts=serialize_properties(parsed)
    pass_record=sub["m_Passes"][0]
    try:
        state=render_state(pass_record["m_State"],allow_selective_color_mask=True)
        header=quoted(parsed["m_Name"])
        sub_tags=tags(sub["m_Tags"])
    except (KeyError,TypeError,ValueError) as exc:
        raise PrivateContractError("SOURCE_STATE") from None
    # Deliberately no HLSLPROGRAM, no pass source, and no pretend program. The
    # explicit marker prevents an accidental publication as a usable shader.
    txt="\n".join([
        "// PRIVATE FRAGMENT ONLY; NOT A UNITY SHADER PROGRAM",
        "Shader "+header+" {", props, "SubShader {",
        "LOD "+str(sub["m_LOD"]),sub_tags, "Pass {",
        state, "// Original VS/FS keyword programs NOT YET INTEGRATED",
        "}", "}", "}",
    ])+"\n"
    require(len(txt.encode("utf-8"))<=MAX_BYTES,"PRIVATE_SHADERLAB_SIZE")
    require("ColorMask RGB" in txt and "HLSLPROGRAM" not in txt
            and "DummyShaderTextExporter" not in txt,"SOURCE_STATE")
    return txt, {
        "schema_version":1,"status":STATUS,**counts,
        "original_one_SubShader_one_Pass":True,
        "original_one_Pass_render_state_translated":True,
        "original_fixed_function_selective_RGB_colormask_preserved":True,
        "original_keyword_VSFS_programs_integrated":False,
        "original_selected_material_texture_bindings_included":False,
        "source_fragment_is_intentionally_not_a_compilable_Unity_shader":True,
        "original_raw_property_names_values_and_shader_text_published":False,
        "native_Android_GPU_pixels_or_emitter_identity_verified":False,
    }

def probe(original,manifest,private_dest):
    import UnityPy
    from scripts import t3_original_renderer_shader_impact as impact
    from scripts.t3_original_particle108_dxbc_feasibility import select
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    chosen={}
    census=impact.load_original(original,manifest,private_particle_slot_counts=chosen)
    owner,pid=select(chosen,census)
    candidate=original/"Raft_Data"/owner
    if candidate.is_symlink() or fingerprint(candidate)!=SHADER_OWNERS[owner]:
        raise ValueError("unverified_private_original_Shader48_source")
    obj=[x for x in UnityPy.load(str(candidate)).file.objects.values()
         if x.path_id==pid]
    if len(obj)!=1 or obj[0].type.name!="Shader":
        raise ValueError("ambiguous_private_original_Particle_Shader48")
    txt,result=source_fragment(obj[0].read_typetree().get("m_ParsedForm"))
    if private_dest is not None:
        if (private_dest.exists() or private_dest.is_symlink() or
            not private_dest.parent.is_dir() or private_dest.parent.is_symlink() or
            private_dest.resolve().is_relative_to(original.resolve())):
            raise ValueError("unsafe_private_fragment_destination")
        private_dest.write_text(txt,encoding="utf-8")
    result["six_original_scenes_sha_authenticated"]=True
    result["four_original_Shader_Material_owner_sha_authenticated"]=True
    result["source_particle_renderer_material_slots"]=108
    result["private_fragment_written_to_temporary_runner_only"]=private_dest is not None
    return result

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original","manifest","out"):
        p.add_argument("--"+key,type=Path,required=True)
    p.add_argument("--private-dest",type=Path)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
        a.out.resolve().is_relative_to(a.original.resolve()) or
        (a.private_dest is not None and
         (a.private_dest.resolve()==a.out.resolve() or
          a.private_dest.resolve().is_relative_to(a.original.resolve())))):
        raise ValueError("unsafe_original_fragment_report_paths")
    try:
        data=probe(a.original,a.manifest,a.private_dest)
    except PrivateContractError as exc:
        data={"schema_version":1,"status":"SOURCE_PROPERTY_OR_STATE_UNSUPPORTED",
              "category":exc.category,
              "native_Android_GPU_pixels_or_emitter_identity_verified":False}
    except Exception as exc:
        data={"schema_version":1,"status":"INCONCLUSIVE",
              "failure_type":type(exc).__name__,
              "native_Android_GPU_pixels_or_emitter_identity_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("T3_PRIVATE_ORIGINAL_PARTICLE108_PROPSTATE_SAFE="+json.dumps(data,sort_keys=True))
    return 0 if data["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
