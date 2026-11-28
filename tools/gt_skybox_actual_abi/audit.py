"""Compare authenticated original source ABI to actual Unity Vulkan modules.
Only aggregate counts are publishable. No runtime equivalence from name-only matches.
"""
import argparse
import contextlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from tools.gt_skybox_compiler_control import control as c
from tools.gt_skybox_actual_abi import metadata_bridge as bridge
from tools.gt_skybox_shader_wrapper import wrapper as w
from tools.gt_skybox_source_register_join import audit as join
from tools.gt_skybox_offset_differential import audit as d
from tools.gt_skybox_shader_program import audit as prior
from scripts.t3_spirv_interface_name_drift import read_reflection

CANDIDATE="0c3571b1db0de5b2fbffbfc352a55a632424d8a31a29c83ed2ff5e0df66d836f"
CAPTURE="PASS_PRIVATE_SOURCE_ABI_CAPTURE"
OBSERVED="OBSERVED_ACTUAL_ABI_COMPARISON_PENDING_RUNTIME_AND_NATIVE_LOG"
REFERENCE_LABEL="abi-reference"
SAFE_CAPTURE_ERRORS={"pinned_compiler_control_required","original_object_sha","independent_source_candidate_digest","original_static_reference_regression","source_population","packet_exists","source_abi_reference_file_missing","source_abi_reference_stage_identity","source_abi_reference_label","private_spirv_input_outside_bounded_size","missing_or_unsafe_private_spirv_reflection_input","private_spirv_interface_reflection_unavailable","private_spirv_interface_reflection_invalid_json"}

def output(report,data,marker):
    report.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print(marker+" "+json.dumps(data,sort_keys=True))

def safe_reason(exc):
    if isinstance(exc,ValueError) and str(exc) in SAFE_CAPTURE_ERRORS:
        return str(exc)
    return w.error_category(exc)

def read_compiled_reference(private,label,reader=read_reflection):
    c.require(label==REFERENCE_LABEL,"source_abi_reference_label")
    reflections=[]
    for stage,_,_,entry in d.STAGES:
        path=private/(label+"-"+stage+".spv")
        c.require(path.is_file() and not path.is_symlink() and path.stat().st_size>0,
                  "source_abi_reference_file_missing")
        ref=reader(path)
        c.require([p.get("name") for p in ref.get("entryPoints",[])]==[entry],
                  "source_abi_reference_stage_identity")
        reflections.append(ref)
    return reflections

def capture(x):
    r=dict(status="INCONCLUSIVE",phase="pinned_control",original_shader_verified=False)
    try:
        s=json.loads(x.control_stage.read_text())
        c.require(s["status"]==c.STAGE and s["candidate_sha256"]==CANDIDATE and
                  c.digest(x.dest/"Assets/Original.shader")==CANDIDATE,"pinned_compiler_control_required")
        r["phase"]="authenticated_source_object"
        with open(os.devnull,"w") as quiet,contextlib.redirect_stdout(quiet),contextlib.redirect_stderr(quiet):
            _,_,_,sh,sha=prior.source_shader(x.destination/"Raft_Data",
                    json.loads(x.skybox_plan.read_text()),json.loads(x.plan.read_text()))
            c.require(sha==w.OBJECT_SHA,"original_object_sha")
            with tempfile.TemporaryDirectory(prefix="gt-skybox-source-abi-",dir=x.destination.parent) as td:
                private=Path(td)
                r["phase"]="source_abi_prepare"
                layout,body,layouts,named,signatures=join.prepare(sh,private,{})
                r["phase"]="independent_candidate_digest"
                raw=w.attach(layout,body).encode("utf-8")
                c.require(c.hash_bytes(raw)==c.ORIGINAL_SHA and c.hash_bytes(c.remove_dxc(raw))==CANDIDATE,
                          "independent_source_candidate_digest")
                r["candidate_replayed"]=True
                r["phase"]="source_bound_baseline"
                v,f,mesh,vo,fi=join.baseline(private,signatures)
                refs=[v,f]
                static={}
                r["phase"]="source_bound_reference_compile"
                c.require(join.compile_body(body,private,REFERENCE_LABEL,layouts,named,(v,f,mesh,vo,fi),static),
                          "original_static_reference_regression")
                c.require(static["original_offsets"]==45 and static["named_resources"]==10 and
                          static["join"]["all_original_registers_linked"],"source_population")
                r.update(source_static_offsets=static["original_offsets"],source_static_resources=static["named_resources"],source_static_registers_joined=static["join"]["original_registers_joined_at_same_actual_location"])
                r["phase"]="read_exact_compiler_output_paths"
                static_refs=read_compiled_reference(private,REFERENCE_LABEL)
                r["reference_stage_files_read"]=len(static_refs)
                r["phase"]="write_private_reference_packet"
                packet=dict(candidate_sha256=CANDIDATE,source_object_sha256=sha,layouts=layouts,
                            named_resources=[n["source_texture_sampler_bindings"] for n in named],
                            refs=refs,mesh=mesh,vo=vo,fi=fi,
                            static_refs=static_refs)
                c.require(not x.packet.exists(),"packet_exists")
                x.packet.write_text(json.dumps(packet,sort_keys=True))
                x.packet.chmod(0o600)
        r.update(status=CAPTURE,phase="complete",reference_packet_sha256=c.digest(x.packet),
                 original_object_sha256=sha,original_static_offsets=45,
                 original_static_named_resources=10,original_varying_registers=7,
                 candidate_sha256=CANDIDATE)
    except Exception as e:r["reason"]=safe_reason(e)
    output(x.report,r,"GT_SKYBOX_ACTUAL_ABI_CAPTURE")
    return 0 if r["status"]==CAPTURE else 2

