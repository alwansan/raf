"""Exact skybox offset regression: differential merge vs stage-local binding.
Static Vulkan validation only; no Unity compiler or device claim.
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
from tools.gt_skybox_shader_program import audit as prior
from tools.gt_light_same_export.audit import require, Rejected
from scripts.gt_original_921_shaderlab import (
    unity_resource_bindings, unity_varying_semantics, verify_entrypoints,
)
from scripts.gt_original_921_semantics import restore_vertex_inputs, pin_varying_locations
from scripts.w1_recover_graphics_programs import command, decoded_platforms, records
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.gt_original_921_all_variants import enumerate_all
from scripts.gt_original_921_keyword_routes import shaderlab_layout
from scripts.t3_spirv_interface_name_drift import read_reflection

STATUS = "PASS_STAGE_ISOLATED_SOURCE_BOUND_WRAPPER_PRIVATE_SAME_EXPORT"
STAGES = (("vs","vert","VERTEX","gt_vs_main"),("fs","frag","FRAGMENT","gt_fs_main"))
RESOURCE_KINDS = ("separate_images","separate_samplers","textures","images","ssbos",
                  "storage_images","subpass_inputs","acceleration_structures")


def source_buffer_name(item, stage):
    if item["name"] == "$Globals":
        return f"gt_{stage}_raft921_cb{item['source_slot']}_Globals"
    return item["name"]


def profile(reflected, layouts, stage):
    """Count only; distinguish absent-in-owner from moved or offset drift."""
    types = reflected.get("types", {})
    blocks = {}
    for row in reflected.get("ubos", []):
        name = row["name"]
        require(name not in blocks, "skybox_offset_duplicate_reflected_block")
        fields = types[row["type"]]["members"]
        members = {m["name"]:m for m in fields}
        require(len(members)==len(fields), "skybox_offset_duplicate_reflected_member")
        blocks[name] = members
    result = dict(expected_blocks=len(layouts), matched_blocks=0, expected_members=0,
        exact_owner_offset=0, wrong_owner_offset=0, missing_from_owner=0,
        found_in_other_block=0, found_in_other_block_same_offset=0,
        absent_from_all_blocks=0, ambiguous_other_block=0)
    for item in layouts:
        name = source_buffer_name(item,stage)
        current = blocks.get(name,{})
        result["matched_blocks"] += int(name in blocks)
        for member in item["members"]+item["structs"]:
            result["expected_members"] += 1
            symbol = member["name"]
            original_offset = member["index"]
            if symbol in current:
                key = "exact_owner_offset" if current[symbol]["offset"]==original_offset else "wrong_owner_offset"
                result[key] += 1
            else:
                result["missing_from_owner"] += 1
                others = [fields[symbol] for owner,fields in blocks.items()
                          if owner!=name and symbol in fields]
                if others:
                    result["found_in_other_block"] += 1
                    result["found_in_other_block_same_offset"] += int(any(m["offset"]==original_offset for m in others))
                    result["ambiguous_other_block"] += int(len(others)>1)
                else:
                    result["absent_from_all_blocks"] += 1
    return result


def shared_global_members(layouts):
    left,right = [{m["name"]:m for b in group if b["name"]=="$Globals"
                  for m in b["members"]} for group in layouts]
    both = left.keys() & right.keys()
    return {"same_original_global_name_across_stages":len(both),
            "shared_global_names_different_offsets":sum(left[k]["index"]!=right[k]["index"] for k in both),
            "shared_global_names_same_offsets":sum(left[k]["index"]==right[k]["index"] for k in both)}


def resources(reflection):
    result = {}
    for kind in RESOURCE_KINDS:
        for r in reflection.get(kind,[]):
            name,typ = r["name"],r["type"]
            require(isinstance(name,str) and isinstance(typ,str) and
                    (kind,name) not in result,"skybox_offset_resource_schema")
            result[kind,name] = (typ,tuple(r.get("array",[])))
    return result


def resource_parity(actual, base):
    a,b = resources(actual),resources(base)
    require(a==b,"skybox_offset_final_named_resource_drift")
    return len(a)


def isolated_body(vs,fs):
    require(all(isinstance(s,str) and s and "#error GT_SKYBOX_STAGE_SELECTION" not in s
                for s in (vs,fs)),"skybox_offset_invalid_stage_source")
    return ("#if defined(SHADER_STAGE_VERTEX) && !defined(SHADER_STAGE_FRAGMENT)\n"
            + vs + "\n#elif defined(SHADER_STAGE_FRAGMENT) && !defined(SHADER_STAGE_VERTEX)\n"
            + fs + "\n#else\n#error GT_SKYBOX_STAGE_SELECTION\n#endif")


def compile_args(hlsl,spv,suffix,entry,macros):
    return ["glslangValidator","-V","-D","--target-env","vulkan1.1","--auto-map-bindings",
            "-S",suffix,"-e",entry,*["-DSHADER_STAGE_"+m+"=1" for m in macros],
            "-o",str(spv),str(hlsl)]


def compile_entry(hlsl,spv,suffix,entry,macro):
    spv.unlink(missing_ok=True)
    require(command(compile_args(hlsl,spv,suffix,entry,[macro])),"skybox_offset_compile_failed")
    require(command(["spirv-val","--target-env","vulkan1.1",str(spv)]),"skybox_offset_spirv_invalid")
    r = read_reflection(spv)
    require([e["name"] for e in r["entryPoints"]]==[entry],"skybox_offset_entry_identity")
    return r


def actual_merge_profile(private, layouts):
    hlsl = private/"combined.hlsl"
    require(hlsl.is_file(),"skybox_offset_original_merge_hlsl_missing")
    out = {}
    for i,(stage,suffix,macro,entry) in enumerate(STAGES):
        r = compile_entry(hlsl,private/(stage+"-merge-control.spv"),suffix,entry,macro)
        row = profile(r,layouts[i],stage)
        try:
            row["strict_original_offsets"] = w.verify_final_offsets(r,layouts[i],stage)
            row["strict_original_offsets_pass"] = True
        except ValueError as exc:
            row["strict_original_offsets_pass"] = False
            row["strict_failure"] = w.error_category(exc)
        out[stage] = row
    return out


def build_isolated(sh,private,layouts,named):
    parsed = sh["m_ParsedForm"]
    table, = [records(parts) for platform,parts in decoded_platforms(sh) if platform==4]
    pairs,orphans,passes,distinct = enumerate_all(parsed,table,variants=stage_variants,
        permutation=variant_key,linker=linked_program,topology=(1,1,0,2))
    require(len(parsed["m_PropInfo"]["m_Props"])==0,"skybox_offset_original_property_population_drift")
    layout,counts = shaderlab_layout(parsed,passes,expected_property_count=0,
        allow_next23b_texture_hdr_flags=True)
    # These are the independently verified original named-CB sources from the
    # failed merge experiment, not its unioned/hoisted declaration output.
    sources = []
    for i,(stage,_,_,entry) in enumerate(STAGES):
        directory = private/f"bound-stage-{i:03d}"
        source = (directory/"named-constant-buffers.hlsl").read_text(encoding="utf-8")
        ident = pairs[0][stage]["program_ref"]
        code = distinct[ident]["source_code"]
        files = [p/"source.dxbc" for p in private.glob("program-*")]
        matches = [p for p in files if hashlib.sha256(p.read_bytes()).hexdigest()==ident[1]]
        require(len(matches)==1 and matches[0].read_bytes()==code,"skybox_offset_stage_program_identity")
        if i==0:
            source,_ = restore_vertex_inputs(source,code)
        source = unity_varying_semantics(pin_varying_locations(source,1-i))
        source,n = re.subn(r"\bmain(?=\s*\()",entry,source)
        require(n==1,"skybox_offset_stage_entry_ambiguous")
        sources.append(unity_resource_bindings(source,stage))
    body = isolated_body(*sources)
    candidate = w.attach(layout,body)
    require(w.MARKER not in candidate,"skybox_offset_layout_marker_remaining")
    return candidate,body


def verify_isolated(candidate,body,private,layouts,named,report):
    # The wrapper uses a strict stage selector, not a new game keyword route.
    verify_entrypoints(candidate,private,routes=[[[]]])
    hlsl = private/"isolated.hlsl"
    hlsl.write_text(body,encoding="utf-8")
    reflected = []
    for i,(stage,suffix,macro,entry) in enumerate(STAGES):
        r = compile_entry(hlsl,private/(stage+"-isolated.spv"),suffix,entry,macro)
        row = profile(r,layouts[i],stage)
        report[stage] = row
        row["strict_original_offsets"] = w.verify_final_offsets(r,layouts[i],stage)
        row["strict_original_offsets_pass"] = True
        require(row["exact_owner_offset"]==row["expected_members"],"skybox_offset_incomplete_member_parity")
        base = read_reflection(private/f"bound-stage-{i:03d}"/"varying-bound.spv")
        row["named_resources_verified"] = resource_parity(r,base)
        require(row["named_resources_verified"]==len(named[i]["source_texture_sampler_bindings"]),
                "skybox_offset_resource_count_drift")
        reflected.append(r)
        # Wrong, absent and simultaneously active stage macros must not compile.
        opposite = STAGES[1-i][2]
        for macros in ([],[opposite],[macro,opposite]):
            bad = private/"forbidden.spv"
            bad.unlink(missing_ok=True)
            require(not command(compile_args(hlsl,bad,suffix,entry,macros)),
                    "skybox_offset_unexpected_stage_selector_acceptance")
        row["rejected_invalid_stage_macro_sets"] = 3
    counts = w.compare_interfaces(*reflected,
        read_reflection(private/"bound-stage-000/varying-bound.spv"),
        read_reflection(private/"bound-stage-001/varying-bound.spv"),
        read_reflection(private/"bound-stage-000/mesh-input-bound.spv"))
    require(sum(report[s]["strict_original_offsets"] for s,_,_,_ in STAGES)==45,
            "skybox_offset_original_45_members_drift")
    require(sum(report[s]["named_resources_verified"] for s,_,_,_ in STAGES)==10,
            "skybox_offset_original_10_resources_drift")
    return dict(counts,entrypoints=2,reflected_original_offsets=45,reflected_named_resources=10,
                invalid_stage_macro_sets_rejected=6,
                static_stage_macro_selection_verified=True,
                Unity_stage_macro_selection_verified=False)


def run(x):
    report = dict(status="INCONCLUSIVE",phase="exact_source_and_export_binding",
        original_object_sha256=w.OBJECT_SHA,same_export_binding_verified=False,
        private_wrapper_installed=False,original_assets_mutated=False,
        original_assets_published=False,Unity_import_verified=False,
        device_pixels_proven=False,production=False,XAPK=False,all_gates_open=True)
    try:
        require(x.project.resolve()==(x.destination.parent/"export/ExportedProject").resolve()
                and not any(p.is_symlink() for p in (x.project,*x.project.parents)),
                "skybox_offset_export_not_disposable")
        with open(os.devnull,"w") as q,contextlib.redirect_stdout(q),contextlib.redirect_stderr(q):
            sh,shader,protected,src = w.exact_source_and_export(x,x.destination/"Raft_Data",
                json.loads(x.skybox_plan.read_text()),json.loads(x.plan.read_text()))
            report["same_export_binding_verified"] = True
            with tempfile.TemporaryDirectory(prefix="offset-differential-",dir=x.destination.parent) as tmp:
                private = Path(tmp)
                replay = {}
                report["phase"] = "reproduce_exact_combined_wrapper_failure"
                try:
                    w.build(sh,private,replay)
                except ValueError as exc:
                    report["prior_merge_failure"] = w.error_category(exc)
                    report["prior_merge_phase"] = replay.get("phase")
                    require(report["prior_merge_failure"]=="named_constant_buffer_offset_mismatch"
                            and report["prior_merge_phase"]=="combined_wrapper_compile_and_interface",
                            "skybox_offset_prior_failure_not_reproduced")
                else:
                    raise Rejected("skybox_offset_prior_failure_not_reproduced")
                report["source_layout"] = replay["source_layout"]
                report["bound_stage_counts"] = replay["bound_stage_counts"]
                require(report["bound_stage_counts"]["named_constant_buffer_reflected_offsets_verified"]==45
                        and report["bound_stage_counts"]["original_vertex_fragment_varying_records_matched"]==7,
                        "skybox_offset_prior_source_binding_drift")
                named = json.loads((private/"original-private-parameter-records.json").read_text())["stage_records"]
                require(len(named)==2 and [r["stage"] for r in named]==[1,0],"skybox_offset_stage_record_order")
                layouts = [r["source_constant_buffer_layouts"] for r in named]
                report["phase"] = "actual_merge_offset_differential"
                report["source_global_name_overlap"] = shared_global_members(layouts)
                report["combined_original_layout_profile"] = actual_merge_profile(private,layouts)
                report["phase"] = "stage_isolated_wrapper_compile_and_reflection"
                candidate,body = build_isolated(sh,private,layouts,named)
                report["isolated_original_layout_profile"] = {}
                report["isolated_final_validation"] = verify_isolated(
                    candidate,body,private,layouts,named,report["isolated_original_layout_profile"])
                structure = prior.classify_program(src,candidate)
                require(structure["status"]=="NON_DUMMY_STRUCTURE_ONLY" and
                        structure["pass_count"]==1 and structure["all_passes_programmed"],
                        "skybox_offset_candidate_structure")
                report["phase"] = "verified_disposable_install"
                report["private_install"] = w.install(shader,protected,x.project,candidate)
                report["private_wrapper_installed"] = True
        report.update(status=STATUS,phase="complete")
    except Exception as exc:
        report["reason"] = w.error_category(exc)
    x.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_OFFSET_DIFFERENTIAL "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("destination","skybox-plan","plan","project","trace","w1","b02","report"):
        p.add_argument("--"+k,type=Path,required=True)
    return run(p.parse_args())


if __name__=="__main__":
    raise SystemExit(main())
