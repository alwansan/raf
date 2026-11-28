"""Private audit of merged source ABI, distinct from engine upload.

Original stage metadata is authoritative. Reflection uses the exact combined
wrapper and separately records optimized and unoptimized Vulkan compilation.
Names, raw layouts, shader binaries and diagnostics remain private.
"""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import tempfile

from scripts.gt_original_921_shaderlab import TOP_LEVEL, MEMBER, PACKOFFSET
from scripts.gt_original_921_cb_hlsl import declaration
from scripts.gt_resource_register_contract import mask_noncode, registered_resources
from scripts.gt_material_route_values import normalize

class MergeError(ValueError): pass
def need(ok,code):
    if not ok:raise MergeError(code)

def type_shape(m):
    # SPIRV-Cross JSON spelling, not Unity's upload rules.
    t="float" if m["type"]==0 else "uint"
    if m["matrix"]:return "mat4"
    n=m["columns"]
    return t if n==1 else ("vec" if t=="float" else "uvec")+str(n)

def collect_wrapper(wrapper):
    code=mask_noncode(wrapper)
    cb={};resources={};loose={}
    for m in TOP_LEVEL.finditer(code):
        if m["kind"]=="cbuffer":
            block=m["name"];need(block not in cb,"merge_duplicate_block")
            rows={}
            for x in MEMBER.finditer(m["body"]):
                off=PACKOFFSET.search(x[0]);need(off is not None,"merge_missing_offset")
                name=x["var"]
                need(name not in rows,"merge_duplicate_member")
                rows[name]=(x["type"],x["array"] or "",int(off[1])*16+"xyzw".index(off[2] or "x")*4)
            cb[block]=rows
        elif m["resource"]:
            name=m["resource"];need(name not in resources,"merge_duplicate_resource")
            resources[name]=m["decl"].split(name,1)[0].strip()
    # combine_stages promotes duplicate original $Globals to a loose uniform.
    for m in re.finditer(r"(?m)^((?:column_major |row_major )?(?:float|uint)\w*) ([A-Za-z_]\w*)(\[\d+\])?;$",code):
        need(m[2] not in loose,"merge_duplicate_loose")
        loose[m[2]]=(m[1],m[3] or "")
    return cb,resources,loose

def source_occurrences(rows,mat,texenvs,parsed):
    saved=normalize(mat)
    numeric=set().union(*(set(v) for v in saved.values()))
    declared={p["m_Name"] for p in parsed["m_PropInfo"]["m_Props"]}
    by_stage=[]
    for row in rows:
        role={1:"vs",0:"fs"}[row["stage"]]
        members=[];resources=[]
        for buf in row["source_constant_buffer_layouts"]:
            need(not buf["structs"],"merge_struct_layout_outside_scope")
            original=buf["name"]
            merged=original if original!="$Globals" else "gt_"+role+"_raft921_cb"+str(buf["source_slot"])+"_Globals"
            for m in buf["members"]:
                name=m["name"]
                category=("material" if name in numeric else "material_st" if name.endswith("_ST") and name[:-3] in texenvs
                          else "declared_unsaved" if name in declared else "external")
                members.append(dict(member=m,original_block=original,merged_block=merged,category=category))
        for r in row["source_texture_sampler_bindings"]:
            name=r["source_texture_name"]
            resources.append(dict(name=("sampler"+name if r["kind"]=="s" else name),kind=r["kind"],
                                  external=name not in texenvs,source_name=name))
        by_stage.append(dict(role=role,members=members,resources=resources))
    need([x["role"] for x in by_stage]==["vs","fs"],"merge_stage_order")
    return by_stage

def source_declarations(stages,wrapper,raw_sources,rows):
    cb,res,loose=collect_wrapper(wrapper)
    out=[]
    for stage,raw,row in zip(stages,raw_sources,rows,strict=True):
        metrics=Counter()
        for item in stage["members"]:
            m=item["member"];name=m["name"];cat=item["category"]
            metrics["named_occurrences"]+=1;metrics[cat+"_occurrences"]+=1
            spelling=declaration(m).split(" "+name,1)[0]
            array="["+str(m["array_size"])+"]" if m["array_size"] else ""
            member=cb.get(item["merged_block"],{}).get(name)
            if member is not None:
                metrics["exact_declaration_offset" if member==(spelling,array,m["index"]) else "declaration_mismatch"]+=1
            elif item["original_block"]=="$Globals" and loose.get(name)==(spelling,array):
                metrics["promoted_loose_globals"]+=1
                if cat=="external":metrics["promoted_external_globals"]+=1
            else:metrics["declaration_missing"]+=1
        regs={(m[3],int(m[2][1:])):re.sub(r"\s+","",m[1]) for m in registered_resources(raw)}
        need(len(regs)==len(row["source_texture_sampler_bindings"]),"merge_resource_original_count")
        for item,source in zip(stage["resources"],row["source_texture_sampler_bindings"],strict=True):
            metrics["resource_occurrences"]+=1
            typ=regs[(source["kind"],source["slot"])]
            merged=re.sub(r"\s+","",res.get(item["name"],""))
            key="resource_type_match" if typ==merged else "resource_type_mismatch"
            metrics[key]+=1
            if item["external"]:
                metrics["external_"+item["kind"]+"_occurrences"]+=1
                metrics["external_"+key]+=1
        out.append(dict(metrics))
    return out

