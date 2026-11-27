"""Private exact final-route compilation admission, same toolchain only.

Inputs MUST be the trusted in-process result of authorized same-object source,
translation and bound-stage admission, plus independently proved runtime
keyword/pass normalization. This tool does not establish those prerequisites.
It reuses the historical stage transformations, independently of the candidate
router/text; it is NOT independent proof of transform semantics. It compares
actual compiler bytes, not asserted hashes or counts. glslang output is NOT
an expected Unity DXC/SMOL-V module. No original acquisition or installation.
"""
from hashlib import sha256
from pathlib import Path
import re
import struct
import tempfile

from tools.gt_next23b_source_program_admission.audit import canonical
from tools.gt_next23b_translation_replay.audit import pins_checked, invoke, read_bounded
from scripts.gt_original_921_shaderlab import (
    paired_uniform_layouts, rebind_constant_buffers, restore_vertex_inputs,
    pin_varying_locations, unity_varying_semantics, unity_resource_bindings,
    combine_stages,
)
from scripts.gt_runtime_keyword_contract import keyword_set, exact_independent_toggle_plan

LIMIT=64*1024*1024
STAGES={1:("vs","vert","VERTEX",0),0:("fs","frag","FRAGMENT",4)}
def need(ok, reason):
    if not ok: raise ValueError("next23b_final_route_"+reason)
def sha(raw):return sha256(raw).hexdigest()

def build_routes(*, witness, keyword_names, records, bound_hlsl, dxbc,
                 normalization, counts):
    """Consume admitted snapshots; route keys never derive from candidate text.
    normalization maps (pass, sorted original names) -> sorted engine names.
    Caller supplies independently established pass/keyword semantics.
    """
    keyword_set(keyword_names)
    need(type(counts) in (tuple,list) and all(type(c) is int and c>0 for c in counts),
         "invalid_counts")
    need(type(witness) is list and len(witness)==2*sum(counts)
         and len(records)==len(witness) and set(bound_hlsl)==set(range(len(witness))),
         "slot_population")
    groups={};positions=set();slots=set();refs=set()
    for row in witness:
        slot=row["slot"]
        need(type(slot) is list and len(slot)==5 and all(type(x) is int and x>=0 for x in slot),
             "invalid_slot")
        sub,p,stage,bucket,ordinal=slot
        need(sub==0 and 0<=p<len(counts) and stage in STAGES and tuple(slot) not in slots,
             "duplicate_or_invalid_slot")
        slots.add(tuple(slot))
        ix=row["keyword_indices"]
        need(type(ix) is list and all(type(x) is int and 0<=x<len(keyword_names) for x in ix)
             and len(set(ix))==len(ix),"invalid_keyword_indices")
        key=(p,tuple(sorted(keyword_names[x] for x in ix)))
        lanes=groups.setdefault(key,{})
        need(stage not in lanes,"duplicate_stage_route")
        pos=row["legacy_directory_ordinal"]
        need(type(pos) is int and 0<=pos<len(records) and pos not in positions,"record_position")
        positions.add(pos)
        record=records[pos];ref=row["program_ref"];refs.add(ref)
        need([record[k] for k in ("subshader","pass","stage","player_bucket","ordinal")]==slot
             and record["original_parameter_blob_index"]==row["parameter_blob_index"]
             and sha(canonical(record))==row["record_sha256"],"record_commitment")
        need(type(bound_hlsl[pos]) is bytes and 0<len(bound_hlsl[pos])<=LIMIT
             and sha(bound_hlsl[pos])==row["resource_bound_sha256"],"bound_commitment")
        need(ref in dxbc and type(dxbc[ref]) is bytes and sha(dxbc[ref])==row["dxbc_sha256"],
             "dxbc_commitment")
        lanes[stage]=(row,record,bound_hlsl[pos].decode("utf-8"))
    need(set(dxbc)==refs and set(normalization)==set(groups)
         and all(set(g)==set(STAGES) for g in groups.values()),"route_population")
    need([sum(p==i for p,_ in groups) for i in range(len(counts))]==list(counts),
         "route_pass_counts")
    used={};fixed_by_pass={};routes={}
    for (p,source_key),lanes in groups.items():
        engine=tuple(sorted(keyword_set(normalization[p,source_key])))
        need(set(engine)<=set(source_key),"normalization_unknown_keyword")
        fixed=frozenset(source_key)-frozenset(engine)
        need(fixed_by_pass.setdefault(p,fixed)==fixed,"normalization_inconsistent_fixed_set")
        k=(p,engine)
        need(k not in used,"normalization_collision")
        used[k]=source_key
        v,f=lanes[1],lanes[0]
        need(v[0]["slot"][3]==f[0]["slot"][3],"paired_bucket_mismatch")
        layouts=paired_uniform_layouts([v[1],f[1]])
        stages=[]
        for offset,(stage,lane) in enumerate(((1,v),(0,f))):
            row,record,source=lane
            text=rebind_constant_buffers(source,layouts[offset])
            if stage==1:text,_=restore_vertex_inputs(text,dxbc[row["program_ref"]])
            text=unity_varying_semantics(pin_varying_locations(text,stage))
            name=STAGES[stage][0]
            text,n=re.subn(r"\bmain(?=\s*\()",f"gt_{name}_main",text)
            need(n==1,"stage_entry")
            stages.append(unity_resource_bindings(text,name))
        combined=combine_stages(*stages)
        routes[k]={"source_key":source_key,"source_refs":{1:v[0]["program_ref"],0:f[0]["program_ref"]},
                   "slots":{1:v[0]["slot"],0:f[0]["slot"]},
                   "stage_source_sha256":{1:sha(stages[0].encode()),0:sha(stages[1].encode())},
                   "body":combined}
    for p in range(len(counts)):
        exact_independent_toggle_plan([k for i,k in routes if p==i])
    return routes

