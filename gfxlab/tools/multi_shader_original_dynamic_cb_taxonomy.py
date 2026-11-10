#!/usr/bin/env python3
"""GFX063: fail-closed authentic DXBC CB dynamic operand SHAPE census.

The first 157 Shader48 Pass-JOINT class representatives are audited only as
private original DXBC source for the dynamic/extended operand taxonomy. The
seven independent SPIR-V diagnostic pairs are chosen for maximal per-Pass
dynamic CB operand occurrence coverage, not for 524 variant parity.
Source-to-SPIR-V dynamic index-expression equivalence is NOT established.
All private source bytes, b/t/s register IDs, CB lengths and variants stay in
the SHA-pinned CI runner and are deleted. Emit anonymous aggregate counts only.
"""
from __future__ import annotations
import argparse
import json
import re
import struct
import tempfile
from collections import Counter
from pathlib import Path

from gfxlab.tools.original_model_probe import stage_originals, ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair, code_from_ref, translate_pair
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_original_decl_profile_coverage import canonical_private_declaration_profile
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import private_signature
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import original_sample_pairs, operand, CUSTOMDATA, MAX_DWORDS, MAX_INST
from gfxlab.tools.multi_shader_original_cb_access_shapes import scan_known_dxbc_cb_operands, KNOWN_ARITHMETIC_ARITY
from gfxlab.tools.multi_shader_original_cb_byte_addresses import private_authenticated_ubo_layouts
from gfxlab.tools.multi_shader_original_cb_global_opname import global_cb_evidence
from gfxlab.tools.multi_shader_pass_joint_batch062 import select_pass_scoped_joint_classes
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet

CATEGORIES=(
    "dynamic_b_and_vec",
    "dynamic_b_only",
    "dynamic_vec_relative",
    "dynamic_vec_immediate32_plus_relative",
    "dynamic_vec_immediate64_plus_relative",
    "extended_modifier_but_literal_indices",
    "unsupported_CB_index_shape",
)
MAX_SPV_BYTES=16*1024*1024
ASSIGN=re.compile(r"^\s*(%[0-9]+)\s*=\s*(Op[A-Za-z0-9_]+)(?:\s+(.*))?$")

