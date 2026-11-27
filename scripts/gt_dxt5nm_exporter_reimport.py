"""V16: import real corrected V15 exporter output, no manual alpha metadata edit.

Historical V12 opt-out and V14 reversible probe remain separate.
Only authored fixture bytes; no production, Android, original shader or
source lower-mip claim. The shared V13 staging route is retained verbatim
except for explicit candidate input verification and V16 probe files.
"""
import argparse
from copy import deepcopy
import json
import re
from pathlib import Path
from scripts import gt_dxt5nm_unity_reimport as v13
from scripts import gt_dxt5nm_texel_policy as v14
from scripts import gt_authored_dxt5nm_alpha_exporter_witness as v15
from scripts.gt_dxt5nm_unity_reimport import (ROOT,TOOLS,V12,FIELD,PNG_SHA,EDITOR_VERSION,
    regular_path,read,write,digest,need,gate,png,SETTINGS,adapt_material_shader_pointer)

V15=ROOT/"clients/GT/sessions/20261127-dxt5nm-alpha-exporter-v15/actual-pass-45975084812.json"
V16_TOOLS=ROOT/"tools/gt_dxt5nm_exporter_reimport"

def historical_meta_stable(raw):
    """Exact V15 published hash convention, distinct from V15 pair checker.

    Normalize only the two already-declared volatile header values in memory;
    never change a candidate file. V15 permanent receipt uses labelled
    VOLATILE headers, whereas its live pair checker uses <volatile>.
    """
    for pattern,replacement in ((rb"(?m)^guid: [0-9a-f]{32}\r?$",b"guid: VOLATILE"),
                                (rb"(?m)^timeCreated: [0-9]+\r?$",b"timeCreated: VOLATILE")):
        raw,n=re.subn(pattern,replacement,raw)
        need(n==1,"historical_V15_volatile_header_population")
    return raw

def historical_expected_rows(h,raw=None):
    """A narrowly scoped archive-backed erratum, never a metadata edit.

    Preserve V15's immutable historical receipt, including its typo.
    Require the original artifact/member hashes, original raw metadata
    hashes and precisely the one wrong hex character in both fields.
    """
    rows={(x["mode"],tuple(x["source_key"])):dict(x) for x in h["independent"]["six_pair_rows"]}
    need(len(rows)==6,"historical_six_pairs")
    need(h["archive"]["id"]==15186083739 and h["archive"]["sha256"]=="25506dd7361b2849b7de90cc78b2d59d8d80fbf2cf6c2913cb3d8c848388059c" and h["archive"]["member_sha256"]["alpha-exporter-actual.json"]=="51ed86ab7908ed2128ea756a0c503e2ef97215111a5d5fd1879a3e5a0ba4fabf","historical_erratum_archive_binding")
    r=rows[("rgba",("sharedassets3.assets",1))]
    need(r["normalized_before_sha256"]==r["normalized_after_sha256"]=="886a66512cc4ffd828e2a5b5c6c03da0e91f54394f7cdce847aa42161dee8ea7" and r["alpha_before"]==r["alpha_after"]==1,"historical_erratum_exact_row")
    need(r["before_guid"]=="f7d698ac048f0f84da74c515ebbf85c5" and r["after_guid"]=="605a4e8ae43c6334685245f7e2c2a1de" and r["before_meta_sha256"]=="5df34a977820ac1fff63a388afa11ac73190caddf6f90520c33fedcc0c9e4784" and r["after_meta_sha256"]=="627b3a0b3506f6bf2afdb5ffeb3785e74b5ff93151b7dc8205e75bda0e16e3ca","historical_erratum_original_row_binding")
    if raw is None:raw=V15.with_name("authored-rgba32-pathid1-historical-before.meta.txt").read_bytes()
    need(digest(raw)==r["before_meta_sha256"],"historical_erratum_raw_meta_drift")
    before_header=b"guid: f7d698ac048f0f84da74c515ebbf85c5\ntimeCreated: 1795772245\n"
    after_header=b"guid: 605a4e8ae43c6334685245f7e2c2a1de\ntimeCreated: 1795772246\n"
    need(raw.count(before_header)==1,"historical_erratum_exact_header")
    after=raw.replace(before_header,after_header)
    need(digest(after)==r["after_meta_sha256"],"historical_erratum_after_meta_drift")
    corrected=digest(historical_meta_stable(raw))
    need(corrected==digest(historical_meta_stable(after))=="886a66512cc4ffd828e2a2b5c6c03da0e91f54394f7cdce847aa42161dee8ea7","historical_erratum_recomputed_digest")
    need(r["normalized_before_sha256"][:21]+corrected[21]+r["normalized_before_sha256"][22:]==corrected,"historical_erratum_single_hex_character")
    r["normalized_before_sha256"]=r["normalized_after_sha256"]=corrected
    return rows

