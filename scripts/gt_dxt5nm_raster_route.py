"""V17 authored-only raster route witness from V16's real exporter candidate.

Only the two diagnostic shader adapters are replaced in the isolated staged
project. Texture/mesh/material bytes and all their metadata are untouched.
Explicit integer fragment Load/repeat is diagnostic, NOT native sampler parity.
"""
import argparse
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools/gt_dxt5nm_raster_route"
V16=ROOT/"clients/GT/sessions/20261127-dxt5nm-exporter-reimport-v16/actual-pass-45977510081.json"
V16_SHA="078b5db2b1453a52e249d73ef5e7859e4f955acfd7d831dd4b7f5f3e702910c2"
W,H=32,16
CLEAR=(-4.,)*4
VERTICES=[-2,-1,0,-.5,-1,0,-2,1,0,-.5,-1,0,2,-1,0,2,1,0]
UV0=[0,0,1,0,0,1,1,0,0,0,0,1]
INDICES=((0,1,2),(3,5,4))
DIMENSIONS=((5,7),(2,3),(1,1))
TOL=3e-5
NORMAL_TOL=.004
UV_SHIFT=.3125

def need(ok,why):
    if not ok:raise ValueError(why)
def digest(raw):return hashlib.sha256(raw).hexdigest()
def read(path):return json.loads(Path(path).read_bytes())
def write(path,value):
    need(not path.exists(),"fresh_receipt")
    path.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+"\n")
def prior():
    raw=V16.read_bytes();need(digest(raw)==V16_SHA,"V16_receipt_bytes")
    p=json.loads(raw)
    need(p["status"]=="PASS_ACTUAL_AUTHORED_V15_EXPORTER_DIRECT_UNITY_REIMPORT" and p["actual_Unity_reimport_verified"] is True and p["actual_mip_hash_matches"]==6 and p["top_mip_exact_pixels"]==70 and p["production_activation"] is False,"V16_actual_PASS")
    return p
def shader_bytes(i):
    need(i in (0,1),"adapter_number")
    template=(TOOLS/"RasterAdapter.shader.txt").read_text()
    need(template.count("__ADAPTER_NAME__")==1 and template.count("__ADAPTER_MARKER__")==1,"adapter_template_tokens")
    return template.replace("__ADAPTER_NAME__","GT/V17/RasterAdapter"+str(i)).replace("__ADAPTER_MARKER__",str(.25+.5*i)).encode()
def historical_rows(m,p):
    rows={tuple(x["source_key"]):x for x in p["rows"]}
    need(len(rows)==len(m["candidate_rows"])==len(m["textures"])==2,"candidate_population")
    for t,c in zip(m["textures"],m["candidate_rows"],strict=True):
        h=rows[tuple(c["source_key"])]
        for k in ("file_id","png_sha256","rgba_sha256","normalized_meta_sha256"):need(c[k]==h[k],"V16_candidate_drift:"+k)
        need(c["guid"]==t["guid"] and c["file_id"]==t["file_id"] and c["png_sha256"]==t["sha256"] and c["meta_sha256"]==t["meta_sha256"],"candidate_identity")
        need(digest(bytes.fromhex(t["expected_rgba_hex"]))==c["rgba_sha256"],"candidate_source_RGBA")
        for hx,hs in zip(h["actual_mip_RGBA_hex"],h["actual_mip_sha256"],strict=True):need(digest(bytes.fromhex(hx))==hs,"V16_mip_receipt")
    return {t["guid"]:rows[tuple(c["source_key"])] for t,c in zip(m["textures"],m["candidate_rows"],strict=True)}

