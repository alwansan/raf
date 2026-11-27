"""Independent authored mesh route Vulkan oracle. No original pixels."""
from copy import deepcopy
import argparse
import json
import math
import re
import struct
import zlib
from pathlib import Path

from scripts.gt_synthetic_material_alpha import regular_path, SETTINGS, EDITOR_VERSION
from scripts.gt_imported_alpha_pixels import digest, strict_json

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools/synthetic_material_alpha"
WIDTH,HEIGHT=8,4
SHADER_A="Assets/AuthoredRouteA.shader"
SHADER_B="Assets/AuthoredRouteB.shader"
PNG_A="Assets/AuthoredRouteA.png"
PNG_B="Assets/AuthoredRouteB.png"
MAT_A="Assets/AuthoredRouteA.mat"
MAT_B="Assets/AuthoredRouteB.mat"
MESH="Assets/AuthoredRoute.asset"
DECOY="Assets/AuthoredRouteDecoy.asset"
PROBE="Assets/Editor/SyntheticSubmeshRouteValidation.cs"
INPUTS=[SHADER_A,SHADER_B,PNG_A,PNG_B,PROBE]
VERTICES=[-2,-1,0,-.5,-1,0,-.5,1,0,-2,1,0,-.5,-1,0,2,-1,0,2,1,0,-.5,1,0]
UV=[0,0,1,0,1,1,0,1,1,0,0,0,0,1,1,1]
INDICES=[0,1,2,0,2,3]
BASE=[
    dict(material=MAT_A,shader=SHADER_A,texture=PNG_A,tint=[.8,.5,.25,1],scale=[.58,.65],offset=[.09,.07]),
    dict(material=MAT_B,shader=SHADER_B,texture=PNG_B,tint=[.4,.9,.7,1],scale=[.76,.70],offset=[.11,.13])
]
NAMES=("baseline","swapped_materials","reversed_mesh_routes","wrong_valid_texture","white_texture",
       "missing_texture","UV_transform_drift","wrong_valid_shader","tint_drift","restored_baseline")
TOL=.008


def case_spec(name):
    if name not in NAMES:raise ValueError("unknown_case")
    slots=deepcopy(BASE)
    mesh=MESH
    if name=="swapped_materials":slots.reverse()
    elif name=="reversed_mesh_routes":mesh=DECOY
    elif name=="wrong_valid_texture":slots[0]["texture"]=PNG_B
    elif name=="white_texture":slots[0]["texture"]="explicit_white"
    elif name=="missing_texture":slots[0]["texture"]="null"
    elif name=="UV_transform_drift":slots[0]["offset"]=[.41,.07]
    elif name=="wrong_valid_shader":slots[0]["shader"]=SHADER_B
    elif name=="tint_drift":slots[0]["tint"]=[1.,1.,1.,1.]
    return mesh,slots


def texel(path,x,y):
    if path==PNG_A:return [32+45*x+11*y,180-23*x-37*y,24+19*x+81*y,255]
    if path==PNG_B:return [191-31*x-53*y,18+44*x+12*y,205-29*x+12*y,255]
    if path in ("null","explicit_white"):return [255]*4
    raise ValueError("unknown_texture")


