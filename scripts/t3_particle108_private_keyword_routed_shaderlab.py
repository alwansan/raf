#!/usr/bin/env python3
"""One PROVISIONAL private original Shader48 keyword-routed ShaderLab; no game edits.

Original SHA-authentic four HLSLPROGRAMs are assembled in runner scratch only.
Do not infer Unity #pragma scope, Material binding, editor import or phone pixels.
Never print original names/indexes, private shader text or compiler diagnostics.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from scripts import t3_particle108_original_keyword_names as names
from scripts import t3_particle108_private_stagewrapper_compile as stages
from scripts import t3_original_renderer_shader_impact as impact
from scripts import t3_original_particle108_dxbc_feasibility as identity
from scripts import t3_original_particle108_spirv_translation as originals
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.w1_recover_depth_passes import stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_stage_zip2_owners import fingerprint

STATUS="T3_PRIVATE_SHADER48_PROVISIONAL_TWO_KEYWORD_SINGLE_SHADERLAB_VALID"
START=re.compile(r"(?m)^[ \t]*HLSLPROGRAM[ \t]*$")
END=re.compile(r"(?m)^[ \t]*ENDHLSL[ \t]*$")
EXPECTED=frozenset("keyword-%d-private.shader"%i for i in range(4))

def source_routes(parsed):
    """Derive pair order used by exact_four_pairs, never sort by guessed macros."""
    check=names.classify(parsed)
    if (check.get("original_switch_index_to_name_table_mapping_proven") is not True
        or check.get("table_category")!="TWO_SWITCH_INDEX_NAMES_FOUND_WITH_FLAGS_UNINTERPRETED"):
        raise ValueError("original_source_keyword_table_unmapped")
    rows=stage_variants(parsed["m_SubShaders"][0]["m_Passes"][0]["progVertex"])
    if len(rows)!=4:
        raise ValueError("original_pair_count_wrong")
    sets=[frozenset(meta["m_KeywordIndices"]) for _,_,meta in rows]
    common=set.intersection(*(set(s) for s in sets))
    if common:
        raise ValueError("original_shared_baseline_keyword_unmodelled")
    switch=sorted(set().union(*sets))
    if len(switch)!=2:
        raise ValueError("original_keyword_dimension_mismatch")
    chosen=tuple(parsed["m_KeywordNames"][i] for i in switch)
    if any(n in ("SHADER_STAGE_VERTEX","SHADER_STAGE_FRAGMENT")
           or n.startswith("GL_") for n in chosen):
        raise ValueError("original_keyword_macro_collides_with_stage")
    routes={tuple(int(i in keys) for i in switch):n for n,keys in enumerate(sets)}
    if len(routes)!=4 or set(routes)!={(0,0),(0,1),(1,0),(1,1)}:
        raise ValueError("incomplete_original_keyword_lattice")
    return chosen,routes

def parts(source):
    # Existing macro compiler guarantees only 3 pragmas, an entrypoint,
    # one stage-switch body, a complete program and bounded candidate size.
    executable=stages.extract(source)
    a=list(START.finditer(source))
    z=list(END.finditer(source))
    if len(a)!=1 or len(z)!=1 or a[0].end()>=z[0].start():
        raise ValueError("private_shaderlab_program_bounds")
    return source[:a[0].start()],executable,source[z[0].end():]

def compose(root,parsed):
    if (not isinstance(root,Path) or not root.is_dir() or root.is_symlink()
        or {p.name for p in root.glob("keyword-*-private.shader")}!=EXPECTED):
        raise ValueError("private_original_stage_candidates_missing")
    keyword_names,routes=source_routes(parsed)
    original=[]
    envelope=None
    for n in range(4):
        file=root/("keyword-%d-private.shader"%n)
        if not file.is_file() or file.is_symlink():
            raise ValueError("unsafe_private_original_stage_file")
        header,program,footer=parts(file.read_text(encoding="utf-8"))
        if envelope is None:
            envelope=(header,footer)
        elif envelope!=(header,footer):
            raise ValueError("private_original_candidate_envelope_mismatch")
        original.append(program)
    lines=["HLSLPROGRAM","#pragma target 5.0","#pragma vertex main",
           "#pragma fragment main",
           *("#pragma multi_compile __ "+name for name in keyword_names)]
    for number,bits in enumerate(((0,0),(0,1),(1,0),(1,1))):
        clause=" && ".join(("defined("+name+")" if bit else "!defined("+name+")")
                         for name,bit in zip(keyword_names,bits))
        lines.extend([("#if " if number==0 else "#elif ")+clause,
                      original[routes[bits]]])
    lines.extend(["#else","#error Unmatched_original_keyword_set","#endif"])
    candidate=envelope[0]+"\n".join(lines)+"\nENDHLSL"+envelope[1]
    if not 0<len(candidate.encode("utf-8"))<=16*1024*1024:
        raise ValueError("oversized_private_unified_shaderlab")
    safe=pass_coverage(candidate)
    if (safe.get("pass_count")!=1 or safe.get("passes_with_complete_program")!=1
        or safe.get("subshader_pass_counts")!=[1]
        or safe.get("pass_braces_balanced") is not True):
        raise ValueError("private_routed_shaderlab_structurally_invalid")
    return candidate,keyword_names,routes

def executable(source,keyword_names):
    a=list(START.finditer(source))
    z=list(END.finditer(source))
    if len(a)!=1 or len(z)!=1 or a[0].end()>=z[0].start():
        raise ValueError("private_routed_shaderlab_program_bounds")
    body=source[a[0].end():z[0].start()]
    pragmas=[x.strip() for x in body.splitlines() if x.strip().startswith("#pragma")]
    expected={"#pragma target 5.0","#pragma vertex main","#pragma fragment main",
              *("#pragma multi_compile __ "+n for n in keyword_names)}
    if len(pragmas)!=5 or set(pragmas)!=expected:
        raise ValueError("private_routed_shaderlab_pragmas_mismatch")
    return "\n".join(x for x in body.splitlines() if not x.strip().startswith("#pragma"))+"\n"

def compile_one(code,stage,keyword_names,bits,root):
    if type(stage) is not int or stage not in (0,1):
        raise ValueError("private_invalid_stage")
    extension,stage_macro=(("vert","SHADER_STAGE_VERTEX") if stage==1
                          else ("frag","SHADER_STAGE_FRAGMENT"))
    with tempfile.TemporaryDirectory(prefix="t3-provisional-routed-",dir=root) as d:
        path=Path(d)
        hlsl=path/("stage."+extension+".hlsl")
        spv=path/"validated.spv"
        hlsl.write_text(code,encoding="utf-8")
        command=["glslangValidator","-V","-D","--target-env","vulkan1.1",
                 "-S",extension,"-e","main","-D"+stage_macro+"=1"]
        command.extend("-D"+key+"=1" for key,enabled in zip(keyword_names,bits) if enabled)
        command.extend(["-o",str(spv),str(hlsl)])
        try:
            a=subprocess.run(command,capture_output=True,timeout=90,check=False)
            if a.returncode!=0 or spv.is_symlink() or not spv.is_file():
                return False
            if not 20<=spv.stat().st_size<=stages.MAX_SPV:
                return False
            b=subprocess.run(["spirv-val","--target-env","vulkan1.1",str(spv)],
                             capture_output=True,timeout=45,check=False)
            return b.returncode==0
        except (OSError,subprocess.TimeoutExpired):
            return False

def verify(root,parsed,*,compiler=compile_one):
    # Detect conflicting output before scanning original keyword candidate files:
    # keyword-routed-private.shader also matches keyword-*-private.shader glob.
    destination=root/"keyword-routed-private.shader"
    if destination.exists() or destination.is_symlink():
        raise ValueError("will_not_overwrite_private_routed_shader")
    private,keywords,routes=compose(root,parsed)
    destination.write_text(private,encoding="utf-8")
    code=executable(private,keywords)
    passed=sum(compiler(code,stage,keywords,bits,root) is True
               for bits in ((0,0),(0,1),(1,0),(1,1)) for stage in (1,0))
    return {"schema_version":1,"status":STATUS if passed==8 else "INCONCLUSIVE",
            "source_original_keyword_name_indices_mapped":True,
            "original_keyword_pair_routes":len(routes),
            "provisional_one_ShaderLab_four_pairs":True,
            "private_combination_stage_compiles_attempted":8,
            "private_combination_stage_Vulkan11_SPIRV_valid":passed,
            "original_keyword_flags_pragma_scope_proven":False,
            "Unity_ShaderLab_import_or_actual_variant_selection_proven":False,
            "original_Material_binding_proven":False,
            "Android_pixels_proven":False,
            "original_keyword_names_indices_shader_code_or_errors_published":False}

def probe(original,manifest,private_dir):
    chosen={}
    census=impact.load_original(original,manifest,private_particle_slot_counts=chosen)
    owner,pid=identity.select(chosen,census)
    file=original/"Raft_Data"/owner
    if file.is_symlink() or fingerprint(file)!=SHADER_OWNERS[owner]:
        raise ValueError("private_original_sha_drift")
    import UnityPy
    items=[x for x in UnityPy.load(str(file)).file.objects.values()
           if x.type.name=="Shader" and x.path_id==pid]
    if len(items)!=1:
        raise ValueError("original_shader_identity_drift")
    tree=items[0].read_typetree()
    tables=[records(blobs) for platform,blobs in decoded_platforms(tree) if platform==4]
    if len(tables)!=1 or len(tables[0])!=16:
        raise ValueError("original_program_table_drift")
    parsed=tree["m_ParsedForm"]
    if len(originals.exact_four_pairs(parsed,tables[0]))!=4:
        raise ValueError("original_four_dxbc_pairs_drift")
    return verify(private_dir,parsed)

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original","manifest","private-dir","out"):
        ap.add_argument("--"+name,type=Path,required=True)
    args=ap.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or not args.out.parent.is_dir()
        or args.out.parent.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve()) or
        args.out.resolve().is_relative_to(args.private_dir.resolve())):
        raise ValueError("unsafe_report_output")
    try:
        result=probe(args.original,args.manifest,args.private_dir)
    except Exception:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_code":"PRIVATE_SHADER48_ROUTER_UNCLASSIFIED",
                "original_keyword_names_indices_shader_code_or_errors_published":False,
                "Unity_ShaderLab_import_or_actual_variant_selection_proven":False}
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("T3_PRIVATE_SHADER48_ROUTING_SAFE="+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
