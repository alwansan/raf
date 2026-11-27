"""V13: stage fresh, V12-verified public export and verify actual Unity observations.

Scene hierarchy is a trace-driven replay, not an import of the incomplete
authored scene YAML. Exact exported mesh/material/PNG/meta files are staged.
Native placeholder shader documents are replaced only in the isolated project
by a declared authored adapter with the same GUID/local ID. No shader parity.
"""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import re
import struct
from scripts import gt_renderer_submesh_routes as gate
from scripts import gt_imported_png_route_pixels as png
from scripts.gt_authored_imported_png_route_witness import load,need
from scripts.gt_synthetic_material_alpha import SETTINGS,EDITOR_VERSION,regular_path

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools/gt_dxt5nm_unity"
V12=ROOT/"clients/GT/sessions/20261127-dxt5nm-importer-v12/actual-pass-45967942717.json"
FIELD="selected_same_route_imported_dxt5nm_supported_serialized_importer_state_verified"
PNG_SHA=("9e6be9b9f97d2bf835fbf3ae21d79f889170b7588dddde3f1c351f85cc3b0a54",
         "5ab65d8dc9fb153f045cdc8ea0b5e8293d0e9006ec22938b7aafcddb9ed575d1")
TOL=.004

def digest(raw):return sha256(raw).hexdigest()
def read(path):return json.loads(path.read_text())
def write(path,value):
    need(not path.exists(),"fresh_receipt_required")
    path.write_text(json.dumps(value,sort_keys=True,indent=2)+"\n")
def binary32(value):return struct.unpack("<I",struct.pack("<f",value))[0]
def as_float(bits):return struct.unpack("<f",struct.pack("<I",bits))[0]

