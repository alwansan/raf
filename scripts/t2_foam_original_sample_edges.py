"""T2 WATER-001: authentic original Foam executable DXBC SAMPLE t/s uses.

Independent of declared resource cardinality: parse original D3D11 executable
SHEX/SHDR and inspect actual opcode69 SAMPLE tN/sM operands. Reuse the
existing inherited Blur operand decoder and native source-authenticated Foam
stage pins. Unknown SAMPLE variants are explicitly counted, never interpreted
as matching source rows; no private shaders, symbols, or bytes are emitted.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from scripts.blur_cb_instruction import operand
from scripts.blur_sample_operands import sample as inherited_sample
from scripts.probe_directx_shader_bridge import inspect_dxbc
from scripts.b20_private_foam_packet import ORIGINAL_STAGE_SHA
from scripts.b24_original_foam_stage_translation import (
    OWNER, OBJECT_ID, ORIGINAL_OBJECT_SHA256, TARGET, validate_stage,
)
from scripts.b25_foam_cb_namebridge import inspect_parsed as inspect_original_names
from scripts.b17_spectrum_compiled_bindings import compiled_declarations
from scripts.t2_foam_original_dxbc_registers import (
    source_texture_registers, compare_numeric_dxbc,
)
from scripts.t2_foam_member_abi import STAGES, _physical
from scripts.t2_foam_resource_abi import ORIGINAL_TEXTURES_PER_STAGE
from scripts.w1_recover_depth_passes import linked_program
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_stage_zip2_owners import PINS, fingerprint

MAX_OPS = 100_000
MAX_INDEX = 255
SAMPLE_CODE = 69
UNSUPPORTED_SAMPLE_VARIANTS = frozenset((70, 71, 72, 73, 74))


def original_dx_sample_pair(words, expected_rows):
    """Decode exactly one direct SAMPLE call and verify original t/s row owner."""
    if not isinstance(words, (list, tuple)) or len(words) < 2:
        raise ValueError("Invalid original DXBC sample instruction")
    # Independent inherited parser rejects dynamic, wrong roles, unexpected
    # trailing words and ambiguous original texture+sampler metadata rows.
    verdict = inherited_sample(words, expected_rows)
    if not verdict.get("unique_original_pair"):
        raise ValueError("Original DXBC SAMPLE has no unique source texture row")
    at = 1
    items = []
    for _ in range(4):
        item, at = operand(words, at)
        items.append(item)
    if at != len(words) or items[2]["type"] != 7 or items[3]["type"] != 6:
        raise ValueError("Unexpected DXBC sample operand count/roles")
    def register(item):
        if (item.get("modifier") or len(item.get("indices", [])) != 1
                or item["indices"][0]["relative"] is not None):
            raise ValueError("Original sample register dynamic or modified")
        reg = item["indices"][0]["immediate"]
        if type(reg) is not int or not 0 <= reg <= MAX_INDEX:
            raise ValueError("Original sample register invalid")
        return reg
    return register(items[2]), register(items[3])


def token_instruction_usage(words, stage, original_texture_rows):
    """Read executable token boundaries and observed opcode69 original t/s uses."""
    if (not isinstance(words, (list, tuple)) or len(words) < 2
            or len(words) > MAX_OPS * 32
            or any(type(w) is not int or not 0 <= w <= 0xffffffff for w in words)
            or type(stage) is not int or stage not in (0, 1)):
        raise ValueError("Bad native executable DXBC instruction stream")
    if (words[1] != len(words) or (words[0] >> 16) != stage
            or ((words[0] >> 4) & 15) not in (4, 5)):
        raise ValueError("Original DXBC stage/version/length altered")
    if not isinstance(original_texture_rows, list):
        raise ValueError("Original source texture rows absent")
    rows = [{"m_Index": x["original_texture_index"],
             "m_SamplerIndex": x["original_sampler_index"]}
            for x in original_texture_rows]
    pos, total, samples, unsupported = 2, 0, [], {}
    while pos < len(words):
        header = words[pos]
        opcode = header & 0x7ff
        width = (words[pos + 1] if opcode == 53 and pos + 1 < len(words)
                 else (header >> 24) & 0x7f)
        if (width < (2 if opcode == 53 else 1) or
                pos + width > len(words) or total >= MAX_OPS):
            raise ValueError("Invalid original DXBC instruction boundary")
        inst = words[pos:pos + width]
        if opcode == SAMPLE_CODE:
            samples.append(original_dx_sample_pair(inst, rows))
        elif opcode in UNSUPPORTED_SAMPLE_VARIANTS:
            unsupported[opcode] = unsupported.get(opcode, 0) + 1
        pos += width
        total += 1
    if pos != len(words):
        raise ValueError("Native executable instruction coverage incomplete")
    distinct = sorted(set(samples))
    source_pairs = {
        (x["original_texture_index"], x["original_sampler_index"])
        for x in original_texture_rows
    }
    return {
        "original_native_dxbc_instructions": total,
        "observed_opcode69_sample_calls": len(samples),
        "observed_unique_opcode69_t_s_pairs": [list(p) for p in distinct],
        "unhandled_sample_variant_counts": [
            {"opcode": k, "count": v} for k, v in sorted(unsupported.items())
        ],
        "original_source_numeric_pair_set": [list(p) for p in sorted(source_pairs)],
        "all_source_pairs_actively_used_proved": (
            set(distinct) == source_pairs and not unsupported
        ),
        "native_dxbc_to_spirv_compiled_binding_identity_verified": False,
        "original_material_upload_or_sampler_state_verified": False,
        "device_shaderlab_or_pixels_verified": False,
        "private_source_names_or_shader_bytes_disclosed": False,
    }


def executable_words(binary, stage):
    inspect_dxbc(binary)
    if type(stage) is not int or stage not in (0, 1):
        raise ValueError("Invalid executable stage")
    chunk_count = struct.unpack_from("<I", binary, 28)[0]
    offsets = struct.unpack_from("<" + "I" * chunk_count, binary, 32)
    found = []
    for off in offsets:
        size = struct.unpack_from("<I", binary, off + 4)[0]
        if binary[off:off + 4] in (b"SHEX", b"SHDR"):
            chunk = binary[off + 8:off + 8 + size]
            if len(chunk) < 8 or len(chunk) % 4:
                raise ValueError("Original native DXBC executable chunk incomplete")
            found.append(list(struct.unpack("<" + "I" * (len(chunk) // 4), chunk)))
    if len(found) != 1:
        raise ValueError("Original DXBC executable chunk missing/ambiguous")
    words = found[0]
    if (words[1] != len(words) or (words[0] >> 16) != stage
            or ((words[0] >> 4) & 15) not in (4, 5)):
        raise ValueError("Unexpected original DXBC stage")
    return words


def audit(source):
    source = Path(source).absolute()
    path = source / OWNER
    if (not source.is_dir() or not _physical(source)
            or not path.is_file() or not _physical(path)
            or fingerprint(path) != PINS[OWNER]):
        raise ValueError("Original Foam ZIP2 owner source SHA missing")
    import UnityPy
    env = UnityPy.load(str(path))
    objs = [o for o in env.file.objects.values()
            if o.type.name == "Shader" and int(o.path_id) == OBJECT_ID]
    if (len(objs) != 1 or
            hashlib.sha256(objs[0].get_raw_data()).hexdigest() != ORIGINAL_OBJECT_SHA256):
        raise ValueError("Original Foam raw object not authenticated")
    tree = objs[0].read_typetree()
    parsed = tree.get("m_ParsedForm")
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original Foam shader parsed identity absent")
    gate = inspect_original_names(parsed)
    if (gate.get("original_passes") != 2 or
            gate.get("authenticated_stage_count") != 4 or
            gate.get("matched_constant_buffer_bindings") != 8):
        raise ValueError("Original Foam name/stage identity unsupported")
    tables = [records(parts) for platform, parts in decoded_platforms(tree)
              if platform == 4]
    if len(tables) != 1:
        raise ValueError("Authentic D3D11 program table not unique")
    outputs = []
    passes = parsed["m_SubShaders"][0]["m_Passes"]
    for pi, stage in STAGES:
        prog = passes[pi]["progVertex" if stage == 1 else "progFragment"]
        metadata, _ = validate_stage(prog, stage, {"original_pass": pi})
        binary, _ = linked_program(metadata, tables[0], stage)
        if hashlib.sha256(binary).hexdigest() != ORIGINAL_STAGE_SHA[(pi, stage)]:
            raise ValueError("Actual native program SHA drift")
        orig = source_texture_registers(
            prog, ORIGINAL_TEXTURES_PER_STAGE[(pi, stage)])
        declared = compare_numeric_dxbc(
            orig, compiled_declarations(binary, stage))
        if not declared["complete_source_texture_sampler_to_dxbc_register_set_parity"]:
            raise ValueError("Original native texture/sampler declaration mismatch")
        usage = token_instruction_usage(executable_words(binary, stage), stage, orig)
        outputs.append({"pass": pi, "stage_code": stage, **usage})
    if (len(outputs) != 4 or
            sum(len(x["original_source_numeric_pair_set"]) for x in outputs) != 6):
        raise ValueError("Authenticated original executable stages not all processed")
    return {
        "status": "original_foam_native_dxbc_sample_instruction_uses_observed",
        "original_stages": 4,
        "original_sample69_calls": sum(x["observed_opcode69_sample_calls"] for x in outputs),
        "original_unique_sampled_pairs": sum(
            len(x["observed_unique_opcode69_t_s_pairs"]) for x in outputs),
        "original_stages_all_source_pairs_actively_used": sum(
            x["all_source_pairs_actively_used_proved"] for x in outputs),
        "stages": outputs,
        "source_to_translated_spirv_descriptor_join_verified": False,
        "unity_shaderlab_or_material_binding_verified": False,
        "adreno_pixels_verified": False,
        "private_binary_or_symbol_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    try:
        out = a.out.absolute()
        if (out.exists() or not out.parent.is_dir() or not _physical(out)
                or out.is_relative_to(a.source.absolute())):
            raise ValueError("Unsafe original sample-use aggregate output")
        r = audit(a.source)
        out.write_text(json.dumps(r, sort_keys=True) + "\n", encoding="utf-8")
        print("T2_NATIVE_SAMPLE_USE " + json.dumps({
            "status": r["status"], "original_stages": 4,
            "sample_calls": r["original_sample69_calls"],
            "unique_native_pairs": r["original_unique_sampled_pairs"],
            "unsupported_variants": sum(
                x["count"] for s in r["stages"]
                for x in s["unhandled_sample_variant_counts"]),
            "shaderlab_or_device_verified": False,
            "raw_shader_published": False,
        }))
        return 0
    except BaseException as exc:
        print("T2_NATIVE_SAMPLE_USE " + json.dumps({
            "status": "blocked", "error_type": type(exc).__name__,
            "original_to_spirv_binding_verified": False,
            "raw_shader_published": False,
        }))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
