"""Observe source-derived external uniforms at the original stage in a diagnostic draw.
No guessed game values: compare only independently available camera/renderer
values. Other observations and texture dimensions are not provider identity.
"""
import re
from collections import Counter
from hashlib import sha256
import numpy as np
from scripts.gt_resource_register_contract import mask_noncode
from tools.gt_top_resource_closure import selected_array_causal as c, selected_merged_abi as merged

CAL_A=(.125,.375,.625,1.)
CAL_B=(.75,.25,.5,.875)
CLASS_OFFSET=256
CLASS_CAL_A=(0.,0.,0.,0.)
CLASS_CAL_B=(0.,.25,.5,.75)
CLASS_LABELS=("finite","nan","positive_inf","negative_inf")
MATRIX_PROVIDERS={"unity_ObjectToWorld":"object_to_world","unity_WorldToObject":"world_to_object",
                  "unity_MatrixV":"view","unity_MatrixInvV":"inverse_view",
                  "unity_MatrixVP":"view_projection"}
TEXTURE_KINDS={"Texture2D":2,"TextureCube":2,"Texture2DArray":3,"Texture3D":3}

def private_rows(rows,mat,texenvs,parsed,wrapper):
    stages=merged.source_occurrences(rows,mat,texenvs,parsed)
    _,resources,_=merged.collect_wrapper(wrapper)
    result=[];names=set();occurrences=0
    def add(**row):
        row["mode"]=len(result)+2
        c.need(len(result)<192,"provider_row_limit")
        result.append(row)
    for stage in stages:
        for item in stage["members"]:
            if item["category"]!="external":continue
            m=item["member"];name=m["name"];role=stage["role"]
            c.need(re.fullmatch(r"[A-Za-z_]\w*",name) is not None,"provider_name")
            occurrences+=1;names.add(name)
            n=m["array_size"] or 1
            c.need(1<=n<=32 and 1<=m["columns"]<=4 and m["type"] in (0,1),"provider_member_schema")
            for k in range(n):
                symbol=name+(f"[{k}]" if m["array_size"] else "")
                if m["matrix"]:
                    for i in range(4):
                        kind=MATRIX_PROVIDERS.get(name,"unresolved") if not m["array_size"] else "unresolved"
                        add(name=name,role=role,kind=kind,lanes=4,row=i,element=k,expression=f"{symbol}[{i}]",
                            numeric_type="float")
                else:
                    width=m["columns"]
                    kind="camera_position" if name=="_WorldSpaceCameraPos" and width>=3 and m["type"]==0 and not m["array_size"] else "unresolved"
                    expr=f"float{width}({symbol})" if width>1 else f"float({symbol})"
                    add(name=name,role=role,kind=kind,lanes=width,row=0,element=k,expression=expr,
                        numeric_type="uint" if m["type"] else "float")
        for item in stage["resources"]:
            if not item["external"] or item["kind"]!="t":continue
            name=item["name"];typ=resources.get(name,"").split("<",1)[0].strip()
            c.need(typ in TEXTURE_KINDS and stage["role"]=="fs","provider_external_texture_type")
            add(name=name,role="fs",kind="texture_dimensions",lanes=TEXTURE_KINDS[typ],row=0,element=0,
                expression="",numeric_type="uint",texture_kind=typ)
    c.need(occurrences==22 and len(names)==21 and sum(x["kind"]=="texture_dimensions" for x in result)==3,"provider_source_population")
    return result

def entry(wrapper,role):
    code=mask_noncode(wrapper)
    matches=list(re.finditer(r"\b([A-Za-z_]\w*)\s+gt_"+role+r"_main\s*\(([^;{}]*)\)\s*(?::\s*SV_Target0?)?\s*\{",code))
    c.need(len(matches)==1,"provider_entry_anchor")
    m=matches[0];start=m.end()-1;end=c.matching(code,start,"{","}")
    returns=list(re.finditer(r"\breturn\s+([A-Za-z_]\w*)\s*;",code[start+1:end]))
    c.need(len(returns)==1 and len(re.findall(r"\breturn\b",code[start+1:end]))==1,"provider_return_anchor")
    return m[1],m[2].strip(),returns[0][1],start+1+returns[0].start()

def struct_anchor(wrapper,name):
    code=mask_noncode(wrapper)
    m=list(re.finditer(r"\bstruct\s+"+re.escape(name)+r"\s*\{([^{}]*)\}\s*;",code))
    c.need(len(m)==1,"provider_struct_anchor")
    return m[0].start(1),m[0].end(1),m[0][1]