def check_module(raw, stage):
    need(type(raw) is bytes and 20<=len(raw)<=LIMIT and len(raw)%4==0
         and raw[:4]==b"\x03\x02\x23\x07","spirv_header")
    at=20;entries=[]
    while at<len(raw):
        header,=struct.unpack_from("<I",raw,at)
        width,op=header>>16,header&65535
        need(width>0 and at+4*width<=len(raw),"spirv_instruction")
        if op==15:
            need(width>=4,"spirv_entry")
            model,=struct.unpack_from("<I",raw,at+4)
            name=raw[at+12:at+width*4].split(b"\0",1)[0]
            entries.append((model,name))
        at+=4*width
    name,_,_,model=STAGES[stage]
    need(entries==[(model,("gt_"+name+"_main").encode("ascii"))],"spirv_stage_entry")

def compile_module(code, key, stage, tools, root):
    """Same exact options as legacy verify_entrypoints default lane."""
    need(type(code) is str and 0<len(code.encode("utf-8"))<=LIMIT,"source_bytes")
    name,suffix,macro,_=STAGES[stage]
    source=root/"route.hlsl";binary=root/"route.spv"
    source.write_bytes(code.encode("utf-8"))
    binary.unlink(missing_ok=True)
    invoke(tools,root,"glslangValidator","-V","-D","--target-env","vulkan1.1",
           "-S",suffix,"-e","gt_"+name+"_main","-DSHADER_STAGE_"+macro+"=1",
           *("-D"+k+"=1" for k in sorted(keyword_set(key))),"-o","route.spv","route.hlsl")
    raw=read_bounded(binary,LIMIT)
    check_module(raw,stage)
    invoke(tools,root,"spirv-val","--target-env","vulkan1.1","route.spv")
    return raw

def candidate_blocks(shader, pass_count):
    need(type(shader) is str and 0<len(shader.encode("utf-8"))<=128*1024*1024,"shader_bytes")
    blocks=re.findall(r"(?ms)^HLSLPROGRAM\n(.*?)^ENDHLSL$",shader)
    need(len(blocks)==pass_count,"pass_blocks")
    return [re.sub(r"(?m)^#pragma [^\n]*\n","",block) for block in blocks]

def expected_modules(routes,pins):
    """Independent per-route compile without candidate routing branches."""
    tools=pins_checked(pins);result={}
    with tempfile.TemporaryDirectory(prefix="gt-final-expected-") as tmp:
        root=Path(tmp)
        for (p,key),row in sorted(routes.items()):
            for stage in (1,0):
                result[p,key,stage]=compile_module(row["body"],key,stage,tools,root)
    pins_checked(pins)
    return result

def candidate_modules(shader,routes,pins):
    tools=pins_checked(pins);blocks=candidate_blocks(shader,1+max(p for p,_ in routes));result={}
    with tempfile.TemporaryDirectory(prefix="gt-final-candidate-") as tmp:
        root=Path(tmp)
        for p,key in sorted(routes):
            for stage in (1,0):
                result[p,key,stage]=compile_module(blocks[p],key,stage,tools,root)
    pins_checked(pins)
    return result

def compare(expected,actual):
    """Exact independently generated same-toolchain module bytes, not hashes.
    Does not accept Unity/DXC modules merely because they validate or match
    reflection. A separately authenticated comparable Unity compilation and
    independent serialized route decoder are still required for Unity admission.
    """
    need(type(expected) is dict and type(actual) is dict and set(expected)==set(actual),
         "module_route_population")
    for k in expected:
        need(type(expected[k]) is bytes and type(actual[k]) is bytes
             and expected[k]==actual[k],"compiled_module_identity_mismatch")
    return {"status":"PASS_EXACT_FINAL_ROUTE_SAME_TOOLCHAIN_ONLY",
            "route_stages":len(expected),"distinct_modules":len({sha(x) for x in expected.values()}),
            "unity_compiled_module_identity_verified":False,
            "source_scope_semantics_verified":False,"semantic_equivalence_verified":False,
            "production_install_allowed":False}

def verify_next23b(*, shader,pins,**inputs):
    """Authorized caller only. Full source profile; diagnostic glslang lane."""
    need(len(inputs["dxbc"])==134,"original_program_count")
    routes=build_routes(**inputs,counts=(512,4,128,512))
    expected=expected_modules(routes,pins)
    actual=candidate_modules(shader,routes,pins)
    return expected,compare(expected,actual)