def validate_replay(a,p,h):
    status="PASS_ACTUAL_AUTHORED_SELECTIVE_DXT5NM_PNG_EXPORTER_ALPHA_POLICY"
    need(a["status"]==h["status"]==status and a["actual_compiled_exporter_modes"]==6 and a["actual_normalmap_policy_changes"]==2 and a["actual_ordinary_policy_unchanged"]==4 and a["actual_metadata_control_count"]==6 and a["source_bytes_unchanged"] is True and a["production_activation"] is False and a["original_assets_read"] is False and a["Unity_reimport_of_candidate_verified"] is False,"V15_actual_replay_required")
    for k in ("original_git_blob","original_sha256","patched_sha256","patch_script_sha256","opt_in_environment","opt_in_value","default_behavior_changed","general_importer_factory_changed","production_activation","source_asset_bytes_modified"):
        need(p[k]==h["patch"][k],"V15_pinned_patch_drift:"+k)
    historical=historical_expected_rows(h)
    need(len(historical)==6 and set(a["scopes"])=={"normal","bc3","rgba"},"six_historical_pairs_required")
    for mode in ("normal","bc3","rgba"):
        scope=a["scopes"][mode];need(len(scope["rows"])==2,"pair_population")
        if mode=="normal":need(scope["historical_V12_actual_candidate_rejected"] is True and scope["historical_V12_restored_counterfactual_only"] is True,"historical_V12_separate")
        for pair in scope["rows"]:
            b,c=pair["before"],pair["after"]
            x=historical.pop((mode,tuple(c["key"])))
            need(b["key"]==c["key"] and b["ptr"][1:]==c["ptr"][1:] and b["alpha"]==x["alpha_before"] and c["alpha"]==x["alpha_after"] and pair["only_alpha_policy_changed"]==(mode=="normal"),"selective_policy_drift")
            for side,row in (("before",b),("after",c)):
                context=f"{mode}:{row['key']}:{side}"
                need(row["png_sha256"]==x["png_sha256"],"historical_V15_PNG_drift:"+context)
                need(row["rgba_sha256"]==x["rgba_sha256"]==digest(bytes.fromhex(row["rgba_hex"])),"historical_V15_RGBA_drift:"+context)
                got=digest(historical_meta_stable(row["metadata"].encode()))
                expected=x["normalized_"+side+"_sha256"]
                need(got==expected,"historical_V15_metadata_drift:"+context+":"+got+":"+expected)
            v15.compare_meta(b["metadata"].encode(),c["metadata"].encode(),mode=="normal")
    need(not historical,"missing_historical_pairs")

