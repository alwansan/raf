"""Offline private bundle-copy program patch and direct native Vulkan dispatch.

Never changes the Unity platform tag or attempts to load a rejected bundle.
A successful result means re-read serialized program execution, not Unity bundle admission.
"""
import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path
from tools.gt_fft_compute_bundle import audit as bundle
from tools.gt_fft_half_image_format import audit as half
from scripts.probe_fft_variant_table import EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT

need=half.need
sha=half.sha
digest=bundle.digest
SLOTS=bundle.SLOTS

def one_word_offsets(data,patched,word):
    need(len(data)==len(patched) and 0<=word<len(data)//4,"one_word_extent")
    changed=[i for i in range(len(data)) if data[i]!=patched[i]]
    need(bool(changed) and all(word*4<=i<word*4+4 for i in changed),"one_word_only")
    return changed

def unique_replace(data,old,new):
    need(len(old)==len(new) and old!=new and data.count(old)==1,"unique_payload")
    return data.replace(old,new,1)

def object_inventory(path,slots,index):
    import UnityPy
    env=UnityPy.load(str(path))
    objs=list(env.objects)
    cs=[o for o in objs if o.type.name=="ComputeShader"]
    need(len(cs)==1,"class72_population")
    obj=cs[0];tree=obj.read_typetree()
    variants=tree["variants"];need(len(variants)==1,"variant_population")
    kernels=variants[0]["kernels"];need(len(kernels)==len(slots),"kernel_population")
    modules={}
    for slot,k in zip(slots,kernels,strict=True):
        need(k["name"]==(f"RaftFftSlot{slot:02d}" if index==0 else "main"),"kernel_name")
        need(not k["globalKeywords"] and not k["localKeywords"] and len(k["variantMap"])==1,"variant_identity")
        e=k["variantMap"][0][1]
        group=EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[slot]
        need(e["threadGroupSize"]==[group,1,1],"group_identity")
        raw=bytes(e["code"]);need(raw[:4]==b"\x03\x02\x23\x07","raw_spirv_only")
        modules[slot]=raw
    other=sorted((int(o.path_id),o.type.name,digest(o.get_raw_data())) for o in objs if o is not obj)
    return int(obj.path_id),obj.get_raw_data(),other,modules

def patch_bundles(private,work,fmt,build,selected=SLOTS,pins=None):
    if pins is None:pins=half.PINS[fmt]
    need(len(selected)==4 and len(set(selected))==4 and set(pins)=={f'{v}-{s}' for s in selected for v in ('indexed','standalone')},"selected_pins")
    before_dir=private/"compiled-bundles";after_dir=work/"patched-bundles";after_dir.mkdir()
    modules={};rows=[]
    for index in range(5):
        path=before_dir/f"fft-{index}"
        need(path.is_file() and not path.is_symlink() and sha(path)==build["bundle_sha256"][index],"bundle_commitment")
        raw=path.read_bytes();need(0<len(raw)<=64*1024*1024 and raw.startswith(b"UnityFS\0"),"bundle_extent")
        slots=list(range(20)) if index==0 else [selected[index-1]]
        pid,original,other,old=object_inventory(path,slots,index)
        expected_obj=original;expected_archive=raw;desired=dict(old);changes=[]
        for slot in slots:
            group=EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[slot]
            prior=bundle.validate_module(old[slot],work,group)
            need(next(x for x in prior["images"] if x["sampled_enum"]==2)["format_enum"]==half.ENUMS[fmt][0],"before_storage")
            if slot not in selected:continue
            label=("indexed" if index==0 else "standalone")+f"-{slot}"
            need(prior["sha256"]==pins[label],"before_live_pin")
            patched,word=half.patch_image_format(old[slot],fmt)
            offsets=one_word_offsets(old[slot],patched,word)
            expected_obj=unique_replace(expected_obj,old[slot],patched)
            expected_archive=unique_replace(expected_archive,old[slot],patched)
            desired[slot]=patched
            changes.append(dict(slot=slot,label=label,word=word,changed_bytes=len(offsets),before_sha=prior["sha256"],after_sha=digest(patched)))
        dst=after_dir/path.name;dst.write_bytes(expected_archive)
        p2,actual,other2,new=object_inventory(dst,slots,index)
        need(p2==pid and actual==expected_obj and other2==other and new==desired,"serialized_roundtrip")
        need(sha(path)==build["bundle_sha256"][index],"source_bundle_unchanged")
        changed=sum(a!=b for a,b in zip(raw,expected_archive,strict=True))
        need(changed==sum(c["changed_bytes"] for c in changes),"archive_diff")
        for slot in slots:
            group=EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[slot]
            after=bundle.validate_module(new[slot],work,group)
            if slot in selected:
                label=("indexed" if index==0 else "standalone")+f"-{slot}"
                need(next(x for x in after["images"] if x["sampled_enum"]==2)["format_enum"]==half.ENUMS[fmt][1],"after_storage")
                target=work/(label+".spv");target.write_bytes(new[slot]);modules[label]=target
            else:need(new[slot]==old[slot],"unselected_program_unchanged")
        rows.append(dict(index=index,original_sha=sha(path),patched_sha=sha(dst),bytes=len(raw),object_path_id=pid,
                         serialized_programs=len(slots),other_objects_unchanged=len(other),changed_bytes=changed,changes=changes))
    need(len(modules)==8 and sum(x["serialized_programs"] for x in rows)==24,"patch_population")
    return rows,modules

def resource_contract(module,source,table,target):
    p=subprocess.run(["spirv-cross",str(module),"--reflect"],capture_output=True,timeout=30)
    need(p.returncode==0,"reflection_process")
    j=json.loads(p.stdout);entries=j["entryPoints"]
    need(len(entries)==1 and entries[0]["mode"]=="comp" and re.fullmatch(r"[A-Za-z0-9_]{1,128}",entries[0]["name"]) is not None,"entrypoint")
    ins=j.get("separate_images",[]);outs=j.get("images",[])
    need(len(ins)==2 and len(outs)==1 and {x["name"] for x in ins}=={source,table} and outs[0]["name"]==target,"reflected_resource_names")
    names={x["name"]:x for x in ins+outs}
    need(all(names[k]["set"]==0 for k in (source,table,target)),"descriptor_set")
    bindings=[names[k]["binding"] for k in (source,table,target)]
    need(sorted(bindings)==[0,1,2],"descriptor_bindings")
    return entries[0]["name"],bindings

def render_host(text,contracts,size=512,stages=8):
    # Four unchanged SPIR-V programs with reflected entrypoints and bindings.
    need(len(contracts)==4 and len({x[1][2] for x in contracts})==1,"storage_layout")
    storage=contracts[0][1][2]
    s=half.render_host(text);r=half.replace
    if size!=512:
        from tools.gt_fft_size_matrix import audit as matrix
        need(matrix.dimensions(size)[0]==stages,"size_stages")
        s=r(s,"dispatchGroupY==512",f"dispatchGroupY=={size}")
        s=r(s,"require(w==512 && h==512",f"require(w=={size} && h=={size}")
        s=r(s,"size_t(w)*(i?8:h)",f"size_t(w)*(i?{stages}:h)")
        s=r(s,"uint32_t texH=t==1?8:h;",f"uint32_t texH=t==1?{stages}:h;")
    s=r(s,"enabled.shaderStorageImageWriteWithoutFormat=VK_TRUE;",
        'enabled.shaderStorageImageWriteWithoutFormat=VK_TRUE;\n    require(features.shaderStorageImageExtendedFormats==VK_TRUE,"Extended storage format");\n    enabled.shaderStorageImageExtendedFormats=VK_TRUE;')
    s=r(s,"bindings[i].descriptorType=i<2?VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE:",f"bindings[i].descriptorType=i!={storage}?VK_DESCRIPTOR_TYPE_SAMPLED_IMAGE:")
    sources=",".join(str(c[1][0]) for c in contracts)
    tables=",".join(str(c[1][1]) for c in contracts)
    names=",".join('"'+c[0]+'"' for c in contracts)
    s=r(s,"    for(int set=0;set<4;set++)for(int binding=0;binding<3;binding++){",
        "    const std::array<int,4> srcBindings={"+sources+"}, tableBindings={"+tables+"};\n    for(int set=0;set<4;set++)for(int binding=0;binding<3;binding++){")
    s=r(s,"const int textureIndex=(binding==0?passSource[set]:\n                               (binding==1?1:passTarget[set]));",
        "const int textureIndex=(binding==srcBindings[set]?passSource[set]:\n                               (binding==tableBindings[set]?1:passTarget[set]));")
    s=r(s,'stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;stage.module=shaderModules[i];stage.pName="main";',
        'const std::array<const char*,4> entries={'+names+'};\n        stage.stage=VK_SHADER_STAGE_COMPUTE_BIT;stage.module=shaderModules[i];stage.pName=entries[i];')
    return s

def execute(private,work,fmt,stage,modules):
    cfg=json.loads((private/"config.json").read_text());rows={x["slot"]:x for x in cfg["rows"]}
    table=(private/"table-native.raw").read_bytes()
    need(digest(table)==stage["table_native_sha"],"table_identity")
    for name,pin in stage["oracle_commitments"].items():need(sha(private/name)==pin,"oracle_commitment")
    results=[]
    for slot in (6,16):
        # Native host order is first indexed, first standalone, second indexed, second standalone.
        labels=[f"{v}-{s}" for s in (slot,slot+1) for v in ("indexed","standalone")]
        contracts=[]
        for label in labels:
            variant,num=label.split("-");row=rows[int(num)]
            props=("_SourceTex","_ButterflyTex","_TargetTex") if variant=="indexed" else (row["source_property"],row["butterfly_property"],row["target_property"])
            contracts.append(resource_contract(modules[label],*props))
        host=work/f"host-{slot}.cpp";runner=work/f"host-{slot}"
        host.write_text(render_host(Path("scripts/a1_fft_two_pass_vulkan.cpp").read_text(),contracts))
        compile_result=subprocess.run(["g++","-std=c++17","-O2",str(host),"-lvulkan","-o",str(runner)],capture_output=True,timeout=90)
        need(compile_result.returncode==0,"native_host_compile")
        for mode in ("signed","zero"):
            source=(private/f"source-{mode}.rgba32f").read_bytes()
            captures=half.capture(runner,[modules[k] for k in labels],work/f"case-{slot}-{mode}",source,table,fmt)
            ref=[(private/f"cpu-{slot}-{mode}-p{p}.raw").read_bytes() for p in (0,1)]
            checks=[half.compare(raw,ref[i%2],fmt) for i,raw in enumerate(captures)]
            results.append(dict(slot=slot,mode=mode,bindings=[c[1] for c in contracts],outputs=checks))
    return results

def main():
    p=argparse.ArgumentParser()
    for k in ("private","stage","out"):p.add_argument("--"+k,type=Path,required=True)
    p.add_argument("--run-id",required=True);p.add_argument("--format",choices=half.FORMATS,required=True);a=p.parse_args()
    result=dict(status="INCONCLUSIVE",format=a.format,patched_archive_roundtrip=False,direct_native_dispatch_verified=False,
                unity_bundle_loaded=False,platform_check_modified=False,runtime_replacement=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)
    try:
        s=json.loads(a.stage.read_text());need(s["status"]==bundle.STAGED and s["format"]==a.format,"stage")
        b=bundle.build_receipt(a.private,a.run_id)
        need(b["config_sha256"]==s["private_config_sha256"]==sha(a.private/"config.json"),"config_identity")
        with tempfile.TemporaryDirectory(prefix="gt-private-patched-bundle-",dir=a.private.parent) as tmp:
            root=Path(tmp)
            records,modules=patch_bundles(a.private,root,a.format,b)
            result.update(patched_archive_roundtrip=True,serialized_modules=24,one_word_modules=8,unchanged_modules=16,records=records)
            result["numeric_cases"]=execute(a.private,root,a.format,s,modules)
            exact=sum(o["raw_bit_different"]==0 and o["nonfinite_lanes"]==0 and o["written_pixels"]==half.n.COUNT for c in result["numeric_cases"] for o in c["outputs"])
            result["exact_outputs"]=exact
            need(exact==16,"numeric_parity")
            result.update(status="OBSERVED_SERIALIZED_COPY_NATIVE_EXECUTION",direct_native_dispatch_verified=True)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
    half.dump(a.out,result);print("GT_FFT_SERIALIZED_COPY "+json.dumps(result,sort_keys=True))
    return 0 if result["direct_native_dispatch_verified"] else 2

if __name__=="__main__":raise SystemExit(main())
