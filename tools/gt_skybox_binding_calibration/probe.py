"""Source-free calibration of Unity's serialized descriptor index observations.

Two different authored declaration orders, slots and offsets. Independent
OpSampledImage operand links and texture dimensions prevent sampler swaps from
being accepted by a count-only join. No general packing rule claimed.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

CASES=("calibration_a","calibration_b")
VIEWS=("direct","low8","low16","high8","high16")
MEMBERS={"vs":{"_GTCalV1":"float","_GTCalV4":"vec4"},
         "fs":{"_GTCalF2":"vec2","_GTCalF4":"vec4"}}
TEXTURES={"_GTCal2D":"texture2D","_GTCalCube":"textureCube","_GTCal3D":"texture3D"}

def require(ok,why):
    if not ok:raise ValueError(why)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def shader(case):
    require(case in CASES,"case")
    b=case==CASES[1]
    v=[("float","_GTCalV1",2 if b else 0),("float4","_GTCalV4",0 if b else 1)]
    f=[("float2","_GTCalF2",3 if b else 0),("float4","_GTCalF4",1 if b else 2)]
    def decl(owner,reg,rows):
        return "cbuffer "+owner+" : register(b"+str(reg)+") {\n"+"".join(
            typ+" "+name+" : packoffset(c"+str(offset)+");\n" for typ,name,offset in (reversed(rows) if b else rows))+"};\n"
    textures=[("Texture2D","_GTCal2D"),("TextureCube","_GTCalCube"),("Texture3D","_GTCal3D")]
    if b:textures.reverse()
    return ('Shader "Hidden/GTStageProbe/'+case+'" {\nSubShader { Pass {\nHLSLPROGRAM\n'
            '#pragma target 4.5\n#pragma only_renderers vulkan\n#pragma vertex gt_vert\n#pragma fragment gt_frag\n'
            +decl("GTCalVertex",4 if b else 2,v)+decl("GTCalFragment",2 if b else 3,f)
            +"".join(typ+" "+name+";\nSamplerState sampler"+name+";\n" for typ,name in textures)
            +"struct Vary { float4 pos : SV_POSITION; float4 val : TEXCOORD0; };\n"
            +"Vary gt_vert(float4 p : POSITION) { Vary o; o.pos=p; o.pos.x+=_GTCalV1*0.001; o.val=_GTCalV4+_GTCalV1; return o; }\n"
            +"float4 gt_frag(Vary i) : SV_Target { float3 u=float3(_GTCalF2,0.5); return i.val*0.01+_GTCalF4*0.02+"
            +"_GTCal2D.Sample(sampler_GTCal2D,u.xy)*0.13+_GTCalCube.Sample(sampler_GTCalCube,u)*0.27+"
            +"_GTCal3D.Sample(sampler_GTCal3D,u)*0.37; }\nENDHLSL\n} } }\n")

def stage(dest):
    dest.mkdir()
    for d in ("Assets/Editor","Packages","ProjectSettings","cases"):(dest/d).mkdir(parents=True)
    (dest/"Assets/Editor/StageProbe.cs").write_bytes(Path(__file__).with_name("StageProbe.cs").read_bytes())
    (dest/"Packages/manifest.json").write_text('{"dependencies":{}}\n')
    (dest/"ProjectSettings/ProjectVersion.txt").write_text("m_EditorVersion: 2021.3.45f2\n")
    for case in CASES:(dest/"cases"/(case+".shader")).write_text(shader(case))
    paths=["Assets/Editor/StageProbe.cs",*["cases/"+c+".shader" for c in CASES]]
    (dest/"authored-sha.json").write_text(json.dumps({p:sha(dest/p) for p in paths},sort_keys=True))

def sampled_pairs(data):
    require(len(data)>=20 and len(data)%4==0 and data[:4]==b"\x03\x02\x23\x07","spirv_header")
    words=struct.unpack("<"+"I"*(len(data)//4),data)
    deco={};loads={};sampled={};used=set();variables=set()
    i=5
    while i<len(words):
        n,op=divmod(words[i],65536)
        require(n>0 and i+n<=len(words),"spirv_instruction")
        a=words[i+1:i+n]
        if op==71 and len(a)==3 and a[1] in (33,34):
            k=(a[0],a[1]);require(k not in deco,"duplicate_decoration");deco[k]=a[2]
        elif op==59 and len(a)>=3:variables.add(a[1])
        elif op==61 and len(a)>=3:loads[a[1]]=a[2]
        elif op==86 and len(a)==4:sampled[a[1]]=(a[2],a[3])
        elif 87<=op<=94 and len(a)>=3:used.add(a[2])
        i+=n
    def coord(result):
        var=loads.get(result)
        require(var in variables and (var,33) in deco and (var,34) in deco,"sample_operand_descriptor_unresolved")
        return deco[var,34],deco[var,33]
    require(used<=set(sampled),"sampled_image_operand_unresolved")
    return {(coord(sampled[k][0]),coord(sampled[k][1])) for k in used}

def pair_profile(known,metadata,slots,pairs,view):
    from tools.gt_skybox_actual_abi import metadata_bridge as b
    matches={};missing=0
    for name,typ in known.items():
        idx=metadata["textures"].get(name)
        if idx is None:missing+=1;continue
        images=[r for r in b.unique_slots(slots,"separate_images",idx[0],view) if r["type"]==typ]
        samplers=[r for r in b.unique_slots(slots,"separate_samplers",idx[1],view) if r["type"]=="sampler"]
        if len(images)!=1 or len(samplers)!=1:missing+=1;continue
        image,sampler=images[0],samplers[0]
        key=((image["set"],image["binding"]),(sampler["set"],sampler["binding"]))
        matches.setdefault(key,[]).append(name)
    unique={k for k,v in matches.items() if len(v)==1}
    return dict(expected=len(known),distinct_type_pairs=len(unique),
                independently_used_sample_pairs=len(unique & pairs),
                missing_or_ambiguous=missing,non_injective=sum(len(v) for v in matches.values() if len(v)>1),
                all_sample_pairs_accounted=unique==pairs and len(unique)==len(known))

def numeric_profile(expected,metadata,slots,view):
    from tools.gt_skybox_actual_abi import metadata_bridge as b
    matched={};missing=0;name_count=0
    for name,typ in expected.items():
        named=[(owner,g["members"][name]) for owner,g in metadata["groups"].items() if name in g["members"]]
        name_count+=bool(named);found=[]
        for owner,offset in named:
            if owner not in metadata["buffers"]:continue
            for u in b.unique_slots(slots,"ubos",metadata["buffers"][owner],view):
                for m in u["members"]:
                    if m["offset"]==offset and m["type"]==typ and not m.get("array"):
                        found.append((u["set"],u["binding"],offset))
        if len(found)!=1:missing+=1;continue
        matched.setdefault(found[0],[]).append(name)
    return dict(expected=len(expected),named_serialized=name_count,
                unique_descriptor_offset_type=sum(len(v)==1 for v in matched.values()),
                non_injective=sum(len(v) for v in matched.values() if len(v)>1),
                missing_or_ambiguous=missing)

def inspect(bundle,case,decoder):
    import UnityPy
    from tools.gt_skybox_actual_abi import metadata_bridge as b
    from scripts.w1_recover_graphics_programs import decoded_platforms,records
    from scripts.w1_recover_depth_passes import stage_variants
    from scripts.b25_foam_cb_namebridge import original_name_registry
    from scripts.t3_spirv_interface_name_drift import read_reflection
    from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules,spirv_execution_models
    ts=[o.read_typetree() for o in UnityPy.load(str(bundle)).objects if o.type.name=="Shader"]
    require(len(ts)==1,"shader_count")
    t=ts[0];parsed=t["m_ParsedForm"]
    require(parsed["m_Name"]=="Hidden/GTStageProbe/"+case and list(t["platforms"])==[18],"identity_platform")
    [(platform,parts)]=list(decoded_platforms(t));require(platform==18,"platform")
    entries=records(parts);subs=parsed["m_SubShaders"]
    require(len(subs)==1 and len(subs[0]["m_Passes"])==1,"pass_count")
    p=subs[0]["m_Passes"][0];names=original_name_registry(p["m_NameIndices"])
    tables={k:stage_variants(p[k]) for k in ("progVertex","progFragment")}
    require(bool(tables["progVertex"]),"missing_vertex")
    fallback=not tables["progFragment"]
    if fallback:tables["progFragment"]=tables["progVertex"]
    result={"stages":{},"fragment_table_fallback":fallback}
    with tempfile.TemporaryDirectory(prefix="gt-binding-calibration-") as td:
        decoded={}
        def decode(idx):
            if idx in decoded:return decoded[idx]
            require(type(idx) is int and 0<=idx<len(entries),"blob_index")
            models={}
            for n,raw in enumerate(unity_vulkan_modules(entries[idx][1])):
                if raw[:4]==b"LOMS":raw=subprocess.run([str(decoder)],input=raw,capture_output=True,timeout=15,check=True).stdout
                mods=spirv_execution_models(raw)
                require(len(mods)==1 and mods<={0,4},"model")
                m=next(iter(mods));require(m not in models,"duplicate_stage")
                spv=Path(td)/f"{idx}-{n}.spv";spv.write_bytes(raw)
                subprocess.run(["spirv-val","--target-env","vulkan1.1",str(spv)],capture_output=True,timeout=15,check=True)
                models[m]=(raw,read_reflection(spv))
            decoded[idx]=models;return models
        for stage,table,model in (("vs","progVertex",0),("fs","progFragment",4)):
            rows=[]
            for row in tables[table]:
                require(all(not row[2].get(k,[]) for k in ("m_KeywordIndices","m_GlobalKeywordIndices","m_LocalKeywordIndices")),"nonempty_route")
                raw,ref=decode(row[2]["m_BlobIndex"])[model]
                slots=b.reflected_slots(ref)
                pairs=sampled_pairs(raw)
                meta=b.full_metadata(p["progVertex" if fallback else table],row,entries,names)
                known=TEXTURES if stage=="fs" else {}
                views={}
                for view in VIEWS:
                    views[view]={"numeric":numeric_profile(MEMBERS[stage],meta,slots,view),
                                 "texture_sampler":pair_profile(known,meta,slots,pairs,view)}
                rows.append(dict(views=views,actual_sample_pair_count=len(pairs),debug_names=b.debug_op_counts(raw),
                                 module_sha256=hashlib.sha256(raw).hexdigest(),variant_blob_decoded=meta["variant"]))
            require(bool(rows),"missing_stage")
            result["stages"][stage]=rows
    return result

def complete_observed_views(cases):
    """Evaluate nested per-view rows; empty or partial reports cannot pass."""
    require(set(cases)==set(CASES),"calibration_case_set")
    rows=[]
    for case in CASES:
        stages=cases[case]["stages"]
        require(set(stages)==set(MEMBERS),"calibration_stage_set")
        for stage_rows in stages.values():
            require(isinstance(stage_rows,list) and bool(stage_rows),"calibration_empty_stage")
            for row in stage_rows:
                require(set(row["views"])==set(VIEWS),"calibration_view_set")
                rows.append(row)
    complete=[]
    for view in VIEWS:
        if all(r["views"][view]["numeric"]["unique_descriptor_offset_type"]==
               r["views"][view]["numeric"]["expected"] and
               r["views"][view]["texture_sampler"]["all_sample_pairs_accounted"] is True and
               r["views"][view]["texture_sampler"]["independently_used_sample_pairs"]==
               r["views"][view]["texture_sampler"]["expected"]
               for r in rows):
            complete.append(view)
    return complete

def verify(dest,decoder,outcome,report):
    result=dict(status="INCONCLUSIVE",editor_outcome=outcome,cases={},original_runtime_abi_verified=False,
                original_shader_verified=False,device_pixels=False,player_built=False,XAPK=False,
                independent_calibration_only=True,global_index_packing_rule_proven=False)
    try:
        manifest=json.loads((dest/"authored-sha.json").read_text())
        expected={"Assets/Editor/StageProbe.cs",*["cases/"+c+".shader" for c in CASES]}
        require(set(manifest)==expected and all(sha(dest/p)==h for p,h in manifest.items()),"source_manifest")
        require(all((dest/"cases"/(c+".shader")).read_text()==shader(c) for c in CASES),"authored_source_identity")
        editor=json.loads((dest/"editor-safe.json").read_text())
        require(editor["version"]=="2021.3.45f2" and editor["androidVulkanOnly"] is True and editor["playerBuilt"] is False,"editor_environment")
        require([x["id"] for x in editor["cases"]]==list(CASES),"case_set")
        for r in editor["cases"]:
            case=r["id"]
            bundle=dest/"private-bundles"/case/"probe"
            require(r["sourceCopyExact"] is True and r["imported"] is True and r["bundleBuilt"] is True and sha(bundle)==r["bundleSha256"],"editor_bundle_identity")
            try:result["cases"][case]=inspect(bundle,case,decoder)
            except Exception as e:result["cases"][case]={"reason":str(e) if isinstance(e,ValueError) and str(e) in {"sample_operand_descriptor_unresolved","sampled_image_operand_unresolved","duplicate_descriptor_coordinate"} else type(e).__name__}
        require(outcome=="success" and all("stages" in x for x in result["cases"].values()),"actual_calibration_missing")
        complete=complete_observed_views(result["cases"])
        result["complete_observed_views"]=complete
        result["ambiguous_complete_views"]=len(complete)>1
        result["status"]="OBSERVED_AUTHORED_METADATA_CALIBRATION_PENDING_GENERALIZATION"
    except Exception as e:result["reason"]=str(e)[:160] if type(e) is ValueError else type(e).__name__
    report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_BINDING_CALIBRATION "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="OBSERVED_AUTHORED_METADATA_CALIBRATION_PENDING_GENERALIZATION" else 2

if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("stage");s.add_argument("--dest",type=Path,required=True)
    v=sub.add_parser("verify")
    for k in ("dest","decoder","report"):v.add_argument("--"+k,type=Path,required=True)
    v.add_argument("--outcome",required=True)
    x=p.parse_args()
    if x.cmd=="stage":stage(x.dest)
    else:raise SystemExit(verify(x.dest,x.decoder,x.outcome,x.report))