def stage(root,project,run_id,receipt,out):
    root,project,out=map(regular_path,(root,project,out))
    need(not project.exists() and project.parent.is_dir() and not out.exists(),"fresh_stage_required")
    historical=read(V12)
    actual=read(receipt)
    need(historical["status"]==actual["status"]=="PASS_ACTUAL_AUTHORED_PUBLIC_DXT5NM_SUPPORTED_IMPORTER_STATE_ROUTE_JOIN" and actual["baseline"][FIELD] and actual["counterfactual_count"]==25,"V12_verified_receipt_required")
    states={}
    objects,externals,mapping,vertices,proofs,requests,pins,producer=load(root,states=states,bc3_mode=True,normalmap=True)
    files,docs=gate.actual_index(root/"project",mapping)
    baseline=gate.compare(objects,externals,mapping,files,docs,vertex_payloads=vertices,material_values=True,material_keywords=True,png_top_mips=proofs,png_normalmap=True,png_importer_states=states)
    need(baseline==actual["baseline"] and baseline[FIELD],"fresh_V12_same_route_recheck")
    staged={};identities={};adapters=[];scene_sources={}
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
        put(dest,raw);put(dest+".meta",md)
        result=dict(path=dest,guid=guid,file_id=fid,sha256=digest(raw),meta_sha256=digest(md))
        identities[key]=result
        return result
    textures=[]
    for i,key in enumerate(sorted(states)):
        id=asset(key);s=states[key];hist=historical["receipt"]["source_and_actual"][i];act=actual["source_and_actual"][i]
        need(id["sha256"]==PNG_SHA[i] and hist["source"]==act["source"] and hist["source_rgba_sha256"]==act["source_rgba_sha256"],"historical_V12_pixel_state_drift")
        need(act["actual_metadata"]==files[id["guid"]][1] and not act["swizzle_present"],"actual_V12_meta_binding")
        textures.append(dict(id,expected_source=act["source"],expected_rgba_hex=historical["v11_replay"]["textures"][i]["actual_rgba_hex"]))
    routes=[]
    for key,(cls,tree) in sorted(objects.items()):
        if cls!=23:continue
        rp=mapping[key][1];go=gate.src_target(key[0],tree["m_GameObject"],externals)
        scene_path,scene_meta=files[rp[0]]
        scene_sources[key[0]]=dict(guid=rp[0],renderer_file_id=rp[1],sha256=digest(gate.bounded_snapshot(scene_path,gate.MAX_DOC)),meta_sha256=digest(Path(str(scene_path)+".meta").read_bytes()))
        filters=[(k,t) for k,(cl,t) in objects.items() if cl==33 and gate.src_target(k[0],t["m_GameObject"],externals)==go]
        need(len(filters)==1,"exact_source_filter")
        fk,ft=filters[0];mk=gate.src_target(fk[0],ft["m_Mesh"],externals)
        layout=objects[mk][1];mesh=asset(mk);mats=[];texs=[];uv=[]
        for raw in tree["m_Materials"]:
            mat=gate.src_target(key[0],raw,externals)
            ms=objects[mat][1];shader=gate.src_target(mat[0],ms["m_Shader"],externals)
            asset(shader);mats.append(asset(mat))
            env=gate.normalize_texenvs(ms["m_SavedProperties"]["m_TexEnvs"])
            need(set(env)=={"_MainTex"},"exact_authored_texenv_scope")
            ptr,transform=env["_MainTex"]
            tex=gate.src_target(mat[0],{"m_FileID":ptr[0],"m_PathID":ptr[1]},externals)
            texs.append(asset(tex));uv.extend(transform)
        routes.append(dict(key=key[0],mesh=mesh,materials=mats,textures=texs,uv=uv,
            vertex_count=layout[0],index_counts=[s[1] for s in layout[-1]],base_vertices=[s[3] for s in layout[-1]]))
    need(len(routes)==len(adapters)==len(textures)==2 and len(identities)==7 and routes[0]["materials"]==routes[1]["materials"][::-1],"authored_route_population")
    put("Assets/GTNormalProbe/NormalRouteProbe.shader",(TOOLS/"SyntheticNormalRouteProbe.shader").read_bytes())
    put("Assets/Editor/SyntheticNormalRouteValidation.cs",(TOOLS/"SyntheticNormalRouteValidation.cs").read_bytes())
    put("Packages/manifest.json",b'{"dependencies":{}}\n')
    put("ProjectSettings/ProjectVersion.txt",("m_EditorVersion: "+EDITOR_VERSION+"\n").encode())
    put("ProjectSettings/ProjectSettings.asset",SETTINGS.encode())
    manifest=dict(schema_version=13,run_id=run_id,synthetic_only=True,source_V12_verified=True,shader_adapter=True,scene_route_replay=True,
        original_assets_read=False,shader_program_parity_verified=False,scene_import_verified=False,
        textures=textures,routes=routes,scene_sources=scene_sources,shader_adapters=adapters,
        staged_files={p:digest(v) for p,v in sorted(staged.items())})
    for p,raw in staged.items():
        target=project/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
    m=project/"gt-normal-route-manifest.json";write(m,manifest)
    out.write_bytes(m.read_bytes())
    print(json.dumps(dict(status="PREPARED_V13",routes=len(routes),textures=len(textures),staged_files=len(staged),manifest_sha256=digest(m.read_bytes()))))

def identity(actual,expected):
    need(type(actual) is dict and all(actual.get(k)==expected[k] for k in ("path","guid","file_id","sha256")),"Unity_asset_identity_or_file_bytes_drift")
    need(type(actual.get("meta_sha256")) is str and re.fullmatch("[0-9a-f]{64}",actual["meta_sha256"]),"observed_meta_hash_missing")
    return actual["meta_sha256"]==expected["meta_sha256"]

def float_vec(values,n):
    need(type(values) is list and len(values)==n and all(type(x) in (float,int) and math.isfinite(x) for x in values),"invalid_readback_vector")
    return values

def normal_oracle(packed,mode):
    r,g,b,a=packed
    if mode==1:return (2*r-1,2*g-1,2*b-1)
    x=2*r*a-1;y=2*g-1
    return (x,y,math.sqrt(max(0,1-x*x-y*y)))