def stage(root,project,run_id,receipt,audit,patch,out):
    root,project,out=map(regular_path,(root,project,out))
    need(not project.exists() and project.parent.is_dir() and not out.exists(),"fresh_stage_required")
    historical=read(V12)
    actual=read(receipt)
    need(historical["status"]==actual["status"]=="PASS_ACTUAL_AUTHORED_PUBLIC_DXT5NM_SUPPORTED_IMPORTER_STATE_ROUTE_JOIN" and actual["baseline"][FIELD] and actual["counterfactual_count"]==25,"V12_verified_receipt_required")
    # Fresh output from the actual opt-in exporter; historical V12 receipt is
    # for the distinct opt-out output, never a rewritten candidate.
    export_audit=read(audit)
    historical_v15=read(V15)
    validate_replay(export_audit,read(patch),historical_v15)
    off,_=v15.inspect(root/"normal-off","normal")
    on,context=v15.inspect(root/"normal-on","normal")
    pairs=v15.compare_pair(off,on,"normal")
    need(pairs==export_audit["scopes"]["normal"]["rows"] and on["baseline"]==export_audit["scopes"]["normal"]["baseline"],"fresh_V15_candidate_route_recheck")
    objects,externals,mapping,vertices,proofs,files,docs,states=context
    need(on["baseline"][v15.V11] and len(states)==2,"fresh_candidate_same_route")
    candidate_rows=[]
    staged={};identities={};adapters=[];material_adapters=[];scene_sources={}
    def put(path,raw):
        need(path.startswith(("Assets/","Packages/","ProjectSettings/")) and ".." not in Path(path).parts and path not in staged,"unique_safe_stage_path")
        staged[path]=raw
    def asset(key):
        if key in identities:return identities[key]
        cls,ptr,exportable=mapping[key];guid,fid,kind=ptr
        path,meta=files[guid]
        raw=gate.bounded_snapshot(path,gate.MAX_DOC if cls!=28 else png.MAX_PNG)
        md=gate.bounded_snapshot(Path(str(path)+".meta"),256*1024)
        need(md.decode("utf-8-sig")==meta,"actual_meta_bytes_drift")
        suffix=path.suffix
        if cls==48:
            need(fid==4800000,"adapter_shader_fileID_boundary")
            dest="Assets/GTAdapters/Adapter"+str(len(adapters))+".shader"
            name="GT/V13/Adapter"+str(len(adapters))
            adapter=("Shader \""+name+"\" { Properties { _MainTex (\"Input\", 2D) = \"white\" {} "
                "_AuthoredTint (\"Tint\", Color)=(1,1,1,1) _AuthoredVector (\"Vector\", Vector)=(0,0,0,0) "
                "_AuthoredFloat (\"Float\", Float)=0 _AuthoredNegative (\"Negative\", Float)=0 "
                "_AuthoredInteger (\"Integer\", Float)=0 _AuthoredSigned (\"Signed\", Float)=0 } "
                "SubShader { Pass { Color (1,1,1,1) } } }\n").encode()
            adapter_meta=("fileFormatVersion: 2\nguid: "+guid+"\nShaderImporter:\n  externalObjects: {}\n  defaultTextures: []\n  nonModifiableTextures: []\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n").encode()
            adapters.append(dict(guid=guid,file_id=fid,source_sha256=digest(raw),source_meta_sha256=digest(md),adapter_sha256=digest(adapter)))
            raw,md=adapter,adapter_meta
        else:
            need(cls in (21,28,43) and suffix in (".mat",".png",".asset",".mesh"),"unsupported_staged_asset_class")
            dest="Assets/GTExport/"+guid+suffix
            if cls==21:
                source_shader=gate.src_target(key[0],objects[key][1]["m_Shader"],externals)
                shader_ptr=mapping[source_shader][1]
                need(source_shader in identities,"staged_shader_adapter_required")
                raw,patch=adapt_material_shader_pointer(raw,shader_ptr)
                material_adapters.append(dict(patch,material_guid=guid,material_file_id=fid,meta_sha256=digest(md)))
        put(dest,raw);put(dest+".meta",md)
        result=dict(path=dest,guid=guid,file_id=fid,sha256=digest(raw),meta_sha256=digest(md))
        identities[key]=result
        return result
    textures=[]
    for i,key in enumerate(sorted(states)):
        id=asset(key);s=states[key];hist=historical["receipt"]["source_and_actual"][i];act=actual["source_and_actual"][i]
        need(id["sha256"]==PNG_SHA[i] and hist["source"]==act["source"] and hist["source_rgba_sha256"]==act["source_rgba_sha256"],"historical_V12_pixel_state_drift")
        pair=pairs[i];before,after=pair["before"],pair["after"]
        need(list(key)==after["key"] and list(mapping[key][1])==after["ptr"] and id["sha256"]==after["png_sha256"],"candidate_export_pointer_binding")
        need(act["actual_metadata"]==before["metadata"] and not act["swizzle_present"],"separate_opt_out_V12_meta_binding")
        need(after["metadata"]==files[id["guid"]][1] and after["alpha"]==0,"actual_candidate_metadata_binding")
        rgba=bytes.fromhex(historical["v11_replay"]["textures"][i]["actual_rgba_hex"])
        need(digest(rgba)==after["rgba_sha256"]==act["source_rgba_sha256"],"actual_candidate_RGBA_binding")
        textures.append(dict(id,expected_source=act["source"],expected_rgba_hex=rgba.hex()))
        candidate_rows.append(dict(source_key=list(key),guid=id["guid"],file_id=id["file_id"],png_sha256=id["sha256"],meta_sha256=id["meta_sha256"],rgba_sha256=digest(rgba),normalized_meta_sha256=digest(historical_meta_stable(after["metadata"].encode()))))
    routes=[]
    for key,(cls,tree) in sorted(objects.items()):
        if cls!=23:continue
        rp=mapping[key][1];go=gate.src_target(key[0],tree["m_GameObject"],externals)
        scene_path,scene_meta=files[rp[0]]
        scene_sources[key[0]]=dict(guid=rp[0],renderer_file_id=rp[1],sha256=digest(gate.bounded_snapshot(scene_path,gate.MAX_DOC)),meta_sha256=digest(Path(str(scene_path)+".meta").read_bytes()))
        filters=[(k,t) for k,(cl,t) in objects.items() if cl==33 and gate.src_target(k[0],t["m_GameObject"],externals)==go]
        need(len(filters)==1,"exact_source_filter")
        fk,ft=filters[0];mk=gate.src_target(fk[0],ft["m_Mesh"],externals)
        layout=objects[mk][1];mesh=asset(mk);mats=[];texs=[];shaders=[];uv=[]
        for raw in tree["m_Materials"]:
            mat=gate.src_target(key[0],raw,externals)
            ms=objects[mat][1];shader=gate.src_target(mat[0],ms["m_Shader"],externals)
            shaders.append(asset(shader));mats.append(asset(mat))
            env=gate.normalize_texenvs(ms["m_SavedProperties"]["m_TexEnvs"])
            need(set(env)=={"_MainTex"},"exact_authored_texenv_scope")
            ptr,transform=env["_MainTex"]
            tex=gate.src_target(mat[0],{"m_FileID":ptr[0],"m_PathID":ptr[1]},externals)
            texs.append(asset(tex));uv.extend(transform)
        routes.append(dict(key=key[0],mesh=mesh,materials=mats,textures=texs,shaders=shaders,uv=uv,
            vertex_count=layout[0],index_counts=[s[1] for s in layout[-1]],base_vertices=[s[3] for s in layout[-1]]))
    need(len(routes)==len(adapters)==len(material_adapters)==len(textures)==2 and len(identities)==7 and routes[0]["materials"]==routes[1]["materials"][::-1],"authored_route_population")
    put("Assets/GTNormalProbe/NormalRouteProbe.shader",(TOOLS/"SyntheticNormalRouteProbe.shader").read_bytes())
    put("Assets/Editor/SyntheticNormalRouteValidation.cs",(TOOLS/"SyntheticNormalRouteValidation.cs").read_bytes())
    put("Assets/Editor/SyntheticNormalExporterReimport.cs",(V16_TOOLS/"SyntheticNormalExporterReimport.cs").read_bytes())
    put("Assets/GTNormalProbe/NormalTexelLoad.compute",(v14.TOOLS/"NormalTexelLoad.compute").read_bytes())
    put("Packages/manifest.json",b'{"dependencies":{}}\n')
    put("ProjectSettings/ProjectVersion.txt",("m_EditorVersion: "+EDITOR_VERSION+"\n").encode())
    put("ProjectSettings/ProjectSettings.asset",SETTINGS.encode())
    manifest=dict(schema_version=16,run_id=run_id,synthetic_only=True,source_V12_verified=False,historical_V12_opt_out_verified=True,V15_candidate_verified=True,shader_adapter=True,scene_route_replay=True,
        exporter_receipt_sha256=digest(audit.read_bytes()),exporter_patch_receipt_sha256=digest(patch.read_bytes()),
        candidate_rows=candidate_rows,manual_alpha_edit=False,prior_V14_run=45972362899,prior_V15_run=45975084812,
        original_assets_read=False,shader_program_parity_verified=False,scene_import_verified=False,
        textures=textures,routes=routes,scene_sources=scene_sources,shader_adapters=adapters,material_shader_pointer_adapters=material_adapters,
        staged_files={p:digest(v) for p,v in sorted(staged.items())})
    for p,raw in staged.items():
        target=project/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    m=project/"gt-normal-route-manifest.json";write(m,manifest)
    out.write_bytes(m.read_bytes())
    # Retain raw exported PNG/meta, not reconstructed metadata.
    for i,t in enumerate(textures):
        for suffix in ("",".meta"):
            raw=staged[t["path"]+suffix]
            p=out.parent/("candidate-"+str(i)+".png"+suffix)
            need(not p.exists(),"fresh_candidate_evidence")
            p.write_bytes(raw)
    print(json.dumps(dict(status="PREPARED_V16",routes=len(routes),textures=len(textures),staged_files=len(staged),manifest_sha256=digest(m.read_bytes()))))