def padded(expr,lanes):
    return "float4("+expr+(", "+", ".join(["0.0"]*(4-lanes)) if lanes<4 else "")+")"

def instrument(wrapper,rows):
    c.need(c.MODE not in wrapper and "gt_provider_" not in wrapper,"provider_name_collision")
    vtype,_,vret,vpos=entry(wrapper,"vs")
    ftype,fargs,fret,fpos=entry(wrapper,"fs")
    fm=re.fullmatch(r"([A-Za-z_]\w*)\s+([A-Za-z_]\w*)",fargs)
    c.need(fm is not None and vtype!=fm[1],"provider_fragment_input_shape")
    vi=struct_anchor(wrapper,vtype);fi=struct_anchor(wrapper,fm[1])
    sem=set(re.findall(r"(?i)\bTEXCOORD(\d+)\b",vi[2]+fi[2]))
    free=next((i for i in range(15,-1,-1) if str(i) not in sem),None)
    c.need(free is not None,"provider_varying_slot")
    lhs=fret
    if ftype!="float4":
        fo=struct_anchor(wrapper,ftype)
        fields=re.findall(r"\bfloat4\s+([A-Za-z_]\w*)\s*:\s*SV_Target0?\s*;",fo[2],re.I)
        c.need(len(fields)==1 and len(re.findall(r":\s*SV_Target\d*",fo[2],re.I))==1,"provider_target_anchor")
        lhs+="."+fields[0]
    field="gt_provider_value"
    vcode=[f"{vret}.{field}=float4(0,0,0,0);"]
    fcode=[f"{lhs}=float4(0.125,0.375,0.625,1.0);",
           f"if (fmod({c.MODE},256.0)==1.0) {lhs}=float4(0.75,0.25,0.5,0.875);"]
    for row in rows:
        cond=f"if (fmod({c.MODE},256.0)=={row['mode']}.0)"
        if row["kind"]=="texture_dimensions":
            args=["gt_provider_w","gt_provider_h"]+["gt_provider_d"]*(row["lanes"]==3)
            fcode.append(cond+" { uint "+", ".join(args)+"; "+row["name"]+".GetDimensions("+", ".join(args)+"); "+
                         lhs+"="+padded(", ".join("float("+a+")" for a in args),row["lanes"])+"; }")
        elif row["role"]=="vs":
            vcode.append(cond+" "+vret+"."+field+"="+padded(row["expression"],row["lanes"])+";")
            fcode.append(cond+" "+lhs+"="+fm[2]+"."+field+";")
        else:
            fcode.append(cond+" "+lhs+"="+padded(row["expression"],row["lanes"])+";")
    # Read finite classification from the shader BEFORE output conversion.
    # The second marker covers all IEEE classes using integer bits directly.
    fcode.append(f"if ({c.MODE}>=256.0) {{")
    fcode.append(f"if (fmod({c.MODE},256.0)==1.0) {lhs}=gt_provider_class4(uint4(0x3f800000u,0x7fc00001u,0x7f800000u,0xff800000u));")
    fcode.append(f"else {lhs}=gt_provider_class4(asuint({lhs})); }}")
    decl=f"\nnointerpolation float4 {field} : TEXCOORD{free};\n"
    edits=[(vi[1],decl),(fi[1],decl),(vpos,"\n"+"\n".join(vcode)+"\n"),(fpos,"\n"+"\n".join(fcode)+"\n")]
    for pos,value in sorted(edits,reverse=True):wrapper=wrapper[:pos]+value+wrapper[pos:]
    anchor="#pragma fragment gt_fs_main\n"
    c.need(wrapper.count(anchor)==1,"provider_pragma_anchor")
    helper=("float "+c.MODE+";\n"
            "float gt_provider_class(uint v) { uint e=v&0x7f800000u; uint m=v&0x007fffffu; "
            "if(e!=0x7f800000u)return 0.0; if(m!=0u)return 0.25; "
            "return (v&0x80000000u)!=0u ? 0.75 : 0.5; }\n"
            "float4 gt_provider_class4(uint4 v) { return float4(gt_provider_class(v.x),gt_provider_class(v.y),"
            "gt_provider_class(v.z),gt_provider_class(v.w)); }\n")
    return wrapper.replace(anchor,anchor+helper,1)