def prepare(project,base,out,run_id):
    project=Path(project).resolve();base=Path(base);out=Path(out)
    raw=base.read_bytes();m0=json.loads(raw);m=deepcopy(m0);p=prior()
    need((project/"gt-normal-route-manifest.json").read_bytes()==raw and m0["schema_version"]==16 and m0["run_id"]==run_id and m0["synthetic_only"] is True and m0["V15_candidate_verified"] is True and m0["manual_alpha_edit"] is False and not m0["original_assets_read"],"fresh_V16_stage")
    historical_rows(m0,p)
    for path,h in m0["staged_files"].items():need(digest((project/path).read_bytes())==h,"V16_stage_file_drift:"+path)
    m.update(schema_version=17,base_V16_stage_manifest_sha256=digest(raw),prior_actual_V16_receipt_sha256=V16_SHA,explicit_fragment_integer_repeat_load=True,native_sampler_parity_verified=False,raster_adapters=[])
    unique={}
    for route in m["routes"]:
        for sh in route["shaders"]:
            unique.setdefault(sh["path"],sh)
    need(set(unique)=={"Assets/GTAdapters/Adapter0.shader","Assets/GTAdapters/Adapter1.shader"},"two_explicit_adapters")
    for i,path in enumerate(sorted(unique)):
        old=unique[path];data=shader_bytes(i);replacement=digest(data)
        need(old["sha256"]==m0["staged_files"][path] and old["file_id"]==4800000,"baseline_adapter_identity")
        m["raster_adapters"].append(dict(path=path,guid=old["guid"],file_id=old["file_id"],meta_sha256=old["meta_sha256"],baseline_shader_sha256=old["sha256"],diagnostic_shader_sha256=replacement,marker=.25+.5*i))
        (project/path).write_bytes(data);m["staged_files"][path]=replacement
        for route in m["routes"]:
            for sh in route["shaders"]:
                if sh["path"]==path:sh["sha256"]=replacement
    editor="Assets/Editor/SyntheticNormalRasterRoute.cs";data=(TOOLS/"SyntheticNormalRasterRoute.cs").read_bytes()
    need(not (project/editor).exists(),"fresh_raster_editor")
    (project/editor).write_bytes(data);m["staged_files"][editor]=digest(data)
    write(project/"gt-normal-raster-manifest.json",m)
    need(not out.exists(),"fresh_raster_manifest")
    out.write_bytes((project/"gt-normal-raster-manifest.json").read_bytes())
    print(json.dumps(dict(status="PREPARED_V17",manifest_sha256=digest(out.read_bytes()),raster_adapters=m["raster_adapters"],manual_alpha_edit=False),sort_keys=True))

def geometry(slot,x,y,orientation):
    need(slot in (0,1) and orientation in ("bottom_first","top_first"),"geometry_args")
    yy=y if orientation=="bottom_first" else H-1-y
    px=(x+.5)*4/W-2;py=(yy+.5)*2/H-1
    a,b,c=INDICES[slot]
    ax,ay=VERTICES[3*a:3*a+2];bx,by=VERTICES[3*b:3*b+2];cx,cy=VERTICES[3*c:3*c+2]
    d=(by-cy)*(ax-cx)+(cx-bx)*(ay-cy)
    u=((by-cy)*(px-cx)+(cx-bx)*(py-cy))/d
    v=((cy-ay)*(px-cx)+(ax-cx)*(py-cy))/d;w=1-u-v
    if min(u,v,w)<-1e-7:return "outside",None
    if min(u,v,w)<=1e-7:return "edge",None
    return "inside",tuple(u*UV0[2*a+k]+v*UV0[2*b+k]+w*UV0[2*c+k] for k in (0,1))
def transformed(uv,st):return uv[0]*st[0]+st[2],uv[1]*st[1]+st[3]
def close(a,b,tol=TOL):
    return len(a)==len(b) and all(type(x) in (float,int) and math.isfinite(x) and abs(x-y)<=tol for x,y in zip(a,b,strict=True))
def pixels(values):
    need(type(values) is list and len(values)==W*H*4 and all(type(x) in (float,int) and math.isfinite(x) for x in values),"actual_float_RT_population")
    return [tuple(values[i:i+4]) for i in range(0,len(values),4)]
