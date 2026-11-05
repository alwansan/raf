"""T2 WATER-001: original Foam serialized texture/sampler indices versus DXBC.

This is NOT a SPIR-V descriptor map, Unity property name bridge, ShaderLab
wrapper or device result. It only decodes numeric original D3D11 shader
resource declarations using B17's authenticated parser and compares each
source m_TextureParams row's t/s candidate to those native registers.
Private names, binaries, decompressed data never enter output/logs.
"""
import argparse
import hashlib
import json
from pathlib import Path

from scripts.b17_spectrum_compiled_bindings import compiled_declarations
from scripts.b20_private_foam_packet import ORIGINAL_STAGE_SHA
from scripts.b24_original_foam_stage_translation import (
    OWNER, OBJECT_ID, ORIGINAL_OBJECT_SHA256, TARGET, validate_stage,
)
from scripts.b25_foam_cb_namebridge import inspect_parsed as attest_name_registry
from scripts.t2_foam_member_abi import STAGES, _physical
from scripts.t2_foam_resource_abi import ORIGINAL_TEXTURES_PER_STAGE
from scripts.w1_recover_depth_passes import linked_program
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_stage_zip2_owners import PINS, fingerprint

MAX_INDEX = 255
MAX_ROWS = 128


def source_texture_registers(program, expected_count):
    """Collect numeric t/s candidates, never treating -1 as a valid sampler."""
    if not isinstance(program, dict) or type(expected_count) is not int:
        raise ValueError("Original Foam program input invalid")
    common = program.get("m_CommonParameters")
    if not isinstance(common, dict):
        raise ValueError("Original Foam source parameter table absent")
    textures = common.get("m_TextureParams")
    samplers = common.get("m_Samplers")
    uavs = common.get("m_UAVParams")
    if (not isinstance(textures, list) or len(textures) != expected_count
            or len(textures) > MAX_ROWS or samplers != [] or uavs != []):
        raise ValueError("Original Foam source texture table authenticity drift")
    rows, seen = [], set()
    for entry in textures:
        if not isinstance(entry, dict):
            raise ValueError("Original texture row malformed")
        index = entry.get("m_Index")
        sampler = entry.get("m_SamplerIndex")
        if (type(index) is not int or not 0 <= index <= MAX_INDEX or
                type(sampler) is not int or not -1 <= sampler <= MAX_INDEX or
                index in seen):
            raise ValueError("Original texture index or sampler candidate invalid")
        seen.add(index)
        rows.append({"original_texture_index": index, "original_sampler_index": sampler})
    return rows


def compare_numeric_dxbc(rows, compiled):
    """Compare original source t/s candidates to actual native DXBC declarations.

    DXBC register sets are authoritative *for native DXBC*, not automatically
    for translated SPIR-V. Register counts alone are never accepted as parity.
    """
    if not isinstance(rows, list) or not isinstance(compiled, dict):
        raise ValueError("Malformed numeric register comparison")
    if set(compiled) != {"texture", "sampler", "uav"}:
        raise ValueError("Unexpected DXBC declaration categories")
    decl = {}
    for category in ("texture", "sampler", "uav"):
        obj = compiled[category]
        if not isinstance(obj, dict) or len(obj) > MAX_ROWS:
            raise ValueError("Malformed DXBC declared register set")
        for slot, control in obj.items():
            if (type(slot) is not int or not 0 <= slot <= MAX_INDEX or
                    type(control) is not int or not 0 <= control <= 255):
                raise ValueError("Invalid DXBC register/control")
        decl[category] = set(obj)
    seen = set()
    sampler_present = set()
    sampler_missing = 0
    pairs = []
    for row in rows:
        if (not isinstance(row, dict) or
                set(row) != {"original_texture_index", "original_sampler_index"}):
            raise ValueError("Unexpected source texture field or private symbol")
        texture, sampler = (row["original_texture_index"],
                            row["original_sampler_index"])
        if (type(texture) is not int or not 0 <= texture <= MAX_INDEX or
                type(sampler) is not int or not -1 <= sampler <= MAX_INDEX or
                texture in seen):
            raise ValueError("Duplicate/invalid source texture register candidate")
        seen.add(texture)
        if sampler < 0:
            sampler_missing += 1
        else:
            sampler_present.add(sampler)
        pairs.append({
            "source_texture_index": texture,
            "source_sampler_index": sampler,
            "texture_register_declared_in_original_dxbc": texture in decl["texture"],
            "sampler_register_declared_in_original_dxbc": (
                None if sampler == -1 else sampler in decl["sampler"]),
        })
    pairs.sort(key=lambda x: x["source_texture_index"])
    texture_parity = seen == decl["texture"]
    # A negative/unknown m_SamplerIndex is explicitly not proof of sN.
    sampler_parity = (sampler_missing == 0 and
                      sampler_present == decl["sampler"])
    return {
        "original_source_texture_rows": len(rows),
        "original_source_sampler_minus_one_rows": sampler_missing,
        "original_source_unique_t_indices": sorted(seen),
        "original_source_nonnegative_s_indices": sorted(sampler_present),
        "native_dxbc_declared_t_indices": sorted(decl["texture"]),
        "native_dxbc_declared_s_indices": sorted(decl["sampler"]),
        "native_dxbc_declared_uav_indices": sorted(decl["uav"]),
        "native_dxbc_sampler_modes": sorted(int(x) for x in compiled["sampler"].values()),
        "individual_numeric_candidate_rows": pairs,
        "original_texture_t_register_set_equal_native_dxbc": texture_parity,
        "original_texture_sampler_s_register_set_equal_native_dxbc": sampler_parity,
        "complete_source_texture_sampler_to_dxbc_register_set_parity": (
            texture_parity and sampler_parity and not decl["uav"]),
        "original_dxbc_instruction_t_s_pair_use_verified": False,
        "native_dxbc_to_translated_spirv_binding_identity_verified": False,
        "unity_material_texture_property_upload_verified": False,
        "shaderlab_import_or_device_pixels_verified": False,
        "private_shader_names_or_binaries_disclosed": False,
    }


