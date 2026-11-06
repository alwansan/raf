#!/usr/bin/env python3
"""SHA-authenticated original Particle108 VS/PS: dual-explicit VKD3D descriptor proof.

Original DXBC source, source registers, private mapping packets and SPIR-V
modules remain runner-private. Output strictly aggregate, no ShaderLab, Unity
or Android pixel equivalence claim. A/B target bindings are deliberately chosen
compiler test locations, not the original Unity material binding model.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from scripts import t3_particle108_dcl_spv_family_census as original
from scripts import t3_particle108_explicit_map_packet as packets
from scripts import t3_particle108_spirv_explicit_pair as dual

STATUS = "T3_SHA_ORIGINAL_PARTICLE108_VKD3D_EXPLICIT_DUAL_PROFILE_PROOF"
FAILURE_CODES = frozenset({
    "T3_PRIVATE_COMPILER_NONZERO", "T3_PRIVATE_COMPILER_UNAVAILABLE",
    "T3_PRIVATE_SPIRV_INVALID", "T3_PRIVATE_SPIRV_TOOL_UNAVAILABLE",
    "T3_PRIVATE_OUTPUT_MISSING", "T3_PRIVATE_DUAL_PROFILE_PAIR_REJECTED",
    "T3_PRIVATE_BASELINE_COMPILER_NONZERO", "T3_PRIVATE_BASELINE_SPIRV_INVALID",
    "T3_PRIVATE_RESULT_CONTRACT", "T3_PRIVATE_SCOPE_INVALID",
})

def _quiet_run(argv,*,run=subprocess.run,code):
    """Suppress stdout/stderr and command arguments that may contain secrets."""
    try:
        proc=run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                 stdin=subprocess.DEVNULL,timeout=50,check=False)
    except (OSError,subprocess.TimeoutExpired):
        raise ValueError(code) from None
    if proc.returncode!=0:
        # Public helper process exit integer (not stderr/stdout, DXBC, paths,
        # register values or SPIR-V content) is needed to separate a parser
        # contract fault from a real vkd3d shader-compiler rejection.
        if code in ("T3_PRIVATE_COMPILER_NONZERO",
                    "T3_PRIVATE_BASELINE_COMPILER_NONZERO",
                    "T3_PRIVATE_EXPLICIT_AFTER_VALID_BASELINE_COMPILER_NONZERO") and 1<=proc.returncode<=127:
            raise ValueError(code+"_EXIT_"+str(proc.returncode)) from None
        raise ValueError(code) from None

def classify(pairs,temporary,compiler,*,layout=original.dx._private_stage_layout,
             maker=packets.private_packets,verifier=dual.verify_pair,
             runner=subprocess.run):
    """Privately compile 4 original VS/FS pairs twice, count only proven pairs."""
    if (type(pairs) is not list or len(pairs)!=4
        or any(type(p) is not tuple or len(p)!=2
               or any(type(code) is not bytes or not 36<=len(code)<=original.origin.MAX_PRIVATE_STAGE_BYTES
                      for code in p) for p in pairs)
        or not isinstance(temporary,Path) or not temporary.is_dir()
        or temporary.is_symlink()
        or not isinstance(compiler,Path) or not compiler.is_file()
        or compiler.is_symlink() or not os.access(compiler,os.X_OK)):
        raise ValueError("T3_PRIVATE_SCOPE_INVALID")
    counts=Counter()
    for keyword_index,(vs,fs) in enumerate(pairs):
        for stage,source in ((1,vs),(0,fs)):
            folder=temporary/("private-pair-%d-stage-%d"%(keyword_index,stage))
            folder.mkdir(exist_ok=False)
            dxbc=folder/"source.dxbc"
            with dxbc.open("xb") as output:
                output.write(source)
            stage_layout=layout(source,stage)
            map_text,metadata=maker(stage_layout,stage)
            if (type(map_text) is not dict or set(map_text)!={"A","B"}
                or type(metadata) is not dict
                or type(metadata.get("source_stage_resource_count")) is not int
                or not 1<=metadata["source_stage_resource_count"]<=64):
                raise ValueError("T3_PRIVATE_RESULT_CONTRACT")
            paths=packets.private_write_packets(map_text,folder)
            # Contrast exact SAME original stage source and C API without any
            # explicit descriptor interface. A valid baseline + A/B rejection
            # isolates the explicit register map contract rather than claiming
            # the original source was corrupt.
            default_spv=folder/"unmapped-baseline.spv"
            _quiet_run([str(compiler),str(dxbc),str(default_spv),"D"],
                       run=runner,code="T3_PRIVATE_BASELINE_COMPILER_NONZERO")
            if (not default_spv.is_file() or default_spv.is_symlink() or
                not 20<=default_spv.stat().st_size<=dual.spv.MAX_SPIRV_BYTES):
                raise ValueError("T3_PRIVATE_OUTPUT_MISSING")
            _quiet_run(["spirv-val","--target-env","vulkan1.1",str(default_spv)],
                       run=runner,code="T3_PRIVATE_BASELINE_SPIRV_INVALID")
            counts["private_unmapped_baseline_compiler_invocations"]+=1
            counts["private_unmapped_baseline_spirv_val_invocations"]+=1
            binaries={}
            for profile in ("A","B"):
                output=folder/("mapped-"+profile+".spv")
                _quiet_run([str(compiler),str(dxbc),str(output),
                            str(paths[profile]),profile],
                           run=runner,code="T3_PRIVATE_EXPLICIT_AFTER_VALID_BASELINE_COMPILER_NONZERO")
                if (not output.is_file() or output.is_symlink() or
                    not 20<=output.stat().st_size<=dual.spv.MAX_SPIRV_BYTES):
                    raise ValueError("T3_PRIVATE_OUTPUT_MISSING")
                _quiet_run(["spirv-val","--target-env","vulkan1.1",str(output)],
                           run=runner,code="T3_PRIVATE_SPIRV_INVALID")
                binaries[profile]=output.read_bytes()
            try:
                proof=verifier(map_text["A"],map_text["B"],
                               binaries["A"],binaries["B"],stage)
            except ValueError:
                raise ValueError("T3_PRIVATE_DUAL_PROFILE_PAIR_REJECTED") from None
            if (type(proof) is not dict or
                proof.get("status")!=dual.STATUS or
                proof.get("chosen_explicit_target_layouts_verified")!=2 or
                proof.get("same_source_to_spirv_variable_identity_across_profiles") is not True or
                proof.get("whole_spirv_program_identical_except_descriptor_literals") is not True or
                proof.get("source_register_numbers_spirv_IDS_descriptor_coordinates_published") is not False or
                proof.get("shaderlab_compiled_or_android_pixels_verified") is not False or
                type(proof.get("source_registers_mapped_under_both_profiles")) is not int or
                proof["source_registers_mapped_under_both_profiles"]!=metadata["source_stage_resource_count"]):
                raise ValueError("T3_PRIVATE_RESULT_CONTRACT")
            counts["source_stages_with_two_explicit_profiles_verified"]+=1
            counts["verified_original_register_rows"]+=metadata["source_stage_resource_count"]
            counts["private_compiler_invocations"]+=2
            counts["private_spirv_val_invocations"]+=2
            counts["verified_vertex_stages" if stage else "verified_fragment_stages"]+=1
        counts["verified_source_keyword_pairs"]+=1
    if (counts["source_stages_with_two_explicit_profiles_verified"]!=8
        or counts["verified_source_keyword_pairs"]!=4
        or counts["private_compiler_invocations"]!=16
        or counts["private_unmapped_baseline_compiler_invocations"]!=8):
        raise ValueError("T3_PRIVATE_RESULT_CONTRACT")
    return {
        "schema_version":1,"status":STATUS,"counts":dict(sorted(counts.items())),
        "explicit_DX_source_register_to_chosen_VK_target_proven_by_dual_profile":True,
        "source_program_identity_except_descriptor_decorations_proven":True,
        "chosen_VK_target_is_original_Unity_binding_or_material_semantics":False,
        "ShaderLab_program_recovered_or_Unity_Android_pixels_proven":False,
        "private_original_registers_source_bytes_SPIRV_ids_or_bindings_published":False,
    }

def probe(root,manifest,compiler):
    if shutil.which("spirv-val") is None:
        raise ValueError("T3_PRIVATE_SPIRV_TOOL_UNAVAILABLE")
    if not compiler.is_file() or not os.access(compiler,os.X_OK):
        raise ValueError("T3_PRIVATE_COMPILER_UNAVAILABLE")
    selected={}
    source=original.rb.identity.source.load_original(
        root,manifest,private_particle_slot_counts=selected)
    owner,pid=original.rb.identity.select(selected,source)
    shader_file=root/"Raft_Data"/owner
    if (any(x.is_symlink() for x in (shader_file,*shader_file.parents))
        or original.fingerprint(shader_file)!=original.SHADER_OWNERS[owner]):
        raise ValueError("T3_PRIVATE_SCOPE_INVALID")
    import UnityPy
    objects=[o for o in UnityPy.load(str(shader_file)).file.objects.values()
             if o.path_id==pid]
    if len(objects)!=1 or objects[0].type.name!="Shader":
        raise ValueError("T3_PRIVATE_SCOPE_INVALID")
    tree=objects[0].read_typetree()
    _,shape=original.serialize_properties(tree["m_ParsedForm"])
    if (shape["original_authored_property_count"]!=13 or
        shape["original_authored_texture_property_count"]!=2):
        raise ValueError("T3_PRIVATE_SCOPE_INVALID")
    table=[original.records(data) for platform,data in original.decoded_platforms(tree)
           if platform==4]
    if len(table)!=1:
        raise ValueError("T3_PRIVATE_SCOPE_INVALID")
    identity=original.rb.identity.inspect(tree["m_ParsedForm"],table[0])
    if (identity.get("status")!=original.rb.identity.STATUS
        or identity.get("matched_vertex_fragment_permutation_pairs")!=4
        or identity.get("original_D3D11_program_table_records")!=16):
        raise ValueError("T3_PRIVATE_SCOPE_INVALID")
    pairs=original.origin.exact_four_pairs(tree["m_ParsedForm"],table[0])
    with tempfile.TemporaryDirectory(prefix="t3-private-real-explicit-shader48-") as temp:
        report=classify(pairs,Path(temp),compiler)
    report["original_six_renderer_scenes_SHA_authenticated"]=True
    report["original_four_shader_owners_SHA_authenticated"]=True
    report["source_original_particle_renderer_material_use_slots"]=108
    return report

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for arg in ("original","manifest","compiler","out"):
        ap.add_argument("--"+arg,required=True,type=Path)
    a=ap.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("T3_PRIVATE_UNSAFE_OUTPUT_PATH")
    try:
        result=probe(a.original,a.manifest,a.compiler)
    except Exception as exc:
        literal=str(exc) if type(exc) is ValueError else ""
        # The C helper's return code is bounded and source-independent.
        # All other exception messages are discarded to protect game data.
        exit_prefixes=("T3_PRIVATE_BASELINE_COMPILER_NONZERO_EXIT_",
                       "T3_PRIVATE_EXPLICIT_AFTER_VALID_BASELINE_COMPILER_NONZERO_EXIT_",
                       "T3_PRIVATE_COMPILER_NONZERO_EXIT_")
        compiler_exit=any(
            literal.startswith(prefix) and
            literal.removeprefix(prefix).isascii() and
            literal.removeprefix(prefix).isdecimal() and
            1<=int(literal.removeprefix(prefix))<=127 for prefix in exit_prefixes)
        reason=literal if literal in FAILURE_CODES or compiler_exit else "T3_PRIVATE_UNCLASSIFIED_FAILURE"
        result={
            "schema_version":1,"status":"INCONCLUSIVE",
            "failure_code":reason,
            "failure_type":type(exc).__name__,
            "explicit_DX_source_register_to_chosen_VK_target_proven_by_dual_profile":False,
            "ShaderLab_program_recovered_or_Unity_Android_pixels_proven":False,
            "private_original_registers_source_bytes_SPIRV_ids_or_bindings_published":False,
        }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print("T3_ORIGINAL_EXPLICIT_DUAL_PROFILE_SAFE="+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