def verify(manifest,receipt,run_id,exit_code):
    need(exit_code==0 and receipt.get("status")=="OBSERVED_AUTHORED_UNITY_REIMPORT","actual_Unity_probe_required:"+str(receipt.get("error","missing")))
    need(manifest["run_id"]==receipt["run_id"]==run_id and receipt["editor"]==EDITOR_VERSION and receipt["backend"]=="Vulkan" and receipt["active_color_space"]=="Linear","exact_editor_run_environment")
    need(receipt["shader_adapter"] is True and receipt["scene_route_replay"] is True and receipt["original_assets_read"] is False,"scope_flags")
    need(len(receipt["routes"])==2 and len(receipt["textures"])==2,"Unity_route_population")
    matched=0;meta_rewrites=0;routes=[]
    for exp,obs in zip(manifest["routes"],receipt["routes"],strict=True):
        need(obs["key"]==exp["key"] and obs["vertex_count"]==exp["vertex_count"] and obs["index_counts"]==exp["index_counts"] and obs["base_vertices"]==exp["base_vertices"],"Unity_submesh_layout_drift")
        need(len(obs["uv"])==len(exp["uv"]) and all(abs(a-b)<1e-6 for a,b in zip(obs["uv"],exp["uv"],strict=True)),"Unity_material_UV_drift")
        meta_rewrites+=not identity(obs["mesh"],exp["mesh"])
        for a,b,c,d in zip(obs["materials"],exp["materials"],obs["textures"],exp["textures"],strict=True):
            meta_rewrites+=not identity(a,b);meta_rewrites+=not identity(c,d);matched+=1
        routes.append(obs["key"])
    need(matched==4,"Unity_four_routes_required")
    rows=[];total=0;maximum=0.;all_diffs=[]
    for exp,obs in zip(manifest["textures"],receipt["textures"],strict=True):
        meta_rewrites+=not identity(obs["identity"],exp)
        src=exp["expected_source"];sampler=src["sampler"]
        expected=dict(type=1,shape=1,srgb=False,mipmap=bool(src["mip_enabled"]),readable=bool(src["readable"]),
            streaming=bool(src["streaming"]),priority=src["priority"],filter=sampler[0],aniso=sampler[1],
            wrap_u=sampler[3],wrap_v=sampler[4],wrap_w=sampler[5],max_size=src["max_size"],npot=0,alpha_source=1,
            alpha_transparency=True,compression_quality=50,convert_normal=False,height_scale=.25,normal_filter=0,
            platform_format=-1,platform_compression=2,platform_override=False)
        diffs={k:{"expected":v,"observed":obs.get(k)} for k,v in expected.items() if type(obs.get(k)) is not type(v) and not (type(v) is float and type(obs.get(k)) is int) or obs.get(k)!=v}
        if binary32(obs["bias"])!=sampler[2]:diffs["bias"]={"expected":as_float(sampler[2]),"observed":obs["bias"]}
        all_diffs.extend(diffs)
        w,h=obs["width"],obs["height"]
        need(type(w) is int and type(h) is int and 0<w<=32 and 0<h<=32,"Unity_actual_dimensions")
        need(type(obs["mip_count"]) is int and 0<obs["mip_count"]<=6 and len(obs["mips"])==obs["mip_count"],"Unity_mip_population")
        need(obs["graphics_srgb"] is False,"normalmap_graphics_format_must_be_linear")
        errors=[];dimensions=[];modes=set()
        for n,mip in enumerate(obs["mips"]):
            mw,mh=max(1,w>>n),max(1,h>>n);count=mw*mh
            need((mip["level"],mip["width"],mip["height"])==(n,mw,mh),"Unity_actual_mip_dimensions")
            packed=float_vec(mip["packed"],4*count);normal=float_vec(mip["normal"],4*count)
            for i in range(0,4*count,4):
                p=packed[i:i+4];q=normal[i:i+4]
                need(all(-.001<=x<=1.001 for x in p) and q[3] in (0,1),"normal_readback_range_or_macro")
                mode=int(q[3]);modes.add(mode);oracle=normal_oracle(p,mode)
                error=max(abs(x-y) for x,y in zip(oracle,q[:3],strict=True))
                need(error<=TOL,"Unity_UnpackNormal_oracle_mismatch")
                errors.append(error);total+=1;maximum=max(maximum,error)
            dimensions.append([mw,mh])
        need(len(modes)==1,"one_actual_shader_macro_required")
        cpu=obs["cpu_top_rgba_hex"];status=obs["readback_status"]
        need(status in ("cpu_GetPixels32_observed","cpu_GetPixels32_unsupported","not_readable_as_imported"),"CPU_scope_status")
        if status=="cpu_GetPixels32_observed":need(obs["runtime_readable"] and len(bytes.fromhex(cpu))==4*w*h,"actual_CPU_readback_population")
        else:need(cpu=="" and (status!="not_readable_as_imported" or not obs["runtime_readable"]),"CPU_nonreadable_scope")
        # Compare source PNG normal XY with sampled signed normals at top mip.
        # Both row orientations are retained as diagnostic; no equality claim.
        top=obs["mips"][0]["normal"];source=bytes.fromhex(exp["expected_rgba_hex"]);source_errors={}
        if [w,h]==src["size"]:
            for flip in (False,True):
                errs=[]
                for y in range(h):
                    for x in range(w):
                        a=4*(y*w+x);b=4*((h-1-y if flip else y)*w+x)
                        errs.extend(abs(top[a+c]-(2*source[b+c]/255-1)) for c in (0,1))
                source_errors["flip_y" if flip else "as_recorded"]=dict(max=max(errs),mean=sum(errs)/len(errs))
        rows.append(dict(guid=exp["guid"],importer_API_differences=diffs,source_mip_count=src["mip_count"],actual_mip_count=obs["mip_count"],
            actual_dimensions=dimensions,actual_format=obs["format"],graphics_format=obs["graphics_format"],
            runtime_readable=obs["runtime_readable"],runtime_streaming=obs["runtime_streaming"],cpu_status=status,macro_mode=next(iter(modes)),
            maximum_unpack_error=max(errors),source_XY_diagnostic=source_errors))
    need(total>0 and maximum<=TOL,"actual_normal_unpack_population")
    return dict(status="PASS_ACTUAL_AUTHORED_UNITY_DXT5NM_ROUTE_OBSERVATION" if not all_diffs else "OBSERVED_AUTHORED_UNITY_DXT5NM_ROUTE_WITH_IMPORTER_API_DRIFT",
        renderer_route_replay_matches=2,submesh_material_texture_matches=matched,actual_Unity_import_verified=True,
        all_supported_importer_API_fields_match=not all_diffs,normal_unpack_readback_pixels=total,maximum_unpack_error=maximum,
        rows=rows,meta_rewrite_observations_per_route=meta_rewrites,scene_import_verified=False,shader_program_parity_verified=False,
        original_assets_read=False,source_lower_mip_parity_verified=False,source_normal_GPU_parity_verified=False,
        serialized_swizzle_verified=False,Android_device=False,XAPK=False)

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("stage")
    for n in ("root","project","receipt","out"):a.add_argument("--"+n,type=Path,required=True)
    a.add_argument("--run-id",required=True)
    a=s.add_parser("verify")
    for n in ("manifest","receipt","out"):a.add_argument("--"+n,type=Path,required=True)
    a.add_argument("--run-id",required=True);a.add_argument("--exit-code",type=int,required=True)
    a=p.parse_args()
    if a.cmd=="stage":stage(a.root,a.project,a.run_id,a.receipt,a.out)
    else:
        need(not a.out.exists() and a.out.parent.is_dir(),"fresh_verify_output")
        try:
            m=read(a.manifest);r=read(a.receipt)
            need(r.get("manifest_sha256")==digest(a.manifest.read_bytes()),"actual_staged_manifest_sha256")
            result=verify(m,r,a.run_id,a.exit_code)
        except (ValueError,TypeError,KeyError,OSError,AssertionError,OverflowError) as e:
            result=dict(status="INCONCLUSIVE",reason=str(e),actual_Unity_import_verified=False,Android_device=False,XAPK=False)
        write(a.out,result);print(json.dumps(result,sort_keys=True))
        if result["status"]=="INCONCLUSIVE":raise SystemExit(2)

if __name__=="__main__":main()
