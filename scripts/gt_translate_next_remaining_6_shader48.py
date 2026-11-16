"""Recover source-authentic next unresolved six-Material 1-pass Shader48 D3D11 stages.

Select exactly one remaining shader from 82 SHA-pinned original ZIP2 owners
using the post-fourteen unique six-Material name digest and source Shader48 identity.
Validate original 1 Pass / 2 VS-FS keyword routes / 0 VS orphans / 3 distinct
DXBC programs. Translate original DXBC privately to SPIR-V and recovered HLSL,
then validate Vulkan 1.1 stage roundtrips. No source code, names, hashes,
identifiers, or compiled shader bytes enter public reports. Does NOT yet
install shader in Unity or prove game pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_original_921_all_variants import enumerate_all, stage_parameter_records
from scripts.gt_original_921_keyword_routes import keyword_routes, compile_routed_stages, shaderlab_layout
from scripts.gt_original_921_shaderlab import compose, verify_entrypoints
from scripts.gt_stage_serialized_owners import read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.t3_original_top_shader_dxbc_feasibility import summarize
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate

STATUS="GT_SHA_ORIGINAL_REMAINING_6_MATERIAL_SHADER48_D3D11_PRIVATE_STAGES_TRANSLATED"
EXPECTED_TOPOLOGY=(1,2,0,3)


def select_exact_6_material_name(source_hashes, material_name_counts):
    # Source-authenticated post14 has exactly one original Shader48 digest
    # referenced by six Custom Material documents; topology 1/2/0/3 is
    # checked independently before mapping its PathID to exported GUID.
    if type(material_name_counts) is not dict:
        raise ValueError("missing_original_6_material_digest_population")
    matches = [digest for digest, amount in material_name_counts.items()
               if amount == 6]
    if len(matches) != 1:
        raise ValueError("missing_or_ambiguous_6_material_original_shader_name_digest")
    digest = matches[0]
    if type(digest) is not str or len(digest) != 64:
        raise ValueError("malformed_original_6_material_source_name_digest")
    selected = [key for key, sha in source_hashes.items() if sha == digest]
    if len(selected) != 1:
        raise ValueError("not_one_authentic_original_6_material_Shader48_object")
    return selected


def choose_original_6_by_topology(original,manifest,source_hashes,usage):
    import UnityPy
    candidates=select_exact_6_material_name(source_hashes, usage)
    verified=[]
    pins=read_expected(manifest)
    for owner,pid in candidates:
        _,size,digest=pins[owner]
        path=original/owner
        if path.is_symlink():
            raise ValueError("unsafe_source_original_6_material_Shader48_provider")
        verify(path,size,digest)
        env=UnityPy.load(str(path))
        objects=[obj for obj in env.objects if obj.path_id==pid and str(obj.type.name)=="Shader"]
        if len(objects)!=1:
            raise ValueError("original_6_material_Shader48_candidate_object_missing")
        tree=objects[0].read_typetree()
        tables=[records(segment) for platform,segment in decoded_platforms(tree) if platform==4]
        if len(tables)!=1:
            raise ValueError("unverifiable_original_6_material_D3D11_table")
        profile=summarize(tree.get("m_ParsedForm"),tables[0])
        topology=(profile["original_source_Shader48_pass_count"],
                  profile["matched_vertex_fragment_permutation_pairs"],
                  profile["unmatched_vertex_permutations"],
                  profile["distinct_original_linked_D3D11_programs"])
        if topology==EXPECTED_TOPOLOGY and profile["unmatched_fragment_permutations"]==0:
            verified.append((owner,pid))
    if len(verified)!=1:
        raise ValueError("ambiguous_original_6_material_Shader48_topology_owner")
    return verified[0]


def original_range_contract_safe_census(parsed):
    """Publish counts only, never original range names, limits or default values."""
    props=parsed.get("m_PropInfo",{}).get("m_Props",[])
    if type(props) is not list or len(props)>128:
        raise ValueError("unverified_original_Shader48_range_property_population")
    out={
        "source_original_ShaderLab_Range_property_count":0,
        "source_original_Range_nonzero_unused_fourth_lane_count":0,
        "source_original_Range_inverted_lower_upper_count":0,
        "source_original_Range_default_outside_lower_upper_count":0,
    }
    for prop in props:
        if type(prop) is not dict or prop.get("m_Type")!=3:
            continue
        values=[prop.get("m_DefValue[%d]"%i) for i in range(4)]
        import math
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
            raise ValueError("unverifiable_original_Shader48_range_property_numbers")
        default,lower,upper,tail=values
        out["source_original_ShaderLab_Range_property_count"]+=1
        out["source_original_Range_nonzero_unused_fourth_lane_count"]+=bool(tail!=0)
        out["source_original_Range_inverted_lower_upper_count"]+=bool(lower>upper)
        out["source_original_Range_default_outside_lower_upper_count"]+=bool(
            default<min(lower,upper) or default>max(lower,upper))
    return out


def safe_original_six_property_flag_attribute_census(parsed):
    """Safe NUMERIC schema evidence; never publish names, attributes, values.

    Source owner/PathID/keyword identifiers, attribute contents and shader text
    remain private. Public evidence is only type, bit-flag and attribute-class
    populations so an explicit ShaderLab attribute bridge can be authorized.
    """
    from collections import Counter
    props=parsed.get("m_PropInfo",{}).get("m_Props",[])
    if type(props) is not list or len(props)>128:
        raise ValueError("unverified_original_6_property_schema")
    flags=Counter()
    attr_classes=Counter()
    types=Counter()
    for prop in props:
        if type(prop) is not dict or type(prop.get("m_Flags")) is not int:
            raise ValueError("unverified_original_6_property_flags_schema")
        flag=prop["m_Flags"]
        if flag<0 or flag>65535:
            raise ValueError("unverified_original_6_property_flags_range")
        flags[str(flag)]+=1
        types[str(prop.get("m_Type"))]+=1
        attributes=prop.get("m_Attributes")
        if type(attributes) is not list:
            raise ValueError("unverified_original_6_property_attributes_schema")
        if not attributes:
            attr_classes["none"]+=1
        for attr in attributes:
            if type(attr) is not str or len(attr)>1024:
                raise ValueError("unverified_original_6_property_attribute_string")
            if attr=="Toggle":
                kind="toggle"
            elif attr.startswith("Toggle(") and attr.endswith(")"):
                kind="toggle_keyword"
            elif attr.startswith("Enum(") and attr.endswith(")"):
                kind="enum"
            elif attr.startswith("KeywordEnum(") and attr.endswith(")"):
                kind="keyword_enum"
            elif attr.startswith("Header(") and attr.endswith(")"):
                kind="header"
            elif attr.startswith("Space(") and attr.endswith(")"):
                kind="space"
            elif attr=="NoScaleOffset":
                kind="no_scale_offset"
            elif attr=="Normal":
                kind="normal"
            elif attr=="HDR":
                kind="hdr"
            elif attr=="Gamma":
                kind="gamma"
            elif attr=="PerRendererData":
                kind="per_renderer_data"
            else:
                kind="other_unclassified"
            attr_classes[kind]+=1
    return {
        "schema_version":1,
        "count":len(props),
        "original_shader_property_type_histogram":dict(sorted(types.items())),
        "original_shader_property_flag_histogram":dict(sorted(flags.items())),
        "original_shader_property_attribute_class_histogram":dict(sorted(attr_classes.items())),
        "names_values_identifiers_and_attribute_strings_published":False,
    }


def source_only_static_parameter_binding_failure_category(exc):
    """Map a PRIVATE source error to an exact PUBLIC constant authored in code.

    Never print the exception itself unless it exactly matches a local static
    ValueError literal from an allowlisted parameter decoder/rebinder module.
    Raw source names, register symbols and private shader bytes never leave CI.
    """
    import ast
    from importlib import import_module
    modules=(
        "scripts.gt_original_921_all_variants",
        "scripts.a12_shader_parameter_decode",
        "scripts.b25_foam_cb_namebridge",
        "scripts.gt_original_921_cb_hlsl",
        "scripts.gt_original_921_cb_layout",
        "scripts.gt_original_921_resource_rebind",
        "scripts.gt_original_921_semantics",
        "scripts.w1_rebind_depth_resources",
    )
    allowed=set()
    for name in modules:
        module=import_module(name)
        source_file=Path(module.__file__).resolve()
        if not source_file.is_relative_to(Path(__file__).resolve().parent):
            raise ValueError("unsafe_source_original_parameter_failure_classifier")
        tree=ast.parse(source_file.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if (isinstance(node,ast.Raise) and
                    isinstance(node.exc,ast.Call) and
                    isinstance(node.exc.func,ast.Name) and
                    node.exc.func.id=="ValueError" and node.exc.args and
                    isinstance(node.exc.args[0],ast.Constant) and
                    type(node.exc.args[0].value) is str):
                allowed.add(node.exc.args[0].value)
    candidate=str(exc)
    return candidate if candidate in allowed else "UNCLASSIFIED_PRIVATE_PARAMETER_BINDING_FAILURE"


def original_six_validator_private_failure_safe_topics(private):
    """No raw glslang/SPIR-V text, original names, IDs or bytes are published."""
    from collections import Counter
    import re
    counts=Counter()
    diagnostics=list(private.glob("bound-stage-*/original-validator-raw-private.log"))
    if len(diagnostics)>16:
        raise ValueError("unsafe_original_six_validator_private_file_population")
    topics={
        "offset_or_stride":("offset","stride","alignment","aligned"),
        "descriptor_or_binding":("descriptor","binding","set 0"),
        "storage_or_uniform":("storage class","uniform","bufferblock","block"),
        "type_or_struct":("type mismatch","type of","struct","array"),
        "pointer_or_access":("pointer","access chain","opaccesschain"),
        "stage_or_entrypoint":("entry point","execution model","interface","location"),
        "capability_or_extension":("capability","extension","environment","vulkan"),
    }
    for p in diagnostics:
        if p.is_symlink() or not p.is_file() or p.stat().st_size>65536:
            raise ValueError("unsafe_original_six_validator_private_diagnostic")
        raw=p.read_bytes().decode("utf-8","replace").lower()
        matched=False
        for code,terms in topics.items():
            if any(term in raw for term in terms):
                counts[code]+=1
                matched=True
        # Classify only statically authored Vulkan validator phrases, never
        # propagate original CB/member names or IDs from the private log.
        categories={
            "member_overlap":r"member\s+\d+.*overlaps previous member",
            "member_bad_alignment":r"member\s+\d+.*(?:not aligned|not properly aligned)",
            "array_stride_invalid":r"arraystride|array stride",
            "matrix_stride_invalid":r"matrixstride|matrix stride",
            "offset_out_of_order":r"out of order",
            "uniform_buffer_standard_layout":r"standard uniform buffer layout",
            "storage_buffer_layout":r"standard storage buffer layout",
            "block_member_offset":r"member\s+\d+.*offset",
            "nested_struct_layout":r"nested struct|structure member",
            "block_extent_or_padding":r"(?:end of|end at|ending at|padding|padded)",
        }
        for category, expression in categories.items():
            if re.search(expression,raw):
                counts["specific_"+category]+=1
                matched=True
        # Expose only a small overlap-length bucket, NEVER SPIR-V member IDs,
        # raw register indices, shader symbols, source names or exact offsets.
        for overlap in re.finditer(
                r"member\s+\d+\s+at offset\s+(\d+)\s+overlaps\s+"
                r"previous member ending at offset\s+(\d+)",raw):
            start,end=int(overlap[1]),int(overlap[2])
            if start<0 or end<start or end-start>65536:
                raise ValueError("untrusted_original_six_spirv_overlap_diagnostic")
            size=end-start+1
            bucket=("1-4" if size<=4 else "5-8" if size<=8
                    else "9-16" if size<=16 else "17-64" if size<=64
                    else "65+")
            counts["overlap_bytes_bucket_"+bucket]+=1
        if not matched:
            counts["unclassified_spirv_validator_error"]+=1
        for vuid in re.findall(r"vuid-[a-z0-9-]{1,96}",raw):
            # Count only; never publish text fragments or private SSA IDs.
            counts["vulkan_vuid_marker_present"]+=1
    return {
        "private_validator_diagnostic_files":len(diagnostics),
        "safe_problem_topic_counts":dict(sorted(counts.items())),
        "original_shader_identifiers_hlsl_spirv_or_raw_validator_text_published":False,
    }


def validate_authentic_source_ranges(parsed):
    """Fail closed on malformed ORIGINAL Range lanes, never expect next23 counts."""
    census=original_range_contract_safe_census(parsed)
    if (census["source_original_Range_nonzero_unused_fourth_lane_count"]!=0
            or census["source_original_Range_inverted_lower_upper_count"]!=0):
        raise ValueError("invalid_authentic_next6_original_Range_shape")
    return census


def run(original,manifest,quality,private):
    import UnityPy
    for binary in ("vkd3d-compiler","spirv-val","spirv-cross","glslangValidator"):
        if shutil.which(binary) is None:
            raise ValueError("missing_original_D3D11_to_Vulkan_translation_tool")
    q=json.loads(quality.read_text("utf-8"))
    if (q.get("status")!="NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
            or q.get("counts",{}).get("material_docs_using_dummy_Shader")!=216
            or q.get("counts",{}).get("distinct_dummy_Shader_targets_referenced")!=46
            or q.get("counts",{}).get("material_documents")!=1536):
        raise ValueError("unverified_post_fourteen_source_original_Material_shader_population")
    names,owners=gather(original,manifest)
    owner,pid=choose_original_6_by_topology(original,manifest,names,q["dummy_shader_material_counts_by_name_digest"])
    kind,size,digest=read_expected(manifest)[owner]
    source=original/owner
    if source.is_symlink():
        raise ValueError("unsafe_original_Shader48_owner")
    verify(source,size,digest)
    env=UnityPy.load(str(source))
    objs=[obj for obj in env.objects if obj.path_id==pid and str(obj.type.name)=="Shader"]
    if len(objs)!=1:
        raise ValueError("source_authenticated_6_material_Shader48_missing")
    tree=objs[0].read_typetree()
    tables=[records(parts) for platform,parts in decoded_platforms(tree) if platform==4]
    if len(tables)!=1:
        raise ValueError("original_D3D11_program_table_for_6_material_shader_not_unique")
    parsed=tree.get("m_ParsedForm")
    census=summarize(parsed,tables[0])
    baseline=(census["original_source_Shader48_pass_count"],
              census["matched_vertex_fragment_permutation_pairs"],
              census["unmatched_vertex_permutations"],
              census["distinct_original_linked_D3D11_programs"])
    if (baseline!=EXPECTED_TOPOLOGY
            or census["unmatched_fragment_permutations"]!=0):
        raise ValueError("authenticated_original_6_Material_shader_D3D11_pass_topology_drift")
    paired,orphans,passes,distinct=enumerate_all(
        parsed,tables[0],variants=stage_variants,permutation=variant_key,
        linker=linked_program,topology=EXPECTED_TOPOLOGY)
    if private.exists() or private.is_symlink() or not private.parent.is_dir():
        raise ValueError("unsafe_private_D3D11_shader_recovery_location")
    private.mkdir(mode=0o700)
    counts=Counter()
    folders={}
    for index,(ident,record) in enumerate(distinct.items()):
        folder=private/("program-%03d"%index)
        folder.mkdir(mode=0o700)
        folders[ident]=folder.name
        translated=translate(record["source_code"],record["stage"],folder)
        counts["original_programs_translated"]+=1
        for field in ("vulkan11_valid","hlsl_recovered","roundtrip_vulkan11_valid"):
            counts[field]+=int(translated.get(field) is True)
    report={
        "schema_version":1,
        "status":STATUS if counts["roundtrip_vulkan11_valid"]==3 else "PARTIAL_ORIGINAL_D3D11_STAGE_TRANSLATION",
        "postfourteen_dummy_materials_linked_to_this_original_shader":6,
        "original_source_Shader48_object_unique_and_82_owner_SHA_verified":True,
        "original_Shader48_SubShader_count":census["original_source_Shader48_SubShader_count"],
        "original_shader_Pass_count":census["original_source_Shader48_pass_count"],
        "original_exact_vertex_fragment_keyword_permutation_pairs":len(paired),
        "original_orphan_vertex_stage_variants":len(orphans),
        "original_unique_D3D11_shader_program_stages":len(distinct),
        "original_unique_D3D11_program_stages_attempted":counts["original_programs_translated"],
        "original_program_stages_Vulkan11_spirv_val_valid":counts["vulkan11_valid"],
        "original_program_stages_recovered_HLSL":counts["hlsl_recovered"],
        "original_program_stages_roundtrip_Vulkan11_valid":counts["roundtrip_vulkan11_valid"],
        "original_source_82_owners_authenticated":82,
        "original_Source_names_PrivateIDs_or_shader_program_bytes_published":False,
        "original_ShaderLab_android_Unity_or_device_render_proven":False,
        "APK_OBB_XAPK_created":False,
    }
    if report["status"]!=STATUS:
        return report
    packet,routing=keyword_routes(parsed,paired,orphans,passes)
    for row in packet:
        for route in row["routes"]:
            for stage in ("vs","fs"):
                route[stage]=folders[route[stage]]
    checkpoint="compile_source_exact_keyword_routes"
    try:
        report["private_original_exact_keyword_routed_programs_compiled"] = compile_routed_stages(packet,private)
        checkpoint="restore_authentic_source_property_contract"
        source_properties=parsed.get("m_PropInfo",{}).get("m_Props",[])
        if not isinstance(source_properties,list):
            raise ValueError("invalid_original_6_material_Shader_properties")
        ranges=validate_authentic_source_ranges(parsed)
        # The next6 source must dictate the exact original Range count and single-Pass mode.
        # Never copy next23's 3-Range/1-outside numeric fingerprint; preserve
        # any source-authenticated outside default without clamping or editing.
        layout,details=shaderlab_layout(parsed,passes,
            expected_property_count=len(source_properties),
            allow_out_of_range_defaults=(
                ranges["source_original_Range_default_outside_lower_upper_count"]>0),
            allow_original_per_renderer_and_drawer=True)
        report["source_original_Range_property_count"]=ranges["source_original_ShaderLab_Range_property_count"]
        report["source_original_Range_defaults_outside_bounds_preserved_unclamped"]=ranges["source_original_Range_default_outside_lower_upper_count"]
        (private/"original-private-shaderlab-layout.txt").write_text(layout,encoding="utf-8")
        report["source_original_ShaderLab_1pass_property_layout_validated"]=True
        report["source_original_keyword_permutation_route_counts_per_pass"]=routing["source_exact_keyword_routes_by_pass"]
        report["source_original_property_count"]=len(source_properties)
        # Preserve all source/Shader48 metadata and GPU program identity
        # privately. Only source-free counters leave CI.
        def stage_row(row):
            return {k:(folders[v] if k=="program_ref" else v) for k,v in row.items()}
        manifest={
            "schema":1,
            "original_passes":passes,
            "original_shader_ParsedForm_full_private":parsed,
            "paired":[
                {"subshader":pair["subshader"],"pass":pair["pass"],
                 "vs":stage_row(pair["vs"]),"fs":stage_row(pair["fs"])}
                for pair in paired
            ],
            "unpaired":[
                {"subshader":orphan["subshader"],"pass":orphan["pass"],
                 "stage":orphan["stage"],"variant":stage_row(orphan["variant"])}
                for orphan in orphans
            ],
        }
        (private/"original-private-variant-manifest.json").write_text(
            json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        (private/"original-private-keyword-routes.json").write_text(
            json.dumps(packet,sort_keys=True,indent=2)+"\n",encoding="utf-8")
        (private/"original-private-layout.txt").write_text(layout,encoding="utf-8")
        checkpoint="bind_source_constant_buffer_resource_and_vertex_semantics"
        named=stage_parameter_records(
            paired,orphans,passes,tables[0],private,folders,
            original_hlsl_offsets=True)
        report["source_variant_named_CB_sampler_stage_bindings_verified"]=True
        report["original_stage_parameter_records_checked"]=named["original_variant_stages_with_parameter_records"]
        report["original_vertex_fragment_varying_records_matched"]=named["original_vertex_fragment_varying_records_matched"]
        report["original_named_constant_buffer_offsets_verified"]=named["named_constant_buffer_reflected_offsets_verified"]
        report["original_texture_sampler_bindings_rebound"]=named["translated_texture_declarations_mapped_to_source_name"]+named["translated_sampler_declarations_mapped_to_source_texture"]
        checkpoint="compose_one_pass_recovered_original_shaderlab"
        shader=compose(private,engine_keywords=False)
        (private/"original-6-material-Shader48-private.shader").write_text(
            shader,encoding="utf-8")
        route_sets=[
            [[] if index==0 else [f"GT_ORIGINAL_921_P{pass_index}_V{index}"]
             for index in range(route_count)]
            for pass_index,route_count in enumerate(routing["source_exact_keyword_routes_by_pass"])
        ]
        checkpoint="verify_4_compiled_shaderlab_vertex_fragment_entrypoints"
        verify_entrypoints(shader,private,routes=route_sets)
        report["private_original_6_material_ShaderLab_1pass_composed"]=True
        report["private_original_6_material_ShaderLab_4_vertex_fragment_entrypoints_validated"]=True
        report["original_ShaderLab_android_Unity_or_device_render_proven"]=False
    except Exception as exc:
        report["source_keyword_router_or_ShaderLab_layout_status"]="INCONCLUSIVE"
        report["source_keyword_router_or_ShaderLab_layout_error_type"]=type(exc).__name__
        report["source_keyword_router_or_ShaderLab_layout_safe_checkpoint"]=checkpoint
        from scripts.t3_particle108_source_propstate import PrivateContractError
        if isinstance(exc,PrivateContractError):
            # This is an allowlisted generic reason, never the private source
            # shader name, value, keyword, ID or binary.
            report["source_original_property_contract_safe_failure_category"]=exc.category
            if exc.category=="PROPERTY_RANGE":
                report["source_original_Shader48_range_contract_numeric_census"]=original_range_contract_safe_census(parsed)
            if exc.category=="PROPERTY_FLAGS_OR_ATTRIBUTES":
                report["source_original_Shader48_property_flags_attributes_safe_census"]=safe_original_six_property_flag_attribute_census(parsed)
        if checkpoint=="bind_source_constant_buffer_resource_and_vertex_semantics":
            report["original_six_parameter_binding_static_safe_failure_category"]=(
                source_only_static_parameter_binding_failure_category(exc))
            report["original_six_shaderlab_private_spirv_validator_safe_topics"]=(
                original_six_validator_private_failure_safe_topics(private))
        # A translated SPIR-V stage is not a restored/compilable ShaderLab:
        # do not report source restoration success when original bindings fail.
        report["status"]="ORIGINAL_SIX_SHADER48_SOURCE_PROGRAMS_ONLY_BINDING_UNVERIFIED"
        report["original_ShaderLab_android_Unity_or_device_render_proven"]=False
    return report


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("original","manifest","quality","private","out"):
        p.add_argument("--"+name,type=Path,required=True)
    a=p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or
            a.out.resolve().is_relative_to(a.original.resolve())
            or a.out.resolve().is_relative_to(a.private.resolve())
            or a.private.is_symlink()
            or a.private.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_original_D3D11_public_private_artifact_separation")
    try:
        result=run(a.original,a.manifest,a.quality,a.private)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "error_type":type(exc).__name__,
                "original_Source_names_PrivateIDs_or_shader_program_bytes_published":False,
                "APK_OBB_XAPK_created":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("GT_NEXT_6_ORIGINAL_SHADER48_D3D11_STAGE_RECOVERY "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
