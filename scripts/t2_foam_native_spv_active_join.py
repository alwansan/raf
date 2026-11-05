"""T2 WATER-001: exact active DXBC SAMPLE↔SPIR-V OpSampledImage resource join.

Reuse SHA-authenticated original B20 stage packet, original serialized texture
registers, T2 native DXBC SAMPLE operand reader and T2 compiled SPIR-V SSA
sampler use tracer. Only accept original tN/sN -> translated descriptor role
mapping previously verified through *two explicit source-register remaps* and
byte-equivalent B20 original SPIR-V. No shader names, private binaries,
materials or sample coordinates are published.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from scripts.b20_private_foam_packet import ORIGINAL_STAGE_SHA
from scripts.b17_spectrum_compiled_bindings import compiled_declarations
from scripts.t2_foam_member_abi import original_source_tree, STAGES, _physical
from scripts.t2_foam_original_dxbc_registers import (
    source_texture_registers, compare_numeric_dxbc,
)
from scripts.t2_foam_original_sample_edges import (
    executable_words, token_instruction_usage,
)
from scripts.t2_foam_spirv_sampler_use import trace_sampled_pairs
from scripts.t2_foam_resource_abi import (
    ORIGINAL_TEXTURES_PER_STAGE, COMPILED_NUMERIC_RESOURCE_BINDINGS,
)

MAX_SLOT = 255


def numeric_pair(pair):
    if (not isinstance(pair, (list,tuple)) or len(pair)!=2 or
            any(type(v) is not int or not 0<=v<=MAX_SLOT for v in pair)):
        raise ValueError("Original numeric t/s register pair malformed")
    return tuple(pair)


def exact_native_translated_sample_join(mapping, native, translated, expected_count):
    """Fail closed on source→descriptor mismatches even if 21/6 counts agree."""
    if (not isinstance(mapping,dict) or not isinstance(native,dict) or
            not isinstance(translated,dict) or type(expected_count) is not int
            or expected_count not in (1,5)):
        raise ValueError("Source-authentic fragment prerequisites incomplete")
    if (mapping.get("source_native_dxbc_to_compiled_original_spirv_id_verified") is not True
            or mapping.get("full_original_spirv_graph_equal_after_only_descriptor_literals_mask") is not True
            or mapping.get("distinct_explicit_profiles_proven") != 2):
        raise ValueError("Explicit source register→compiled SPIR-V identity unavailable")
    if (native.get("all_source_pairs_actively_used_proved") is not True or
            translated.get("all_declared_resources_used_verified") is not True or
            translated.get("private_identifiers_published") is not False):
        raise ValueError("Original/compiled active resource coverage incomplete")
    n_calls = native.get("observed_opcode69_sample_calls")
    c_calls = translated.get("compiled_sampling_ops")
    if (type(n_calls) is not int or type(c_calls) is not int or
            not 0<n_calls<=4096 or n_calls!=c_calls):
        raise ValueError("Native SAMPLE versus compiled SSA sample-use count drift")
    if native.get("unhandled_sample_variant_counts") != []:
        raise ValueError("Unsupported native sample variants not accounted")
    original_source_set = native.get("original_source_numeric_pair_set")
    actual_native = native.get("observed_unique_opcode69_t_s_pairs")
    if not isinstance(original_source_set,list) or not isinstance(actual_native,list):
        raise ValueError("Native source or executable register pairs unavailable")
    source = [numeric_pair(x) for x in original_source_set]
    native_pairs = [numeric_pair(x) for x in actual_native]
    if (len(source)!=expected_count or len(set(source))!=len(source) or
            len(native_pairs)!=expected_count or len(set(native_pairs))!=len(native_pairs)
            or set(source)!=set(native_pairs)):
        raise ValueError("Original registered or active native t/s pairs ambiguous")
    rows = mapping.get("source_register_to_default_compiled_descriptors")
    if not isinstance(rows,list) or len(rows)!=2*expected_count+1:
        raise ValueError("Compiled role-identity table incomplete")
    by_role={"image":{}, "sampler":{}, "cb":{}}
    seen_default={"image":set(), "sampler":set(), "cb":set()}
    for row in rows:
        if (not isinstance(row,dict)
                or set(row)!={"source_kind","original_dxbc_register",
                               "compiled_image_sampler_or_cb_set","compiled_binding"}):
            raise ValueError("Unknown original-to-SPIR-V descriptor identity row")
        kind = row["source_kind"]
        slot = row["original_dxbc_register"]
        desc = row["compiled_image_sampler_or_cb_set"],row["compiled_binding"]
        if (kind not in by_role or type(slot) is not int or
                any(type(v) is not int or not 0<=v<=MAX_SLOT for v in desc)):
            raise ValueError("Original DXBC register/target descriptor shape invalid")
        maximum=1 if kind=="cb" else expected_count
        if (not 0<=slot<maximum or slot in by_role[kind]
                or desc in seen_default[kind]):
            raise ValueError("Source register/compiled descriptor alias or duplicate")
        by_role[kind][slot]=desc
        seen_default[kind].add(desc)
    if (set(by_role["image"])!=set(range(expected_count)) or
            set(by_role["sampler"])!=set(range(expected_count)) or
            set(by_role["cb"])!={0}):
        raise ValueError("Native tN/sN source-to-descriptor bijection incomplete")
    reverse_images={v:k for k,v in by_role["image"].items()}
    reverse_samplers={v:k for k,v in by_role["sampler"].items()}
    spv_use=translated.get("used_image_sampler_pairs")
    if not isinstance(spv_use,list) or len(spv_use)!=expected_count:
        raise ValueError("Translated actual sampled resource-use set drift")
    used=[]
    for item in spv_use:
        if (not isinstance(item,dict) or
                set(item)!={"image_set","image_binding","sampler_set","sampler_binding"} or
                any(type(x) is not int or not 0<=x<=MAX_SLOT for x in item.values())):
            raise ValueError("Translated compiled use not a complete numeric pair")
        image=(item["image_set"],item["image_binding"])
        sampler=(item["sampler_set"],item["sampler_binding"])
        if image not in reverse_images or sampler not in reverse_samplers:
            raise ValueError("Sampled translated descriptor unowned by native source register")
        used.append((reverse_images[image],reverse_samplers[sampler]))
    if len(set(used))!=expected_count or set(used)!=set(native_pairs):
        raise ValueError("Compiled active sampler/image pairing disagrees with original DXBC")
    return {
        "native_sample_calls":n_calls,
        "translated_sample_calls":c_calls,
        "source_active_pair_count":expected_count,
        "translated_to_original_native_register_pairs":[list(x) for x in sorted(set(used))],
        "source_to_translated_active_sample_pair_identity_verified":True,
        "native_to_spirv_register_to_descriptor_id_provenance":"two explicit remaps and all SPIR-V code equal except descriptor numeric literals",
        "unity_material_upload_sampler_state_verified":False,
        "shaderlab_or_adreno_pixels_verified":False,
        "private_source_identifiers_or_binaries_published":False,
    }


def audit(source,packet,manifest,mapping_report):
    source,packet,manifest,mapping_report=map(lambda p:Path(p).absolute(),
                                               (source,packet,manifest,mapping_report))
    if (not source.is_dir() or not packet.is_dir() or
            not manifest.is_file() or not mapping_report.is_file()
            or not all(_physical(x) for x in (source,packet,manifest,mapping_report))):
        raise ValueError("Private original Foam data or explicit mapping unavailable")
    manifest_data=json.loads(manifest.read_text())
    proof=json.loads(mapping_report.read_text())
    if (manifest_data.get("status")!="private_two_pass_inputs_staged" or
            manifest_data.get("original_stage_programs")!=4 or
            not manifest_data.get("private_packet_staged") or
            proof.get("status")!="original_foam_explicit_native_to_spirv_binding_identity_verified" or
            proof.get("original_fragments_explicit_verified")!=2 or
            proof.get("original_t_s_pairs_mapped")!=6 or
            not isinstance(proof.get("stages"),list) or len(proof["stages"])!=4):
        raise ValueError("Exact original Foam stage and mapped compiler proof unavailable")
    passes=original_source_tree(source)["m_SubShaders"][0]["m_Passes"]
    rows=[]
    for order,(pi,stage) in enumerate(STAGES):
        record=proof["stages"][order]
        if (not isinstance(record,dict) or
                (record.get("pass"),record.get("stage_code"))!=(pi,stage)):
            raise ValueError("Pass/stage context mismatched in explicit provenance")
        stage_dir=packet/("pass%d-stage%d"%(pi,stage))
        binary=stage_dir/"source.dxbc"
        compiled=stage_dir/"original.spv"
        if (not _physical(binary) or not _physical(compiled)
                or not binary.is_file() or not compiled.is_file() or
                hashlib.sha256(binary.read_bytes()).hexdigest()!=ORIGINAL_STAGE_SHA[(pi,stage)]):
            raise ValueError("SHA-authentic native DXBC program missing")
        actual_src=passes[pi]["progVertex" if stage==1 else "progFragment"]
        count=ORIGINAL_TEXTURES_PER_STAGE[(pi,stage)]
        candidates=source_texture_registers(actual_src,count)
        parity=compare_numeric_dxbc(candidates,compiled_declarations(binary.read_bytes(),stage))
        if not parity["complete_source_texture_sampler_to_dxbc_register_set_parity"]:
            raise ValueError("Authentic Unity texture t/s register declaration parity missing")
        native=token_instruction_usage(executable_words(binary.read_bytes(),stage),stage,candidates)
        previous=COMPILED_NUMERIC_RESOURCE_BINDINGS[(pi,stage)]
        images=[(set_,bind) for kind,set_,bind in previous if kind=="separate_images"]
        samplers=[(set_,bind) for kind,set_,bind in previous if kind=="separate_samplers"]
        run=subprocess.run(["spirv-dis",str(compiled)],stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL,text=True,
                           stdin=subprocess.DEVNULL,timeout=35,check=False)
        if run.returncode or not run.stdout or len(run.stdout)>8*1024*1024:
            raise ValueError("SPIR-V native translation disassembly unavailable")
        translated=trace_sampled_pairs(run.stdout,images,samplers)
        if stage==1:
            if (count!=0 or native["observed_opcode69_sample_calls"]!=0 or
                    translated["compiled_sampling_ops"]!=0 or
                    record.get("genuine_sampler_register_mapping_covered") is not False):
                raise ValueError("Vertex source declared unexpected Foam texture sample")
            rows.append({"pass":pi,"stage_code":stage,"source_texture_pairs":0,
                         "actual_native_and_translated_sample_calls":0,
                         "source_to_spirv_active_sample_pair_identity_verified":True,
                         "nonempty_tex_sampler_roles_verified":False})
            continue
        pair=exact_native_translated_sample_join(record,native,translated,count)
        rows.append({"pass":pi,"stage_code":stage,"source_texture_pairs":count,
                     **pair})
    if (len(rows)!=4 or
            sum(s["source_texture_pairs"] for s in rows)!=6 or
            sum(s.get("native_sample_calls",0) for s in rows)!=21 or
            not all(x["source_to_spirv_active_sample_pair_identity_verified"] for x in rows)):
        raise ValueError("Authentic original-to-compiled active source pair sample census drift")
    return {
        "status":"foam_actual_native_sample_to_spirv_resource_pair_identity_verified",
        "source_authentic_original_stages":4,
        "verified_sampled_fragment_stages":2,
        "original_texture_sampler_pairs":6,
        "authentic_native_sample_calls":21,
        "translated_spirv_sample_calls":21,
        "exact_active_native_to_translated_pair_identity_proven":True,
        "stages":rows,
        "unity_material_texture_upload_verified":False,
        "original_sampler_filter_wrap_or_uv_verified":False,
        "authentic_shaderlab_import_or_adreno_pixels_verified":False,
        "proprietary_program_source_identifiers_binaries_published":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ("source","packet","manifest","mapping","out"):
        p.add_argument("--"+key,type=Path,required=True)
    a=p.parse_args()
    try:
        out=a.out.absolute()
        if out.exists() or not out.parent.is_dir() or not _physical(out) or (
                out.is_relative_to(a.packet.absolute()) or
                out.is_relative_to(a.source.absolute())):
            raise ValueError("Unsafe native↔translated sampler proof report path")
        result=audit(a.source,a.packet,a.manifest,a.mapping)
        out.write_text(json.dumps(result,sort_keys=True)+"\n",encoding="utf-8")
        print("T2_FOAM_NATIVE_SPV_ACTIVE "+json.dumps({
            "status":result["status"],
            "actual_native_DXBC_sample_calls":21,
            "actual_translated_SPV_sample_calls":21,
            "active_source_to_translated_sample_pairs_verified":6,
            "unity_material_or_device_proven":False,
            "private_shader_published":False,
        }))
        return 0
    except BaseException as exc:
        # An exception key or message could contain private Unity/Shader names.
        # Publish only a static-source module token and numeric source line.
        frame=exc.__traceback__
        while frame is not None and frame.tb_next is not None:
            frame=frame.tb_next
        public_files={
            "t2_foam_native_spv_active_join.py",
            "t2_foam_original_sample_edges.py",
            "t2_foam_spirv_sampler_use.py",
            "t2_foam_original_dxbc_registers.py",
        }
        module=Path(frame.tb_frame.f_code.co_filename).name if frame else ""
        site=({"source_module":module,"source_line":frame.tb_lineno}
              if frame is not None and module in public_files else
              {"source_module":"external","source_line":None})
        print("T2_FOAM_NATIVE_SPV_ACTIVE "+json.dumps({
            "status":"blocked","failure_class":type(exc).__name__,**site,
            "actual_native_to_spv_proven":False,
            "private_shader_published":False,
        }))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
