#!/usr/bin/env python3
"""Independent offline archive inspection for V16, with no game data access.

Requires Pillow; input is the actual Actions ZIP and its reported SHA256.
Does not use the V16 runtime verifier or mutate any metadata.
"""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import re
import zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[4]
V14=ROOT/"clients/GT/sessions/20261127-dxt5nm-texel-policy-v14/actual-pass-45972362899.json"
V15=ROOT/"clients/GT/sessions/20261127-dxt5nm-alpha-exporter-v15/actual-pass-45975084812.json"
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(b):return hashlib.sha256(b).hexdigest()
def json_bytes(b):return json.loads(b.decode("utf-8"))
def meta_stable(raw):
    for p in (rb"(?m)^guid: [0-9a-f]{32}\r?$",rb"(?m)^timeCreated: [0-9]+\r?$"):
        raw,n=re.subn(p,b"<volatile>",raw)
        need(n==1,"volatile_header_population")
    return raw
def flip_top(raw):
    return b"".join(raw[y*20:(y+1)*20] for y in range(6,-1,-1))
def inspect(archive,digest,run,head,attempt):
    raw_zip=archive.read_bytes()
    need(len(raw_zip)<20*1024*1024 and sha(raw_zip)==digest,"archive_digest_or_size")
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:
        entries=z.infolist()
        need(0<len(entries)<200 and sum(x.file_size for x in entries)<50*1024*1024,"archive_extent")
        names=[x.filename for x in entries]
        need(len(names)==len(set(names)) and all(not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts and "\\" not in n for n in names),"unsafe_archive_names")
        need(z.testzip() is None,"archive_crc")
        files={n:z.read(n) for n in names if not n.endswith("/")}
    def load(n):return json_bytes(files[n])
    mname="normalmap-exporter-reimport-manifest.json"
    m=load(mname);r=load("normalmap-exporter-reimport-raw.json")
    v=load("normalmap-exporter-reimport-verified.json")
    a=load("alpha-exporter-actual.json");p=load("alpha-policy-patch.json")
    h14=json_bytes(V14.read_bytes());h15=json_bytes(V15.read_bytes())
    rid=f"{run}-{attempt}-{head}"
    need(m["run_id"]==r["run_id"]==rid and r["route_manifest_sha256"]==sha(files[mname]),"exact_immutable_run_manifest")
    need(m["exporter_receipt_sha256"]==sha(files["alpha-exporter-actual.json"]) and m["exporter_patch_receipt_sha256"]==sha(files["alpha-policy-patch.json"]),"actual_export_receipt_binding")
    need(p==h15["patch"],"actual_pinned_export_patch")
    build=load("build.json");need(build["head"]==head and str(build["run_id"])==str(run) and build["original_assets_read"] is False,"build_receipt_identity")
    need(m["schema_version"]==16 and m["manual_alpha_edit"] is False and m["historical_V12_opt_out_verified"] is True and m["source_V12_verified"] is False and m["V15_candidate_verified"] is True,"candidate_stage_scope")
    need(r["status"]=="OBSERVED_AUTHORED_DIRECT_EXPORTER_REIMPORT" and r["editor"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["active_color_space"]=="Linear" and r["unfiltered_compute_load"] is True and r["exact_exporter_meta_unchanged"] is True and r["original_assets_read"] is False and r["shader_adapter"] is True and r["scene_route_replay"] is True,"actual_Unity_observation_scope")
    need(v["status"]=="PASS_ACTUAL_AUTHORED_V15_EXPORTER_DIRECT_UNITY_REIMPORT" and v["actual_Unity_reimport_verified"] is True and v["exact_exporter_metadata_unchanged"] is True and v["actual_receipt_negative_control_count"]==10,"actual_verified_PASS")
    for flag in ("source_lower_mip_parity_verified","original_assets_read","original_shader_program_parity_verified","scene_import_verified","production_activation","Android_device","XAPK","manual_alpha_edit"):
        need(v[flag] is False,"unexpected_scope:"+flag)
    tests={}
    for name,b in files.items():
        if name.startswith("test_") and name.endswith(".log"):
            s=b.decode();q=re.search(r"^Ran (\d+) tests? in ",s,re.M)
            need(q is not None and re.search(r"^OK$",s,re.M),"regression_failure:"+name)
            tests[name]=int(q[1])
    report=load("normalmap-importer-report.json")
    need(len(tests)==19 and sum(tests.values())==291 and report["tests"]==tests and report["counterfactual_count"]==37,"regression_population")
    need(a["status"]==h15["status"] and a["actual_compiled_exporter_modes"]==6 and a["actual_normalmap_policy_changes"]==2 and a["actual_ordinary_policy_unchanged"]==4 and a["actual_metadata_control_count"]==6 and a["production_activation"] is False,"six_export_modes_scope")
    old={(x["mode"],tuple(x["source_key"])):x for x in h15["independent"]["six_pair_rows"]}
    need(set(a["scopes"])=={"normal","bc3","rgba"} and len(old)==6,"historical_six_pairs")
    for mode,scope in a["scopes"].items():
        need(len(scope["rows"])==2,"pair_count")
        for pair in scope["rows"]:
            b,c=pair["before"],pair["after"];hist=old.pop((mode,tuple(c["key"])))
            need(b["key"]==c["key"] and b["ptr"][1:]==c["ptr"][1:] and b["alpha"]==hist["alpha_before"] and c["alpha"]==hist["alpha_after"],"policy_or_pointer")
            for tag,side in (("before",b),("after",c)):
                need(sha(bytes.fromhex(side["rgba_hex"]))==side["rgba_sha256"]==hist["rgba_sha256"] and side["png_sha256"]==hist["png_sha256"] and sha(meta_stable(side["metadata"].encode()))==hist["normalized_"+tag+"_sha256"],"historical_V15_bytes")
            before=meta_stable(b["metadata"].encode());after=meta_stable(c["metadata"].encode())
            if mode=="normal":
                expected,n=re.subn(rb"(?m)^  alphaIsTransparency: 1$",b"  alphaIsTransparency: 0",before)
                need(n==1 and after==expected,"normal_meta_non_policy_drift")
            else:need(after==before,"ordinary_meta_drift")
    need(not old and a["scopes"]["normal"]["historical_V12_actual_candidate_rejected"] is True and a["scopes"]["normal"]["historical_V12_restored_counterfactual_only"] is True,"separate_V12_policy")
    need(len(r["phases"])==1 and r["phases"][0]["name"]=="exporter_candidate","candidate_phase")
    ph=r["phases"][0]
    def identity(x,y):
        need(all(x[k]==y[k] for k in ("path","guid","file_id","sha256","meta_sha256")),"actual_route_identity")
    need(len(ph["routes"])==len(m["routes"])==2,"renderer_count")
    for obs,exp in zip(ph["routes"],m["routes"],strict=True):
        need(obs["key"]==exp["key"] and all(obs[k]==exp[k] for k in ("vertex_count","index_counts","base_vertices")),"mesh_layout")
        need(len(obs["uv"])==len(exp["uv"])==8 and all(abs(x-y)<1e-6 for x,y in zip(obs["uv"],exp["uv"],strict=True)),"route_UV")
        identity(obs["mesh"],exp["mesh"])
        for k in ("materials","textures","shaders"):
            need(len(obs[k])==len(exp[k])==2,"slot_population")
            for x,y in zip(obs[k],exp[k],strict=True):identity(x,y)
    rows=[];max_error=0
    dims=((5,7),(2,3),(1,1))
    need(len(m["textures"])==len(ph["textures"])==len(v["rows"])==2,"texture_count")
    for i,(tex,obs,checked,pair,prior,prior_raw) in enumerate(zip(m["textures"],ph["textures"],v["rows"],a["scopes"]["normal"]["rows"],h14["verified"]["rows"],h14["independent"]["phase_mip_RGBA_hex"],strict=True)):
        png=files[f"candidate-{i}.png"];meta=files[f"candidate-{i}.png.meta"];after=pair["after"]
        need(sha(png)==tex["sha256"]==after["png_sha256"] and sha(meta)==tex["meta_sha256"] and meta.decode("utf-8-sig")==after["metadata"],"actual_candidate_file_bytes")
        need(after["ptr"][:2]==[tex["guid"],tex["file_id"]] and after["key"]==["sharedassets3.assets",i+1] and re.findall(rb"(?m)^  alphaIsTransparency: (\d+)$",meta)==[b"0"],"actual_candidate_GUID_alpha_policy")
        with Image.open(io.BytesIO(png)) as im:
            need(im.mode=="RGBA" and im.size==(5,7),"candidate_png_shape")
            rgba=im.tobytes()
        need(sha(rgba)==after["rgba_sha256"] and rgba.hex()==tex["expected_rgba_hex"],"candidate_png_RGBA")
        identity(obs["identity"],tex)
        need(obs["alpha_transparency"] is False and obs["type"]==1 and obs["format"]=="RGBA32" and obs["graphics_format"]=="R8G8B8A8_UNorm" and obs["mip_count"]==3 and len(obs["mips"])==3,"candidate_runtime_import")
        hashes=[];hexes=[]
        for level,(mp,(w,h)) in enumerate(zip(obs["mips"],dims,strict=True)):
            need((mp["level"],mp["width"],mp["height"])==(level,w,h),"mip_dimensions")
            pix=bytes.fromhex(mp["rgba_hex"]);err=mp["max_unorm_error"]
            need(len(pix)==w*h*4 and math.isfinite(err) and 0<=err<=1e-6,"mip_readback_extent_or_precision")
            max_error=max(max_error,err);hashes.append(sha(pix));hexes.append(pix.hex())
        need(hashes==prior["alpha_off_mip_sha256"]==checked["actual_mip_sha256"]==checked["V14_alpha_off_mip_sha256"] and hexes==prior_raw["alpha_off"]==checked["actual_mip_RGBA_hex"],"V14_alpha_off_mip_bytes")
        top=bytes.fromhex(hexes[0]);cpu=bytes.fromhex(obs["cpu_top_rgba_hex"])
        packed=bytes(q for x,y,z,a0 in zip(*[iter(rgba)]*4) for q in (255,y,y,x))
        need(flip_top(top)==packed,"top_mip_exact_source_repack")
        if tex["expected_source"]["readable"]:
            need(cpu==top and cpu!=flip_top(top),"CPU_GPU_orientation")
        else:need(cpu==b"" and obs["cpu_status"]=="not_readable_as_imported","nonreadable_CPU_bypass")
        rows.append(dict(source_key=after["key"],guid=tex["guid"],file_id=tex["file_id"],png_sha256=sha(png),meta_sha256=sha(meta),rgba_sha256=sha(rgba),actual_mip_sha256=hashes,actual_mip_RGBA_hex=hexes))
    return dict(status=v["status"],run=run,head=head,attempt=attempt,actual_regressions=291,actual_V11_V12_controls=37,actual_V15_controls=6,actual_V16_controls=10,actual_mip_hash_matches=6,actual_GPU_texels=84,top_mip_exact_pixels=70,max_unorm_error=max_error,renderer_route_matches=2,submesh_material_texture_matches=4,shader_adapter_matches=4,archive=dict(bytes=len(raw_zip),sha256=sha(raw_zip),crc_verified=True,member_count=len(files),member_sha256={n:sha(b) for n,b in sorted(files.items())}),rows=rows,original_assets_read=False,source_lower_mip_parity_verified=False,production_activation=False,Android_device=False,XAPK=False)
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True,type=Path)
    p.add_argument("--sha256",required=True)
    p.add_argument("--run",required=True,type=int)
    p.add_argument("--head",required=True)
    p.add_argument("--attempt",type=int,default=1)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    need(not a.out.exists(),"fresh_inspection_receipt_required")
    result=inspect(a.archive,a.sha256,a.run,a.head,a.attempt)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("rows","archive")},sort_keys=True))
if __name__=="__main__":main()