def compare_mips(gpu,cpu,source,hist,raw_hist,readable):
    need(len(gpu)==3 and [len(x) for x in gpu]==[140,24,4],"observed_mip_population")
    hashes=[digest(x) for x in gpu]
    need(hashes==hist["alpha_off_mip_sha256"] and [x.hex() for x in gpu]==raw_hist["alpha_off"] and raw_hist["guid"]==hist["guid"],"V14_alpha_off_mip_bytes_drift")
    if readable:
        need(cpu==gpu[0] and cpu!=v14.flip(gpu[0],5,7),"unique_readable_CPU_GPU_orientation")
    else:need(cpu==b"","nonreadable_CPU_bypass")
    top=v14.comparison(v14.repack(source),v14.flip(gpu[0],5,7),source)
    need(top["matches"]==35,"corrected_top_mip_source_repack_drift")
    return hashes

def verify(m,r,run_id,exit_code):
    need(exit_code==0 and r.get("status")=="OBSERVED_AUTHORED_DIRECT_EXPORTER_REIMPORT","actual_Unity_candidate_probe_required:"+str(r.get("error","missing")))
    need(m["schema_version"]==16 and m["synthetic_only"] is True and m["V15_candidate_verified"] is True and m["historical_V12_opt_out_verified"] is True and m["source_V12_verified"] is False and m["manual_alpha_edit"] is False,"candidate_scope")
    need(r["run_id"]==m["run_id"]==run_id and r["editor"]==EDITOR_VERSION and r["backend"]=="Vulkan" and r["active_color_space"]=="Linear","actual_run_environment")
    need(r["unfiltered_compute_load"] is True and r["exact_exporter_meta_unchanged"] is True and r["scene_route_replay"] is True and r["shader_adapter"] is True and r["original_assets_read"] is False,"candidate_scope_or_metadata_drift")
    need(len(r["phases"])==1 and r["phases"][0]["name"]=="exporter_candidate","candidate_single_phase")
    # Adapter for V14's read-only route and settings checker; no patch data or
    # on/off mutation is staged or executed in V16.
    exact_meta={"texture_patches":[{"guid":t["guid"],"off_sha256":t["meta_sha256"]} for t in m["textures"]]}
    observed=v14.phase_data(m,exact_meta,r["phases"][0],False)
    h=read(v15.V14)
    need(h["status"]=="PASS_ACTUAL_AUTHORED_DXT5NM_ALPHA_POLICY_CAUSAL_TEXEL_WITNESS" and h["verified"]["actual_GPU_row_orientation"]=="bottom_first","V14_actual_reference")
    rows=[]
    for i,((gpu,cpu),t,candidate,prior,raw_prior,src) in enumerate(zip(observed,m["textures"],m["candidate_rows"],h["verified"]["rows"],h["independent"]["phase_mip_RGBA_hex"],h["source_and_actual"],strict=True)):
        need(candidate["source_key"]==["sharedassets3.assets",i+1] and candidate["guid"]==t["guid"] and candidate["file_id"]==t["file_id"] and candidate["png_sha256"]==t["sha256"]==PNG_SHA[i] and candidate["meta_sha256"]==t["meta_sha256"],"candidate_source_pointer_or_file_drift")
        source=bytes.fromhex(t["expected_rgba_hex"])
        need(src["source"]==t["expected_source"] and src["source_rgba_sha256"]==candidate["rgba_sha256"]==digest(source),"V14_source_identity_drift")
        hashes=compare_mips(gpu,cpu,source,prior,raw_prior,bool(t["expected_source"]["readable"]))
        rows.append(dict(candidate,observed_mip_dimensions=[list(x) for x in v14.DIMS],actual_mip_sha256=hashes,V14_alpha_off_mip_sha256=prior["alpha_off_mip_sha256"],actual_mip_RGBA_hex=[x.hex() for x in gpu],exact_top_pixels=35))
    need(len(rows)==2,"two_candidate_textures")
    return dict(status="PASS_ACTUAL_AUTHORED_V15_EXPORTER_DIRECT_UNITY_REIMPORT",actual_Unity_reimport_verified=True,
        actual_unfiltered_GPU_texels=84,top_mip_exact_pixels=70,actual_mip_hash_matches=6,renderer_route_matches=2,submesh_material_texture_matches=4,shader_adapter_identity_matches=4,
        exact_exporter_metadata_unchanged=True,manual_alpha_edit=False,rows=rows,actual_GPU_row_orientation="bottom_first",historical_V14_run=45972362899,historical_V15_run=45975084812,
        source_lower_mip_parity_verified=False,original_assets_read=False,scene_import_verified=False,original_shader_program_parity_verified=False,production_activation=False,Android_device=False,XAPK=False)

