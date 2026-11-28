"""Private serialized compute-bundle admission; no player or production mutation."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile
from tools.gt_fft_half_image_format import audit as half
from tools.gt_fft_typed_dxc import audit as typed
from tools.gt_fft_live_module import audit as live
from tools.gt_fft_compiler_directive import audit as directive
from scripts.probe_directx_shader_bridge import inspect
from scripts.probe_fft_spirv_images import image_resource_contracts
from scripts.probe_fft_variant_table import EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT

FORMATS={**half.FORMATS,"RGFloat":typed.FORMATS["RGFloat"]}
STATUS="OBSERVED_COMPUTE_BUNDLE_ADMISSION"
STAGED="STAGED_COMPUTE_BUNDLE_ADMISSION"
need=half.need
sha=half.sha
dump=half.dump
SLOTS=(6,7,16,17)
MAGICS=(b"\x03\x02\x23\x07",b"LOMS")

def digest(data):return hashlib.sha256(data).hexdigest()

def byte_leaves(value,path=(),depth=0):
    need(depth<=12,"serialized_depth")
    if isinstance(value,(bytes,bytearray)):
        if len(value)>=20:
            need(len(value)<=1048576,"serialized_byte_extent")
            yield path,bytes(value)
    elif isinstance(value,(list,tuple)):
        need(len(value)<=1048576,"serialized_sequence_extent")
        if len(value)>=20 and all(type(x) is int and 0<=x<=255 for x in value):
            yield path,bytes(value)
        else:
            for i,x in enumerate(value):yield from byte_leaves(x,(*path,i),depth+1)
    elif isinstance(value,dict):
        need(len(value)<=128 and all(type(k) is str and re.fullmatch(r"[A-Za-z0-9_ -]{1,96}",k) for k in value),"serialized_fields")
        for k,v in value.items():yield from byte_leaves(v,(*path,k),depth+1)

def validate_module(data,work,group):
    p=inspect(data)
    need(p["container"]=="SPIR-V" and p["entrypoint_execution_models"]=={5:1} and p["declared_local_workgroup_sizes"]==[[group,1,1]],"serialized_module_group")
    file=work/"module.spv";file.write_bytes(data)
    val=subprocess.run(["spirv-val","--target-env","vulkan1.1",str(file)],capture_output=True,timeout=30)
    need(val.returncode==0,"serialized_module_validator")
    images=image_resource_contracts(data)["typed_image_declarations"]
    need(len(images)==3 and sum(x["sampled_enum"]==1 for x in images)==2 and sum(x["sampled_enum"]==2 for x in images)==1,"serialized_image_abi")
    return dict(sha256=digest(data),bytes=len(data),validator_exit=0,local_size=[group,1,1],images=images,generator=directive.generator(file))

def decode_payload(raw,decoder,work,group):
    # Only bounded raw or SMOL-V payloads. Small headers/alignment are
    # recorded rather than guessed to be part of the shader program.
    found=[]
    for magic in MAGICS:
        at=raw.find(magic,0,min(len(raw),260))
        if at<0:continue
        for pad in range(4):
            if pad and raw[-pad:]!=b"\0"*pad:continue
            payload=raw[at:len(raw)-pad if pad else len(raw)]
            if len(payload)<20:continue
            if magic==MAGICS[0]:
                decoded=payload;encoding="raw_spirv"
            else:
                try:
                    r=subprocess.run([str(decoder)],input=payload,capture_output=True,timeout=15)
                    if r.returncode!=0:continue
                    decoded=r.stdout;encoding="smolv"
                except (OSError,subprocess.TimeoutExpired):continue
            try:module=validate_module(decoded,work,group)
            except (ValueError,struct.error,KeyError):continue
            found.append((dict(encoding=encoding,prefix_bytes=at,trailing_padding=pad,payload_sha256=digest(raw),payload_bytes=len(raw),module=module),decoded))
            break
    need(len(found)<=1,"ambiguous_serialized_encoding")
    return found

def bundle_inventory(private,decoder,fmt):
    import UnityPy
    folder=private/"compiled-bundles";reports=[]
    if not folder.is_dir():return reports
    with tempfile.TemporaryDirectory(prefix="gt-bundle-inspect-",dir=private.parent) as tmp:
        work=Path(tmp)
        for i in range(5):
            file=folder/f"fft-{i}"
            if not file.is_file() or file.is_symlink():continue
            record=dict(bundle_index=i,bundle_bytes=file.stat().st_size,bundle_sha256=sha(file),status="INCONCLUSIVE",rows=[])
            reports.append(record)
            try:
                need(0<file.stat().st_size<=64*1024*1024,"bundle_extent")
                env=UnityPy.load(str(file))
                objs=[o for o in env.objects if o.type.name=="ComputeShader"]
                need(len(objs)==1,"class72_population")
                obj=objs[0];tree=obj.read_typetree()
                record.update(class_id=72,path_id=int(obj.path_id),serialized_object_sha256=digest(obj.get_raw_data()),
                    serialized_object_bytes=len(obj.get_raw_data()),top_level_fields=sorted(tree))
                variants=tree.get("variants")
                need(isinstance(variants,list) and 0<len(variants)<=8,"variant_population")
                record["serialized_variants"]=len(variants)
                expected_slots=list(range(20)) if i==0 else [SLOTS[i-1]]
                for vi,variant in enumerate(variants):
                    kernels=variant.get("kernels");need(isinstance(kernels,list) and len(kernels)==len(expected_slots),"kernel_population")
                    for ordinal,(slot,kernel) in enumerate(zip(expected_slots,kernels,strict=True)):
                        row=dict(variant=vi,ordinal=ordinal,slot=slot,fields=sorted(kernel),module_candidates=[],byte_fields=[])
                        record["rows"].append(row)
                        expected=f"RaftFftSlot{slot:02d}" if i==0 else "main"
                        need(kernel.get("name")==expected,"kernel_order")
                        vm=kernel.get("variantMap")
                        need(isinstance(vm,list) and len(vm)==1 and isinstance(vm[0],(list,tuple)) and len(vm[0])==2,"kernel_variant_map")
                        entry=vm[0][1];need(isinstance(entry,dict),"kernel_entry")
                        group=EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT[slot]
                        row.update(kernel_name=expected,entry_fields=sorted(entry),thread_group=entry.get("threadGroupSize"),
                                   global_keyword_count=len(kernel.get("globalKeywords",[])),local_keyword_count=len(kernel.get("localKeywords",[])))
                        need(row["thread_group"]==[group,1,1] and row["global_keyword_count"]==row["local_keyword_count"]==0,"kernel_route_contract")
                        for path,raw in byte_leaves(entry):
                            field=dict(path=list(path),bytes=len(raw),sha256=digest(raw),raw_magic=raw.count(MAGICS[0]),smolv_magic=raw.count(MAGICS[1]))
                            row["byte_fields"].append(field)
                            for decoded,code in decode_payload(raw,decoder,work,group):
                                row["module_candidates"].append(dict(decoded,path=list(path)))
                        row["decoded_modules"]=len(row["module_candidates"])
                record["status"]="OBSERVED_SERIALIZED_TOPOLOGY"
                record["all_routes_decoded"]=all(row["decoded_modules"]==1 for row in record["rows"])
                record["decoded_modules"]=sum(row["decoded_modules"] for row in record["rows"])
                record["all_routes_expected_storage"]=record["all_routes_decoded"] and all(
                    next(x for x in row["module_candidates"][0]["module"]["images"] if x["sampled_enum"]==2)["format_enum"]==(typed.TYPES[fmt][1] if fmt=="RGFloat" else half.ENUMS[fmt][0]) for row in record["rows"])
            except Exception as e:
                record["failure_type"]=type(e).__name__
                if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):record["failure_reason"]=str(e)
    return reports

def join_captures(reports,receipt,fmt):
    need(len(reports)==5 and [x["bundle_index"] for x in reports]==list(range(5)),"bundle_population")
    need(all(r["status"]=="OBSERVED_SERIALIZED_TOPOLOGY" and r["all_routes_decoded"] and r["all_routes_expected_storage"] and r["serialized_variants"]==1 for r in reports),"bundle_modules")
    need(sum(r["decoded_modules"] for r in reports)==24,"serialized_module_population")
    rows=[]
    for cap in receipt["modules"]:
        slot,variant=cap["slot"],cap["variant"]
        bundle=reports[0 if variant=="indexed" else SLOTS.index(slot)+1]
        matched=[r for r in bundle["rows"] if r["slot"]==slot]
        need(len(matched)==1,"serialized_slot")
        mod=matched[0]["module_candidates"][0]["module"]
        if fmt=="RGFloat":
            need(mod["sha256"]==cap["capture"]["module"]["sha256"],"serialized_live_sha")
            rows.append(dict(bundle_index=bundle["bundle_index"],slot=slot,variant=variant,serialized_sha256=mod["sha256"],
                             actual_captured_sha256=cap["capture"]["module"]["sha256"],replacement=False))
        else:
            need(mod["sha256"]==cap["baseline"]["sha256"]==half.PINS[fmt][f"{variant}-{slot}"],"serialized_live_sha")
            rows.append(dict(bundle_index=bundle["bundle_index"],slot=slot,variant=variant,serialized_sha256=mod["sha256"],
                             actual_before_sha256=cap["baseline"]["sha256"],actual_after_sha256=cap["capture"]["module"]["sha256"]))
    need(len(rows)==8 and {(x["slot"],x["variant"]) for x in rows}=={(s,v) for s in SLOTS for v in ("indexed","standalone")},"capture_population")
    return rows

def bundle_load_fields(r):
    # Strictly bounded authored fields only; no raw asset names or log text.
    bounds={"bundle_load_index":(-1,4),"bundle_load_step":(0,6),"bundle_asset_count":(-1,1024)}
    bounds.update({k:(0,5) for k in ("bundle_crc_verified","bundle_opened","bundle_named","bundle_typed","bundle_distinct")})
    return {k:r[k] for k,(a,b) in bounds.items() if type(r.get(k)) is int and a<=r[k]<=b}

def stage(src,managed,project,private,run_id,fmt):
    result=(typed if fmt=="RGFloat" else half).stage(src,managed,project,private,run_id,fmt)
    editor=project/"Assets/Editor/IndexedPair.cs"
    editor.write_text(half.replace(Path(__file__).with_name("IndexedPair.cs").read_text(),"__FORMAT__",fmt))
    result.update(status=STAGED,editor_sha=sha(editor))
    return result

def verify(project,private,s,run_id,outcome,fmt,decoder):
    need(s["status"]==STAGED,"stage")
    backend=typed if fmt=="RGFloat" else half
    receipt=dict(s,status=backend.STAGED)
    r=json.loads((private/"receipt.json").read_text())
    need(r["bundle_built"] is True and r["bundle_loaded"] is True and r["bundle_vulkan_only"] is True and r["bundle_count"]==5,"editor_bundle")
    fields=bundle_load_fields(r)
    need(fields==dict(bundle_load_index=4,bundle_load_step=6,bundle_asset_count=1,bundle_crc_verified=5,bundle_opened=5,bundle_named=5,bundle_typed=5,bundle_distinct=5),"bundle_load_identity")
    reports=bundle_inventory(private,decoder,fmt)
    need([x["bundle_sha256"] for x in reports]==r["bundle_sha256"],"bundle_commitment")
    if fmt=="RGFloat":
        need(not (private/"half-map.txt").exists(),"replacement_map_absent")
    observed=backend.verify(project,private,receipt,run_id,outcome,fmt)
    need(observed["isolated_format_numeric_parity"] and observed["exact_outputs"]==16,"bundle_numeric_parity")
    joins=join_captures(reports,observed,fmt)
    return dict(status=STATUS,format=fmt,actual_bundle_loaded=True,serialized_modules=24,registered_kernels=20,
                bundle_inventory=reports,serialized_live_joins=joins,bundle_load_fields=fields,
                runtime_replacement_used=(fmt!="RGFloat"),direct_serialized_execution_verified=(fmt=="RGFloat"),numeric_evidence=observed,
                exact_outputs=16,actual_descriptor_resource_mapping_verified=False,original_runtime_kernel_mapping_proven=False,
                serialized_patch_verified=False,original_fft_numeric_parity_verified=False,water_rendering_verified=False,android_device=False,production=False,XAPK=False)

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    st=sub.add_parser("stage");v=sub.add_parser("verify")
    for k in ("source","managed","project","private","out"):st.add_argument("--"+k,type=Path,required=True)
    for k in ("project","private","stage","out","decoder"):v.add_argument("--"+k,type=Path,required=True)
    for q in (st,v):q.add_argument("--run-id",required=True);q.add_argument("--format",choices=FORMATS,required=True)
    v.add_argument("--outcome",required=True);a=p.parse_args()
    result=dict(status="INCONCLUSIVE",format=a.format,water_rendering_verified=False,android_device=False,production=False,XAPK=False)
    try:
        if a.action=="stage":result=stage(a.source,a.managed,a.project,a.private,a.run_id,a.format)
        else:result=verify(a.project,a.private,json.loads(a.stage.read_text()),a.run_id,a.outcome,a.format,a.decoder)
    except Exception as e:
        result["failure_type"]=type(e).__name__
        if isinstance(e,ValueError) and re.fullmatch(r"[a-z_]+",str(e)):result["failure_reason"]=str(e)
        if a.action=="verify":
            result.update(directive.failure_receipt(a.private,a.run_id))
            try:result["bundle_inventory"]=bundle_inventory(a.private,a.decoder,a.format)
            except Exception:pass
            try:
                r=json.loads((a.private/"receipt.json").read_text())
                for key in ("bundle_built","bundle_loaded","bundle_vulkan_only","bundle_count"):
                    if type(r.get(key)) in (bool,int):result[key]=r[key]
                if r.get("run_id")==a.run_id:result["bundle_load_fields"]=bundle_load_fields(r)
            except Exception:pass
            trace=a.private/"vktrace";result["observed_modules"]=[]
            for label in live.LABELS:
                try:result["observed_modules"].append(dict(label=label,capture=live.captured(trace,label),before_sha=sha(trace/(label+".before.spv")) if (trace/(label+".before.spv")).is_file() else None))
                except Exception:pass
    dump(a.out,result);print("GT_FFT_COMPUTE_BUNDLE_"+a.action.upper()+" "+json.dumps(result,sort_keys=True))
    return 0 if result["status"] in (STAGED,STATUS) else 2
if __name__=="__main__":raise SystemExit(main())
