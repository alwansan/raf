"""Private exact Shader48 single-pass candidate. No raw programs in receipts."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from tools.gt_skybox_shader_program import audit as prior
from tools.gt_ambient_same_export import audit as ambient
from tools.gt_light_same_export.audit import require, Rejected
from scripts.verify_export_lineage import identity
from scripts.w1_audit_export_material_shaders import ENGINE
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate, command
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.gt_original_921_all_variants import enumerate_all, stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes, shaderlab_layout
from scripts.gt_original_921_shaderlab import (
    combine_stages, paired_uniform_layouts, unity_resource_bindings,
    unity_varying_semantics, verify_entrypoints,
)
from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers, verify_offsets
from scripts.gt_original_921_semantics import restore_vertex_inputs, pin_varying_locations
from scripts.t3_spirv_interface_name_drift import read_reflection

OBJECT_SHA = "ef5c31aa0751308a026445ad4503ace5b1114ead41edb5408f84b11751e667d9"
STATUS = "PASS_SOURCE_BOUND_WRAPPER_PRIVATE_SAME_EXPORT"
MARKER = "// Original stage programs attach here"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def single_route(routes):
    require(len(routes) == 1, "skybox_route_count")
    row = routes[0]
    require(row["subshader"] == 0 and row["pass"] == 0 and
            len(row["routes"]) == 1 and row["routes"][0]["enabled"] == [] and
            row["keyword_universe"] == [] and row["unmatched_vertex_keywords"] == [],
            "skybox_not_single_empty_permutation")
    return row


def attach(layout, source):
    require(layout.count(MARKER) == 1, "skybox_layout_pass_count")
    program = "\n".join(("HLSLPROGRAM", "#pragma target 5.0",
                         "#pragma vertex gt_vs_main", "#pragma fragment gt_fs_main",
                         "#pragma use_dxc vulkan", source, "ENDHLSL"))
    return layout.replace(MARKER, program, 1)


def interface(reflection, side):
    entries = reflection.get(side, [])
    require(isinstance(entries, list), "skybox_interface_schema")
    result = {}
    for row in entries:
        loc = row.get("location")
        require(type(loc) is int and loc >= 0 and loc not in result and
                isinstance(row.get("type"), str), "skybox_interface_duplicate_or_invalid")
        result[loc] = row["type"]
    return result


def compare_interfaces(vs, fs, base_vs, base_fs, mesh):
    checks = ((vs, "inputs", mesh), (vs, "outputs", base_vs),
              (fs, "inputs", base_fs), (fs, "outputs", base_fs))
    for actual, side, expected in checks:
        require(interface(actual, side) == interface(expected, side),
                "skybox_final_interface_differs_from_source_bound_stage")
    outputs, inputs = interface(vs, "outputs"), interface(fs, "inputs")
    require(all(outputs.get(k) == v for k, v in inputs.items()),
            "skybox_final_varying_pair_mismatch")
    return {"mesh_inputs": len(interface(vs, "inputs")), "varyings": len(inputs),
            "fragment_outputs": len(interface(fs, "outputs"))}


def verify_final_offsets(reflected, layouts, stage):
    """Use actual reflected slots for the name-bound wrapper, not guessed slots."""
    ubos = reflected.get("ubos", [])
    buffers = []
    for item in layouts:
        name = item["name"]
        if name == "$Globals":
            name = f"gt_{stage}_raft921_cb{item['source_slot']}_Globals"
        matches = [r for r in ubos if r.get("name") == name]
        require(len(matches) == 1 and matches[0].get("set") == 0 and
                type(matches[0].get("binding")) is int,
                "skybox_final_source_buffer_not_uniquely_reflected")
        buffers.append(dict(item, name=name, translated_binding=matches[0]["binding"]))
    return verify_offsets(reflected, buffers)


def final_pair(shader, private, layouts):
    # First use the unchanged historical two-entry validator on the exact wrapper.
    verify_entrypoints(shader, private, routes=[[[]]])
    blocks = re.findall(r"(?ms)^HLSLPROGRAM\n(.*?)^ENDHLSL$", shader)
    require(len(blocks) == 1, "skybox_final_program_count")
    hlsl = private / "combined.hlsl"
    hlsl.write_text(re.sub(r"(?m)^#pragma [^\n]*\n", "", blocks[0]), encoding="utf-8")
    reflected = []
    offsets = 0
    for i, (stage, suffix, macro, entry) in enumerate(
            (("vs", "vert", "VERTEX", "gt_vs_main"), ("fs", "frag", "FRAGMENT", "gt_fs_main"))):
        binary = private / (stage + "-combined.spv")
        # Auto-map is a validation-only descriptor allocation for name-bound
        # declarations. This is not Unity descriptor assignment evidence.
        require(command(["glslangValidator", "-V", "-D", "--target-env", "vulkan1.1",
                         "--auto-map-bindings", "-S", suffix, "-e", entry,
                         "-DSHADER_STAGE_" + macro + "=1", "-o", str(binary), str(hlsl)]),
                "skybox_final_named_entry_compile_failed")
        require(command(["spirv-val", "--target-env", "vulkan1.1", str(binary)]),
                "skybox_final_named_entry_invalid")
        reflection = read_reflection(binary)
        require([r["name"] for r in reflection["entryPoints"]] == [entry],
                "skybox_final_entry_identity")
        offsets += verify_final_offsets(reflection, layouts[i], stage)
        reflected.append(reflection)
    counts = compare_interfaces(*reflected,
        read_reflection(private / "bound-stage-000/varying-bound.spv"),
        read_reflection(private / "bound-stage-001/varying-bound.spv"),
        read_reflection(private / "bound-stage-000/mesh-input-bound.spv"))
    return dict(counts, entrypoints=2, reflected_original_offsets=offsets,
                name_bound_descriptor_validation_only=True)


def exact_source_and_export(x, root, sky, plan):
    mat, body, target, sh, obj_sha = prior.source_shader(root, sky, plan)
    require(target[0] == "globalgamemanagers.assets" and obj_sha == OBJECT_SHA,
            "skybox_original_object_digest_mismatch")
    src = prior.source_programs(sh)
    require(src["source_program_schema_complete"] and
            tuple(src[k] for k in ("source_subshaders", "source_passes", "vertex_slots",
                "fragment_slots", "other_stage_slots", "source_d3d11_table_count",
                "linked_d3d11_stage_slots", "distinct_linked_dxbc",
                "unlinked_d3d11_stage_slots")) == (1,1,1,1,0,1,2,2,0),
            "skybox_original_topology_drift")
    st,w1,b02 = [ambient.read_trace(p) for p in (x.trace,x.w1,x.b02)]
    ambient.same_instance(st,w1,b02)
    _,sid,_ = ambient.read_source(root)
    sg,sf,_ = ambient.settings_mapping(st,w1,b02,sid)
    scene_path = ambient.file_for_guid(x.project,sg,{".unity"})
    scene = ambient.doc_body(scene_path,104,sf,"RenderSettings")
    mp = ambient.material_mapping(w1,*mat)
    require(ambient.export_pointer(scene.get("m_SkyboxMaterial")) == mp,
            "skybox_scene_material_regression")
    material_path = ambient.file_for_guid(x.project,mp[0],{".mat",".asset"})
    material = ambient.doc_body(material_path,21,mp[1],"Material")
    mr = prior.exact_row(w1,mat,21)
    normalized = (Path(target[0]).name,target[1])
    sr = prior.exact_row(w1,normalized,48)
    expected = prior.shader_trace_pointer(sr["export"])
    require(expected[1] not in ENGINE and identity(mr["shader_source"]) == normalized and
            prior.shader_trace_pointer(mr["shader_export"]) == expected and
            prior.shader_pointer(material.get("m_Shader")) == expected,
            "skybox_material_shader_edge_regression")
    peers = [q for q in w1["objects"] if q.get("class_id") == 48 and q.get("export") == sr["export"]]
    require(len(peers) == 1, "skybox_collapsed_shader_trace")
    shader = ambient.file_for_guid(x.project,expected[1],{".shader"})
    meta = Path(str(shader)+".meta")
    require(shader.stat().st_size <= 8*1024*1024 and
            re.search(r"(?m)^ShaderImporter:\s*$",meta.read_text(encoding="utf-8-sig")),
            "skybox_actual_shader_meta")
    require(prior.classify_program(src,shader.read_text(encoding="utf-8-sig"))["status"]
            == "ORIGINAL_PROGRAMS_PRESENT_EXPORTED_DUMMY", "skybox_not_proven_actual_dummy")
    props = prior.properties(body,material)
    for group,n in ((props["colors"],6),(props["scalars"]["m_Floats"],20),
                    (props["scalars"]["m_Ints"],0),(props["texenvs"]["uv"],0),
                    (props["texenvs"]["nullness"],0)):
        require(group == dict(source=n,export=n,equal=n,changed=0,missing=0,extra=0),
                "skybox_material_property_regression")
    for k in prior.KEYWORDS:
        require(props[k] == dict(source=0,export=0,equal=True), "skybox_material_keyword_regression")
    fanout = prior.scoped_fanout(w1,normalized,expected,x.project)
    require(fanout["same_instance_trace_material_rows"] == 1 and
            fanout["unique_actual_material_documents_matching_shader"] == 1,
            "skybox_scoped_material_fanout_regression")
    protected = [meta,scene_path,Path(str(scene_path)+".meta"),
                 material_path,Path(str(material_path)+".meta")]
    return sh,shader,protected,src


def build(sh, private, report):
    parsed = sh["m_ParsedForm"]
    report["phase"] = "original_route_and_layout"
    tables = [records(parts) for platform,parts in decoded_platforms(sh) if platform == 4]
    require(len(tables) == 1, "skybox_d3d11_table")
    pairs,orphans,passes,distinct = enumerate_all(parsed,tables[0],variants=stage_variants,
        permutation=variant_key,linker=linked_program,topology=(1,1,0,2))
    routes,_ = keyword_routes(parsed,pairs,orphans,passes)
    single_route(routes)
    layout,counts = shaderlab_layout(parsed,passes,
        expected_property_count=len(parsed["m_PropInfo"]["m_Props"]),
        allow_next23b_texture_hdr_flags=True)
    report["source_layout"] = {"original_properties": counts["original_authored_property_count"],
        "render_states": counts["original_render_states_serialized"], "empty_keyword_routes": 1}
    report["phase"] = "original_program_translation"
    folders = {}
    for i,(ident,item) in enumerate(distinct.items()):
        folder = private / f"program-{i:03d}"
        folder.mkdir(mode=0o700)
        folders[ident] = folder.name
        translated = translate(item["source_code"],item["stage"],folder)
        require(all(translated.get(k) is True for k in ("vulkan11_valid","hlsl_recovered",
                "roundtrip_vulkan11_valid")), "skybox_original_translation_failed")
    report["translated_original_programs"] = len(folders)
    report["phase"] = "original_parameter_mesh_and_varying_binding"
    report["bound_stage_counts"] = stage_parameter_records(pairs,orphans,passes,tables[0],private,folders)
    named = json.loads((private/"original-private-parameter-records.json").read_text())["stage_records"]
    require(len(named) == 2 and [r["stage"] for r in named] == [1,0],
            "skybox_bound_stage_order")
    layouts = paired_uniform_layouts(named)
    sources = []
    for i,stage in enumerate(("vs","fs")):
        source = rebind_constant_buffers(
            (private/f"bound-stage-{i:03d}"/"resource-bound.hlsl").read_text(),layouts[i])
        if i == 0:
            source,_ = restore_vertex_inputs(source,
                (private/folders[pairs[0]["vs"]["program_ref"]]/"source.dxbc").read_bytes())
        source = unity_varying_semantics(pin_varying_locations(source,1-i))
        source,n = re.subn(r"\bmain(?=\s*\()", "gt_"+stage+"_main", source)
        require(n == 1, "skybox_entrypoint_ambiguous")
        sources.append(unity_resource_bindings(source,stage))
    report["phase"] = "combined_wrapper_compile_and_interface"
    candidate = attach(layout,combine_stages(*sources))
    report["final_wrapper_validation"] = final_pair(candidate,private,layouts)
    return candidate


def safe_path(path, project):
    require(path.is_file() and not any(p.is_symlink() for p in (path,*path.parents))
            and path.resolve().is_relative_to(project.resolve()), "skybox_unsafe_private_export_path")


def install(shader, protected, project, candidate):
    """Change only one authenticated file in the disposable export, rollback on failure."""
    for path in [shader,*protected]:
        safe_path(path,project)
    require(len(set([shader,*protected])) == 1+len(protected), "skybox_duplicate_export_paths")
    before = {p:digest(p) for p in protected}
    old = shader.read_bytes()
    require(b"//DummyShaderTextExporter" in old, "skybox_install_dummy_precondition")
    require("//DummyShaderTextExporter" not in candidate and
            "// No subprograms found" not in candidate, "skybox_candidate_dummy_marker")
    data = candidate.encode("utf-8")
    with tempfile.NamedTemporaryFile(dir=shader.parent, prefix=".gt-skybox-", delete=False) as f:
        tmp = Path(f.name)
        f.write(data)
    try:
        require(shader.read_bytes() == old and all(digest(p)==h for p,h in before.items()),
                "skybox_export_changed_before_install")
        os.chmod(tmp,shader.stat().st_mode & 0o777)
        os.replace(tmp,shader)
        if shader.read_bytes() != data or any(digest(p)!=h for p,h in before.items()):
            shader.write_bytes(old)
            raise Rejected("skybox_post_install_integrity")
    finally:
        tmp.unlink(missing_ok=True)
    return {"before_sha256": hashlib.sha256(old).hexdigest(),
        "after_sha256": digest(shader), "protected_files_unchanged": len(before)}


def error_category(exc):
    msg = str(exc)
    if isinstance(exc,(ValueError,Rejected)) and re.fullmatch(
            r"(?:skybox|original_921|named_constant_buffer|original_shader|original_property|original_|invalid_original|missing_original)_[a-z0-9_]{1,100}",msg):
        return msg
    if isinstance(exc,KeyError) and len(exc.args)==1 and exc.args[0] in (
            "m_ParameterBlobIndices","m_CommonParameters","m_KeywordNames","m_KeywordFlags",
            "m_ParsedForm","m_PropInfo","m_Props","m_State","m_NameIndices"):
        return "unsupported_serialized_schema_"+exc.args[0]
    return type(exc).__name__


def run(x):
    report = dict(status="INCONCLUSIVE", phase="exact_source_and_export_binding",
        original_object_sha256=OBJECT_SHA, same_export_binding_verified=False,
        private_wrapper_installed=False, original_assets_mutated=False,
        original_assets_published=False, Unity_import_verified=False,
        device_pixels_proven=False, production=False, XAPK=False, all_gates_open=True)
    try:
        require(x.project.resolve() == (x.destination.parent/"export/ExportedProject").resolve()
                and not any(p.is_symlink() for p in (x.project,*x.project.parents)),
                "skybox_export_not_disposable")
        with open(os.devnull,"w") as quiet,contextlib.redirect_stdout(quiet),contextlib.redirect_stderr(quiet):
            sh,shader,protected,src = exact_source_and_export(
                x,x.destination/"Raft_Data",json.loads(x.skybox_plan.read_text()),
                json.loads(x.plan.read_text()))
            report["same_export_binding_verified"] = True
            with tempfile.TemporaryDirectory(prefix="wrapper-",dir=x.destination.parent) as temp:
                candidate = build(sh,Path(temp),report)
                program = prior.classify_program(src,candidate)
                require(program["status"] == "NON_DUMMY_STRUCTURE_ONLY" and
                        program["pass_count"] == 1 and program["all_passes_programmed"],
                        "skybox_candidate_structure")
                report["phase"] = "verified_disposable_install"
                report["private_install"] = install(shader,protected,x.project,candidate)
                report["private_wrapper_installed"] = True
        report.update(status=STATUS,phase="complete")
    except Exception as exc:
        report["reason"] = error_category(exc)
    x.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_SKYBOX_SOURCE_BOUND_WRAPPER "+json.dumps(report,sort_keys=True))
    return 0 if report["status"] == STATUS else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for k in ("destination","skybox-plan","plan","project","trace","w1","b02","report"):
        parser.add_argument("--"+k,type=Path,required=True)
    return run(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