def members(reflection):
    out={}
    for u in reflection.get("ubos",[]):
        for m in reflection["types"][u["type"]]["members"]:
            key=(u["name"],m["name"])
            c.require(key not in out,"duplicate_reflected_member")
            out[key]=(m["offset"],m.get("type"),tuple(m.get("array",[])),
                      m.get("array_stride"),m.get("matrix_stride"),bool(m.get("row_major",False)))
    return out

def map_profile(expected,actual):
    common=set(expected)&set(actual)
    return dict(expected=len(expected),actual=len(actual),exact=sum(expected[k]==actual[k] for k in common),
                same_name_different_value=sum(expected[k]!=actual[k] for k in common),
                missing=len(set(expected)-set(actual)),extra=len(set(actual)-set(expected)),
                exact_map=expected==actual)

def metadata_members(program,row,entries,names):
    from scripts.a12_shader_parameter_decode import parse_parameter_blob
    common=program.get("m_CommonParameters")
    c.require(type(common) is dict,"common_parameter_schema")
    result={}; resource=set(); block_bindings={}
    def put(owner,name,value):
        k=(owner,name)
        c.require(k not in result,"duplicate_metadata_member")
        result[k]=value
    for b in common.get("m_ConstantBuffers",[]):
        owner=names[b["m_NameIndex"]]
        for field,matrix in (("m_VectorParams",False),("m_MatrixParams",True)):
            for a in b.get(field,[]):
                put(owner,names[a["m_NameIndex"]],a["m_Index"])
        for a in b.get("m_StructParams",[]):put(owner,names[a["m_NameIndex"]],a["m_Index"])
    for a in common.get("m_ConstantBufferBindings",[]):
        name=names[a["m_NameIndex"]];c.require(name not in block_bindings,"duplicate_metadata_binding")
        block_bindings[name]=a["m_Index"]
    for a in common.get("m_TextureParams",[]):resource.add(names[a["m_NameIndex"]])
    bucket,ordinal,_=row
    indices=program.get("m_ParameterBlobIndices",[])
    if not indices or bucket is None:
        return result,resource,block_bindings,False
    idx=indices[bucket][ordinal]
    c.require(type(idx) is int and 0<=idx<len(entries),"parameter_blob_index")
    layout={}
    parse_parameter_blob(entries[idx][1],private_layout=layout)
    for group in layout["groups"]:
        for a in group["members"]+group["structs"]:put(group["name"],a["name"],a["index"])
    for a in layout["resources"]:
        if a["kind"]==0:resource.add(a["name"])
        elif a["kind"]==1:
            name=a["name"];old=block_bindings.get(name)
            c.require(old is None or old==a["index"],"metadata_binding_conflict")
            block_bindings[name]=a["index"]
    return result,resource,block_bindings,True

