"""Authenticate M02's original Forward stages and inventory their draw inputs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from gfxlab.tools.multi_shader_android_stage_pack094 import controlled_glsl_names
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import original_sample_pairs, stage_compare
from gfxlab.tools.multi_shader_material_cb_payload095 import partial_payload_private, saved_values_private
from gfxlab.tools.multi_shader_one_pass_spirv import code_from_ref, exact_pairs, translate_pair
from gfxlab.tools.multi_shader_original_cb_byte_addresses import (
    private_authenticated_ubo_layouts, spv_used_literal_byte_addresses,
)
from gfxlab.tools.multi_shader_parameter_blob093 import (
    linked_parameters_private, load_original_shader_private, merged_parameters_private,
)
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_material_texture_semantics import named_entries
from gfxlab.tools.multi_model_transport import all_model_entries
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.original_model_probe import ZIP2_SHA, stage_originals
from gfxlab.tools.shears_provenance_probe import resolve_pptr


def source_material(stage):
    selection, _ = selected_five(stage)
    entries, types, _ = all_model_entries(stage)
    model = entries[2]
    selected = selection["selected"][1]
    if model["id"] != "M02" or (selected["owner"], selected["mesh_pid"]) != (model["owner"], model["mesh_pid"]):
        raise ValueError("M02 selection identity changed")
    source, = selected["materials"]
    material, = model["materials"]
    obj = types[source["owner"]][source["material_pid"]]
    data = obj.read_typetree(check_read=False)
    external = [x.path for x in obj.assets_file.externals]
    expected = {name: (r["owner"],r["pid"]) for name,r in material["textures"].items()}
    return data, source["owner"], external, expected


def keywords(program, row):
    selected = program[row["m_BlobIndex"]]
    return set(selected.m_Keywords or ()) | set(selected.m_LocalKeywords or ())


def declared_material_data(material, merged, sizes, properties):
    payloads, stats = partial_payload_private(merged, sizes, saved_values_private(material), properties)
    env = dict(named_entries(material["m_SavedProperties"]["m_TexEnvs"]))
    slots = {b["name"]:b["index"] for b in merged["bindings"] if b["type"] == 1}
    st_writes = 0
    for group in merged["groups"]:
        slot = slots[group["name"]]
        if slot not in payloads:
            continue
        payload, mask = payloads[slot]
        for member in group["parameters"].values():
            name = member["name"]
            if not name.endswith("_ST") or name[:-3] not in env:
                continue
            tex = env[name[:-3]]
            values = [tex[field][axis] for field in ("m_Scale","m_Offset") for axis in ("x","y")]
            offset = member["index"]
            if (member["columns"] != 4 or member["matrix"] or member["array"] not in (0,1)
                    or not 0 <= offset <= len(mask)-16 or any(mask[offset:offset+16])):
                raise ValueError("Invalid TexEnv ST register")
            payload[offset:offset+16] = struct.pack("<4f",*values)
            mask[offset:offset+16] = b"\1"*16
            st_writes += 1
    return payloads, {"saved_float_writes":stats["saved_float_member_writes"],
                      "saved_color_writes":stats["saved_color_member_writes"],
                      "texenv_st_writes":st_writes,
                      "known_material_bytes":sum(sum(mask) for _,mask in payloads.values()),
                      "total_declared_cb_bytes":sum(n*16 for n in sizes.values())}


def texture_contract(material, owner, external, expected, merged, shdr, slots):
    env = dict(named_entries(material["m_SavedProperties"]["m_TexEnvs"]))
    bindings = {b["index"]:b for b in merged["bindings"] if b["type"] == 0}
    pairs, sample_stats = original_sample_pairs(shdr, slots["resource"], slots["sampler"])
    if sample_stats["source_original_unresolved_dynamic_t_s"]:
        raise ValueError("Unresolved original texture sampling operands")
    categories = Counter()
    roles = {"_MainTex":"basecolor","_BumpMap":"normal","_MetallicGlossMap":"metallic"}
    for t,s in set(pairs):
        binding = bindings[t]
        name = binding["name"]
        if binding["extra"] >= 0 and binding["extra"] != s:
            raise ValueError("Texture parameter metadata conflicts with exact DXBC sample")
        if name in roles:
            if resolve_pptr(env[name]["m_Texture"],owner,external)[1] != expected[roles[name]]:
                raise ValueError("Source texture identity changed")
            categories["verified_source_texture_pairs"] += 1
        elif name in env:
            if resolve_pptr(env[name]["m_Texture"],owner,external)[0] != "null":
                raise ValueError("Unexpected bound material texture")
            categories["material_null_texture_pairs_requiring_runtime_default"] += 1
        else:
            categories["engine_texture_pairs_requiring_runtime_binding"] += 1
        if binding["extra"] < 0:
            categories["sampler_resolved_from_dxbc_only"] += 1
    return dict(categories, distinct_sample_pairs=len(set(pairs)), sample_operations=len(pairs))


def run_tool(args):
    result = subprocess.run(args,capture_output=True,timeout=90,check=False)
    if result.returncode:
        raise ValueError(f"Private {args[0]} stage failed")
    return result.stdout


def audit(stage, translate, private_consumer=None, *, model="M02", material_source=None, shader_source=None, pass_name="FORWARD",
          engine_keywords=("DIRECTIONAL",), filter_absent_keys=False):
    material, owner, external, expected = material_source if material_source is not None else source_material(stage)
    tree, raw, programs = shader_source if shader_source is not None else load_original_shader_private(stage)
    parsed = tree["m_ParsedForm"]
    pp, = [row for row in parsed["m_SubShaders"][0]["m_Passes"] if row["m_State"]["m_Name"] == pass_name]
    if material.get("m_InvalidKeywords"):
        raise ValueError("Expected valid material keywords")
    source_keys = set(material["m_ValidKeywords"])
    pairs = list(exact_pairs(pp))
    selected_keys = source_keys
    if filter_absent_keys:
        observed_keys = set().union(*(keywords(programs, vertex) for vertex, _ in pairs))
        selected_keys = source_keys & observed_keys
    controlled = selected_keys | set(engine_keywords)
    match = [(v,f) for v,f in pairs
             if keywords(programs,v) == keywords(programs,f) == controlled]
    if len(match) != 1:
        raise ValueError("Original controlled pair not unique")
    linked, _ = linked_parameters_private(tree,raw)
    properties = {x["m_Name"]:x["m_Type"] for x in parsed["m_PropInfo"]["m_Props"]}
    stages = {}
    private = {}
    for label, meta, src_stage, kind in zip(("vertex","fragment"),match[0],
                                               ("progVertex","progFragment"),("Vertex","Pixel"),strict=True):
        params, = [p for pass_tree,st,row,_,p in linked if pass_tree is pp and st == src_stage and row == meta]
        merged = merged_parameters_private(pp,src_stage,params)
        dxbc = code_from_ref(meta,programs,kind)
        shdr = source_shader_chunk(dxbc)
        slots, sizes = private_source_slots(shdr)
        payloads, coverage = declared_material_data(material,merged,sizes,properties)
        stages[label] = {
            "dxbc_sha256":hashlib.sha256(dxbc).hexdigest(), "declared_cb_slots":len(sizes), **coverage,
            "texture_contract":texture_contract(material,owner,external,expected,merged,shdr,slots),
        }
        private[label] = (dxbc,sizes,payloads,merged)
    result = {"experiment":"GFX118","source_sha":ZIP2_SHA,"model":model,
              "material_keyword_count":len(source_keys),"controlled_global_keyword":"DIRECTIONAL",
              "exact_source_pair_count":len(match),"stages":stages,"gles_offline_link_passed":False,
              "gpu_draw_completed":False,"original_shader_restored":False,"phase_closed":False}
    if filter_absent_keys:
        result.update(pass_name=pass_name, controlled_global_keyword=engine_keywords[0],
                      pass_absent_material_keywords_filtered=len(source_keys-selected_keys),
                      unity_variant_selection_verified=False)
    if not translate:
        if private_consumer is not None:
            private_consumer(None, private)
        return result
    with tempfile.TemporaryDirectory(prefix="gfx118-private-") as temp:
        folder = Path(temp)
        converted = translate_pair(private["vertex"][0],private["fragment"][0],folder)
        for label, extension in (("vertex","vert"),("fragment","frag")):
            if not converted[label]["vulkan11_spirv_validation_success"]:
                raise ValueError("Selected source stage did not validate as SPIR-V")
            spv = folder / (label+".spv")
            reflection = json.loads(run_tool(["spirv-cross",str(spv),"--reflect"]))
            dis = run_tool(["spirv-dis","--raw-id",str(spv)])
            dxbc, sizes, payloads, _ = private[label]
            authenticated, _ = private_authenticated_ubo_layouts(dis,sizes,reflection)
            _, ranges, loads = spv_used_literal_byte_addresses(dis,authenticated)
            full = partial = unavailable = 0
            for slot, vectors in ranges.items():
                mask = payloads.get(slot,(None,bytearray(sizes[slot]*16)))[1]
                for v in vectors:
                    known = sum(mask[16*v:16*v+16])
                    full += known == 16
                    partial += 0 < known < 16
                    unavailable += known == 0
            source = run_tool(["spirv-cross",str(spv),"--version","310","--es"]).decode()
            (folder/("probe."+extension)).write_text(controlled_glsl_names(source,reflection,label))
            stages[label].update(spirv_validated=True,gles_source_emitted=True,
                translated_authenticated_cb_slots=len(authenticated),
                translated_literal_read_vec4_ranges_known_material_full=full,
                translated_literal_read_vec4_ranges_known_material_partial=partial,
                translated_literal_read_vec4_ranges_without_material_bytes=unavailable,
                translated_dynamic_or_unsupported_cb_chains=loads["SPV_access_chains_dynamic_or_unsupported"],
                translated_texture_sample_contract=stage_compare(dxbc,spv,reflection,dis))
        run_tool(["glslangValidator","-l",str(folder/"probe.vert"),str(folder/"probe.frag")])
        result["gles_offline_link_passed"] = True
        if private_consumer is not None:
            private_consumer(folder, private)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("zip2","stage","safe"):
        parser.add_argument("--"+name,type=Path,required=True)
    parser.add_argument("--translate",action="store_true")
    args = parser.parse_args()
    if run_tool(["git","-C",str(args.zip2),"rev-parse","HEAD"]).decode().strip() != ZIP2_SHA:
        raise ValueError("Source checkout SHA mismatch")
    report = audit(stage_originals(args.zip2,args.stage),args.translate)
    args.safe.write_text(json.dumps(report,indent=2)+"\n")
