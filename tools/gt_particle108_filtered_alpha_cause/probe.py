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
PRIOR_SHA="06f9def4b062f5076733b6d02f7234021890affe43b34fd1b502f63aca4ce784"
def filtered(raw,w,h,opaque=False,nearest=False):
    # Exact half-texel grid in bottom-origin order, independent of the mesh.
    result=[]
    for y2 in range(2*h-1):
        for x2 in range(2*w-1):
            x,y=x2//2,y2//2
            xx,yy=x2%2/2,y2%2/2
            if nearest:
                x=min(w-1,x+(x2%2));y=min(h-1,y+(y2%2));xx=yy=0
            x1,y1=min(x+1,w-1),min(y+1,h-1)
            def c(a,b,k):return raw[4*(b*w+a)+k]
            sample=[(1-yy)*((1-xx)*c(x,y,k)+xx*c(x1,y,k))+yy*((1-xx)*c(x,y1,k)+xx*c(x1,y1,k)) for k in range(4)]
            result.extend(blend(sample,opaque))
    return result
def changed_meta(raw):
    pat=rb"(?m)^([ \t]*alphaIsTransparency:[ \t]*)1([ \t]*\r?)$"
    need(len(list(re.finditer(pat,raw)))==1,"one original alphaIsTransparency field")
    return re.sub(pat,lambda m:m[1]+b"0"+m[2],raw)