def metadata_profile(layouts,stage,named,actual,resources,bindings,reflected,variant):
    expected={}
    original={}
    for b in layouts:
        alias=d.source_buffer_name(b,stage)
        for m in b["members"]+b["structs"]:
            expected[(alias,m["name"])]=m["index"]
            original[(b["name"],m["name"])]=m["index"]
    aliases=map_profile(expected,actual)
    source=map_profile(original,actual)
    names={k[1] for k in actual}
    actual_reflected={k:v[0] for k,v in members(reflected).items()}
    textures={r["source_texture_name"] for r in named}
    rows=reflected.get("ubos",[])
    # Do not equate serialized index to a Vulkan descriptor unless name matches.
    bound=[r for r in rows if r["name"] in bindings]
    return dict(variant_blob_decoded=variant,original_owner_offsets=source,
                generated_owner_offsets=aliases,original_members_named_any_owner=sum(k[1] in names for k in original),
                reflected_to_serialized_members=map_profile(actual_reflected,actual),
                expected_source_texture_names=len(textures),source_texture_names_present=len(textures&resources),
                reflected_ubo_count=len(rows),serialized_ubo_name_matches=len(bound),
                serialized_index_equal_reflected_binding=sum(bindings[r["name"]]==r.get("binding") for r in bound))

def compare_stage(expected,actual,layouts,stage,original):
    # Distinguish exact source owner/offset from name-only, moved or absent.
    row=d.profile(actual,layouts,stage)
    row["full_static_member_type_stride_layout"]=map_profile(members(expected),members(actual))
    row["named_resources"]=map_profile(d.resources(original),d.resources(actual))
    row["descriptor_pairs_unique"]=len({(r.get("set"),r.get("binding")) for r in actual.get("ubos",[])})==len(actual.get("ubos",[]))
    row["reflected_ubo_count"]=len(actual.get("ubos",[]))
    return row

def descriptor_map(reflection):
    out={}
    for kind in ("ubos",*d.RESOURCE_KINDS):
        for item in reflection.get(kind,[]):
            if "set" not in item or "binding" not in item:
                continue
            key=(item["set"],item["binding"])
            c.require(all(type(n) is int and n>=0 for n in key),"descriptor_coordinate")
            if kind=="ubos":
                fields=reflection["types"][item["type"]]["members"]
                shape=tuple((m["name"],m["offset"],m.get("type"),tuple(m.get("array",[])),
                             m.get("array_stride"),m.get("matrix_stride"),bool(m.get("row_major",False))) for m in fields)
                typ="ubo"
            else:
                shape=tuple(item.get("array",[]));typ=item["type"]
            out.setdefault(key,[]).append((kind,item["name"],typ,shape))
    return out

def descriptor_profile(v,f):
    left,right=descriptor_map(v),descriptor_map(f)
    shared=set(left)&set(right)
    one=[k for k in shared if len(left[k])==len(right[k])==1]
    return dict(vertex_slots=len(left),fragment_slots=len(right),shared_slots=len(shared),
                vertex_duplicate_slots=sum(len(x)>1 for x in left.values()),
                fragment_duplicate_slots=sum(len(x)>1 for x in right.values()),
                shared_exact_name_kind_shape=sum(left[k][0]==right[k][0] for k in one),
                shared_different_name_or_kind_shape=sum(left[k][0]!=right[k][0] for k in one),
                shared_ambiguous_slots=len(shared)-len(one))

