"""Compare real opt-out/opt-in public exporter outputs, not rewritten .meta.

Use the historical V12 baseline independently, fresh V11 same-route proof
for the corrected output, and ordinary BC3/RGBA non-interference controls.
Only GUID/timeCreated are volatile between exports. Every importer field
other than the single intended policy byte must remain identical.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
from PIL import Image
import yaml
from scripts import gt_renderer_submesh_routes as gate
from scripts import gt_authored_imported_png_route_witness as authored
from scripts import gt_imported_dxt5nm_route_importer as normal
from scripts import gt_imported_png_route_pixels as png
from scripts import gt_dxt5nm_texel_policy as policy
from scripts import gt_patch_dxt5nm_png_alpha_policy as patch

need=authored.need
V11="selected_same_route_imported_dxt5nm_png_top_mip_and_importer_verified"
V12="selected_same_route_imported_dxt5nm_supported_serialized_importer_state_verified"
ROOT=Path(__file__).resolve().parents[1]
V14=ROOT/"clients/GT/sessions/20261127-dxt5nm-texel-policy-v14/actual-pass-45972362899.json"
def digest(raw):return sha256(raw).hexdigest()
def read(p):return json.loads(p.read_text())
def meta_stable(raw):
    # GUID and creation time are generated per actual export; do not rewrite
    # either file on disk. Strictly remove exactly these header fields.
    for pattern in (rb"(?m)^guid: [0-9a-f]{32}\r?$",rb"(?m)^timeCreated: [0-9]+\r?$"):
        raw,n=re.subn(pattern,b"<volatile>",raw)
        need(n==1,"actual_meta_volatile_header_population")
    return raw
def compare_meta(before,after,enabled):
    a,b=meta_stable(before),meta_stable(after)
    if enabled:
        expected,pos=policy.policy_byte(a)
    else:
        expected,pos=a,None
        need(yaml.safe_load(a.replace(b"<volatile>",b"comment: 0"))["TextureImporter"]["alphaIsTransparency"]==1,"ordinary_alpha_policy")
    need(b==expected,"actual_importer_non_target_byte_drift")
    return pos

def inspect(root,mode):
    normalmap=mode=="normal";bc3=mode in ("normal","bc3")
    states={} if normalmap else None
    objects,externals,mapping,vertices,proofs,requests,pins,producer=authored.load(root,states=states,bc3_mode=bc3,normalmap=normalmap)
    files,docs=gate.actual_index(root/"project",mapping)
    need(len(files)==9 and len(docs)==11 and len(requests)==2,"actual_route_population")
    kw=dict(vertex_payloads=vertices,material_values=True,material_keywords=True,png_top_mips=proofs)
    if normalmap:kw["png_normalmap"]=True
    elif bc3:kw["png_bc3"]=True
    result=gate.compare(objects,externals,mapping,files,docs,**kw)
    field=V11 if normalmap else "selected_same_route_imported_bc3_png_top_mip_verified" if bc3 else "selected_same_route_imported_png_top_mip_verified"
    need(result[field] and result["counts"]["complete_imported_png_bound_submesh_routes"]==4,"actual_same_route_pixel_gate:"+str(result["reason_counts"]))
    source=read(root/"source.json")
    rows=[]
    for key in sorted(requests):
        ptr=mapping[key][1];path,meta=files[ptr[0]]
        imp=png.importer_document(meta,ptr,texture_type=1 if normalmap else 0)
        raw=path.read_bytes()
        with Image.open(path) as im:
            rgba=im.tobytes()
        rows.append(dict(key=list(key),ptr=list(ptr),metadata=meta,texture_type=imp["textureType"],alpha=imp["alphaIsTransparency"],
            png_sha256=digest(raw),rgba_sha256=digest(rgba),rgba_hex=rgba.hex()))
    return dict(source=source,provider_sha256=next(iter(pins.values()))[2],rows=rows,baseline=result), (objects,externals,mapping,vertices,proofs,files,docs,states)

def compare_pair(a,b,mode):
    need(a["source"]==b["source"] and a["provider_sha256"]==b["provider_sha256"],"actual_authored_source_drift")
    need(a["baseline"]==b["baseline"],"actual_route_proof_drift")
    rows=[]
    for x,y in zip(a["rows"],b["rows"],strict=True):
        need(x["key"]==y["key"] and x["ptr"][1:]==y["ptr"][1:] and x["png_sha256"]==y["png_sha256"] and x["rgba_sha256"]==y["rgba_sha256"] and x["rgba_hex"]==y["rgba_hex"],"actual_route_PNG_identity_drift")
        normalmap=mode=="normal"
        need(x["alpha"]==1 and y["alpha"]==(0 if normalmap else 1),"actual_exported_alpha_policy_drift")
        pos=compare_meta(x["metadata"].encode(),y["metadata"].encode(),normalmap)
        rows.append(dict(before=x,after=y,only_alpha_policy_changed=normalmap,normalized_changed_byte_offset=pos))
    return rows

def audit(root,out):
    hist=read(V14)
    need(hist["status"]=="PASS_ACTUAL_AUTHORED_DXT5NM_ALPHA_POLICY_CAUSAL_TEXEL_WITNESS" and hist["verified"]["actual_alpha_zero_repack_loss_isolated"],"V14_actual_causality_required")
    results={};controls={}
    for mode in ("normal","bc3","rgba"):
        off,_=inspect(root/(mode+"-off"),mode)
        on,context=inspect(root/(mode+"-on"),mode)
        rows=compare_pair(off,on,mode)
        results[mode]=dict(rows=rows,baseline=on["baseline"],provider_sha256=on["provider_sha256"])
        if mode=="normal":
            need([x["after"]["png_sha256"] for x in rows]==["9e6be9b9f97d2bf835fbf3ae21d79f889170b7588dddde3f1c351f85cc3b0a54","5ab65d8dc9fb153f045cdc8ea0b5e8293d0e9006ec22938b7aafcddb9ed575d1"],"historical_PNG_bytes")
            # Keep V12 historical semantics intact. It rejects the corrected
            # policy as drift. Reversing the one field in memory reproduces
            # the old V12 proof (counterfactual only, not actual fixed meta).
            objects,externals,mapping,vertices,proofs,files,docs,states=context
            def old(f):
                return gate.compare(objects,externals,mapping,f,docs,vertex_payloads=vertices,material_values=True,material_keywords=True,png_top_mips=proofs,png_normalmap=True,png_importer_states=states)
            actual=old(files)
            need(not actual[V12] and actual["reason_counts"].get("same_route_png_exporter_policy_alphaIsTransparency_drift",0)>0,"V12_scope_not_preserved")
            restored=dict(files)
            for key in states:
                guid=mapping[key][1][0];path,md=files[guid]
                pat=r"(?m)^  alphaIsTransparency: 0$"
                fixed,n=re.subn(pat,"  alphaIsTransparency: 1",md)
                need(n==1,"corrected_policy_anchor");restored[guid]=(path,fixed)
            need(old(restored)[V12],"historical_V12_counterfactual_replay")
            results[mode]["historical_V12_actual_candidate_rejected"]=True
            results[mode]["historical_V12_restored_counterfactual_only"]=True
            x,y=rows[0]["before"]["metadata"].encode(),rows[0]["after"]["metadata"].encode()
            for name,mut in (("revert_alpha",y.replace(b"alphaIsTransparency: 0",b"alphaIsTransparency: 1")),
                    ("other_sampler",y.replace(b"aniso: 2",b"aniso: 3")),
                    ("other_importer_type",y.replace(b"textureType: 1",b"textureType: 0")),
                    ("unrelated_policy",y.replace(b"compressionQuality: 50",b"compressionQuality: 51"))):
                need(mut!=y,"degenerate_actual_metadata_control")
                try:compare_meta(x,mut,True)
                except ValueError as e:controls[name]=str(e)
                else:raise ValueError("V15_control_not_rejected:"+name)
        else:
            y=rows[0]["after"]["metadata"].encode()
            try:compare_meta(rows[0]["before"]["metadata"].encode(),y.replace(b"alphaIsTransparency: 1",b"alphaIsTransparency: 0"),False)
            except ValueError as e:controls[mode+"_global_alpha_disable"]=str(e)
            else:raise ValueError("ordinary_control_not_rejected")
    result=dict(status="PASS_ACTUAL_AUTHORED_SELECTIVE_DXT5NM_PNG_EXPORTER_ALPHA_POLICY",actual_compiled_exporter_modes=6,
        actual_normalmap_policy_changes=2,actual_ordinary_policy_unchanged=4,actual_metadata_controls=controls,
        actual_metadata_control_count=len(controls),scopes=results,source_bytes_unchanged=True,
        original_assets_read=False,production_activation=False,Unity_reimport_of_candidate_verified=False,Android_device=False,XAPK=False)
    need(not out.exists(),"fresh_V15_receipt")
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="scopes"},sort_keys=True))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();audit(a.root,a.out)