def original_stage_numeric_audit(source):
    source = Path(source).absolute()
    path = source / OWNER
    if (not source.is_dir() or not _physical(source)
            or not path.is_file() or not _physical(path)
            or fingerprint(path) != PINS[OWNER]):
        raise ValueError("Original ZIP2 Foam owner SHA/bytes prerequisite failed")
    import UnityPy
    env = UnityPy.load(str(path))
    objs = [obj for obj in env.file.objects.values()
            if obj.type.name == "Shader" and int(obj.path_id) == OBJECT_ID]
    if len(objs) != 1:
        raise ValueError("Original Foam Shader object missing or ambiguous")
    if hashlib.sha256(objs[0].get_raw_data()).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original Foam Shader object fingerprint mismatch")
    tree = objs[0].read_typetree()
    parsed = tree.get("m_ParsedForm")
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original Foam parsed Shader identity absent")
    attest = attest_name_registry(parsed)
    if (attest.get("original_passes") != 2 or
            attest.get("authenticated_stage_count") != 4 or
            attest.get("matched_constant_buffer_bindings") != 8):
        raise ValueError("Original name registry/stage authentication absent")
    tables = [records(parts) for platform, parts in decoded_platforms(tree)
              if platform == 4]
    if len(tables) != 1:
        raise ValueError("Original Foam D3D11 compiled table unavailable")
    entries = tables[0]
    passes = parsed["m_SubShaders"][0]["m_Passes"]
    stages = []
    for pi, stage in STAGES:
        program = passes[pi]["progVertex" if stage == 1 else "progFragment"]
        metadata, _ = validate_stage(program, stage, {"original_pass": pi})
        original_dxbc, _ = linked_program(metadata, entries, stage)
        if (hashlib.sha256(original_dxbc).hexdigest()
                != ORIGINAL_STAGE_SHA[(pi, stage)]):
            raise ValueError("Original D3D11 shader stage SHA changed")
        declared = compiled_declarations(original_dxbc, stage)
        numeric = source_texture_registers(
            program, ORIGINAL_TEXTURES_PER_STAGE[(pi, stage)])
        result = compare_numeric_dxbc(numeric, declared)
        stages.append({"pass": pi, "stage_code": stage,
                       "exact_original_dxbc_sha_attested": True, **result})
    if len(stages) != 4 or sum(x["original_source_texture_rows"] for x in stages) != 6:
        raise ValueError("Original Foam source stage coverage incomplete")
    return {
        "status": "foam_original_source_to_native_dxbc_numeric_registers_audited",
        "source_original_owner_sha256": PINS[OWNER][1],
        "original_shader_raw_object_sha256": ORIGINAL_OBJECT_SHA256,
        "original_stages": 4,
        "original_textures": 6,
        "source_to_dxbc_t_register_stages_equal": sum(
            x["original_texture_t_register_set_equal_native_dxbc"] for x in stages),
        "source_to_dxbc_s_register_stages_equal": sum(
            x["original_texture_sampler_s_register_set_equal_native_dxbc"] for x in stages),
        "stages": stages,
        "original_dxbc_sample_instruction_pair_join_verified": False,
        "dxbc_to_spirv_descriptor_mapping_verified": False,
        "unity_material_upload_or_device_verified": False,
        "private_program_or_shader_names_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        out = args.out.absolute()
        source = args.source.absolute()
        if (out.exists() or not out.parent.is_dir() or not _physical(out)
                or out.is_relative_to(source)):
            raise ValueError("Unsafe original Foam numeric report output path")
        result = original_stage_numeric_audit(source)
        out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
        print("T2_FOAM_NATIVE_DXBC " + json.dumps({
            "status": result["status"], "source_stages": result["original_stages"],
            "original_textures": result["original_textures"],
            "t_register_parity_stages": result["source_to_dxbc_t_register_stages_equal"],
            "s_register_parity_stages": result["source_to_dxbc_s_register_stages_equal"],
            "unity_or_device_verified": False, "private_shader_published": False,
        }))
        return 0
    except BaseException as exc:
        # Never put private shader names, file paths, or DXBC in logs.
        print("T2_FOAM_NATIVE_DXBC " + json.dumps({
            "status": "blocked", "reason_class": type(exc).__name__,
            "original_to_material_verified": False, "private_shader_published": False,
        }))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