def stage(root,parsed,passes,wrapper,rows,mat,texenvs,shader_factory):
    from scripts.gt_original_921_shaderlab import verify_entrypoints
    private=private_rows(rows,mat,texenvs,parsed,wrapper)
    body=instrument(wrapper,private)
    verify_entrypoints(body,root,routes=[[[]]])
    raw,_=shader_factory(parsed,passes,body,diagnostic=True)
    (root/"array-tap-shader.bytes").write_bytes(raw)
    return dict(provider_probe=True,provider_transport_version=2,tap_available=True,tap_shader_sha=sha256(raw).hexdigest(),
                provider_rows=[{k:v for k,v in r.items() if k!="expression"} for r in private])

def finite_uniform(pixels,mask,lanes):
    a=pixels[mask]
    if not a.size or not np.isfinite(a).all():return None
    if lanes<4 and np.max(np.abs(a[:,lanes:]))>1e-5:return None
    sample=a[0,:lanes].astype(np.float64)
    if not np.allclose(a[:,:lanes],sample,atol=1e-4,rtol=1e-5):return None
    return sample

def raw_classes(a):
    """Return lane category, not floating values or NaN payloads."""
    codes=np.zeros(a.shape,dtype=np.uint8)
    codes[np.isnan(a)]=1;codes[np.isposinf(a)]=2;codes[np.isneginf(a)]=3
    return codes

def class_image(a):
    c.need(np.isfinite(a).all(),"provider_class_image_nonfinite")
    nearest=np.rint(a*4)
    c.need(np.all((nearest>=0)&(nearest<=3)) and np.all(np.abs(a-nearest/4)<=1e-6),
           "provider_class_image_invalid_code")
    return nearest.astype(np.uint8)

def classify_row(raw,encoded,mask,lanes):
    c.need(raw.shape==encoded.shape and raw.ndim==3 and raw.shape[-1]==4 and
           raw.shape[:2]==mask.shape and 1<=lanes<=4 and mask.any(),"provider_row_shape")
    a=raw[mask];b=encoded[mask]
    x=raw_classes(a);y=class_image(b)
    result=Counter()
    result["background_nonfinite_lanes"]=int((~np.isfinite(raw[~mask])).sum())
    result["foreground_pixels"]=len(a)
    for i,label in enumerate(CLASS_LABELS):
        result["raw_"+label+"_lanes"]=int((x[:,:lanes]==i).sum())
        result["encoded_"+label+"_lanes"]=int((y[:,:lanes]==i).sum())
    result["raw_encoded_class_mismatch_lanes"]=int((x!=y).sum())
    result["raw_nonfinite_padding_lanes"]=int((x[:,lanes:]!=0).sum())
    result["encoded_nonfinite_padding_lanes"]=int((y[:,lanes:]!=0).sum())
    bad_transport=(result["raw_encoded_class_mismatch_lanes"] or result["background_nonfinite_lanes"])
    if bad_transport:status="transport_mismatch"
    elif np.any(y[:,lanes:]!=0):status="invalid_padding"
    elif np.any(y[:,:lanes]!=0):status="shader_nonfinite"
    else:
        val=finite_uniform(raw,mask,lanes)
        status="finite_uniform" if val is not None else "finite_nonuniform_or_padding"
    return status,dict(result)