def png_bytes(path):
    def chunk(tag,data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
    raw=b"".join(b"\0"+bytes(v for x in range(4) for v in texel(path,x,y)) for y in (1,0))
    return b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",4,2,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(raw,9))+chunk(b"IEND",b"")


def candidates():
    return {SHADER_A:(TOOLS/"AuthoredRouteA.shader").read_bytes(),SHADER_B:(TOOLS/"AuthoredRouteB.shader").read_bytes(),
            PNG_A:png_bytes(PNG_A),PNG_B:png_bytes(PNG_B),PROBE:(TOOLS/"SyntheticSubmeshRouteValidation.cs").read_bytes()}


def hashes():return {k:digest(v) for k,v in candidates().items()}


def stage(project):
    project=regular_path(project)
    if project.exists() or not project.parent.is_dir():raise ValueError("fresh_project_required")
    files=candidates()
    files.update({"Packages/manifest.json":b'{"dependencies":{}}\n',
                  "ProjectSettings/ProjectVersion.txt":("m_EditorVersion: "+EDITOR_VERSION+"\n").encode(),
                  "ProjectSettings/ProjectSettings.asset":SETTINGS.encode()})
    for k,v in files.items():
        p=project/k;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(v)
    return dict(status="PREPARED",source_hashes=hashes(),Unity_render_executed=False)


def expected_pixel(name,x,y):
    mesh,slots=case_spec(name)
    side=int(x>=3)
    slot=slots[side if mesh==MESH else 1-side]
    u=(x+.5)/3 if side==0 else 1-(x-3+.5)/5
    v=(y+.5)/4
    u=u*slot["scale"][0]+slot["offset"][0]
    v=v*slot["scale"][1]+slot["offset"][1]
    raw=texel(slot["texture"],min(3,max(0,math.floor(u*4))),min(1,max(0,math.floor(v*2))))
    rgb=raw[:3] if slot["shader"]==SHADER_A else raw[:3][::-1]
    return [c/255*t for c,t in zip(rgb,slot["tint"][:3])]+[1.]


def need(test,reason):
    if not test:raise ValueError(reason)


def eq(row,key,wanted):
    need(type(row.get(key)) is type(wanted) and row[key]==wanted,"receipt_contract:"+key)


def vector(raw,expected,tol=1e-6):
    need(type(raw) is list and len(raw)==len(expected) and all(type(v) in (float,int) and math.isfinite(v) for v in raw),"finite_vector_required")
    err=max(abs(a-b) for a,b in zip(raw,expected))
    need(err<=tol,"numeric_vector_mismatch")
    return err


def identity(row,key,table,name):
    guid=row.get(key)
    need(type(guid) is str and re.fullmatch("[0-9a-f]{32}",guid) and guid!="0"*32,"persistent_asset_GUID_required")
    need(table.setdefault(name,guid)==guid,"asset_identity_changed")
    return guid


def validate(report,run_id,source_hashes,exit_code):
    need(type(report) is dict and type(exit_code) is int and exit_code==0,"actual_successful_Unity_process_required")
    for k,v in dict(schema_version=1,run_id=run_id,status="OBSERVED",Unity_version=EDITOR_VERSION,
                    backend="Vulkan",active_color_space="Linear",synthetic_only=True,Unity_render_executed=True,
                    Android_device=False,production_pixels=False,XAPK=False,source_paths=INPUTS,
                    source_sha256_before=[source_hashes[p] for p in INPUTS],
                    source_sha256_after=[source_hashes[p] for p in INPUTS]).items():eq(report,k,v)
    need(isinstance(report.get("graphics_device_name"),str) and report["graphics_device_name"].strip(),"graphics_device_required")
    imported=report.get("imported")
    need(type(imported) is list and len(imported)==2,"two_actual_imports_required")
    assets={};instances={};seen=set()
    for row in imported:
        path=row.get("path")
        need(path in (PNG_A,PNG_B) and path not in seen,"unique_imported_texture_required")
        seen.add(path);identity(row,"guid",assets,path)
        for k,v in dict(filter="Point",wrap="Clamp",shape="Texture2D",alpha_source="FromInput",
                        compression="Uncompressed",srgb=False,graphics_srgb=False,readable=True,mipmaps=False,
                        width=4,height=2,mip_count=1).items():eq(row,k,v)
        need(row.get("format") in ("RGB24","RGBA32","ARGB32","BGRA32"),"uncompressed_import_required")
        eq(row,"rgba8",[c for y in range(2) for x in range(4) for c in texel(path,x,y)])
    rows=report.get("cases")
    need(type(rows) is list and len(rows)==len(NAMES),"complete_case_population_required")
    errors={};diffs={};all_pixels={}
    for row,name in zip(rows,NAMES,strict=True):
        eq(row,"name",name);mesh,slots=case_spec(name);eq(row,"mesh",mesh)
        identity(row,"mesh_guid",assets,mesh)
        mid=row.get("mesh_instance");need(type(mid) is int and mid!=0 and instances.setdefault(mesh,mid)==mid,"mesh_instance_changed")
        bases=[0,4] if mesh==MESH else [4,0]
        for k,v in dict(submesh_count=2,vertex_count=8,checked_pixel_count=WIDTH*HEIGHT,base_vertices=bases,
                        indices0=[i+bases[0] for i in INDICES],indices1=[i+bases[1] for i in INDICES]).items():eq(row,k,v)
        vector(row.get("vertices"),VERTICES);vector(row.get("uv0"),UV)
        need(type(row.get("slots")) is list and len(row["slots"])==2,"actual_ordered_material_slots_required")
        for actual,expect in zip(row["slots"],slots,strict=True):
            for k in ("material","shader","texture"):eq(actual,k,expect[k])
            mat=expect["material"];identity(actual,"material_guid",assets,mat)
            mid=actual.get("material_instance");need(type(mid) is int and mid!=0 and instances.setdefault(mat,mid)==mid,"material_instance_changed")
            tex=expect["texture"]
            eq(actual,"texture_guid",assets[tex] if tex in (PNG_A,PNG_B) else "")
            for key in ("tint","scale","offset"):vector(actual.get(key),expect[key])
        samples=row.get("pixels")
        need(type(samples) is list and len(samples)==WIDTH*HEIGHT,"complete_readback_required")
        pixels={};error=0.;diff=0.
        for sample in samples:
            x,y=sample.get("x"),sample.get("y")
            need(type(x) is int and type(y) is int and 0<=x<WIDTH and 0<=y<HEIGHT and (x,y) not in pixels,"invalid_pixel_coordinate")
            obs=sample.get("observed")
            error=max(error,vector(obs,expected_pixel(name,x,y),TOL))
            diff=max(diff,max(abs(a-b) for a,b in zip(obs,expected_pixel("baseline",x,y))))
            pixels[(x,y)]=obs
        if name not in ("baseline","restored_baseline"):need(diff>=.05,"counterfactual_not_distinguished:"+name)
        errors[name]=error;diffs[name]=diff;all_pixels[name]=pixels
    need(len(assets)==6 and len(set(assets.values()))==6 and len(instances)==4 and len(set(instances.values()))==4,"distinct_persistent_assets_required")
    for key in all_pixels["baseline"]:
        vector(all_pixels["restored_baseline"][key],all_pixels["baseline"][key],TOL)
        # Swapping the slots vs swapping index routes can have the same pixels.
        # Only the actual observed mesh+material binding disambiguates them.
        vector(all_pixels["swapped_materials"][key],all_pixels["reversed_mesh_routes"][key],TOL)
    return dict(status="PASS_AUTHORED_SUBMESH_ROUTE_VULKAN",reason="independent_route_and_pixel_oracle_passed",
                run_id=run_id,source_hashes=source_hashes,actual_imported_RGBA8_pixels_verified=16,
                actual_Vulkan_RGBA_pixels_verified=len(NAMES)*WIDTH*HEIGHT,cases_verified=len(NAMES),
                counterfactual_cases_distinguished_from_baseline=len(NAMES)-2,
                swapped_materials_and_reversed_mesh_same_pixels_distinct_observed_bindings=True,
                persistent_mesh_material_texture_assets=6,restored_baseline_verified=True,
                max_rendered_error=max(errors.values()),case_rendered_errors=errors,case_difference_from_baseline=diffs,
                backend="Vulkan",Unity_version=EDITOR_VERSION,device=report["graphics_device_name"],
                synthetic_only=True,original_assets_read=False,white_mesh_repaired=False,production_pixels=False,Android_device=False,XAPK=False)


def verify_file(receipt,out,run_id,exit_code):
    receipt,out=regular_path(receipt),regular_path(out)
    if out.exists() or not out.parent.is_dir():raise ValueError("fresh_output_required")
    result=dict(status="NOT_RUN",reason="Unity_receipt_missing",run_id=run_id,synthetic_only=True,
                Android_device=False,production_pixels=False,XAPK=False)
    try:
        if receipt.is_file():
            data=receipt.read_bytes()
            need(len(data)<=256*1024,"bounded_receipt_required")
            report=strict_json(data)
            result.update(receipt_status=report.get("status"),receipt_reason=str(report.get("reason",""))[:256])
            result.update(validate(report,run_id,hashes(),exit_code),receipt_sha256=digest(data))
    except (ValueError,TypeError,KeyError,OSError) as e:result.update(status="FAIL",reason=str(e))
    out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=("stage","verify"));p.add_argument("--project",type=Path)
    p.add_argument("--receipt",type=Path);p.add_argument("--out",type=Path);p.add_argument("--run-id");p.add_argument("--exit-code",type=int)
    a=p.parse_args()
    if a.action=="stage":
        if a.project is None:p.error("stage requires --project")
        r=stage(a.project)
    else:
        if a.receipt is None or a.out is None or not a.run_id or a.exit_code is None:p.error("verify requires complete parameters")
        r=verify_file(a.receipt,a.out,a.run_id,a.exit_code)
    print(json.dumps(r,sort_keys=True))
    return 0 if r["status"] in ("PREPARED","PASS_AUTHORED_SUBMESH_ROUTE_VULKAN") else 2


if __name__=="__main__":raise SystemExit(main())
