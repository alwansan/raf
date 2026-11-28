"""Replay the exact authored export archive in a fresh isolated Unity project.
Only the original authored identity-only shader pointer type is adapted on
private material copies. No replacement PNG or texture meta changes.
"""
import argparse,hashlib,json,math,re,zipfile
from pathlib import Path
from io import BytesIO
from PIL import Image
import yaml

ARCHIVE_SHA="ae5000e1dd1466dc7531e44a91b1c1274b0939579d4de1524270aa297c92707c"
OWNER_SHA="a9849829dc7c6bb261d73fca5467066cddf2cf5645d91818f0bd69d8f0af409c"
DIR=Path(__file__).resolve().parent
BG=(.125,.25,.5,.25)
TOL=.008
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(x):return hashlib.sha256(x).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+"\n")
class Strict(yaml.BaseLoader):pass
def mapping(loader,node,deep=False):
    out={}
    for k,v in node.value:
        k=loader.construct_object(k,deep=deep);need(k not in out,"duplicate YAML key")
        out[k]=loader.construct_object(v,deep=deep)
    return out
Strict.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
def y(raw):
    s=raw.decode("utf-8-sig")
    s=re.sub(r"(?m)^%[^\n]*\n","",s)
    s=re.sub(r"(?m)^--- !u!\d+ &-?\d+[^\n]*$","---",s)
    return yaml.load(s,Loader=Strict)
def ptr(p):return {"fileID":int(p["fileID"]),"guid":p["guid"],"type":int(p["type"])}
def guid(meta):
    g=y(meta)["guid"];need(re.fullmatch("[0-9a-f]{32}",g) and g!="0"*32,"GUID");return g
def png(raw):
    with Image.open(BytesIO(raw)) as im:
        im=im.convert("RGBA").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return im.width,im.height,list(im.tobytes())
def from_archive(archive):
    data=archive.read_bytes();need(len(data)==16667 and sha(data)==ARCHIVE_SHA,"retained archive digest")
    with zipfile.ZipFile(BytesIO(data)) as z:
        need(len(z.infolist())==31 and z.testzip() is None,"archive CRC")
        files={n:z.read(n) for n in z.namelist() if n.startswith("actual-assets/")}
        cap=json.loads(z.read("capture.json"));approval=json.loads(z.read("approval.json"));report=json.loads(z.read("report.json"))
        need(report["status"]=="PASS_ACTUAL_AUTHORED_VERIFIED_TEXTURE_PRESERVATION" and report["after_actual_pngs"]==4,"actual export receipt")
        need(sha(z.read("source/gt-collection-authored.assets"))==OWNER_SHA==approval["owner_sha256"],"retained owner")
    need(len(files)==17 and len(cap)==4,"actual export population")
    tex={guid(files[n+".meta"]):n for n in files if n.endswith(".png")}
    need(len(tex)==4,"texture GUID population")
    shader_meta=next(n for n in files if n.startswith("actual-assets/Shader/") and n.endswith(".meta"))
    sg=guid(files[shader_meta])
    need(y(files[shader_meta])["NativeFormatImporter"]["mainObjectFileID"]=="4800000","native shader identity")
    out={};rows=[];patches=[]
    for pid in (821,822,823,824):
        p=next(c["pointer"] for c in cap if c["path_id"]==pid and c["exportable"])
        need(p["fileID"]==2800000 and p["type"]==3 and p["guid"] in tex,"actual texture capture")
        tn=tex[p["guid"]];mn=f"actual-assets/Material/GT Collection Material {pid-10}.mat"
        raw=files[mn];mat=y(raw)["Material"];meta=files[mn+".meta"]
        need(y(meta)["NativeFormatImporter"]["mainObjectFileID"]=="2100000","material fileID")
        slots=mat["m_SavedProperties"]["m_TexEnvs"]
        if isinstance(slots,list):need(len(slots)==1,"single TexEnv");slots=slots[0]
        slot=slots["_MainTex"];need(set(slots)=={"_MainTex"} and ptr(slot["m_Texture"])==p,"actual Material route")
        need(ptr(mat["m_Shader"])=={"fileID":4800000,"guid":sg,"type":2},"authored identity-only shader")
        pattern=rb"(?m)^([ \t]+m_Shader:[ \t]*\{fileID:[ \t]*4800000,[ \t]*guid:[ \t]*"+sg.encode()+rb",[ \t]*type:[ \t]*)2(\}[ \t]*\r?$)"
        matches=list(re.finditer(pattern,raw));need(len(matches)==1,"single shader adapter byte")
        pos=matches[0].end(1);patched=raw[:pos]+b"3"+raw[pos+1:]
        need(patched[:pos]+b"2"+patched[pos+1:]==raw,"only shader pointer type changed")
        expected=y(raw);expected["Material"]["m_Shader"]["type"]="3";need(y(patched)==expected,"all other material values exact")
        w,h,rgba=png(files[tn]);need(sha(bytes(rgba))==approval["payload_sha256"][str(pid)],"PNG exact source RGBA")
        matpath=mn.replace("actual-assets/","Assets/");texpath=tn.replace("actual-assets/","Assets/")
        for n,b in ((matpath,patched),(matpath+".meta",meta),(texpath,files[tn]),(texpath+".meta",files[tn+".meta"])):
            need(n not in out,"duplicate stage path");out[n]=b
        scale=[float(slot["m_Scale"][k]) for k in ("x","y")];offset=[float(slot["m_Offset"][k]) for k in ("x","y")]
        rows.append(dict(path_id=pid,width=w,height=h,material_path=matpath,material_guid=guid(meta),material_file_id=2100000,
            texture_path=texpath,texture_guid=p["guid"],texture_file_id=p["fileID"],scale=scale,offset=offset,rgba=rgba))
        patches.append(dict(path=matpath,source_sha256=sha(raw),staged_sha256=sha(patched),changed_byte=pos,shader_guid=sg,source_type=2,adapter_type=3))
    need(len({r["material_guid"] for r in rows})==4 and len({r["texture_guid"] for r in rows})==4,"unique identities")
    out["Assets/GT_PreservedTextureAlpha.shader"]=(DIR/"PreservedTextureAlpha.shader").read_bytes()
    out["Assets/GT_PreservedTextureAlpha.shader.meta"]=(f"fileFormatVersion: 2\nguid: {sg}\nShaderImporter:\n  externalObjects: {{}}\n  defaultTextures: []\n  nonModifiableTextures: []\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n").encode()
    out["Assets/Editor/PreservedTextureAlphaValidation.cs"]=(DIR/"PreservedTextureAlphaValidation.cs").read_bytes()
    return out,rows,patches,sg