def verify(archive,prior,project,results,run_id,exit_code):
    report=dict(status="INCONCLUSIVE",run_id=run_id,archive_sha256=ARCHIVE_SHA,prior_sha256=PRIOR_SHA,unity_step_exit=exit_code,
        original_assets_read=False,Android_device=False,production=False,XAPK=False)
    try:
        files,rows,patches,sg=from_archive(archive)
        stage=json.loads((results/"stage.json").read_text())
        need(stage["rows"]==rows and stage["patches"]==patches and stage["shader_guid"]==sg and stage["run_id"]==run_id and stage["archive_sha256"]==ARCHIVE_SHA,"stage exact join")
        need(all(stage["files"][n]==sha(b) for n,b in files.items()),"stage file hashes")
        prior_data=prior.read_bytes()
        need(len(prior_data)==4711 and sha(prior_data)==PRIOR_SHA,"prior actual receipt archive")
        with zipfile.ZipFile(BytesIO(prior_data)) as z:
            need(len(z.infolist())==7 and z.testzip() is None,"prior CRC")
            prev=json.loads(z.read("raw.unity.json"))
            need(prev["status"]=="OBSERVED" and prev["run_id"].startswith("46086079821-") and prev["archive_sha256"]==ARCHIVE_SHA,"prior actual run identity")
        prior_obs={o["path_id"]:o for o in prev["imported"]}
        r=json.loads((results/"raw.unity.json").read_text())
        report["actual_status"]=r["status"];report["actual_reason"]=r["reason"]
        need(exit_code==0 and r["status"]=="OBSERVED" and r["run_id"]==run_id and r["archive_sha256"]==ARCHIVE_SHA,"actual Unity success")
        need(r["unity_version"]=="2021.3.45f2" and r["backend"]=="Vulkan" and r["color_space"]=="Linear" and r["device"],"actual Vulkan environment")
        need(r["authored_only"] is True and all(r[k] is False for k in ("original_assets_read","Android_device","production","XAPK")),"scope")
        report["backend"]=r["backend"];report["device"]=r["device"]
        phases=("baseline","alpha-off");ids=(821,822,823,824)
        obs={(o["phase"],o["path_id"]):o for o in r["imported"]};draw={d["name"]:d for d in r["draws"]}
        need(len(r["imported"])==len(obs)==8 and set(obs)=={(p,i) for p in phases for i in ids},"actual unique import observations")
        need(len(r["draws"])==len(draw)==12 and set(draw)=={f"{p}-{i}" for p in phases for i in (*ids,"swap","opaque")},"actual unique draws")
        by_id={row["path_id"]:row for row in rows}
        allowed={row["texture_path"]+".meta" for row in rows}
        diffs=[]
        for n,b in files.items():
            expected=changed_meta(b) if n in allowed else b
            if not (project/n).is_file() or (project/n).read_bytes()!=expected:diffs.append(n)
        report["unexpected_staged_file_drift"]=diffs
        need(not diffs,"single field disk change only")
        raw_drifts={};restored=0;alpha_loss=0;errors={};source_errors={};phase_deltas={};nearest_separations={};midpoint_changes={};controls={}
        for i in ids:
            row=by_id[i];a,b=(obs[(p,i)] for p in phases)
            prior_o=prior_obs[i];source=row["rgba"];w,h=row["width"],row["height"]
            for p,o in zip(phases,(a,b)):
                for k in ("width","height","material_guid","material_file_id","texture_guid","texture_file_id","scale","offset"):
                    need(o[k]==row[k],"actual identity/UV "+k)
                for k in ("texture_format","graphics_format","alpha_source","compression","filter_mode","readable","srgb","mip_count","shader_guid"):
                    need(o[k]==prior_o[k],"unchanged observed importer "+k)
                need(o["alpha_is_transparency"]==(p=="baseline"),"actual policy")
                meta=files[row["texture_path"]+".meta"]
                need(o["meta_sha256"]==sha(meta if p=="baseline" else changed_meta(meta)),"actual phase meta hash")
                rgba=o["imported_rgba8"]
                need(len(rgba)==len(source) and all(type(v) is int and 0<=v<=255 for v in rgba),"actual RGBA8")
                alpha_loss+=sum(x!=y for x,y in zip(rgba[3::4],source[3::4]))
                d=draw[f"{p}-{i}"]
                need(d["material_guid"]==row["material_guid"] and d["bound_texture_guid"]==row["texture_guid"] and d["filter_mode"]=="Bilinear" and (d["width"],d["height"])==(2*w-1,2*h-1),"actual filtered renderer")
                errors[f"{p}-{i}"]=vec_error(d["rgba"],filtered(rgba,w,h))
                source_errors[f"{p}-{i}"]=vec_error(d["rgba"],filtered(source,w,h))
                nearest_separations[f"{p}-{i}"]=vec_error(d["rgba"],filtered(rgba,w,h,nearest=True))
            need(a["imported_rgba8"]==prior_o["imported_rgba8"],"baseline not equal to actual previous import")
            av,bv=a["imported_rgba8"],b["imported_rgba8"]
            raw_drifts[str(i)]=[j//4 for j in range(0,len(source),4) if av[j:j+4]!=source[j:j+4]]
            restored+=sum(av[j:j+4]!=source[j:j+4] and bv[j:j+4]==source[j:j+4] for j in range(0,len(source),4))
            d0,d1=(draw[f"{p}-{i}"]["rgba"] for p in phases)
            phase_deltas[str(i)]=vec_error(d0,d1)
            midpoint_changes[str(i)]=[(k%(2*w-1),k//(2*w-1)) for k in range((2*w-1)*(2*h-1)) if ((k%(2*w-1))%2 or (k//(2*w-1))%2) and vec_error(d0[k*4:k*4+4],d1[k*4:k*4+4])>.02]
            # Centers must retain the old point-blend result even though only linear draws execute here.
            center_error=max(vec_error(d0[4*(2*y*(2*w-1)+2*x):4*(2*y*(2*w-1)+2*x)+4],blend(source[4*(y*w+x):4*(y*w+x)+4])) for y in range(h) for x in range(w))
            need(center_error<=TOL,"baseline center blending")
        a=by_id[821];w,h=a["width"],a["height"]
        for p in phases:
            for suffix,i,opaque in (("swap",822,False),("opaque",821,True)):
                d=draw[f"{p}-{suffix}"];o=obs[p,i]
                need(d["material_guid"]==a["material_guid"] and d["bound_texture_guid"]==o["texture_guid"] and d["filter_mode"]=="Bilinear" and (d["width"],d["height"])==(2*w-1,2*h-1),"control actual binding")
                error=vec_error(d["rgba"],filtered(o["imported_rgba8"],w,h,opaque=opaque))
                separation=vec_error(d["rgba"],draw[f"{p}-821"]["rgba"])
                controls[f"{p}-{suffix}"]=dict(expected_error=error,baseline_separation=separation)
        report.update(actual_import_observations=8,actual_rendered_pixels=sum(d["width"]*d["height"] for d in draw.values()),
            alpha_mismatches=alpha_loss,baseline_source_drift_pixels=raw_drifts,restored_pixels=restored,
            gpu_to_imported_linear_errors=errors,gpu_to_source_linear_errors=source_errors,
            nearest_negative_separations=nearest_separations,policy_draw_deltas=phase_deltas,
            changed_midpoint_coordinates=midpoint_changes,controls=controls)
        need(raw_drifts=={"821":[3],"822":[],"823":[3],"824":[]} and alpha_loss==0,"baseline exact drift/alpha")
        need(max(errors.values())<=TOL,"GPU actual linear blend")
        need(all(nearest_separations[f"{p}-821"]>.05 for p in phases),"nearest negative does not discriminate")
        need(all(c["expected_error"]<=TOL and c["baseline_separation"]>.05 for c in controls.values()),"negative controls")
        need(restored==2 and all(obs["alpha-off",i]["imported_rgba8"]==by_id[i]["rgba"] for i in ids),"single policy did not restore all RGBA")
        need(all(source_errors[f"alpha-off-{i}"]<=TOL for i in ids),"counterfactual source linear blend")
        need(all(phase_deltas[str(i)]>.02 and midpoint_changes[str(i)] for i in (821,823)),"affected midpoint policy effect absent")
        need(all(phase_deltas[str(i)]<=TOL for i in (822,824)),"unaffected controls changed")
        report["status"]="PASS_ACTUAL_RETAINED_AUTHORED_ALPHA_FILTERED_CAUSE"
    except (ValueError,KeyError,TypeError,IndexError,OSError,zipfile.BadZipFile) as exc:
        report["reason"]=str(exc)
    dump(results/"verified.json",report);print("GT_FILTERED_ALPHA_RESULT "+json.dumps(report,sort_keys=True))
    if not report["status"].startswith("PASS"):raise SystemExit(1)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("stage","verify"))
    p.add_argument("--archive",type=Path,required=True);p.add_argument("--prior",type=Path)
    p.add_argument("--project",type=Path,required=True);p.add_argument("--results",type=Path,required=True)
    p.add_argument("--run-id",required=True);p.add_argument("--exit-code",type=int,default=1)
    a=p.parse_args()
    if a.mode=="stage":
        stage(a.archive,a.project,a.results,a.run_id)
    else:
        verify(a.archive,a.prior,a.project,a.results,a.run_id,a.exit_code)