def controls(m,r,run_id):
    results={}
    def reject(name,mutate):
        q=deepcopy(r);mutate(q)
        try:verify(m,q,run_id,0)
        except (ValueError,KeyError,TypeError,AssertionError,OverflowError) as e:results[name]=str(e)
        else:raise ValueError("V16_control_not_rejected:"+name)
    reject("wrong_run",lambda q:q.update(run_id="wrong"))
    reject("metadata_changed",lambda q:q.update(exact_exporter_meta_unchanged=False))
    reject("old_alpha_policy",lambda q:q["phases"][0]["textures"][0].update(alpha_transparency=True))
    reject("texture_slot_swap",lambda q:q["phases"][0]["routes"][0]["textures"].reverse())
    reject("shader_adapter_swap",lambda q:q["phases"][0]["routes"][0]["shaders"].reverse())
    reject("file_id_drift",lambda q:q["phases"][0]["textures"][0]["identity"].update(file_id=1))
    reject("meta_hash_drift",lambda q:q["phases"][0]["textures"][0]["identity"].update(meta_sha256="0"*64))
    reject("other_sampler",lambda q:q["phases"][0]["textures"][0].update(aniso=999))
    reject("lower_mip_drift",lambda q:q["phases"][0]["textures"][0]["mips"][1].update(rgba_hex="00"*24))
    reject("nonreadable_CPU_fabrication",lambda q:q["phases"][0]["textures"][1].update(cpu_top_rgba_hex="00"*140))
    return results