def stage(archive,project,results,run_id):
    need(not project.exists() and not results.exists(),"fresh stage")
    out,rows,patches,sg=from_archive(archive)
    input=dict(run_id=run_id,archive_sha256=ARCHIVE_SHA,rows=rows)
    out["GTInput.json"]=(json.dumps(input,sort_keys=True,indent=2)+"\n").encode()
    out["Packages/manifest.json"]=b'{"dependencies":{}}\n'
    out["ProjectSettings/ProjectVersion.txt"]=b"m_EditorVersion: 2021.3.45f2\n"
    out["ProjectSettings/ProjectSettings.asset"]=b"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!129 &1\nPlayerSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 26\n  companyName: GTAuthoredValidation\n  productName: GTPreservedTextureAlpha\n  m_ActiveColorSpace: 1\n"
    for n,b in out.items():
        p=project/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    results.mkdir()
    dump(results/"stage.json",dict(archive_sha256=ARCHIVE_SHA,run_id=run_id,shader_guid=sg,rows=rows,patches=patches,
        files={n:sha(b) for n,b in out.items()},status="PREPARED_ONLY"))
    print("GT_PRESERVED_ALPHA_STAGE",len(rows),sum(r["width"]*r["height"] for r in rows))
def blend(p,opaque=False):
    c=[v/255 for v in p];a=1 if opaque else c[3]
    return [c[i]*a+BG[i]*(1-a) for i in range(3)]+[a+BG[3]*(1-a)]
def vec_error(a,b):
    need(len(a)==len(b) and all(type(x) in (float,int) and math.isfinite(x) for x in a),"finite readback")
    return max(abs(x-y) for x,y in zip(a,b))
def render_expected(raw,opaque=False):
    return [v for i in range(0,len(raw),4) for v in blend(raw[i:i+4],opaque)]