def reflect_index(data):
    types=data.get("types",{});members={};res={}
    for block in data.get("ubos",[]):
        name=block["name"]
        for m in types[block["type"]]["members"]:
            members.setdefault(m["name"],[]).append((name,m))
    for key,kind in (("separate_images","t"),("separate_samplers","s"),("textures","t")):
        for r in data.get(key,[]):
            res.setdefault((kind,r["name"]),[]).append(r)
    return members,res

def reflection_counts(stage,data):
    members,res=reflect_index(data)
    counts=Counter()
    for item in stage["members"]:
        m=item["member"];cat=item["category"]
        rows=members.get(m["name"],[])
        counts["named_occurrences"]+=1;counts[cat+"_occurrences"]+=1
        if not rows:label="absent"
        elif len(rows)!=1:label="ambiguous"
        else:
            block,entry=rows[0]
            typ_ok=(entry.get("type")==type_shape(m) and
                    entry.get("array",[])==([m["array_size"]] if m["array_size"] else []) and
                    (not m["matrix"] or entry.get("matrix_stride")==16) and
                    (not m["array_size"] or entry.get("array_stride")== (64 if m["matrix"] else 16)))
            if not typ_ok:label="type_or_stride_mismatch"
            elif block!=item["merged_block"]:label="block_relocated"
            elif entry.get("offset")!=m["index"]:label="offset_mismatch"
            else:label="exact_block_offset_type"
        counts[label]+=1;counts[cat+"_"+label]+=1
    for item in stage["resources"]:
        n=len(res.get((item["kind"],item["name"]),[]))
        k="resource_reflected" if n==1 else "resource_missing" if n==0 else "resource_ambiguous"
        counts[k]+=1
        if item["external"]:counts["external_"+item["kind"]+"_"+k]+=1
    return dict(counts)

def command(args,timeout=90):
    try:
        return subprocess.run(args,capture_output=True,check=False,timeout=timeout).returncode==0
    except (OSError,subprocess.TimeoutExpired):return False

def compile_reflection(wrapper,root,stage,mode):
    # Default compile mirrors the prior explicit candidate; noopt is a
    # separate diagnostic and cannot be used to waive a default mismatch.
    from scripts.t3_spirv_interface_name_drift import read_reflection
    suffix,macro,entry=("vert","VERTEX","gt_vs_main") if stage=="vs" else ("frag","FRAGMENT","gt_fs_main")
    code=re.sub(r"(?m)^#pragma [^\n]*\n","",wrapper)
    need(code.startswith("HLSLPROGRAM\n") and code.endswith("\nENDHLSL"),"merge_wrapper_boundary")
    code=code[len("HLSLPROGRAM\n"):-len("\nENDHLSL")]
    with tempfile.TemporaryDirectory(prefix="merged-reflection-",dir=root) as tmp:
        src=Path(tmp)/"source.hlsl";binary=Path(tmp)/"source.spv";src.write_text(code)
        args=["glslangValidator","-V","-D","--target-env","vulkan1.1"]
        if mode=="noopt_hlsl_offsets":args+=["--hlsl-offsets","-Od"]
        ok=command(args+["-S",suffix,"-e",entry,"-DSHADER_STAGE_"+macro+"=1","-o",str(binary),str(src)])
        result=dict(compiled=ok,validated=False,reflected=False)
        if not ok:return result,None
        result["validated"]=command(["spirv-val","--target-env","vulkan1.1",str(binary)])
        if not result["validated"]:return result,None
        try:data=read_reflection(binary)
        except (ValueError,OSError,subprocess.TimeoutExpired):return result,None
        need([r["name"] for r in data["entryPoints"]]==[entry],"merge_reflected_entrypoint")
        result["reflected"]=True
        return result,data

def audit(root,wrapper,rows,raw_sources,mat,texenvs,parsed):
    stages=source_occurrences(rows,mat,texenvs,parsed)
    declarations=source_declarations(stages,wrapper,raw_sources,rows)
    total=Counter()
    for x in declarations:total.update(x)
    need(total["named_occurrences"]==55 and total["external_occurrences"]==22 and
         total["external_t_occurrences"]==3,"merge_expected_source_population")
    # The original per-stage gate already proved the individual buffers.
    # Deliberate promotion is reported independently from exact parity.
    modes={}
    for mode in ("default","noopt_hlsl_offsets"):
        output=[]
        for stage in stages:
            result,data=compile_reflection(wrapper,root,stage["role"],mode)
            if data is not None:result["comparison"]=reflection_counts(stage,data)
            output.append(result)
        modes[mode]=output
    both_default=all(x["reflected"] for x in modes["default"])
    exact_default=both_default and all(x["comparison"].get("exact_block_offset_type",0)==len(s["members"])
                       and x["comparison"].get("resource_reflected",0)==len(s["resources"])
                       for x,s in zip(modes["default"],stages,strict=True))
    exact_source=(total["exact_declaration_offset"]==55 and total["resource_type_match"]==total["resource_occurrences"])
    return dict(status="OBSERVED_MERGED_SOURCE_ABI_CONTEXT" if both_default else "INCONCLUSIVE_MERGED_REFLECTION",
                source_declaration_counts=dict(total),stage_declaration_counts=declarations,compile_modes=modes,
                exact_merged_source_declarations=exact_source,exact_merged_default_reflection=exact_default,
                distinct_external_numeric_names=len({i["member"]["name"] for s in stages for i in s["members"] if i["category"]=="external"}),
                distinct_external_texture_names=len({i["source_name"] for s in stages for i in s["resources"] if i["external"] and i["kind"]=="t"}),
                runtime_uniform_upload_verified=False,original_game_global_resources_verified=False,
                Unity_execution=False,white_mesh_repair_verified=False,production=False,XAPK=False)