def summarize(cfg,receipt,read):
    rows=cfg["provider_rows"];views=receipt["views"]
    c.need(cfg.get("provider_transport_version")==2 and len(views)==3 and len(rows)>0 and len(rows)<=192,"provider_population")
    c.need([r["mode"] for r in rows]==list(range(2,len(rows)+2)),"provider_mode_order")
    counts=Counter();observed=[[] for _ in rows];known=[[] for _ in rows]
    per_row=[Counter() for _ in rows];groups={}
    for view,v in enumerate(views):
        c.need(v["view"]==view and len(v["expected"])==len(rows),"provider_view_schema")
        def load(mode):return read(f"provider-{view}-{mode}.f32")
        a,b,ca,cb=(load(m) for m in (0,1,CLASS_OFFSET,CLASS_OFFSET+1))
        c.need(a.shape==b.shape==ca.shape==cb.shape and a.ndim==3 and a.shape[-1]==4 and
               all(np.isfinite(z).all() for z in (a,b,ca,cb)),"provider_calibration_schema")
        ma=c.near(a,CAL_A);mb=c.near(b,CAL_B)
        mca=c.near(ca,CLASS_CAL_A);mcb=c.near(cb,CLASS_CAL_B)
        c.need(ma.any() and np.array_equal(ma,mb) and np.array_equal(ma,mca) and
               np.array_equal(ma,mcb),"provider_calibration")
        counts["calibrated_views"]+=1;counts["classification_calibrated_views"]+=1
        counts["calibration_pixels"]+=int(ma.sum())
        for i,(r,e) in enumerate(zip(rows,v["expected"],strict=True)):
            c.need(e["mode"]==r["mode"],"provider_expected_order")
            lanes=r["lanes"];p=load(r["mode"]);encoded=load(CLASS_OFFSET+r["mode"])
            status,stats=classify_row(p,encoded,ma,lanes)
            counts["lane_observations"]+=1;counts[status]+=1
            counts.update(stats);per_row[i][status]+=1;per_row[i].update(stats)
            key=(r["role"],r["kind"])
            group=groups.setdefault(key,Counter());group[status]+=1;group["lane_observations"]+=1
            if e["known"]:
                expected=np.asarray(e["value"],dtype=np.float64);n=e["compare_lanes"]
                c.need(expected.shape==(4,) and 1<=n<=lanes and np.isfinite(expected).all(),"provider_expected_value")
                c.need(r["kind"]!="unresolved","provider_unknown_claim")
                counts["cpu_expected_observations"]+=1
            else:counts["unknown_provider_observations"]+=1
            if status!="finite_uniform":
                if e["known"]:counts["cpu_expected_unusable_observations"]+=1
                observed[i].append(None);known[i].append(False);continue
            val=finite_uniform(p,ma,lanes);c.need(val is not None,"provider_finite_class_inconsistency")
            observed[i].append(val)
            if r["kind"]=="texture_dimensions":
                counts["texture_dimension_observations"]+=1
                if np.all(val>0):counts["texture_positive_dimensions"]+=1
            if not e["known"]:known[i].append(False);continue
            good=bool(np.allclose(val[:n],expected[:n],atol=1e-4,rtol=1e-4))
            wrong=expected[:n].copy();wrong[0]+=max(1.,abs(wrong[0])*.5)
            bad=not np.allclose(val[:n],wrong,atol=1e-4,rtol=1e-4)
            counts["cpu_comparable_observations"]+=1
            verdict="cpu_matching_observations" if good and bad else "cpu_mismatching_observations"
            counts[verdict]+=1;per_row[i][verdict]+=1;group[verdict]+=1
            if r["kind"]=="texture_dimensions":counts["texture_dimension_cpu_matches"]+=int(good and bad)
            else:counts["engine_numeric_cpu_matches"]+=int(good and bad)
            known[i].append(good and bad)
    summary=[]
    for i,r in enumerate(rows):
        a=observed[i]
        if all(x is not None for x in a):
            counts["fully_observed_rows"]+=1
            if any(not np.allclose(a[0],x,atol=1e-4,rtol=1e-5) for x in a[1:]):
                counts["view_dependent_rows"]+=1
                if r["kind"] not in ("unresolved","texture_dimensions") and all(known[i]):
                    counts["verified_view_dependent_engine_numeric_rows"]+=1
        if all(known[i]):counts["all_views_cpu_matching_rows"]+=1
        summary.append(dict(ordinal=i,stage=r["role"],provider_category=r["kind"],lanes=r["lanes"],
                            observations=dict(per_row[i])))
    c.need(counts["lane_observations"]==3*len(rows) and counts["classification_calibrated_views"]==3,"provider_observation_population")
    # Nonfinite shader values are a diagnosed defect, not a verified upload.
    # A discrepancy between shader classification and raw transport remains
    # inconclusive, even if some other rows have usable measurements.
    transport_ok=counts["transport_mismatch"]==0
    observed_ok=counts["finite_uniform"]>0 or counts["shader_nonfinite"]>0
    return dict(status="OBSERVED_SOURCE_STAGE_PROVIDER_DIAGNOSTIC" if transport_ok and observed_ok else "INCONCLUSIVE_PROVIDER_TRANSPORT",
                source_probe_rows=len(rows),stage_rows=dict(Counter(r["role"] for r in rows)),
                provider_categories=dict(Counter(r["kind"] for r in rows)),counts=dict(counts),
                per_stage_category=[dict(stage=k[0],provider_category=k[1],counts=dict(v)) for k,v in sorted(groups.items())],
                row_observations=summary,nonfinite_classification_transport_verified=transport_ok,
                original_game_global_resources_verified=False,runtime_uniform_upload_verified=False,
                white_mesh_repair_verified=False,diagnostic_only=True)