def verify_files(m,manifest,audit,patch,project):
    need(digest(audit.read_bytes())==m["exporter_receipt_sha256"] and digest(patch.read_bytes())==m["exporter_patch_receipt_sha256"],"candidate_export_receipt_hash_binding")
    validate_replay(read(audit),read(patch),read(V15))
    need((project/"gt-normal-route-manifest.json").read_bytes()==manifest.read_bytes(),"Unity_manifest_file_drift")
    for p,h in m["staged_files"].items():
        if p.startswith("Assets/"):
            need(digest(regular_path(project/p).read_bytes())==h,"actual_staged_asset_bytes_drift:"+p)
    for i,t in enumerate(m["textures"]):
        need(digest(historical_meta_stable((manifest.parent/("candidate-"+str(i)+".png.meta")).read_bytes()))==m["candidate_rows"][i]["normalized_meta_sha256"],"retained_V15_normalized_metadata_drift")
        for suffix,field in (("","sha256"),(".meta","meta_sha256")):
            evidence=manifest.parent/("candidate-"+str(i)+".png"+suffix)
            need(evidence.read_bytes()==(project/(t["path"]+suffix)).read_bytes() and digest(evidence.read_bytes())==t[field],"retained_direct_exporter_file_drift")

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("stage")
    for n in ("root","project","receipt","audit","patch","out"):a.add_argument("--"+n,type=Path,required=True)
    a.add_argument("--run-id",required=True)
    a=s.add_parser("verify")
    for n in ("manifest","project","receipt","audit","patch","out"):a.add_argument("--"+n,type=Path,required=True)
    a.add_argument("--run-id",required=True);a.add_argument("--exit-code",type=int,required=True)
    a=p.parse_args()
    if a.cmd=="stage":stage(a.root,a.project,a.run_id,a.receipt,a.audit,a.patch,a.out);return
    need(not a.out.exists(),"fresh_V16_output")
    try:
        m,r=read(a.manifest),read(a.receipt)
        need(r["route_manifest_sha256"]==digest(a.manifest.read_bytes()),"actual_manifest_hash_binding")
        verify_files(m,a.manifest,a.audit,a.patch,a.project)
        result=verify(m,r,a.run_id,a.exit_code)
        result["actual_receipt_negative_controls"]=controls(m,r,a.run_id)
        result["actual_receipt_negative_control_count"]=len(result["actual_receipt_negative_controls"])
    except (ValueError,KeyError,TypeError,AssertionError,OSError,OverflowError) as e:
        result=dict(status="INCONCLUSIVE",reason=str(e),actual_Unity_reimport_verified=False,Android_device=False,XAPK=False)
    write(a.out,result);print(json.dumps(result,sort_keys=True))
    if result["status"]!="PASS_ACTUAL_AUTHORED_V15_EXPORTER_DIRECT_UNITY_REIMPORT":raise SystemExit(2)
if __name__=="__main__":main()