def compare_pair(v,f,packet):
    vo={int(k):tuple(a) for k,a in packet["vo"].items()}
    fi={int(k):tuple(a) for k,a in packet["fi"].items()}
    out=dict(mesh_input_location_type=map_profile(w.interface(packet["mesh"],"inputs"),w.interface(v,"inputs")),
             fragment_output_location_type=map_profile(w.interface(packet["refs"][1],"outputs"),w.interface(f,"outputs")))
    out["actual_location_type_link"]=map_profile(w.interface(f,"inputs"),w.interface(v,"outputs"))
    try:out["cross_stage_descriptor_profile"]=descriptor_profile(v,f)
    except Exception as e:out["cross_stage_descriptor_profile"]={"observed":False,"reason":w.error_category(e)}
    try:
        out["original_register_join"]=join.join(join.reflected_registers(v,"outputs","o"),
                                join.reflected_registers(f,"inputs","v"),vo,fi)
    except Exception as e:
        out["original_register_join"]={"all_original_registers_linked":False,"reason":w.error_category(e)}
    return out

def inspect_bundle(path,decoder,name,packet):
    import UnityPy
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    from scripts.w1_recover_depth_passes import stage_variants
    from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules,spirv_execution_models
    from scripts.b25_foam_cb_namebridge import original_name_registry
    ts=[o.read_typetree() for o in UnityPy.load(str(path)).objects if o.type.name=="Shader"]
    c.require(len(ts)==1 and ts[0]["m_ParsedForm"]["m_Name"]==name,"bundle_identity")
    tree=ts[0];c.require(list(tree["platforms"])==[18],"not_vulkan_only")
    [(platform,segments)]=list(decoded_platforms(tree));c.require(platform==18,"platform")
    entries=records(segments);parsed=tree["m_ParsedForm"]
    tables,fallback,_=c.validate_route_tables(parsed,stage_variants)
    p=parsed["m_SubShaders"][0]["m_Passes"][0]
    names=None
    try:names=original_name_registry(p["m_NameIndices"])
    except Exception:pass
    reflection={}; blobs={}; results={}; stage_hashes={}; debug_counts={}
    with tempfile.TemporaryDirectory(prefix="gt-actual-skybox-abi-") as td:
        def decode(i):
            c.require(type(i) is int and 0<=i<len(entries),"blob_index")
            if i not in blobs:
                hashes=[]
                for data in unity_vulkan_modules(entries[i][1]):
                    if data[:4]==b"LOMS":data=subprocess.run([str(decoder)],input=data,capture_output=True,timeout=15,check=True).stdout
                    h=c.hash_bytes(data)
                    if h not in reflection:
                        models=spirv_execution_models(data)
                        c.require(len(models)==1 and models<={0,4},"stage_model")
                        spv=Path(td)/(h+".spv");spv.write_bytes(data)
                        subprocess.run(["spirv-val","--target-env","vulkan1.1",str(spv)],capture_output=True,timeout=30,check=True)
                        reflection[h]=(next(iter(models)),read_reflection(spv))
                        debug_counts[h]=bridge.debug_op_counts(data)
                    hashes.append(h)
                c.require(bool(hashes),"empty_blob")
                blobs[i]=hashes
            return blobs[i]
        for i,(stage,table,model) in enumerate((("vs","progVertex",0),("fs","progFragment",4))):
            rr=[]
            for row in tables[table]:
                hh=[h for h in decode(row[2]["m_BlobIndex"]) if reflection[h][0]==model]
                c.require(len(hh)==1,"missing_ambiguous_stage")
                rr.append(hh[0])
            c.require(len(set(rr))==1,"different_stage_module_per_bucket")
            h=rr[0];stage_hashes[stage]=h;actual=reflection[h][1]
            result=compare_stage(packet["static_refs"][i],actual,packet["layouts"][i],stage,packet["refs"][i])
            result["module_sha256"]=h;result["serialized_stage_rows"]=len(rr)
            result["runtime_metadata_rows"]=[]
            result["actual_spirv_debug_name_counts"]=debug_counts[h]
            result["descriptor_metadata_bridge_rows"]=[]
            for row in tables[table]:
                try:
                    c.require(names is not None,"name_registry_unavailable")
                    owner_table="progVertex" if fallback and stage=="fs" else table
                    m,res,b,variant=metadata_members(p[owner_table],row,entries,names)
                    result["runtime_metadata_rows"].append(metadata_profile(packet["layouts"][i],stage,
                                    packet["named_resources"][i],m,res,b,actual,variant))
                except Exception as e:
                    result["runtime_metadata_rows"].append({"observed":False,"reason":w.error_category(e)})
                try:
                    c.require(names is not None,"name_registry_unavailable")
                    owner_table="progVertex" if fallback and stage=="fs" else table
                    full=bridge.full_metadata(p[owner_table],row,entries,names)
                    result["descriptor_metadata_bridge_rows"].append(bridge.view_profiles(packet["layouts"][i],stage,
                                    packet["named_resources"][i],packet["static_refs"][i],packet["refs"][i],full,actual))
                except Exception as e:
                    result["descriptor_metadata_bridge_rows"].append({"observed":False,"reason":w.error_category(e)})
            results[stage]=result
        pair=compare_pair(reflection[stage_hashes["vs"]][1],reflection[stage_hashes["fs"]][1],packet)
    return dict(stages=results,interfaces=pair,fragment_table_fallback=fallback,
                actual_original_offsets_exact=sum(r["exact_owner_offset"] for r in results.values()),
                actual_original_named_resources_exact=sum(r["named_resources"]["exact"] for r in results.values()),
                all_expected_owner_offsets_match=all(r["exact_owner_offset"]==r["expected_members"] for r in results.values()),
                all_static_member_layouts_match=all(r["full_static_member_type_stride_layout"]["exact_map"] for r in results.values()),
                all_named_resource_maps_match=all(r["named_resources"]["exact_map"] for r in results.values()))

