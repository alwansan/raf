"""Independent authored PNG/TextureImporter Vulkan pixel oracle, not game acceptance."""
import argparse
import hashlib
import json
import math
import re
import struct
import zlib
from pathlib import Path

from scripts.gt_synthetic_material_alpha import regular_path, SETTINGS, EDITOR_VERSION

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools/synthetic_material_alpha"
SHADER = "Assets/SyntheticMaterialAlpha.shader"
PROBE = "Assets/Editor/SyntheticImportedAlphaValidation.cs"
PNG = "Assets/AuthoredAlpha.png"
WIDTH, HEIGHT = 6, 4
# Grayscale RGB deliberately separates independent alpha from grayscale.
GRAY = (0, 64, 128, 192, 255, 32)
ALPHA = (255, 0, 128, 255, 64, 0)
BG = (.125, .25, .5, .25)
TINT = (.5, .75, .25, 1.)
CASES = {
    "input_linear": ("FromInput", False, "imported", TINT, 5, 10),
    "none_linear": ("None", False, "imported", TINT, 5, 10),
    "grayscale_linear": ("FromGrayScale", False, "imported", TINT, 5, 10),
    "input_srgb": ("FromInput", True, "imported", TINT, 5, 10),
    "wrong_blend": ("FromInput", False, "imported", TINT, 1, 0),
    "white_binding": ("FromInput", False, "explicit_white", TINT, 5, 10),
    "missing_binding": ("FromInput", False, "null", TINT, 5, 10),
    "missing_tint": ("FromInput", False, "imported", (1.,)*4, 5, 10),
}
TOL = .008
MIN_CONTROL = .05


def digest(data):
    return hashlib.sha256(data).hexdigest()


def png_bytes():
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag+data)&0xffffffff)
    row = b"\0"+bytes(c for x in range(WIDTH) for c in (GRAY[x],)*3+(ALPHA[x],))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(row*HEIGHT, 9)) + chunk(b"IEND", b""))


def candidates():
    return {SHADER:(TOOLS/"SyntheticMaterialAlpha.shader").read_bytes(),
            PROBE:(TOOLS/"SyntheticImportedAlphaValidation.cs").read_bytes(),
            PNG:png_bytes()}


def hashes():
    return {key:digest(value) for key,value in candidates().items()}


def stage(project):
    project=regular_path(project)
    if project.exists() or not project.parent.is_dir():
        raise ValueError("fresh_project_required")
    files=candidates()
    files.update({"Packages/manifest.json":b'{"dependencies":{}}\n',
                  "ProjectSettings/ProjectVersion.txt":("m_EditorVersion: "+EDITOR_VERSION+"\n").encode(),
                  "ProjectSettings/ProjectSettings.asset":SETTINGS.encode()})
    for key,value in files.items():
        p=project/key
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(value)
    (project/"synthetic-alpha-fixture.json").write_text(json.dumps(
        {"schema_version":1,"synthetic_only":True,"files":{k:digest(v) for k,v in files.items()}},indent=2)+"\n")
    return {"status":"PREPARED","source_hashes":hashes(),"Unity_render_executed":False}


def strict_json(data):
    def unique(pairs):
        out={}
        for k,v in pairs:
            if k in out:
                raise ValueError("duplicate_receipt_key")
            out[k]=v
        return out
    def reject(v):
        raise ValueError("nonfinite_JSON")
    return json.loads(data,object_pairs_hook=unique,parse_constant=reject)


def expected_rgba8(mode,x):
    g=GRAY[x]
    return [g,g,g,{"None":255,"FromInput":ALPHA[x],"FromGrayScale":g}[mode]]


def linear(x):
    return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4


def expected_pixel(case,x):
    mode,srgb,binding,tint,src,_=CASES[case]
    raw=[c/255 for c in expected_rgba8(mode,x)]
    if binding!="imported":
        raw=[1.]*4
    elif srgb:
        raw[:3]=[linear(c) for c in raw[:3]]
    rgba=[c*t for c,t in zip(raw,tint)]
    a=rgba[3]
    rgb=rgba[:3] if src==1 else [rgba[i]*a+BG[i]*(1-a) for i in range(3)]
    return rgb+[a+BG[3]*(1-a)]


