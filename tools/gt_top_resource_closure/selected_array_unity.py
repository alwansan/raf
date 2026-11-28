"""Same-export, original selected array import and full top-mip GPU observation.

Stage only after original layer parity and grid repair. Private files are
withheld from the startup importer until the editor log wrapper is active.
No original shader, material render, Android device or lower-mip acceptance.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import numpy as np
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts import gt_particle108_local_texture_document as native
from tools.gt_top_resource_closure import recheck, selected_array, texture_observation as obs, probe as prior

class Failure(ValueError):
    pass

def need(ok,code):
    if not ok:
        raise Failure(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write(path,obj):
    with path.open("x") as f:
        json.dump(obj,f,sort_keys=True)
        f.write("\n")

def stage(a):
    need(not a.unity_project.exists() and not a.private.exists(),"fresh_selected_array_Unity_stage_required")
    receipt=json.loads(a.receipt.read_text())
    need(receipt["status"]==recheck.STATUS and receipt["selected_exact_original_graph_rejoined"]
         and receipt["all_saved_TexEnv_edges_and_UV_match"] and receipt["serialized_mesh_fields_match"]
         and receipt["serialized_material_values_match"],"selected_resource_receipt_not_admitted")
    rows=[x for x in receipt["texture_results"] if x["class"]==187]
    need(len(rows)==1 and rows[0]["status"]=="ARRAY_GRID_REPAIRED_TOP_MIPS_MATCH",
         "same_export_selected_array_repair_required")
    proof=rows[0]["selected_array_repair"]
    need(all(proof[k] is True for k in ("private_grid_repair_applied","only_two_grid_digits_changed",
                                       "png_bytes_unchanged","GUID_preserved","material_bytes_unchanged"))
         and proof["pixel_comparison"]["all_top_mip_layers_exact"]
         and proof["pixel_comparison"]["pillow_independent_top_mip_layers_exact"]==2,
         "selected_array_original_layer_proof_required")
    plan=json.loads(a.plan.read_text())
    source=recheck.Source(a)
    mat,mk,xk,trace=recheck.join(a,plan,source)
    actual_path=prior.file_index(a.project,{mk[0]})[mk[0]][0]
    actual=native.strict_mapping(prior.document(actual_path,mk[1],21))["Material"]
    before=normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"])
    after=normalize_texenvs(actual["m_SavedProperties"]["m_TexEnvs"],exported=True)
    props=[p for p,v in plan["texture_targets"].items() if v is not None and v["class"]==187]
    need(len(props)==1,"selected_array_slot_not_unique")
    prop=props[0]
    key,exp,kind,cls=recheck.exact_slot(before[prop],after[prop],plan["material"][0],mk[0],source,trace,plan["texture_targets"][prop])
    need(cls==187 and exp[1]==18700000 and kind in (2,3),"selected_array_pointer_not_exact")
    path,meta=prior.file_index(a.project,{exp[0]})[exp[0]]
    tree=source.obj(key,"Texture2DArray").read_typetree(check_read=False)
    shape,raw=selected_array.exact_inline(tree)
    grid=obs.array_png_observation(shape,path,meta,exp[1],kind)
    need(grid["importer_grid_matches"] and (grid["flipbookRows"],grid["flipbookColumns"])==(2,1),"corrected_array_grid_not_present")
    atlas=pixels.read_export_png(path)
    parity=selected_array.compare_layers(raw,atlas,1024,1024,2,11)
    need(parity["all_top_mip_layers_exact"] and parity["layer_order_distinguished"] and parity["orientation_distinguished"],
         "independent_array_redecode_failed")
    asset=pixels.bounded_snapshot(path,64*1024*1024)
    metadata=pixels.bounded_snapshot(path.with_name(path.name+".meta"),4*1024*1024)
    need(metadata.decode("utf-8-sig").replace("\r\n","\n")==meta,"selected_array_meta_snapshot_drift")
    need(path.suffix.lower()==".png" and path.name==Path(path.name).name and "\\" not in path.name,"unsafe_selected_array_basename")
    # Expected PNG is independently re-decoded from exactly these bytes.
    from PIL import Image
    import io
    with Image.open(io.BytesIO(asset)) as image:
        need(image.format=="PNG" and image.convert("RGBA").tobytes()==atlas.tobytes(),"selected_array_PNG_snapshot_drift")
    cfg={"run_id":a.run_id,"asset_path":"Assets/GTSource/"+path.name,"guid":exp[0],"file_id":exp[1],
         "asset_sha256":sha(asset),"meta_sha256":sha(metadata),"width":1024,"height":1024,"depth":2,"mip_count":11,
         "source_srgb":True}
    a.private.mkdir(mode=0o700)
    (a.private/"array.png.bytes").write_bytes(asset)
    (a.private/"array.meta.bytes").write_bytes(metadata)
    write(a.private/"expected.json",cfg)
    here=Path(__file__).parent
    files={"Assets/Editor/SelectedArrayUnity.cs":(here/"SelectedArrayUnity.cs").read_bytes(),
           "Assets/GTSelectedArray.compute":(here/"GTSelectedArray.compute").read_bytes(),
           "Packages/manifest.json":b'{"dependencies":{}}\n',
           "ProjectSettings/ProjectVersion.txt":b"m_EditorVersion: 2021.3.45f2\n",
           "ProjectSettings/ProjectSettings.asset":b"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!129 &1\nPlayerSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 26\n  companyName: GTValidation\n  productName: GTSelectedArray\n  m_ActiveColorSpace: 1\n"}
    for rel,data in files.items():
        target=a.unity_project/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    write(a.unity_project/"GTInput.json",cfg)
    print("GT_SELECTED_ARRAY_UNITY_STAGE "+json.dumps({"status":"PREPARED_ONLY","source_top_mip_layers":2,
          "same_export_class187_pointer":True,"original_asset_withheld_until_private_log_guard":True,
          "source_srgb":True,"private_payload_published":False},sort_keys=True))

def calibration_expected():
    out=np.empty((2,4,4,4),dtype=np.float32)
    for layer in range(2):
        for y in range(4):
            for x in range(4):
                out[layer,y,x]=np.asarray((13+70*layer+11*x+3*y,21+20*layer+5*x+9*y,
                                          31+50*layer+2*x+7*y,41+30*layer+9*x+13*y),dtype=np.float32)/255
    return out

def calibrate(actual):
    need(actual.shape==(2,4,4,4) and np.isfinite(actual).all(),"invalid_authored_calibration_extent")
    expected=calibration_expected()
    modes=[name for name,val in (("bottom_first",expected),("top_first",expected[:,::-1])) if np.max(np.abs(actual-val))<=1e-6]
    need(len(modes)==1,"authored_calibration_orientation_unproven")
    val=expected if modes[0]=="bottom_first" else expected[:,::-1]
    need(np.max(np.abs(actual-val[::-1]))>0.05,"authored_wrong_layer_control_not_distinguished")
    return modes[0]

def expected_linear(rgba):
    x=rgba.astype(np.float32)/255.0
    rgb=x[...,:3]
    x[...,:3]=np.where(rgb<=0.04045,rgb/12.92,((rgb+0.055)/1.055)**2.4)
    return x

def compare(actual,expected):
    need(actual.shape==expected.shape and actual.ndim==4 and actual.shape[-1]==4
         and np.isfinite(actual).all() and np.isfinite(expected).all(),"invalid_actual_GPU_readback")
    need(np.min(actual)>=-1e-5 and np.max(actual)<=1+1e-5,"actual_GPU_samples_outside_UNORM")
    delta=np.abs(actual-expected)
    rows=[]
    for d in delta:
        rows.append({"coordinates":int(d.shape[0]*d.shape[1]),
                     "rgb_mismatches_over_1e_5":int(np.count_nonzero(np.max(d[...,:3],axis=-1)>1e-5)),
                     "alpha_mismatches_over_1e_5":int(np.count_nonzero(d[...,3]>1e-5)),
                     "RGBA_mismatches_over_1_div_255":int(np.count_nonzero(np.max(d,axis=-1)>1/255)),
                     "RGBA_mismatches_over_2_div_255":int(np.count_nonzero(np.max(d,axis=-1)>2/255)),
                     "max_RGB_abs_error":float(np.max(d[...,:3])),"max_alpha_abs_error":float(np.max(d[...,3]))})
    return rows

def readback(path,d,w,h):
    need(path.is_file() and not path.is_symlink() and path.stat().st_size==d*w*h*16,"actual_GPU_readback_extent")
    return np.fromfile(path,dtype="<f4").reshape(d,h,w,4)

def verify(a):
    result={"status":"INCONCLUSIVE","phase":"verify","actual_Unity_import_verified":False,
            "actual_GPU_observation":False,"original_shader_draw_verified":False,"full_lower_mip_pixel_equivalence":False,
            "Android_device":False,"white_mesh_repair_verified":False,"production":False,"XAPK":False,"private_payload_published":False}
    try:
        cfg=json.loads((a.private/"expected.json").read_text())
        need(cfg["run_id"]==a.run_id and cfg==json.loads((a.unity_project/"GTInput.json").read_text()),"stage_run_mismatch")
        marker=a.private/"editor-output-private"
        need(marker.is_file() and marker.read_text().strip()==a.run_id and (a.private/"editor.log").is_file(),"private_editor_log_guard_missing")
        raw=json.loads((a.private/"receipt.json").read_text())
        need(raw["run_id"]==a.run_id,"actual_receipt_wrong_run")
        result["editor_phase"]=raw.get("phase") if raw.get("phase") in ("environment","private_guard","private_stage","refresh","identity","descriptor","compute","calibration","complete") else "unknown"
        need(a.exit_code==0 and raw["status"]=="OBSERVED" and raw["private_log_guard"],"actual_Unity_method_inconclusive")
        need(raw["unity_version"]=="2021.3.45f2" and raw["backend"]=="Vulkan" and raw["color_space"]=="Linear","actual_backend_not_admitted")
        asset=a.unity_project/cfg["asset_path"]
        need(asset.is_file() and not asset.is_symlink() and sha(asset.read_bytes())==cfg["asset_sha256"],"actual_imported_PNG_bytes_changed")
        meta=asset.with_name(asset.name+".meta")
        need(meta.is_file() and not meta.is_symlink(),"actual_imported_meta_missing")
        result["actual_imported_meta_bytes_unchanged"]=sha(meta.read_bytes())==cfg["meta_sha256"]
        need(raw["guid"]==cfg["guid"] and raw["file_id"]==18700000 and raw["texture_importer"] and raw["texture_shape"]==4,"actual_Texture2DArray_identity_or_shape")
        need((raw["width"],raw["height"],raw["depth"])==(1024,1024,2),"actual_array_dimensions_or_depth")
        result.update(actual_Unity_import_verified=True,actual_GUID_fileID_preserved=True,actual_dimensions=[raw["width"],raw["height"],raw["depth"]],
                      actual_mip_count=raw["mip_count"],source_mip_count=11,actual_mip_count_matches_source=raw["mip_count"]==11,
                      actual_srgb=raw["srgb"],source_srgb=True,actual_srgb_matches_source=raw["srgb"] is True,
                      actual_format=raw["texture_format"] if re.fullmatch(r"[A-Za-z0-9_]{1,64}",raw["texture_format"]) else "unrecognized",
                      actual_graphics_format=raw["graphics_format"] if re.fullmatch(r"[A-Za-z0-9_]{1,64}",raw["graphics_format"]) else "unrecognized",
                      actual_importer_readable=raw["readable"],actual_importer_mipmap_enabled=raw["mipmap_enabled"])
        mode=calibrate(readback(a.private/"calibration.f32",2,4,4))
        actual=readback(a.private/"top.f32",2,1024,1024)
        from PIL import Image
        import io
        image_bytes=(a.private/"array.png.bytes").read_bytes()
        need(sha(image_bytes)==cfg["asset_sha256"],"private_expected_PNG_drift")
        with Image.open(io.BytesIO(image_bytes)) as image:
            rgba=np.asarray(image.convert("RGBA")).reshape(2,1024,1024,4)
        # Source original GraphicsFormat100 is sRGB. Do NOT use a wrong
        # actual importer color-space setting to redefine the expected values.
        expected=expected_linear(rgba if mode=="top_first" else rgba[:,::-1])
        rows=compare(actual,expected)
        wrong=compare(actual,expected[::-1])
        result.update(status="OBSERVED_ACTUAL_SELECTED_ARRAY_IMPORT_AND_VULKAN_LOAD",phase="complete",
                      actual_GPU_observation=True,authored_calibration_texels=32,GPU_row_orientation=mode,
                      actual_GPU_coordinates=2097152,per_layer=rows,reversed_layer_control=wrong,
                      correct_layer_order_lower_error=sum(x["RGBA_mismatches_over_2_div_255"] for x in rows)<sum(x["RGBA_mismatches_over_2_div_255"] for x in wrong),
                      all_top_mip_GPU_RGBA_within_1e_5=all(x["rgb_mismatches_over_1e_5"]==0 and x["alpha_mismatches_over_1e_5"]==0 for x in rows))
    except Exception as exc:
        result["reason"]=str(exc) if isinstance(exc,Failure) else type(exc).__name__
    write(a.safe,result)
    print("GT_SELECTED_ARRAY_UNITY_RESULT "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="OBSERVED_ACTUAL_SELECTED_ARRAY_IMPORT_AND_VULKAN_LOAD" else 2

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("stage","verify"))
    for key in ("original","manifest","project","w1","b02","renderer-trace","plan","receipt","out","unity-project","private","safe"):
        p.add_argument("--"+key,type=Path)
    p.add_argument("--run-id",required=True);p.add_argument("--exit-code",type=int,default=1)
    a=p.parse_args()
    if a.mode=="verify":
        return verify(a)
    try:
        stage(a)
        return 0
    except Exception as exc:
        print("GT_SELECTED_ARRAY_UNITY_STAGE_INCONCLUSIVE "+(str(exc) if isinstance(exc,Failure) else type(exc).__name__))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