def verify(x):
    r=dict(status="INCONCLUSIVE",original_shader_verified=False,original_runtime_abi_verified=False,
           native_log_reconciled=False,device_pixels=False,player_built=False,XAPK=False)
    try:
        capture=json.loads(x.capture_report.read_text())
        proof=json.loads(x.control_verify.read_text())
        c.require(capture["status"]==CAPTURE and capture["reference_packet_sha256"]==c.digest(x.packet) and
                  capture["candidate_sha256"]==CANDIDATE,"reference_packet_commitment")
        c.require(proof["status"]==c.PASS and proof["editor"]["candidateSha256"]==CANDIDATE,"decoded_control_required")
        packet=json.loads(x.packet.read_text())
        expected=json.loads((x.dest/"expected-private.json").read_text())
        bundle=x.dest/"private-bundle"/"skybox-private"
        c.require(c.digest(bundle)==proof["bundle_sha256"] and packet["candidate_sha256"]==CANDIDATE and
                  c.digest(x.dest/"Assets/Original.shader")==CANDIDATE,"same_execution_binding")
        r["bundle_sha256"]=proof["bundle_sha256"]
        r["comparison"]=inspect_bundle(bundle,x.decoder,expected["shaderName"],packet)
        a=r["comparison"]
        r["exact_reflected_source_contract"]=(a["actual_original_offsets_exact"]==45 and
            a["actual_original_named_resources_exact"]==10 and a["all_expected_owner_offsets_match"] and
            a["all_static_member_layouts_match"] and a["all_named_resource_maps_match"] and
            a["interfaces"]["mesh_input_location_type"]["exact_map"] and
            a["interfaces"]["fragment_output_location_type"]["exact_map"] and
            a["interfaces"]["original_register_join"]["all_original_registers_linked"])
        r["status"]=OBSERVED
        r["metadata_bridge_observed_rows"]=sum(sum("views" in x for x in stage["descriptor_metadata_bridge_rows"]) for stage in a["stages"].values())
        r["original_runtime_abi_verified"]=False
    except Exception as e:r["reason"]=w.error_category(e)
    output(x.report,r,"GT_SKYBOX_ACTUAL_ABI_VERIFY")
    # Completing comparison is not ABI acceptance. A measured mismatch is retained,
    # while missing original reference/program/inspection fails the experiment.
    return 0 if r["status"]==OBSERVED else 2

if __name__=="__main__":
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="action",required=True)
    a=s.add_parser("capture")
    for k in ("destination","skybox-plan","plan","dest","control-stage","packet","report"):a.add_argument("--"+k,type=Path,required=True)
    v=s.add_parser("verify")
    for k in ("dest","capture-report","control-verify","packet","decoder","report"):v.add_argument("--"+k,type=Path,required=True)
    x=p.parse_args()
    raise SystemExit(capture(x) if x.action=="capture" else verify(x))