def original_cb_source_dynamic_taxonomy(shdr,declared):
    """Revisit ONLY the previously covered nine DXBC arithmetic families.

    Categories partition the unresolved operands previously counted by GFX051.
    More detailed tokenization does not prove an unknown dynamic vec4 index;
    it only identifies which kind of CB index was present.
    """
    if (not isinstance(shdr,bytes) or len(shdr)<12 or len(shdr)%4
        or len(shdr)>MAX_DWORDS*4 or not isinstance(declared,dict)):
        raise ValueError("GFX063_BAD_DXBC_INPUT")
    if any(type(b)!=int or type(n)!=int or not 0<=b<=65535
           or not 0<n<=65535 for b,n in declared.items()):
        raise ValueError("GFX063_CB_DECLARATION_INVALID")
    words=struct.unpack("<%dI"%(len(shdr)//4),shdr)
    if words[1]!=len(words):raise ValueError("GFX063_SOURCE_DXBC_LENGTH_INVALID")
    c=Counter({k:0 for k in CATEGORIES})
    c.update({
      "source_arithmetic_instructions_covered":0,
      "source_arithmetic_instructions_not_covered":0,
      "source_arithmetic_parse_rejected":0,
      "source_CB_operands_in_covered_arithmetic":0,
      "source_CB_static_unmodified_operand_occurrences":0,
      "source_CB_unresolved_dynamic_or_extended_occurrences":0,
      "source_CB_relative_or_extended_operand_modifier_occurrences":0,
    })
    p=2;num=0
    while p<len(words):
        opword=words[p]
        op=opword&2047
        if op==CUSTOMDATA:
            if p+1>=len(words):raise ValueError("GFX063_CUSTOMDATA_TRUNCATED")
            ln=words[p+1]
            if ln<2:raise ValueError("GFX063_CUSTOMDATA_BAD_LENGTH")
        else:
            ln=(opword>>24)&127
            if not ln:raise ValueError("GFX063_SOURCE_OPCODE_ZERO_LENGTH")
        end=p+ln
        if end>len(words):raise ValueError("GFX063_SOURCE_OPCODE_OVERRUN")
        num+=1
        if num>MAX_INST:raise ValueError("GFX063_SOURCE_INSTRUCTION_LIMIT")
        if op not in KNOWN_ARITHMETIC_ARITY:
            c["source_arithmetic_instructions_not_covered"]+=1
            p=end;continue
        cursor=p+1
        extension=bool(opword&0x80000000)
        n_ext=0
        while extension:
            if cursor>=end or n_ext>=4:
                raise ValueError("GFX063_OPCODE_EXTENSION_INVALID")
            ext=words[cursor];cursor+=1
            if (ext&63) not in (0,1,2,3):
                raise ValueError("GFX063_UNRECOGNIZED_OPCODE_EXTENSION")
            extension=bool(ext&0x80000000)
            n_ext+=1
        args=[]
        try:
            for _ in range(KNOWN_ARITHMETIC_ARITY[op]):
                first=words[cursor]
                decoded,cursor2=operand(words,cursor,end)
                args.append((first,decoded))
                cursor=cursor2
            if cursor!=end:raise ValueError("GFX063_SOURCE_ARITY_MISMATCH")
        except (ValueError,IndexError):
            c["source_arithmetic_parse_rejected"]+=1
            raise ValueError("GFX063_KNOWN_ARITHMETIC_OPERAND_REJECTED") from None
        c["source_arithmetic_instructions_covered"]+=1
        if args[0][1]["type"]==8:
            raise ValueError("GFX063_CB_AS_DESTINATION")
        for token,operand_data in args[1:]:
            if operand_data["type"]!=8:continue
            c["source_CB_operands_in_covered_arithmetic"]+=1
            dim=operand_data["dimension"]
            idx=operand_data["indices"]
            rep0=(token>>22)&7
            rep1=(token>>25)&7
            ext=bool(operand_data["extended"])
            if ext:c["source_CB_relative_or_extended_operand_modifier_occurrences"]+=1
            if dim!=2 or len(idx)!=2:
                category="unsupported_CB_index_shape"
            elif rep0 in (2,3,4) and rep1 in (2,3,4):
                category="dynamic_b_and_vec"
            elif rep0 in (2,3,4):
                category="dynamic_b_only"
            elif rep0 in (0,1) and rep1 in (2,3,4):
                category={
                    2:"dynamic_vec_relative",
                    3:"dynamic_vec_immediate32_plus_relative",
                    4:"dynamic_vec_immediate64_plus_relative",
                }[rep1]
            elif rep0 in (0,1) and rep1 in (0,1):
                if type(idx[0])!=int or type(idx[1])!=int:
                    category="unsupported_CB_index_shape"
                else:
                    b,v=idx
                    if b not in declared:raise ValueError("GFX063_UNDECLARED_CB_REGISTER")
                    if not 0<=v<declared[b]:raise ValueError("GFX063_CB_VECTOR_OUT_OF_BOUNDS")
                    category="extended_modifier_but_literal_indices" if ext else None
            else:
                category="unsupported_CB_index_shape"
            if category is None:
                c["source_CB_static_unmodified_operand_occurrences"]+=1
            else:
                c[category]+=1
                c["source_CB_unresolved_dynamic_or_extended_occurrences"]+=1
        p=end
    if p!=len(words):raise ValueError("GFX063_DXBC_NOT_TERMINATED")
    if (sum(c[k] for k in CATEGORIES)!=c["source_CB_unresolved_dynamic_or_extended_occurrences"]
        or c["source_CB_static_unmodified_operand_occurrences"]+
           c["source_CB_unresolved_dynamic_or_extended_occurrences"]!=
           c["source_CB_operands_in_covered_arithmetic"]):
        raise ValueError("GFX063_UNRESOLVED_TAXONOMY_ACCOUNTING_DRIFT")
    result={k:int(v) for k,v in c.items()}
    result["dynamic_CB_index_expression_equivalent_to_SPV_proven"]=False
    result["original_Material_CB_member_semantics_proven"]=False
    return result

def spv_authenticated_dynamic_cb_pointer_loads(dis,authenticated):
    """Observe dynamic indexed real SPV Uniform UBO access-chain to OpLoad.

    Authenticated original b/array layout must be proven independently by the
    caller. A real loaded dynamic SPV pointer does NOT prove any individual
    original DXBC relative index expression translates identically.
    Unknown pointer alias, nonzero member, wrong index type and no-load chains
    are never counted as proven reads.
    """
    if (not isinstance(dis,bytes) or not 0<len(dis)<=MAX_SPV_BYTES
        or not isinstance(authenticated,dict)):
        raise ValueError("GFX063_SPV_INPUT_INVALID")
    lines=dis.decode("utf8","strict").splitlines()
    if len(lines)>300000:raise ValueError("GFX063_SPV_TEXT_LIMIT")
    definition={};int32=set()
    for raw in lines:
        line=raw.split(";",1)[0].strip()
        m=ASSIGN.fullmatch(line)
        if not m:continue
        ident,op,tail=m.groups()
        if ident in definition:raise ValueError("GFX063_SPV_DUPLICATE_RESULT_ID")
        args=(tail or "").split()
        definition[ident]=(op,args)
        if op=="OpTypeInt" and args in (["32","0"],["32","1"]):
            int32.add(ident)
    constants={}
    for ident,(op,args) in definition.items():
        if op=="OpConstant" and len(args)==2 and args[0] in int32:
            try:value=int(args[1],10)
            except ValueError:continue
            constants[ident]=value
        elif op=="OpConstantNull" and len(args)==1 and args[0] in int32:
            constants[ident]=0
    def index(token):
        if token in constants:return ("literal",constants[token])
        op,args=definition.get(token,(None,[]))
        if op and op not in ("OpSpecConstant","OpSpecConstantOp","OpSpecConstantComposite",
                            "OpConstant","OpConstantNull","OpUndef") and args and args[0] in int32:
            return ("dynamic",None)
        return ("unsupported",None)
    states={}
    c=Counter({
      "spv_access_chains_from_authenticated_UBO_global":0,
      "spv_authentic_CB_dynamic_vec_access_chains":0,
      "spv_authentic_CB_dynamic_vec_access_chains_without_load":0,
      "spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences":0,
      "spv_authentic_CB_dynamic_vec_global_roots_with_loads":0,
      "spv_invalid_struct_member_or_unsupported_index_chains":0,
      "spv_literal_vector_index_out_of_bounds":0,
      "spv_unproven_select_phi_aliases":0,
    })
    loaded_roots=set()
    created=0
    loaded_pointers=set()
    for raw in lines:
        m=ASSIGN.fullmatch(raw.split(";",1)[0].strip())
        if not m:continue
        ident,op,tail=m.groups();a=(tail or "").split()
        if op in ("OpAccessChain","OpInBoundsAccessChain") and len(a)>=3:
            root=a[1]
            if root in authenticated:
                c["spv_access_chains_from_authenticated_UBO_global"]+=1
                data=authenticated[root]
                if (not isinstance(data,tuple) or len(data)!=4 or
                    type(data[0]) is not int or type(data[1]) is not int or
                    type(data[2]) is not int or type(data[3]) is not int or
                    data[1]!=0 or data[2]!=16 or data[3]<=0):
                    raise ValueError("GFX063_AUTHENTICATED_UBO_LAYOUT_INVALID")
                parent=("global",root,data[3])
            elif root in states:
                parent=states[root]
            else:continue
            kind,origin,extent=parent
            inds=a[2:]
            if kind=="global":
                first=index(inds[0])
                if first!=("literal",0):
                    c["spv_invalid_struct_member_or_unsupported_index_chains"]+=1
                    continue
                indices=inds[1:]
                if len(indices)==0:
                    states[ident]=("array",origin,extent)
                    continue
            elif kind=="array":
                indices=inds
            elif kind=="dynamic_vector":
                if len(inds)==1 and index(inds[0])[0]=="literal" and 0<=index(inds[0])[1]<4:
                    states[ident]=("dynamic_scalar",origin,extent)
                else:
                    c["spv_invalid_struct_member_or_unsupported_index_chains"]+=1
                continue
            else:continue
            if len(indices) not in (1,2):
                c["spv_invalid_struct_member_or_unsupported_index_chains"]+=1;continue
            first_kind,first_val=index(indices[0])
            if first_kind=="literal":
                if not 0<=first_val<extent:
                    c["spv_literal_vector_index_out_of_bounds"]+=1
                    continue
                continue  # Literal index paths were already proved by GFX053.
            if first_kind!="dynamic":
                c["spv_invalid_struct_member_or_unsupported_index_chains"]+=1;continue
            if len(indices)==2:
                component_kind,component_val=index(indices[1])
                if component_kind!="literal" or not 0<=component_val<4:
                    c["spv_invalid_struct_member_or_unsupported_index_chains"]+=1;continue
                states[ident]=("dynamic_scalar",origin,extent)
            else:
                states[ident]=("dynamic_vector",origin,extent)
            c["spv_authentic_CB_dynamic_vec_access_chains"]+=1
            created+=1
        elif op=="OpCopyObject" and len(a)>=2 and a[1] in states:
            states[ident]=states[a[1]]
        elif op=="OpLoad" and len(a)>=2:
            ptr=a[1]
            if ptr in states and states[ptr][0] in ("dynamic_vector","dynamic_scalar"):
                c["spv_authentic_CB_dynamic_vec_pointer_OpLoad_occurrences"]+=1
                loaded_roots.add(states[ptr][1])
                loaded_pointers.add(ptr)
        elif op in ("OpSelect","OpPhi") and any(x in states for x in a):
            c["spv_unproven_select_phi_aliases"]+=1
    c["spv_authentic_CB_dynamic_vec_global_roots_with_loads"]=len(loaded_roots)
    # This is chain vs used-pointer occurrence, not exact source operand parity.
    c["spv_authentic_CB_dynamic_vec_access_chains_without_load"]=max(
        0,created-len(loaded_pointers))
    ans=dict(c)
    ans["dynamic_source_CB_operand_to_SPV_dynamic_expression_parity_proven"]=False
    ans["SPV_dynamic_index_runtime_bounds_proven"]=False
    ans["original_Shader48_Material_CB_semantics_proven"]=False
    return ans

def audit(stage):
    programs,passes=source_pair(stage)
    if len(programs)!=1656 or len(passes)!=7:
        raise ValueError("GFX063_ORIGINAL_PROGRAM_TABLE_DRIFT")
    cache={}
    def inspect(meta,kind):
        idx=meta.get("m_BlobIndex") if isinstance(meta,dict) else None
        typ=meta.get("m_GpuProgramType") if isinstance(meta,dict) else None
        if type(idx)!=int or type(typ)!=int or not 0<=idx<len(programs):
            raise ValueError("GFX063_PRIVATE_PROGRAM_ID_BAD")
        key=(idx,typ,kind)
        if key not in cache:
            original=code_from_ref(meta,programs,kind)
            shdr=source_shader_chunk(original)
            slots,cb=private_source_slots(shdr)
            pairs,stats=original_sample_pairs(shdr,slots["resource"],slots["sampler"])
            cache[key]={"decl":canonical_private_declaration_profile(slots,cb),
                        "sampling":private_signature(pairs),
                        "unresolved":stats["source_original_unresolved_dynamic_t_s"],
                        "shdr":shdr,"dxbc":original,"cb":cb}
        return cache[key]
    selected=[];safe_profiles=None
    for start in (0,24,48,72,96,120,144):
        part,counts,_=select_pass_scoped_joint_classes(passes,inspect,budget=24,start=start)
        required={"original_exact_pairs_scanned":524,
                  "global_declaration_classes_ignoring_pass":110,
                  "pass_scoped_declaration_classes":132,
                  "global_sample_use_classes_ignoring_pass":58,
                  "pass_scoped_sample_use_classes":80,
                  "pass_scoped_joint_declaration_and_sample_use_classes":157}
        if any(counts.get(key)!=value for key,value in required.items()):
            raise ValueError("GFX063_PRIVATE_SOURCE_CLASS_CENSUS_DRIFT")
        if counts["batch_end_index_exclusive"]!=min(start+24,157):
            raise ValueError("GFX063_PRIVATE_REPRESENTATIVE_ORDER_DRIFT")
        selected.extend(part)
        safe_profiles=required
    if len(cache)!=936 or len(selected)!=157:
        raise ValueError("GFX063_SOURCE_REPRESENTATIVE_ACCOUNTING_DRIFT")
    totals=Counter()
    best_per_pass={}
    stage_count=0
    for row,vm,fm in selected:
        stage_count+=2
        private_case_score=0
        for meta,kind in ((vm,"Vertex"),(fm,"Pixel")):
            s=inspect(meta,kind)
            present=original_cb_source_dynamic_taxonomy(s["shdr"],s["cb"])
            _,legacy=scan_known_dxbc_cb_operands(s["shdr"],s["cb"])
            if (present["source_CB_unresolved_dynamic_or_extended_occurrences"] !=
                legacy["source_dynamic_or_extended_CB_accesses_in_covered_arithmetic"]
                or present["source_CB_static_unmodified_operand_occurrences"] !=
                legacy["source_static_CB_vector_accesses_in_covered_arithmetic"]
                or present["source_arithmetic_parse_rejected"]):
                raise ValueError("GFX063_INDEPENDENT_LEGACY_DYNAMIC_COUNT_DISAGREEMENT")
            private_case_score+=present["source_CB_unresolved_dynamic_or_extended_occurrences"]
            for key,value in present.items():
                if type(value) is int:totals[key]+=value
        key=(row["subshader"],row["pass"])
        if key not in best_per_pass or private_case_score>best_per_pass[key][0]:
            best_per_pass[key]=(private_case_score,vm,fm)
    if stage_count!=314 or len(best_per_pass)!=7:
        raise ValueError("GFX063_PRIVATE_CLASS_STAGE_OR_PASS_COUNT_DRIFT")
    if totals["source_CB_unresolved_dynamic_or_extended_occurrences"]!=1190:
        raise ValueError("GFX063_1190_LEGACY_UNRESOLVED_SOURCE_COUNT_DRIFT")
    if sum(totals[x] for x in CATEGORIES)!=1190:
        raise ValueError("GFX063_TAXONOMY_CATEGORY_PARTITION_DRIFT")
    spv_totals=Counter()
    spv_original_unresolved_count=0
    for _,vm,fm in best_per_pass.values():
        vs=inspect(vm,"Vertex");fs=inspect(fm,"Pixel")
        with tempfile.TemporaryDirectory(prefix="gfxlab063-private-") as tmp:
            folder=Path(tmp)
            output=translate_pair(vs["dxbc"],fs["dxbc"],folder)
            for kind,original in (("vertex",vs),("fragment",fs)):
                if not output[kind]["vulkan11_spirv_validation_success"]:
                    raise ValueError("GFX063_REAL_SOURCE_VULKAN_SPV_VALIDATION_FAILED")
                spv_totals["source_stage_instances_vulkan11_SPV_validated"]+=1
                spv=folder/(kind+".spv")
                ok,data=run_quiet(["spirv-cross",str(spv),"--reflect"])
                if not ok:raise ValueError("GFX063_SPV_REFLECTION_FAILED")
                reflection=json.loads(data.decode("utf8","strict"))
                if not isinstance(reflection,dict):
                    raise ValueError("GFX063_SPV_REFLECTION_NOT_OBJECT")
                ok,dis=run_quiet(["spirv-dis","--raw-id","--no-color",str(spv)])
                if not ok:raise ValueError("GFX063_SPV_DISASSEMBLY_FAILED")
                authentic,layout=private_authenticated_ubo_layouts(dis,original["cb"],reflection)
                source_global=global_cb_evidence(dis,original["cb"],reflection.get("ubos",[]))
                if (len(authentic)!=len(original["cb"])
                    or layout["UBO_globals_strict_single_vec4_array_member_layout"]!=len(original["cb"])
                    or not source_global["all_original_CB_registers_symbolically_correlated_with_actual_spv_UBO_globals"]):
                    raise ValueError("GFX063_REAL_SOURCE_CB_GLOBAL_OR_LAYOUT_NOT_AUTHENTICATED")
                private_tax=original_cb_source_dynamic_taxonomy(original["shdr"],original["cb"])
                spv_original_unresolved_count+=private_tax["source_CB_unresolved_dynamic_or_extended_occurrences"]
                observed=spv_authenticated_dynamic_cb_pointer_loads(dis,authentic)
                for k,v in observed.items():
                    if type(v) is int:spv_totals[k]+=v
                spv_totals["source_stage_instances_real_authenticated_CB_layout"]+=1
    if spv_totals["source_stage_instances_vulkan11_SPV_validated"]!=14:
        raise ValueError("GFX063_SPV_PILOT_ACCOUNTING_INVALID")
    result={
      "experiment":"GFX-MULTI-063",
      "original_zip2_sha":ZIP2_SHA,
      "evidence_level":"ORIGINAL_SOURCE_157_CLASS_REPRESENTATIVE_DXBC_CB_DYNAMIC_SHAPE_CENSUS_AND_SEVEN_PASS_REAL_SPV_DYNAMIC_LOAD_DIAGNOSTIC_CPU_ONLY",
      "original_source_all_exact_pairs_rechecked":safe_profiles["original_exact_pairs_scanned"],
      "source_compiled_stage_programs_inspected":len(cache),
      "original_pass_joint_declaration_and_sampling_classes":157,
      "source_class_representatives_classified":len(selected),
      "source_stage_instances_scanned":stage_count,
      "source_taxonomy_covered_opcode_family_count":len(KNOWN_ARITHMETIC_ARITY),
      "source_taxonomy_safe_aggregate_counts":dict(totals),
      "seven_original_pass_diagnostic_pair_count":len(best_per_pass),
      "seven_original_pass_diagnostic_stage_instances":spv_totals["source_stage_instances_vulkan11_SPV_validated"],
      "source_dynamic_CB_unresolved_occurrences_in_7_diagnostic_pairs":spv_original_unresolved_count,
      "SPV_authenticated_dynamic_CB_load_diagnostic_safe_counts":dict(spv_totals),
      "prior_1190_unresolved_dynamic_source_operands_now_proven_per_operand_equivalent":0,
      "source_CB_dynamic_index_operand_to_SPV_expression_semantic_equivalence_proven":False,
      "source_arithmetic_opcode_subset_is_complete_DXBC_CB_coverage":False,
      "all_524_individual_variant_shader_programs_SPV_translated_in_this_experiment":False,
      "Material_original_property_to_t_s_b_or_CB_member_mapping_proven":False,
      "GPU_Adreno_original_shader_run_proven":False,
      "originalShaderRestored":False,"phase_closed":False,
      "private_original_shader_register_CB_layout_source_or_SPV_exported":False,
    }
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip2",type=Path,required=True)
    p.add_argument("--stage",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(stage_originals(a.zip2,a.stage))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("GFX063_SAFE_ORIGINAL_CB_DYNAMIC_SHAPES_AND_SPV_DYNAMIC_LOADS "+json.dumps(result,sort_keys=True))
if __name__=="__main__":main()
