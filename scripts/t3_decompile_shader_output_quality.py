#!/usr/bin/env python3
"""T3 genuine source-linked USC Decompile ShaderLab OUTPUT classifier.

The strict original->same-export checker deliberately rejects malformed or
incomplete ShaderLab. This bounded read-only companion classifies all nine
EXACT source-to-export GUID-linked custom Shader48 outputs without treating
their lack of parseable Passes as source data corruption.

Run only on 12 SHA-pinned original ZIP2 providers and W1+B02 traces from one
real exporter invocation. No original source shader, output ShaderLab text,
filenames, original per-object IDs, GUIDs or private exceptions are published.
A successful classification does NOT mean a buildable shader or phone pixels.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_material_shader_same_export as links
from scripts import t3_same_export_shader_pass_topology as topology
from scripts.probe_a13_exported_material_shader_guids import GUID, BUILTIN
from scripts.verify_export_lineage import identity, pointer
from scripts.b49_shaderlab_pass_contract import pass_coverage

MAX_FILES=150000
MAX_META_BYTES=256000
MAX_SHADER_BYTES=8_000_000


def custom_source_map(profiles, w1):
    """True Shader48 original identity ↔ exported pointer; never by name."""
    if len(profiles)!=10 or not isinstance(w1,dict) or not isinstance(w1.get("objects"),list):
        raise ValueError("untrusted_exact_original_Shader48_source_trace")
    found={}
    engine=0
    originals=set()
    for row in w1["objects"]:
        if row.get("class_id")!=48:continue
        key=identity(row["source"])
        if key not in profiles:continue
        if key in originals:
            raise ValueError("duplicate_selected_original_Shader48")
        originals.add(key)
        dest=pointer(row["export"])
        if dest[1] in BUILTIN:
            if dest[2]!="0":raise ValueError("invalid_original_builtin_reference")
            engine+=1
        else:
            if dest[2]!="3":raise ValueError("unexpected_custom_Shader_reference_type")
            if dest[1] in found:
                raise ValueError("two_original_Shaders_share_one_exported_GUID")
            found[dest[1]]=profiles[key]["pass_count"]
    if originals!=set(profiles) or engine!=1 or len(found)!=9:
        raise ValueError("missing_selected_original_Shader48_or_bad_builtin_scope")
    if sum(v["pass_count"] for v in profiles.values())!=38:
        raise ValueError("original_ten_Shader_parsed_pass_count_mismatch")
    return found


def classify_outputs(assets:Path,expected:dict):
    if not assets.is_dir() or assets.is_symlink() or any(p.is_symlink() for p in assets.parents):
        raise ValueError("unsafe_actual_export_assets")
    if len(expected)!=9 or any(type(p) is not int or p<=0 for p in expected.values()):
        raise ValueError("untrusted_original_custom_Shader_scope")
    entries=sorted(assets.rglob("*"))
    if len(entries)>MAX_FILES or any(p.is_symlink() for p in entries):
        raise ValueError("unsafe_or_oversize_actual_export_file_inventory")
    selected={}
    counts=Counter()
    output_pass_histogram=Counter()
    for file in entries:
        if not file.is_file() or not file.name.endswith(".shader.meta"):
            continue
        if file.stat().st_size>MAX_META_BYTES:
            raise ValueError("oversize_exported_ShaderImporter_meta")
        try:
            gids=GUID.findall(file.read_text("utf-8-sig"))
        except UnicodeError:
            counts["invalid_ShaderImporter_meta_utf8"]+=1
            continue
        if len(gids)!=1:
            counts["ambiguous_ShaderImporter_meta_GUIDs"]+=1
            continue
        guid=gids[0].lower()
        if guid not in expected:continue
        if guid in selected:
            raise ValueError("duplicate_selected_original_Shader_GUID")
        shader=Path(str(file)[:-5])
        if not shader.is_file() or shader.is_symlink():
            selected[guid]="no_exported_shader_file"
            counts["selected_ShaderLab_file_missing"]+=1
            continue
        counts["selected_ShaderLab_files_present"]+=1
        if shader.stat().st_size>MAX_SHADER_BYTES:
            selected[guid]="oversize_ShaderLab_file"
            counts["selected_ShaderLab_files_too_large"]+=1
            continue
        try:
            text=shader.read_text("utf-8-sig")
        except UnicodeError:
            selected[guid]="shader_text_decode_failed"
            counts["selected_ShaderLab_text_decode_failed"]+=1
            continue
        counts["selected_with_DummyShaderTextExporter_marker"]+=int("//DummyShaderTextExporter" in text)
        counts["selected_with_No_subprograms_found_marker"]+=int("// No subprograms found" in text)
        counts["selected_with_ShaderUnknownExporter_marker"]+=int("ShaderUnknownExporter" in text)
        counts["selected_text_with_any_CG_or_HLSL_PROGRAM"]+=int("CGPROGRAM" in text or "HLSLPROGRAM" in text)
        try:
            coverage=pass_coverage(text)
        except (ValueError,TypeError):
            selected[guid]="shaderlab_coverage_parser_error"
            counts["selected_ShaderLab_pass_parser_failed"]+=1
            continue
        sourcepass=expected[guid]
        count=coverage["pass_count"]
        output_pass_histogram[count]+=1
        counts["selected_ShaderLab_parsed"]+=1
        counts["selected_actual_passes"]+=count
        counts["selected_actual_programmed_passes"]+=coverage["passes_with_complete_program"]
        counts["selected_original_passes_with_parseable_export"]+=sourcepass
        counts["selected_ShaderLab_all_subshaders_programmed"]+=int(coverage["all_subshaders_programmed"])
        if not coverage["pass_braces_balanced"]:
            counts["selected_ShaderLab_unbalanced_braces"]+=1
            selected[guid]="unbalanced_shaderlab"
        elif sourcepass==count:
            counts["selected_ShaderLab_original_pass_count_equal"]+=1
            selected[guid]="pass_count_equal"
        elif sourcepass>count:
            counts["selected_ShaderLab_source_pass_deficit"]+=1
            counts["selected_source_passes_missing_in_parseable_export"]+=sourcepass-count
            selected[guid]="pass_deficit"
        else:
            counts["selected_ShaderLab_extra_passes"]+=1
            counts["selected_extra_exported_passes"]+=count-sourcepass
            selected[guid]="extra_passes"
    for guid in expected:
        if guid not in selected:
            counts["selected_ShaderLab_meta_missing"]+=1
    counts["selected_original_custom_Shader_objects"]=9
    counts["selected_original_custom_Shader_passes"]=sum(expected.values())
    counts["selected_export_GUID_entries_classified"]=len(selected)
    if counts["selected_export_GUID_entries_classified"]+counts["selected_ShaderLab_meta_missing"]!=9:
        raise ValueError("incomplete_bounded_shader_classification")
    allcount=dict(sorted(counts.items()))
    return {
        "schema_version":1,
        "experiment":"T3-authentic-original-ShaderUSC-Decompile-output-quality",
        "selected_original_source_custom_Shaders":9,
        "selected_source_custom_original_Pass_records":sum(expected.values()),
        "aggregate_output":allcount,
        "parsed_actual_ShaderLab_pass_histogram":dict(sorted(output_pass_histogram.items())),
        "exact_original_to_export_GUID_correspondence_required":True,
        "complete_original_program_subprogram_or_compiler_equivalence_proven":False,
        "unity_or_android_device_rendering_proven":False,
        "proprietary_program_names_paths_Guids_disclosed":False,
        "status":"SCOPED_USC_DECOMPILE_OUTPUT_CLASSIFIED_NOT_SHADER_READY",
    }


def run(root:Path,project:Path,w1path:Path,b02path:Path):
    # Reuse the REAL 41/41 Material.m_Shader→Shader48→.shader.meta exact
    # original export bridge, which already passed in USC run42021786476.
    proof=links.run(root,project,w1path,b02path)
    if not proof.get("original_Material_Shader_pptr_target_preserved"):
        raise ValueError("unverified_original_Material_to_Shader_source_export")
    edges,shaders=links.original_source(root)
    if len(edges)!=41 or len(shaders)!=10:
        raise ValueError("unexpected_original_41_10_scope")
    profiles=topology.source_profiles(root,shaders)
    trace=json.loads(w1path.read_text("utf8"))
    guid_map=custom_source_map(profiles,trace)
    return classify_outputs(project/"Assets",guid_map)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original","project","w1-trace","b02-trace","out"):
        p.add_argument("--"+flag,type=Path,required=True)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()) or a.out.resolve().is_relative_to(a.project.resolve()):
        raise ValueError("report_inside_private_original_or_export_rejected")
    stage="authentic_original_to_actual_USC_export_link_verification"
    try:
        # Only safe symbolic phase and exception TYPE appear; never library's
        # raw error string, original object/source/output file or GUID.
        result=run(a.original,a.project,a.w1_trace,a.b02_trace)
    except Exception as exc:
        result={
            "schema_version":1,
            "experiment":"T3-authentic-original-ShaderUSC-Decompile-output-quality",
            "status":"INCONCLUSIVE","phase":stage,"error_type":type(exc).__name__,
            "complete_original_program_subprogram_or_compiler_equivalence_proven":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf8")
    print("T3_TRUE_SHADER_USC_DECOMPILE_OUTPUT_CENSUS "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]=="SCOPED_USC_DECOMPILE_OUTPUT_CLASSIFIED_NOT_SHADER_READY" else 2

if __name__=="__main__":
    raise SystemExit(main())
