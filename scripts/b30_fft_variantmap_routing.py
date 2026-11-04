"""B30: source-pinned FFT variantMap discriminator collision proof.

Compiled slots and keyword/map tags are NOT Unity runtime FindKernel IDs.
Output only aggregate collision counts; never proprietary program data.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

GROUPS = (64,64,128,128,256,256,512,512,1024,1024)*2

def _keywords(value):
    if not isinstance(value, (list,tuple)) or len(value)>64:
        raise ValueError("Invalid original keyword bundle")
    out=[]
    for v in value:
        if type(v) is str and 0<len(v)<=128: out.append(("s",v))
        elif type(v) is int and 0<=v<=0xffffffff: out.append(("i",v))
        else: raise ValueError("Invalid original keyword element")
    if len(out)!=len(set(out)): raise ValueError("Duplicate original keywords")
    return tuple(out)

def _tag_group(vm):
    if not isinstance(vm,list) or len(vm)!=1:
        raise ValueError("Original variantMap cardinality drift")
    row=vm[0]
    if not isinstance(row,tuple) or len(row)!=2 or type(row[0]) is not int:
        raise ValueError("Invalid variantMap tuple")
    tag,items=row
    if not 0<=tag<2**31 or not isinstance(items,dict) or len(items)>32:
        raise ValueError("Invalid variantMap header or fields")
    group=[]; binaries=0
    for key,value in items.items():
        if not isinstance(key,str) or len(key)>128:
            raise ValueError("Unsafe private field key")
        if isinstance(value,(list,tuple)) and len(value)==3 and all(type(v) is int and v>0 for v in value):
            group.append(tuple(value))
        elif isinstance(value,(list,tuple)) and len(value)>32 and all(type(v) is int and 0<=v<=255 for v in value):
            if bytes(value[:4])==b"DXBC": binaries+=1
    if len(group)!=1 or binaries!=1:
        raise ValueError("Ambiguous original typed workgroup or DXBC")
    return tag,group[0]

def summarize_routing(tree):
    variants=tree.get("variants") if isinstance(tree,dict) else None
    if not isinstance(variants,list) or len(variants)!=1 or not isinstance(variants[0],dict):
        raise ValueError("Original variant sets drift")
    rows=variants[0].get("kernels")
    if not isinstance(rows,list) or len(rows)!=20:
        raise ValueError("Original compiled slot count drift")
    names=[]; headers=[]; keywords=[]; combined=[]
    for i,row in enumerate(rows):
        if not isinstance(row,dict) or not isinstance(row.get("name"),str) or not 0<len(row["name"])<=256:
            raise ValueError("Invalid private name")
        names.append(hashlib.sha256(row["name"].encode()).hexdigest())
        tag,group=_tag_group(row.get("variantMap"))
        if group!=(GROUPS[i],1,1):
            raise ValueError("Original compiled workgroup order drift")
        keys=(_keywords(row.get("globalKeywords")),_keywords(row.get("localKeywords")))
        headers.append(tag); keywords.append(keys); combined.append((tag,keys))
    if len(set(names))!=1:
        raise ValueError("Original one-name alias drift")
    h=Counter(headers); k=Counter(keywords); c=Counter(combined)
    return {
      "original_compiled_slots":20,
      "original_distinct_kernel_names":1,
      "original_variant_map_header_unique_values":len(h),
      "original_variant_map_header_alias_sizes":sorted(h.values(),reverse=True),
      "original_keyword_bundle_unique_combinations":len(k),
      "original_keyword_bundle_alias_sizes":sorted(k.values(),reverse=True),
      "header_and_keyword_combined_unique_combinations":len(c),
      "header_and_keyword_collision_sizes":sorted(c.values(),reverse=True),
      "source_candidate_adjacent_pairs_with_same_discriminator":sum(combined[i]==combined[i+1] for i in range(0,20,2)),
      "source_candidate_cross_bank_positions_with_same_discriminator":sum(combined[i]==combined[i+10] for i in range(10)),
      "opaque_map_header_meaning_inferred":False,
      "keyword_identity_is_runtime_selector_verified":False,
      "runtime_findkernel_id_to_compiled_slot_verified":False,
      "source_or_game_assets_modified":False,
      "private_kernel_names_keywords_or_bytecode_published":False,
      "unity_compiled_or_android_device_verified":False,
    }

def inspect(root):
    from scripts.probe_authentic_fft_dxbc_translation import OWNER,PATH_ID,ORIGINAL_OBJECT_SHA256
    from scripts.probe_fft_variant_table import correlate_original_variant_bytecode,EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT
    from scripts.probe_original_compute_containers import scan_blob
    from scripts.verify_targeted_lfs_compute_sources import EXPECTED,verify_sources
    verified=verify_sources(root,expected={OWNER:EXPECTED[OWNER]})
    if verified.get("authenticated_owners")!=1: raise ValueError("Original asset SHA verification absent")
    import UnityPy
    env=UnityPy.load(str(Path(root)/OWNER))
    objects=[o for o in env.file.objects.values() if o.type.name=="ComputeShader" and int(o.path_id)==PATH_ID]
    if len(objects)!=1: raise ValueError("Original FFT ComputeShader identity absent")
    raw=objects[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest()!=ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original ComputeShader object SHA changed")
    tree=objects[0].read_typetree()
    result=summarize_routing(tree)
    compiled=correlate_original_variant_bytecode(tree,scan_blob(raw)["valid_dxbc_containers"],EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT)
    if compiled.get("authentic_compiled_variants_verified_in_original_order")!=20 or compiled.get("original_compiled_program_order_sha256_correlated") is not True:
        raise ValueError("Original DXBC compiled order not authenticated")
    return {"source_pin":"15964ea8f246b6e076ce26b60931ee2e1a9a2385",
            "original_owner_sha256":EXPECTED[OWNER][1],"original_object_sha256":ORIGINAL_OBJECT_SHA256,
            "same_slot_original_dxbc_sha_verified":True,**result}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",required=True,type=Path)
    try: report=inspect(p.parse_args().source)
    except (ValueError,KeyError,TypeError,OSError) as e:
        safe_reasons={"Original variantMap cardinality drift","Invalid variantMap tuple","Invalid variantMap header or fields","Invalid original keyword bundle","Invalid original keyword element","Duplicate original keywords","Invalid private name","Invalid private field key","Ambiguous original typed workgroup or DXBC","Original compiled workgroup order drift","Original one-name alias drift","Original variant sets drift","Original compiled slot count drift","Original asset SHA verification absent","Original FFT ComputeShader identity absent","Original ComputeShader object SHA changed","Original DXBC compiled order not authenticated"}
        reason=str(e) if str(e) in safe_reasons else "unclassified_authenticity_or_structure"
        print("RAFT_B30_FFT_VARIANTMAP "+json.dumps({"status":"REJECTED","reason":reason,"runtime_findkernel_id_to_compiled_slot_verified":False},sort_keys=True))
        return 2
    print("RAFT_B30_FFT_VARIANTMAP "+json.dumps(report,sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
