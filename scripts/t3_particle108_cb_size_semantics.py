#!/usr/bin/env python3
"""Verify SM4.0–5.0 DXBC DCL_CONSTANT_BUFFER second index is size in 16-byte vectors.

Source: Microsoft DirectX-Headers D3D12TokenizedProgramFormat.hpp.
Index 0 is cb register, index 1 is vector count; zero means UNKNOWN size.
SM5.1 switches to a 3-index resource range; reject it, never guess.
Original bytecode, registers, size values and identities stay process-private.
"""
import argparse,json,struct
from pathlib import Path
from collections import Counter,defaultdict
from scripts import t3_particle108_original_dxbc_operand_bindings as bind
from scripts import t3_particle108_original_dxbc_declarations as dec
from scripts import t3_particle108_original_dxbc_rdef as native

STATUS="T3_ORIGINAL_SM4_SM5_CB_DECL_SIZE16_CLASSIFIED"
def private_cb_declarations(dx,stage):
    full=bind._private_stage_layout(dx,stage)  # validates all DCL operand bounds
    code=dec.shader_chunk(dx)
    words=struct.unpack("<"+"I"*(len(code)//4),code)
    major,minor=(words[0]>>4)&15,words[0]&15
    if not ((major==4 and minor in (0,1)) or (major==5 and minor==0)):
        raise ValueError("DXBC_CB_UNSUPPORTED_SHADER_MODEL")
    found=[]
    i=2
    while i<len(words):
        op=words[i]&0x7ff
        size=words[i+1] if op==dec.CUSTOMDATA else (words[i]>>24)&127
        if op==89:
            family,_,index=bind._private_parse_decl_operand(words[i:i+size],89)
            if family!="cbuffer" or len(index)!=2:
                raise ValueError("DXBC_CB_EXPECT_TWO_INDEX_DECL")
            found.append((index[0],index[1],(words[i]>>11)&1))
        i+=size
    if len(found)!=sum(x[0]=="cbuffer" for x in full):
        raise ValueError("DXBC_CB_DCL_CARDINALITY_MISMATCH")
    return (major,minor),tuple(found)

def classify_four_pairs(pairs):
    if type(pairs)!=list or len(pairs)!=4 or any(type(x)!=tuple or len(x)!=2 for x in pairs):
        raise ValueError("ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED")
    c=Counter()
    for stage,label in ((1,"VS"),(0,"PS")):
        signatures={"full":[],"slot":[],"size":[]}
        occurrences=Counter()
        sizes=defaultdict(set)
        for pair in pairs:
            version,rows=private_cb_declarations(pair[0 if stage==1 else 1],stage)
            c["source_original_SM_"+str(version[0])+"_"+str(version[1])+"_stages"]+=1
            c["original_CB_declaration_stage_programs"]+=1
            c["original_CB_16byte_vector_size_declarations"]+=len(rows)
            c["original_CB_zero_unknown_size_declarations"]+=sum(sz==0 for _,sz,_ in rows)
            c["original_CB_nonzero_known_size_declarations"]+=sum(sz!=0 for _,sz,_ in rows)
            c["original_CB_dynamic_access_declarations"]+=sum(access==1 for _,_,access in rows)
            signatures["full"].append(tuple(sorted(rows)))
            signatures["slot"].append(tuple(sorted(slot for slot,_,_ in rows)))
            signatures["size"].append(tuple(sorted(sz for _,sz,_ in rows)))
            for slot,sz,_ in rows:
                occurrences[slot]+=1
                sizes[slot].add(sz)
        for key,variants in signatures.items():
            c["original_"+label+"_CB_"+key+"_profile_distinct"]=len(set(variants))
        c["original_"+label+"_CB_slots_repeated_across_variants"]=sum(v>1 for v in occurrences.values())
        c["original_"+label+"_CB_slots_with_size_change"]=sum(
            occurrences[slot]>1 and len(v)>1 for slot,v in sizes.items())
    if c["original_CB_declaration_stage_programs"]!=8:
        raise ValueError("DXBC_CB_WRONG_STAGE_COUNT")
    return {"schema_version":1,"status":STATUS,"counts":dict(sorted(c.items())),
      "CB_second_index_semantics":"16_BYTE_VECTOR_COUNT",
      "CB_zero_size_means_UNKNOWN":True,
      "private_CB_register_ids_and_sizes_published":False,
      "original_SPIRV_descriptor_parity_or_pixel_fix_proven":False}

def probe(root,manifest):
    import UnityPy
    ids={}
    evidence=native.identity.source.load_original(root,manifest,private_particle_slot_counts=ids)
    owner,pid=native.identity.select(ids,evidence)
    path=root/"Raft_Data"/owner
    if path.is_symlink() or native.fingerprint(path)!=native.SHADER_OWNERS[owner]:
        raise ValueError("ORIGINAL_OWNER_SHA")
    objs=[o for o in UnityPy.load(str(path)).file.objects.values() if o.path_id==pid]
    if len(objs)!=1 or objs[0].type.name!="Shader":
        raise ValueError("ORIGINAL_SHADER_IDENTITY")
    tree=objs[0].read_typetree()
    _,shape=native.serialize_properties(tree["m_ParsedForm"])
    if shape["original_authored_property_count"]!=13 or shape["original_authored_texture_property_count"]!=2:
        raise ValueError("ORIGINAL_SHADER_SCOPE")
    ps=[native.records(s) for plat,s in native.decoded_platforms(tree) if plat==4]
    if len(ps)!=1:raise ValueError("ORIGINAL_D3D11_PROGRAM_TABLE")
    basis=native.identity.inspect(tree["m_ParsedForm"],ps[0])
    if (basis.get("status")!=native.identity.STATUS or
        basis.get("matched_vertex_fragment_permutation_pairs")!=4 or
        basis.get("original_D3D11_program_table_records")!=16):
        raise ValueError("ORIGINAL_FOUR_PAIRS_CHANGED")
    report=classify_four_pairs(native.stage.exact_four_pairs(tree["m_ParsedForm"],ps[0]))
    report.update(source_original_four_owner_SHA_authenticated=True,
        source_original_six_scenes_SHA_authenticated=True,source_original_keyword_pairs=4,
        source_particle_renderer_material_slots=108)
    return report

SAFE_REASONS={
    "DXBC_CB_UNSUPPORTED_SHADER_MODEL":"UNSUPPORTED_SHADER_MODEL",
    "DXBC_CB_EXPECT_TWO_INDEX_DECL":"CB_NOT_2D",
    "DXBC_CB_DCL_CARDINALITY_MISMATCH":"CB_COUNT_MISMATCH",
    "ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED":"WRONG_PAIR_SCOPE",
}
def main(argv=None):
    p=argparse.ArgumentParser()
    for x in ("original","manifest","out"):p.add_argument("--"+x,type=Path,required=True)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()):
        raise ValueError("unsafe_original_report_path")
    try:report=probe(a.original,a.manifest)
    except Exception as exc:
        report={"status":"INCONCLUSIVE","schema_version":1,
          "safe_reason":SAFE_REASONS.get(str(exc),"UNCLASSIFIED_SOURCE"),
          "private_CB_register_ids_and_sizes_published":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("T3_CB_DECL_SIZE_SAFE="+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2
if __name__=="__main__":raise SystemExit(main())
