"""Skybox: verify original register identity across actual compiler locations.

No invented varying values, weakened constant-buffer checks, or Unity/device claim.
The pinned-location control is diagnostic and never eligible for installation.
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

from tools.gt_skybox_shader_wrapper import wrapper as w
from tools.gt_skybox_offset_differential import audit as d
from tools.gt_skybox_shader_program import audit as prior
from tools.gt_light_same_export.audit import require, Rejected
from scripts.gt_original_921_all_variants import enumerate_all, stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes, shaderlab_layout
from scripts.gt_original_921_semantics import pin_varying_locations
from scripts.gt_original_921_shaderlab import unity_varying_semantics, verify_entrypoints
from scripts.t3_original_921_dxbc_semantic_join import read_original_dxbc_signatures
from scripts.w1_recover_graphics_programs import command, decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.t3_spirv_interface_name_drift import read_reflection

STATUS = "PASS_SOURCE_REGISTER_JOIN_PRIVATE_SAME_EXPORT"
PREFIX = "#if defined(SHADER_STAGE_VERTEX) && !defined(SHADER_STAGE_FRAGMENT)\n"
MID = "\n#elif defined(SHADER_STAGE_FRAGMENT) && !defined(SHADER_STAGE_VERTEX)\n"
END = "\n#else\n#error GT_SKYBOX_STAGE_SELECTION\n#endif"
FIELD = re.compile(r"(?m)^([ \t]+)((?:nointerpolation |linear |centroid |sample |noperspective )?\w+)\s+([ov])([0-9]+)\s*:\s*TEXCOORD([0-9]+);[ \t]*$")


def split_body(body):
    require(body.startswith(PREFIX) and body.endswith(END) and body.count(MID)==1,
            "skybox_interface_stage_body_schema")
    vs,fs = body[len(PREFIX):-len(END)].split(MID)
    require(d.isolated_body(vs,fs)==body,"skybox_interface_stage_body_roundtrip")
    return vs,fs


def original_registers(rows):
    out = {}
    for row in rows:
        if row["system_value"]:
            continue
        reg = row["register"]
        require(type(reg) is int and 0<=reg<=4095 and reg not in out,
                "skybox_interface_original_register_not_unique")
        out[reg] = row
    return out


def source_pair(vs,fs):
    vo = original_registers(vs["output"])
    fi = original_registers(fs["input"])
    for reg,row in fi.items():
        other = vo.get(reg)
        require(other is not None and
                (row["semantic"],row["index"],row["type"])==
                (other["semantic"],other["index"],other["type"]) and
                not (row["used_mask"] & ~other["mask"]),
                "skybox_interface_original_semantic_or_lane_mismatch")
    require(len(fi)==7,"skybox_interface_original_seven_varyings_drift")
    return vo,fi


def reflected_registers(reflection,side,prefix):
    result = {}
    used_locations = set()
    for row in reflection.get(side,[]):
        name,typ,loc = row.get("name"),row.get("type"),row.get("location")
        match = re.fullmatch(r"(?:[^.\r\n]+\.)*"+prefix+r"([0-9]+)",name or "")
        require(match is not None and isinstance(typ,str) and
                type(loc) is int and 0<=loc<=65535,
                "skybox_interface_reflected_register_identity_unresolved")
        reg = int(match[1])
        require(reg not in result and loc not in used_locations,
                "skybox_interface_duplicate_register_or_location")
        used_locations.add(loc)
        result[reg] = (typ,loc)
    return result


def profile(actual,baseline):
    common = set(actual)&set(baseline)
    matched = {r for r in common if actual[r][0]==baseline[r][0]}
    same = sum(actual[r][1]==baseline[r][1] for r in matched)
    return {"expected":len(baseline),"actual":len(actual),
        "same_register_and_type":len(matched),"same_original_location":same,
        "relocated_register":len(matched)-same,"missing_register":len(set(baseline)-set(actual)),
        "extra_register":len(set(actual)-set(baseline)),"different_type":len(common)-len(matched),
        "complete_identity":set(actual)==set(baseline) and len(matched)==len(baseline)}


def join(vs,fs,expected_vs,expected_fs):
    vp,fp = profile(vs,expected_vs),profile(fs,expected_fs)
    joined = 0
    wrong = 0
    for reg,row in expected_fs.items():
        if reg in vs and reg in fs and vs[reg]==fs[reg] and fs[reg][0]==row[0]:
            joined += 1
        else:
            wrong += 1
    # A type-only join would accept an equal-type register substitution.
    # Every consumer must instead match its own original producer register.
    return {"vs_outputs":vp,"fs_inputs":fp,
        "original_registers_joined_at_same_actual_location":joined,
        "original_registers_not_joined":wrong,
        "all_original_registers_linked":vp["complete_identity"] and fp["complete_identity"]
             and joined==len(expected_fs) and wrong==0,
        "absolute_original_vulkan_locations_preserved":
            vp["complete_identity"] and fp["complete_identity"] and
            vp["relocated_register"]==fp["relocated_register"]==0}


def struct_fields(source,stage):
    name = "SPIRV_Cross_Output" if stage=="vs" else "SPIRV_Cross_Input"
    matches = list(re.finditer(r"\bstruct\s+"+name+r"\s*\{([^{}]*)\}",source))
    require(len(matches)==1,"skybox_interface_struct_schema")
    structure = matches[0]
    body = structure[1]
    fields = list(FIELD.finditer(body))
    require(fields and not re.search(r":\s*TEXCOORD[0-9]+\b",FIELD.sub("",body)),
            "skybox_interface_unrecognized_varying_declaration")
    rows = {}
    expected = "o" if stage=="vs" else "v"
    for f in fields:
        reg = int(f[4])
        require(f[3]==expected and f[4]==f[5] and reg not in rows,
                "skybox_interface_source_field_register_mismatch")
        rows[reg] = f
    return structure,body,rows


def align_fragment(vs,fs,expected_vs,expected_fs):
    """Preserve used FS declarations; expose only original producer fields as anchors.
    No new reads, values, or fake semantics. Reject if compiled active interface grows.
    """
    _,_,producer = struct_fields(vs,"vs")
    struct,body,consumer = struct_fields(fs,"fs")
    require(set(producer)==set(expected_vs) and set(consumer)==set(expected_fs)
            and set(consumer)<=set(producer),"skybox_interface_anchor_source_coverage")
    current = list(consumer)
    wanted = list(producer)
    if current==wanted:
        return fs,0
    matches = list(consumer.values())
    start,end = matches[0].start(),matches[-1].end()
    require(not FIELD.sub("",body[start:end]).strip(),
            "skybox_interface_anchor_noncontiguous_declarations")
    outside = fs[:struct.start(1)] + body[:start] + body[end:] + fs[struct.end(1):]
    lines = []
    for reg,p in producer.items():
        if reg in consumer:
            # Preserve the actual fragment type and interpolation declaration.
            f = consumer[reg]
            lines.append(f[0])
        else:
            require(not re.search(r"\bv"+str(reg)+r"\b",outside),
                    "skybox_interface_anchor_symbol_already_used")
            lines.append(matches[0][1]+p[2]+" v"+str(reg)+" : TEXCOORD"+str(reg)+";")
    replacement = body[:start]+"\n".join(lines)+body[end:]
    result = fs[:struct.start(1)]+replacement+fs[struct.end(1):]
    _,_,new = struct_fields(result,"fs")
    require(list(new)==wanted and all(new[r][0]==consumer[r][0] for r in consumer),
            "skybox_interface_anchor_changed_original_input_declaration")
    return result,len(set(producer)-set(consumer))


def prepare(sh,private,report):
    parsed=sh["m_ParsedForm"]
    tables=[records(parts) for platform,parts in decoded_platforms(sh) if platform==4]
    require(len(tables)==1,"skybox_interface_source_d3d11_table")
    pairs,orphans,passes,distinct=enumerate_all(parsed,tables[0],variants=stage_variants,
        permutation=variant_key,linker=linked_program,topology=(1,1,0,2))
    routes,_=keyword_routes(parsed,pairs,orphans,passes)
    w.single_route(routes)
    layout,counts=shaderlab_layout(parsed,passes,expected_property_count=0,
                                   allow_next23b_texture_hdr_flags=True)
    folders={}
    for i,(ident,item) in enumerate(distinct.items()):
        folder=private/f"program-{i:03d}"
        folder.mkdir(mode=0o700)
        require(hashlib.sha256(item["source_code"]).hexdigest()==ident[1],
                "skybox_interface_original_program_commitment")
        folders[ident]=folder.name
        tr=translate(item["source_code"],item["stage"],folder)
        require(all(tr.get(k) is True for k in
            ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid")),
            "skybox_interface_original_translation")
    report["bound_stage_counts"]=stage_parameter_records(pairs,orphans,passes,tables[0],private,folders)
    require(report["bound_stage_counts"]["named_constant_buffer_reflected_offsets_verified"]==45 and
            report["bound_stage_counts"]["original_vertex_fragment_varying_records_matched"]==7,
            "skybox_interface_prior_original_stage_counts_drift")
    named=json.loads((private/"original-private-parameter-records.json").read_text())["stage_records"]
    require(len(named)==2 and [r["stage"] for r in named]==[1,0],"skybox_interface_stage_record_order")
    layouts=[r["source_constant_buffer_layouts"] for r in named]
    code=[distinct[pairs[0][s]["program_ref"]]["source_code"] for s in ("vs","fs")]
    signatures=source_pair(*(read_original_dxbc_signatures(c) for c in code))
    candidate,body=d.build_isolated(sh,private,layouts,named)
    require(w.attach(layout,body)==candidate,"skybox_interface_layout_commitment")
    return layout,body,layouts,named,signatures


def baseline(private,signatures):
    v=read_reflection(private/"bound-stage-000/varying-bound.spv")
    f=read_reflection(private/"bound-stage-001/varying-bound.spv")
    mesh=read_reflection(private/"bound-stage-000/mesh-input-bound.spv")
    vo=reflected_registers(v,"outputs","o")
    fi=reflected_registers(f,"inputs","v")
    require(set(vo)==set(signatures[0]) and set(fi)==set(signatures[1]) and
            all(r==loc for entries in (vo,fi) for r,(_,loc) in entries.items()) and
            all(vo.get(r)==row for r,row in fi.items()),
            "skybox_interface_pinned_source_register_join")
    return v,f,mesh,vo,fi


def compile_body(body,private,label,layouts,named,reference,report):
    hlsl=private/(label+".hlsl")
    hlsl.write_text(body,encoding="utf-8")
    stages=[]
    report["stages"]={}
    for i,(stage,suffix,macro,entry) in enumerate(d.STAGES):
        r=d.compile_entry(hlsl,private/(label+"-"+stage+".spv"),suffix,entry,macro)
        row=d.profile(r,layouts[i],stage)
        report["stages"][stage]=row
        row["strict_original_offsets"]=w.verify_final_offsets(r,layouts[i],stage)
        row["strict_original_offsets_pass"]=True
        require(row["exact_owner_offset"]==row["expected_members"],"skybox_interface_offset_regression")
        row["named_resources_verified"]=d.resource_parity(r,reference[i])
        require(row["named_resources_verified"]==len(named[i]["source_texture_sampler_bindings"]),
                "skybox_interface_named_resource_regression")
        stages.append(r)
    v,f,mesh,vo,fi=reference
    report["nonvarying_interfaces"]={
        "mesh_inputs_exact":w.interface(stages[0],"inputs")==w.interface(mesh,"inputs"),
        "fragment_outputs_exact":w.interface(stages[1],"outputs")==w.interface(f,"outputs"),
        "mesh_input_count":len(w.interface(mesh,"inputs")),
        "fragment_output_count":len(w.interface(f,"outputs"))}
    report["join"]=join(reflected_registers(stages[0],"outputs","o"),
                        reflected_registers(stages[1],"inputs","v"),vo,fi)
    report["original_offsets"]=sum(row["strict_original_offsets"] for row in report["stages"].values())
    report["named_resources"]=sum(row["named_resources_verified"] for row in report["stages"].values())
    require(report["original_offsets"]==45 and report["named_resources"]==10,
            "skybox_interface_source_binding_population_drift")
    return (report["nonvarying_interfaces"]["mesh_inputs_exact"] and
            report["nonvarying_interfaces"]["fragment_outputs_exact"] and
            report["join"]["all_original_registers_linked"])


def negative_macros(body,private):
    hlsl=private/"selected.hlsl"
    hlsl.write_text(body,encoding="utf-8")
    for i,(_,suffix,macro,entry) in enumerate(d.STAGES):
        other=d.STAGES[1-i][2]
        for macros in ([],[other],[macro,other]):
            bad=private/"forbidden.spv"
            bad.unlink(missing_ok=True)
            require(not command(d.compile_args(hlsl,bad,suffix,entry,macros)),
                    "skybox_interface_invalid_stage_selector_accepted")
    return 6


def run(x):
    report=dict(status="INCONCLUSIVE",phase="exact_source_and_export_binding",
        original_object_sha256=w.OBJECT_SHA,same_export_binding_verified=False,
        private_wrapper_installed=False,original_assets_mutated=False,original_assets_published=False,
        Unity_import_verified=False,device_pixels_proven=False,production=False,XAPK=False,all_gates_open=True)
    try:
        require(x.project.resolve()==(x.destination.parent/"export/ExportedProject").resolve()
                and not any(p.is_symlink() for p in (x.project,*x.project.parents)),
                "skybox_interface_export_not_disposable")
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            sh,shader,protected,src=w.exact_source_and_export(x,x.destination/"Raft_Data",
                json.loads(x.skybox_plan.read_text()),json.loads(x.plan.read_text()))
            report["same_export_binding_verified"]=True
            with tempfile.TemporaryDirectory(prefix="source-register-join-",dir=x.destination.parent) as tmp:
                private=Path(tmp)
                report["phase"]="original_source_binding"
                layout,body,layouts,named,signatures=prepare(sh,private,report)
                report["phase"]="original_pinned_register_reference"
                ref=baseline(private,signatures)
                vs,fs=split_body(body)
                pinned=[pin_varying_locations(s,1-i) for i,s in enumerate((vs,fs))]
                require([unity_varying_semantics(s) for s in pinned]==[vs,fs],
                        "skybox_interface_pinned_control_not_reversible")
                report["pinned_reference_control"]={}
                pinned_ok=compile_body(d.isolated_body(*pinned),private,"explicit-pin",layouts,named,ref,
                                       report["pinned_reference_control"])
                require(pinned_ok and report["pinned_reference_control"]["join"]
                        ["absolute_original_vulkan_locations_preserved"],"skybox_interface_pinned_control_failed")
                report["phase"]="attribute_free_actual_register_join"
                report["attribute_free"]={}
                ok=compile_body(body,private,"attribute-free",layouts,named,ref,report["attribute_free"])
                selected=body
                report["selected_mode"]="unmodified_stage_isolated_hlsl" if ok else None
                if not ok:
                    report["phase"]="original_producer_field_order_control"
                    try:
                        aligned,n=align_fragment(vs,fs,ref[3],ref[4])
                        report["source_producer_anchor_fields_added"]=n
                        if aligned!=fs:
                            report["producer_order"]={}
                            alternative=d.isolated_body(vs,aligned)
                            ok=compile_body(alternative,private,"producer-order",layouts,named,ref,
                                            report["producer_order"])
                            if ok:
                                selected=alternative
                                report["selected_mode"]="original_producer_field_order"
                        else:
                            report["producer_order_no_change"]=True
                    except ValueError as exc:
                        report["producer_order_failure"]=w.error_category(exc)
                require(ok,"skybox_interface_no_attribute_free_register_join")
                report["phase"]="selected_wrapper_regression_and_private_install"
                require("[[vk::location" not in selected,"skybox_interface_diagnostic_attribute_in_candidate")
                candidate=w.attach(layout,selected)
                verify_entrypoints(candidate,private,routes=[[[]]])
                report["invalid_stage_macro_sets_rejected"]=negative_macros(selected,private)
                structure=prior.classify_program(src,candidate)
                require(structure["status"]=="NON_DUMMY_STRUCTURE_ONLY" and
                        structure["pass_count"]==1 and structure["all_passes_programmed"],
                        "skybox_interface_candidate_structure")
                report["private_install"]=w.install(shader,protected,x.project,candidate)
                report["private_wrapper_installed"]=True
                report["static_original_register_join_verified"]=True
                report["Unity_stage_macro_selection_verified"]=False
        report.update(status=STATUS,phase="complete")
    except Exception as exc:
        report["reason"]=w.error_category(exc)
    x.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_SOURCE_REGISTER_JOIN "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for k in ("destination","skybox-plan","plan","project","trace","w1","b02","report"):
        parser.add_argument("--"+k,type=Path,required=True)
    return run(parser.parse_args())


if __name__=="__main__":
    raise SystemExit(main())