def uv_oracle(slot,st,orientation,values):
    actual=pixels(values);inside=outside=0
    for n,a in enumerate(actual):
        kind,uv=geometry(slot,n%W,n//W,orientation)
        if kind=="outside":need(close(a,CLEAR),"raster_outside_coverage");outside+=1
        elif kind=="inside":need(close(a,(*uv,*transformed(uv,st))),"raster_UV_or_transform");inside+=1
    need(inside>=70 and outside>=200,"raster_coverage_population")
    return inside,outside
def point_load(uv,w,h,rgba):
    q=[(u-math.floor(u))*d for u,d in zip(uv,(w,h),strict=True)]
    # Exclude exact texel boundaries only; do not choose per-pixel rounding.
    if any(abs(t-round(t))<2e-5 for t in q):return None
    idx=4*(math.floor(q[1])*w+math.floor(q[0]))
    return tuple(x/255 for x in rgba[idx:idx+4])
def unpack(p,marker):
    x=p[0]*p[3]*2-1;y=p[1]*2-1
    return x,y,math.sqrt(max(0,1-min(1,x*x+y*y))),marker
def color_oracle(slot,st,orientation,values,rgba,level,marker=None):
    actual=pixels(values);w,h=DIMENSIONS[level]
    need(len(rgba)==4*w*h,"mip_extent")
    checked=[];outside=0;max_error=0
    for n,a in enumerate(actual):
        kind,uv=geometry(slot,n%W,n//W,orientation)
        if kind=="outside":need(close(a,CLEAR),"fragment_outside_coverage");outside+=1
        elif kind=="inside":
            need(not close(a,CLEAR),"fragment_missing_coverage")
            expected=point_load(transformed(uv,st),w,h,rgba)
            if expected is None:continue
            if marker is not None:expected=unpack(expected,marker)
            need(close(a,expected,NORMAL_TOL if marker is not None else 1e-6),"fragment_normal_or_packed_drift")
            max_error=max(max_error,max(abs(x-y) for x,y in zip(a,expected,strict=True)));checked.append(n)
    need(len(checked)>=40 and outside>=200,"fragment_nonboundary_population")
    return checked,max_error
def identity(a,b):
    need(all(a[k]==b[k] for k in ("path","guid","file_id","sha256","meta_sha256")),"actual_same_route_identity")
def verify(m,r,run_id,exit_code,p):
    need(exit_code==0 and r["status"]=="OBSERVED_AUTHORED_DIRECT_RASTER_ROUTE" and r["run_id"]==m["run_id"]==run_id,"actual_Unity_raster_required")
    need(m["schema_version"]==17 and m["prior_actual_V16_receipt_sha256"]==V16_SHA and m["manual_alpha_edit"] is False and m["explicit_fragment_integer_repeat_load"] is True and m["native_sampler_parity_verified"] is False,"V17_scope")
    need(r["editor"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["active_color_space"]=="Linear" and r["width"]==W and r["height"]==H and r["explicit_fragment_integer_repeat_load"] is True and r["exact_candidate_metadata_unchanged"] is True and r["original_assets_read"] is False,"actual_raster_environment")
    historical=historical_rows(m,p);markers={x["guid"]:x["marker"] for x in m["raster_adapters"]}
    need(len(r["routes"])==len(m["routes"])==2 and len(markers)==2,"actual_renderer_population")
    tasks=[]
    for o,e in zip(r["routes"],m["routes"],strict=True):
        need(o["key"]==e["key"] and o["vertex_count"]==e["vertex_count"]==6 and o["index_counts"]==e["index_counts"]==[3,3] and o["base_vertices"]==e["base_vertices"]==[0,3],"actual_mesh_layout")
        identity(o["mesh"],e["mesh"]);need(close(o["positions"],VERTICES) and close(o["uv0"],UV0),"actual_mesh_position_UV_bytes")
        need(len(o["slots"])==2,"actual_slot_population")
        for i,s in enumerate(o["slots"]):
            need(s["slot"]==i and s["indices"]==list(INDICES[i]),"actual_submesh_indices")
            identity(s["material"],e["materials"][i]);identity(s["texture"],e["textures"][i]);identity(s["shader"],e["shaders"][i])
            need(close(s["uv_transform"],e["uv"][4*i:4*i+4]) and s["alpha_transparency"] is False and s["mip_count"]==3 and s["format"]=="RGBA32" and s["graphics_format"]=="R8G8B8A8_UNorm","actual_material_importer_state")
            tasks.append((o["key"],i,s,historical[s["texture"]["guid"]],markers[s["shader"]["guid"]]))
    orientations=[]
    for orientation in ("bottom_first","top_first"):
        try:
            for _,i,s,_,_ in tasks:uv_oracle(i,s["uv_transform"],orientation,s["uv_pixels"])
        except ValueError:continue
        orientations.append(orientation)
    need(len(orientations)==1,"unique_geometry_anchored_RT_orientation");orientation=orientations[0]
    rows=[];packed_count=normal_count=0;max_p=max_n=0;control_counts={}
    for key,i,s,h,marker in tasks:
        st=s["uv_transform"];inside,outside=uv_oracle(i,st,orientation,s["uv_pixels"]);row=dict(route=key,slot=i,texture_guid=s["texture"]["guid"],shader_guid=s["shader"]["guid"],marker=marker,geometry_inside=inside,geometry_outside=outside,mips=[])
        need(len(s["mips"])==3,"actual_mip_draw_population")
        for level,mp in enumerate(s["mips"]):
            need(mp["level"]==level,"actual_draw_mip_order")
            raw=bytes.fromhex(h["actual_mip_RGBA_hex"][level])
            ix,pe=color_oracle(i,st,orientation,mp["packed"],raw,level)
            nx,ne=color_oracle(i,st,orientation,mp["normal"],raw,level,marker)
            need(ix==nx,"same_pixel_population")
            packed_count+=len(ix);normal_count+=len(nx);max_p=max(max_p,pe);max_n=max(max_n,ne)
            row["mips"].append(dict(level=level,checked_pixels=len(ix),max_packed_error=pe,max_normal_error=ne))
        if key=="level1" and i==0:
            other=next(v for guid,v in historical.items() if guid!=s["texture"]["guid"])
            base_raw=bytes.fromhex(h["actual_mip_RGBA_hex"][0]);other_raw=bytes.fromhex(other["actual_mip_RGBA_hex"][0])
            ix,_=color_oracle(i,st,orientation,s["wrong_texture"],other_raw,0)
            uv=list(st);uv[2]+=UV_SHIFT
            nx,_=color_oracle(i,uv,orientation,s["wrong_uv"],base_raw,0)
            base=pixels(s["mips"][0]["packed"]);wt=pixels(s["wrong_texture"]);wu=pixels(s["wrong_uv"])
            baseline_ix,_=color_oracle(i,st,orientation,s["mips"][0]["packed"],base_raw,0)
            control_counts["wrong_texture_changed_pixels"]=sum(not close(base[n],wt[n],1e-6) for n in set(ix)&set(baseline_ix))
            control_counts["wrong_UV_changed_pixels"]=sum(not close(base[n],wu[n],1e-6) for n in set(nx)&set(baseline_ix))
            need(min(control_counts.values())>=10 and s["restored_packed"]==s["mips"][0]["packed"],"actual_controls_non_degenerate_and_restored")
        else:need(not s.get("wrong_texture") and not s.get("wrong_uv") and not s.get("restored_packed"),"unexpected_control_scope")
        rows.append(row)
    need(len(rows)==4 and len(control_counts)==2 and packed_count==normal_count and packed_count>=480,"raster_checked_population")
    return dict(status="PASS_ACTUAL_AUTHORED_V16_CANDIDATE_RASTER_ROUTE",actual_Unity_raster_verified=True,geometry_anchored_RT_orientation=orientation,renderer_routes=2,submesh_draw_routes=4,actual_packed_pixels=packed_count,actual_normal_pixels=normal_count,max_packed_error=max_p,max_normal_error=max_n,actual_pixel_controls=control_counts,rows=rows,original_assets_read=False,production_activation=False,source_lower_mip_parity_verified=False,original_shader_program_parity_verified=False,scene_import_verified=False,native_sampler_parity_verified=False,Android_device=False,XAPK=False)
def controls(m,r,run_id,p):
    results={}
    def reject(name,mutation):
        q=deepcopy(r);mutation(q)
        try:verify(m,q,run_id,0,p)
        except (ValueError,KeyError,TypeError,IndexError) as e:results[name]=str(e)
        else:raise ValueError("V17_control_not_rejected:"+name)
    reject("texture_pointer_drift",lambda q:q["routes"][0]["slots"][0]["texture"].update(guid="0"*32))
    reject("shader_identity_swap",lambda q:q["routes"][0]["slots"][0].update(shader=q["routes"][0]["slots"][1]["shader"]))
    reject("UV_drift",lambda q:q["routes"][0]["slots"][0]["uv_transform"].__setitem__(2,.99))
    reject("mesh_index_drift",lambda q:q["routes"][0]["slots"][0]["indices"].reverse())
    reject("raster_packed_corruption",lambda q:q["routes"][0]["slots"][0]["mips"][0].update(packed=[0.]*(W*H*4)))
    reject("normal_branch_corruption",lambda q:q["routes"][0]["slots"][0]["mips"][0].update(normal=[0.]*(W*H*4)))
    reject("actual_wrong_texture_control_missing",lambda q:q["routes"][0]["slots"][0].update(wrong_texture=q["routes"][0]["slots"][0]["mips"][0]["packed"]))
    return results
def verify_files(project,base,manifest,m):
    raw=base.read_bytes();m0=json.loads(raw)
    need(m["base_V16_stage_manifest_sha256"]==digest(raw) and (project/"gt-normal-route-manifest.json").read_bytes()==raw and (project/"gt-normal-raster-manifest.json").read_bytes()==manifest.read_bytes(),"actual_manifest_files")
    need(m["textures"]==m0["textures"] and m["candidate_rows"]==m0["candidate_rows"],"V16_texture_records_unchanged")
    for file,key in (("alpha-exporter-actual.json","exporter_receipt_sha256"),("alpha-policy-patch.json","exporter_patch_receipt_sha256")):
        need(digest((manifest.parent/file).read_bytes())==m[key]==m0[key],"actual_export_receipt_bytes")
    restored=deepcopy(m["routes"]);adapters={x["path"]:x for x in m["raster_adapters"]}
    for rt in restored:
        for sh in rt["shaders"]:
            a=adapters[sh["path"]]
            need(sh["sha256"]==a["diagnostic_shader_sha256"] and sh["guid"]==a["guid"] and sh["meta_sha256"]==a["meta_sha256"] and sh["file_id"]==a["file_id"],"diagnostic_adapter_identity")
            sh["sha256"]=a["baseline_shader_sha256"]
    need(restored==m0["routes"],"only_declared_shader_adapter_changed")
    need(set(m["staged_files"])-set(m0["staged_files"])=={"Assets/Editor/SyntheticNormalRasterRoute.cs"},"new_stage_file_scope")
    for i,path in enumerate(sorted(adapters)):
        a=adapters[path]
        need(digest(shader_bytes(i))==a["diagnostic_shader_sha256"]==m["staged_files"][path] and a["marker"]==.25+.5*i,"pinned_diagnostic_shader_bytes")
    for name,h in m0["staged_files"].items():
        if name not in adapters:need(m["staged_files"][name]==h,"non_adapter_stage_drift")
    for name,h in m["staged_files"].items():
        if name.startswith("Assets/"):need(digest((project/name).read_bytes())==h,"post_Unity_stage_file_drift:"+name)
    for i,t in enumerate(m["textures"]):
        for suffix,key in (("","sha256"),(".meta","meta_sha256")):
            data=(manifest.parent/("candidate-"+str(i)+".png"+suffix)).read_bytes()
            need(data==(project/(t["path"]+suffix)).read_bytes() and digest(data)==t[key],"actual_candidate_file_drift")

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("prepare")
    for k in ("project","base","out"):a.add_argument("--"+k,type=Path,required=True)
    a.add_argument("--run-id",required=True)
    a=s.add_parser("verify")
    for k in ("project","base","manifest","receipt","out"):a.add_argument("--"+k,type=Path,required=True)
    a.add_argument("--run-id",required=True);a.add_argument("--exit-code",type=int,required=True)
    a=p.parse_args()
    if a.cmd=="prepare":prepare(a.project,a.base,a.out,a.run_id);return
    try:
        m=read(a.manifest);r=read(a.receipt);need(r["raster_manifest_sha256"]==digest(a.manifest.read_bytes()),"actual_raster_manifest_binding")
        verify_files(a.project,a.base,a.manifest,m);p=prior();result=verify(m,r,a.run_id,a.exit_code,p);result["actual_receipt_negative_controls"]=controls(m,r,a.run_id,p)
    except (ValueError,KeyError,TypeError,IndexError,OSError) as e:
        result=dict(status="INCONCLUSIVE",reason=str(e),actual_Unity_raster_verified=False,original_assets_read=False,production_activation=False,Android_device=False,XAPK=False)
    write(a.out,result);print(json.dumps(result,sort_keys=True))
    if result["status"]!="PASS_ACTUAL_AUTHORED_V16_CANDIDATE_RASTER_ROUTE":raise SystemExit(2)
if __name__=="__main__":main()
