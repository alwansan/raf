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
           f"if ({c.MODE}==1.0) {lhs}=float4(0.75,0.25,0.5,0.875);"]
    for row in rows:
        cond=f"if ({c.MODE}=={row['mode']}.0)"
        if row["kind"]=="texture_dimensions":
            args=["gt_provider_w","gt_provider_h"]+["gt_provider_d"]*(row["lanes"]==3)
            fcode.append(cond+" { uint "+", ".join(args)+"; "+row["name"]+".GetDimensions("+", ".join(args)+"); "+
                         lhs+"="+padded(", ".join("float("+a+")" for a in args),row["lanes"])+"; }")
        elif row["role"]=="vs":
            vcode.append(cond+" "+vret+"."+field+"="+padded(row["expression"],row["lanes"])+";")
            fcode.append(cond+" "+lhs+"="+fm[2]+"."+field+";")
        else:
            fcode.append(cond+" "+lhs+"="+padded(row["expression"],row["lanes"])+";")
    decl=f"\nnointerpolation float4 {field} : TEXCOORD{free};\n"
    edits=[(vi[1],decl),(fi[1],decl),(vpos,"\n"+"\n".join(vcode)+"\n"),(fpos,"\n"+"\n".join(fcode)+"\n")]
    for pos,value in sorted(edits,reverse=True):wrapper=wrapper[:pos]+value+wrapper[pos:]
    anchor="#pragma fragment gt_fs_main\n"
    c.need(wrapper.count(anchor)==1,"provider_pragma_anchor")
    return wrapper.replace(anchor,anchor+"float "+c.MODE+";\n",1)

def stage(root,parsed,passes,wrapper,rows,mat,texenvs,shader_factory):
    from scripts.gt_original_921_shaderlab import verify_entrypoints
    private=private_rows(rows,mat,texenvs,parsed,wrapper)
    body=instrument(wrapper,private)
    verify_entrypoints(body,root,routes=[[[]]])
    raw,_=shader_factory(parsed,passes,body,diagnostic=True)
    (root/"array-tap-shader.bytes").write_bytes(raw)
    return dict(provider_probe=True,tap_available=True,tap_shader_sha=sha256(raw).hexdigest(),
                provider_rows=[{k:v for k,v in r.items() if k!="expression"} for r in private])

def finite_uniform(pixels,mask,lanes):
    a=pixels[mask]
    if not a.size or not np.isfinite(a).all():return None
    if lanes<4 and np.max(np.abs(a[:,lanes:]))>1e-5:return None
    sample=a[0,:lanes].astype(np.float64)
    if not np.allclose(a[:,:lanes],sample,atol=1e-4,rtol=1e-5):return None
    return sample

def summarize(cfg,receipt,read):
    rows=cfg["provider_rows"];views=receipt["views"]
    c.need(len(views)==3 and len(rows)>0 and len(rows)<=192,"provider_population")
    c.need([r["mode"] for r in rows]==list(range(2,len(rows)+2)),"provider_mode_order")
    counts=Counter();observed=[[] for _ in rows];known=[[] for _ in rows]
    for view,v in enumerate(views):
        c.need(v["view"]==view and len(v["expected"])==len(rows),"provider_view_schema")
        a=read(f"provider-{view}-0.f32");b=read(f"provider-{view}-1.f32")
        ma=c.near(a,CAL_A);mb=c.near(b,CAL_B)
        c.need(ma.any() and np.array_equal(ma,mb),"provider_calibration")
        counts["calibrated_views"]+=1;counts["calibration_pixels"]+=int(ma.sum())
        for i,(r,e) in enumerate(zip(rows,v["expected"],strict=True)):
            c.need(e["mode"]==r["mode"],"provider_expected_order")
            lanes=r["lanes"];p=read(f"provider-{view}-{r['mode']}.f32")
            val=finite_uniform(p,ma,lanes)
            counts["lane_observations"]+=1
            if val is None:counts["nonfinite_or_nonuniform"]+=1;observed[i].append(None);known[i].append(False);continue
            counts["finite_uniform"]+=1;observed[i].append(val)
            if r["kind"]=="texture_dimensions":
                counts["texture_dimension_observations"]+=1
                if np.all(val>0):counts["texture_positive_dimensions"]+=1
            if not e["known"]:
                counts["unknown_provider_observations"]+=1;known[i].append(False);continue
            expected=np.asarray(e["value"],dtype=np.float64)
            n=e["compare_lanes"]
            c.need(expected.shape==(4,) and 1<=n<=lanes and np.isfinite(expected).all(),"provider_expected_value")
            c.need(r["kind"]!="unresolved","provider_unknown_claim")
            good=bool(np.allclose(val[:n],expected[:n],atol=1e-4,rtol=1e-4))
            # Negative comparator must actually disagree, not just be a label.
            wrong=expected[:n].copy();wrong[0]+=max(1.,abs(wrong[0])*.5)
            bad=not np.allclose(val[:n],wrong,atol=1e-4,rtol=1e-4)
            counts["cpu_comparable_observations"]+=1
            counts["cpu_matching_observations" if good and bad else "cpu_mismatching_observations"]+=1
            if r["kind"]=="texture_dimensions":counts["texture_dimension_cpu_matches"]+=int(good and bad)
            else:counts["engine_numeric_cpu_matches"]+=int(good and bad)
            known[i].append(good and bad)
    for i,r in enumerate(rows):
        a=observed[i]
        if all(x is not None for x in a):
            counts["fully_observed_rows"]+=1
            if any(not np.allclose(a[0],x,atol=1e-4,rtol=1e-5) for x in a[1:]):
                counts["view_dependent_rows"]+=1
                if r["kind"] not in ("unresolved","texture_dimensions") and all(known[i]):
                    counts["verified_view_dependent_engine_numeric_rows"]+=1
        if all(known[i]):counts["all_views_cpu_matching_rows"]+=1
    c.need(counts["finite_uniform"]>0 and counts["calibrated_views"]==3,"provider_no_readback")
    return dict(status="OBSERVED_SOURCE_STAGE_PROVIDER_DIAGNOSTIC",
                source_probe_rows=len(rows),stage_rows=dict(Counter(r["role"] for r in rows)),
                provider_categories=dict(Counter(r["kind"] for r in rows)),counts=dict(counts),
                original_game_global_resources_verified=False,runtime_uniform_upload_verified=False,
                white_mesh_repair_verified=False,diagnostic_only=True)