def match(obj,key,expected):
    if type(obj.get(key)) is not type(expected) or obj[key]!=expected:
        raise ValueError("receipt_contract:"+key)


def vector(value):
    if type(value) is not list or len(value)!=4 or any(type(v) not in (int,float) or not math.isfinite(v) for v in value):
        raise ValueError("finite_RGBA_required")
    return value


def delta(a,b):
    return max(abs(x-y) for x,y in zip(a,b))


def validate(report,run_id,source_hashes,exit_code):
    if type(report) is not dict or type(exit_code) is not int or exit_code!=0:
        raise ValueError("actual_successful_Unity_process_required")
    for k,v in {
        "schema_version":1,"run_id":run_id,"status":"OBSERVED","Unity_version":EDITOR_VERSION,
        "backend":"Vulkan","active_color_space":"Linear","synthetic_only":True,
        "Unity_render_executed":True,"Android_device":False,"production_pixels":False,"XAPK":False,
        "rendered_case_count":len(CASES),"reimport_count":5,
        "shader_sha256":source_hashes[SHADER],"probe_sha256":source_hashes[PROBE],
        "png_sha256":source_hashes[PNG],"png_sha256_after":source_hashes[PNG]
    }.items():
        match(report,k,v)
    if not isinstance(report.get("graphics_device_name"),str) or not report["graphics_device_name"].strip():
        raise ValueError("graphics_device_required")
    rows=report.get("cases")
    if type(rows) is not list or len(rows)!=len(CASES):
        raise ValueError("eight_cases_required")
    seen=set(); guids=set(); materials=set(); errors={}; mismatches={}; imported_errors={}; observed_alpha={}
    for row in rows:
        if type(row) is not dict:
            raise ValueError("object_case_required")
        name=row.get("name")
        if name not in CASES or name in seen:
            raise ValueError("unique_known_case_required")
        seen.add(name)
        mode,srgb,binding,tint,src,dst=CASES[name]
        for k,v in {
            "alpha_source":mode,"srgb_import":srgb,"srgb_graphics_format":srgb,"bound_texture":binding,
            "filter_mode":"Point","wrap_mode":"Clamp","texture_shape":"Texture2D","texture_type":"Default",
            "compression":"Uncompressed","npot_scale":"None","png_sha256":source_hashes[PNG],
            "readable":True,"mipmaps_enabled":False,"alpha_is_transparency":False,
            "width":WIDTH,"height":HEIGHT,"mip_count":1,"aniso_level":0,
            "src_blend":src,"dst_blend":dst,"checked_pixel_count":WIDTH*HEIGHT,
        }.items():
            match(row,k,v)
        if row.get("texture_format") not in ("RGB24","RGBA32","ARGB32","BGRA32"):
            raise ValueError("uncompressed_8bit_texture_required")
        if not isinstance(row.get("graphics_format"),str) or not row["graphics_format"]:
            raise ValueError("graphics_format_required")
        guid=row.get("asset_guid")
        mid=row.get("material_id")
        if type(guid) is not str or not re.fullmatch("[0-9a-f]{32}",guid) or guid=="0"*32 or type(mid) is not int or not mid:
            raise ValueError("asset_and_material_identity_required")
        guids.add(guid); materials.add(mid)
        if delta(vector(row.get("tint")),tint)>1e-6:
            raise ValueError("material_tint_mismatch")
        samples=row.get("samples")
        if type(samples) is not list or len(samples)!=WIDTH*HEIGHT:
            raise ValueError("complete_pixel_population_required")
        pixels=set(); max_error=0.; max_cpu=0; mismatch=0.; alphas={}
        for pixel in samples:
            if type(pixel) is not dict:
                raise ValueError("object_pixel_required")
            x,y=pixel.get("x"),pixel.get("y")
            if type(x) is not int or type(y) is not int or not (0<=x<WIDTH and 0<=y<HEIGHT) or (x,y) in pixels:
                raise ValueError("pixel_coordinate_mismatch")
            pixels.add((x,y))
            raw=pixel.get("imported_rgba8")
            if type(raw) is not list or len(raw)!=4 or any(type(c) is not int or not 0<=c<=255 for c in raw):
                raise ValueError("imported_RGBA8_required")
            max_cpu=max(max_cpu,delta(raw,expected_rgba8(mode,x)))
            obs=vector(pixel.get("observed"))
            max_error=max(max_error,delta(obs,expected_pixel(name,x)))
            mismatch=max(mismatch,delta(obs,expected_pixel("input_linear",x)))
            if y==0:
                alphas[str(x)]=raw[3]
        if max_cpu>1:
            raise ValueError("imported_RGBA8_mismatch:"+name)
        if max_error>TOL:
            raise ValueError("rendered_RGBA_mismatch:"+name)
        if name!="input_linear" and mismatch<MIN_CONTROL:
            raise ValueError("counterfactual_not_distinguished:"+name)
        errors[name]=max_error; imported_errors[name]=max_cpu; mismatches[name]=mismatch
        observed_alpha[name]=[alphas[str(x)] for x in range(WIDTH)]
    if len(guids)!=1 or len(materials)!=1:
        raise ValueError("same_asset_and_material_identity_required")
    return {
        "status":"PASS_AUTHORED_IMPORTED_ALPHA_VULKAN","run_id":run_id,"source_hashes":source_hashes,
        "reason":"independent_imported_and_rendered_RGBA_validation_passed",
        "actual_imported_RGBA8_pixels_verified":len(CASES)*WIDTH*HEIGHT,
        "actual_Vulkan_RGBA_pixels_verified":len(CASES)*WIDTH*HEIGHT,
        "TextureImporter_reimports_verified":5,"cases_verified":len(CASES),
        "counterfactual_cases_distinguished":len(CASES)-1,"same_asset_and_material_identity":True,
        "max_rendered_error":max(errors.values()),"max_RGBA8_error":max(imported_errors.values()),
        "case_rendered_errors":errors,"case_imported_RGBA8_errors":imported_errors,
        "case_difference_from_input":mismatches,"first_row_observed_alpha8":observed_alpha,
        "device":report["graphics_device_name"],"backend":"Vulkan","Unity_version":EDITOR_VERSION,
        "synthetic_only":True,"original_assets_read":False,"original_alpha_loss_proven":False,
        "production_pixels":False,"Android_device":False,"XAPK":False,
    }