def verify(archive,project,results,run_id,exit_code):
    stage=json.loads((results/"stage.json").read_text())
    files,rows,patches,sg=from_archive(archive)
    need(stage["archive_sha256"]==ARCHIVE_SHA and stage["rows"]==rows and stage["patches"]==patches and stage["shader_guid"]==sg and stage["run_id"]==run_id,"stage/archive exact join")
    # Unity may canonicalize importer files on first import; record exact drift
    # and refuse PASS if any preserved PNG, texture/meta, material/meta or adapter bytes changed.
    changed=[n for n,b in files.items() if not (project/n).is_file() or (project/n).read_bytes()!=b]
    raw_path=results/"raw.unity.json"
    report={"status":"INCONCLUSIVE","run_id":run_id,"archive_sha256":ARCHIVE_SHA,"changed_staged_files":changed,
        "unity_step_exit":exit_code,"original_assets_read":False,"Android_device":False,"production":False,"XAPK":False}
    try:
        need(raw_path.is_file(),"Unity receipt absent")
        r=json.loads(raw_path.read_text());report["actual_status"]=r["status"];report["actual_reason"]=r["reason"]
        need(exit_code==0 and r["status"]=="OBSERVED" and r["run_id"]==run_id and r["archive_sha256"]==ARCHIVE_SHA,"actual successful Unity receipt")
        need(r["unity_version"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["color_space"]=="Linear" and r["device"],"actual Vulkan environment")
        need(r["authored_only"] is True and all(r[k] is False for k in ("original_assets_read","Android_device","production","XAPK")),"scope")
        report["device"]=r["device"];report["backend"]=r["backend"]
        need(len(r["imported"])==4 and len(r["draws"])==6,"actual route/draw population")
        obs={o["path_id"]:o for o in r["imported"]};dr={d["name"]:d for d in r["draws"]}
        need(set(obs)=={821,822,823,824} and set(dr)=={*(f"baseline-{i}" for i in obs),"swap-821-to-822","opaque-821"},"unique route keys")
        alpha_loss=0;rgb_drift=0;alpha_differences=[];baseline_errors={};gpu_errors={};imported_pixels=0
        for row in rows:
            i=row["path_id"];o=obs[i]
            for k in ("width","height","material_guid","material_file_id","texture_guid","texture_file_id","scale","offset"):
                need(o[k]==row[k],"imported exact identity/UV "+k)
            need(o["shader_guid"]==sg and o["mip_count"]==1 and o["readable"] and not o["srgb"] and o["filter_mode"]=="Point","importer scope")
            rgba=o["imported_rgba8"];source=row["rgba"]
            need(len(rgba)==len(source) and all(type(v) is int and 0<=v<=255 for v in rgba),"actual RGBA8")
            alpha_loss+=sum(a!=b for a,b in zip(rgba[3::4],source[3::4]))
            rgb_drift+=sum(any(a!=b for a,b in zip(rgba[j:j+3],source[j:j+3])) for j in range(0,len(rgba),4))
            imported_pixels+=row["width"]*row["height"]
            d=dr[f"baseline-{i}"]
            need(d["material_guid"]==row["material_guid"] and d["bound_texture_guid"]==row["texture_guid"] and (d["width"],d["height"])==(row["width"],row["height"]),"actual baseline renderer binding")
            baseline_errors[str(i)]=vec_error(d["rgba"],render_expected(source))
            gpu_errors[str(i)]=vec_error(d["rgba"],render_expected(rgba))
        a,b=rows[:2];oa,ob=obs[821],obs[822]
        a_alpha=oa["imported_rgba8"][3::4];b_alpha=ob["imported_rgba8"][3::4]
        alpha_differences=[i for i,(x,y) in enumerate(zip(a_alpha,b_alpha)) if x!=y]
        controls={}
        for name,which,opaque in (("swap-821-to-822",822,False),("opaque-821",821,True)):
            d=dr[name];o=obs[which]
            need(d["material_guid"]==a["material_guid"] and d["bound_texture_guid"]==o["texture_guid"] and (d["width"],d["height"])==(a["width"],a["height"]),"actual control binding")
            correct=vec_error(d["rgba"],render_expected(o["imported_rgba8"],opaque))
            separation=vec_error(d["rgba"],render_expected(a["rgba"]))
            controls[name]=dict(expected_control_error=correct,wrong_baseline_error=separation,
                rejected_as_correct_baseline=separation>.05)
        report.update(imported_pixels=imported_pixels,actual_rendered_pixels=sum(d["width"]*d["height"] for d in dr.values()),
            actual_material_texture_guid_fileid_matches=4,source_alpha_mismatches=alpha_loss,source_rgb_pixel_drift=rgb_drift,
            distinct_alpha_pixels=len(alpha_differences),baseline_source_blend_errors=baseline_errors,
            actual_imported_to_blend_errors=gpu_errors,controls=controls)
        need(not changed,"retained staged asset bytes changed")
        need(alpha_loss==0 and len(alpha_differences)==3,"source alpha loss or collapse")
        need(max(baseline_errors.values())<=TOL and max(gpu_errors.values())<=TOL,"actual blend/source parity")
        need(all(c["expected_control_error"]<=TOL and c["rejected_as_correct_baseline"] for c in controls.values()),"negative controls not discriminating")
        report["status"]="PASS_ACTUAL_RETAINED_AUTHORED_ALPHA_VULKAN"
    except (ValueError,KeyError,TypeError,IndexError) as exc:
        report["reason"]=str(exc)
    dump(results/"verified.json",report);print("GT_PRESERVED_ALPHA_RESULT "+json.dumps(report,sort_keys=True))
    if not report["status"].startswith("PASS"):raise SystemExit(1)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("stage","verify"));p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--project",type=Path,required=True);p.add_argument("--results",type=Path,required=True);p.add_argument("--run-id",required=True);p.add_argument("--exit-code",type=int,default=1)
    a=p.parse_args()
    if a.mode=="stage":stage(a.archive,a.project,a.results,a.run_id)
    else:verify(a.archive,a.project,a.results,a.run_id,a.exit_code)