def verify_file(receipt,out,run_id,exit_code):
    receipt,out=regular_path(receipt),regular_path(out)
    if out.exists() or not out.parent.is_dir():
        raise ValueError("fresh_output_required")
    result={"status":"NOT_RUN","run_id":run_id,"reason":"Unity_receipt_missing",
            "synthetic_only":True,"Android_device":False,"production_pixels":False,"XAPK":False}
    try:
        if receipt.is_file():
            data=receipt.read_bytes()
            if len(data)>256*1024:
                raise ValueError("bounded_receipt_required")
            report=strict_json(data)
            result.update(receipt_status=report.get("status"),receipt_reason=str(report.get("reason",""))[:256])
            result.update(validate(report,run_id,hashes(),exit_code),receipt_sha256=digest(data))
    except (ValueError,TypeError,KeyError,OSError) as error:
        result.update(status="FAIL",reason=str(error))
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("action",choices=("stage","verify"))
    p.add_argument("--project",type=Path)
    p.add_argument("--receipt",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--run-id")
    p.add_argument("--exit-code",type=int)
    a=p.parse_args()
    if a.action=="stage":
        if a.project is None:p.error("stage requires --project")
        result=stage(a.project)
    else:
        if a.receipt is None or a.out is None or not a.run_id or a.exit_code is None:
            p.error("verify requires --receipt --out --run-id --exit-code")
        result=verify_file(a.receipt,a.out,a.run_id,a.exit_code)
    print(json.dumps(result,sort_keys=True))
    return 0 if result["status"] in ("PREPARED","PASS_AUTHORED_IMPORTED_ALPHA_VULKAN") else 2


if __name__=="__main__":
    raise SystemExit(main())
