"""B17 WATER-001: source-authentic Spectrum DXBC/Unity numeric register parity.

No original bytecode, proprietary names, shader source or asset bytes are emitted.
Numeric register agreement is not a ShaderLab/Unity/Adreno or pixel guarantee.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from scripts.probe_directx_shader_bridge import inspect_dxbc
from scripts.b09_stage_original_spectrum import _selected_original, _variant_key
from scripts.w1_recover_depth_passes import linked_program, stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.verify_targeted_lfs_compute_sources import verify_sources, EXPECTED

OWNER = "sharedassets0.assets"
STAGES = {"progVertex": 1, "progFragment": 0}
DECLARATIONS = {88: ("texture", 7, 4), 90: ("sampler", 6, 3),
                156: ("uav", 30, 4)}
UNSUPPORTED_RESOURCES = {157, 158, 161, 162}
SLOTS = {"texture": ("m_TextureParams", "m_TextureParameters"),
         "sampler": ("m_SamplerParams", "m_SamplerParameters"),
         "uav": ("m_UAVParams", "m_UAVParameters")}
MAX_SLOTS = 256


def _bounded_slot(value):
    if type(value) is not int or not 0 <= value <= MAX_SLOTS:
        raise ValueError("Unbounded or noninteger resource register")
    return value


def compiled_declarations(data: bytes, stage: int) -> dict:
    """Decode executable SM4/5 dcl_resource/dcl_sampler/dcl_uav_typed only."""
    inspect_dxbc(data)
    offsets = struct.unpack_from("<" + "I" * struct.unpack_from("<I", data, 28)[0], data, 32)
    executable = []
    for start in offsets:
        length = struct.unpack_from("<I", data, start + 4)[0]
        if data[start:start + 4] in (b"SHEX", b"SHDR"):
            executable.append(data[start + 8:start + 8 + length])
    if len(executable) != 1 or len(executable[0]) % 4 or len(executable[0]) < 8:
        raise ValueError("Unique aligned executable shader stage required")
    words = struct.unpack("<" + "I" * (len(executable[0]) // 4), executable[0])
    if (words[1] != len(words) or (words[0] >> 16) != stage or
            ((words[0] >> 4) & 15) not in (4, 5)):
        raise ValueError("Compiled shader stage/version/length mismatch")
    result = {kind: {} for kind in SLOTS}
    pos = 2
    while pos < len(words):
        opcode = words[pos]
        op = opcode & 0x7ff
        width = (words[pos + 1] if op == 53 and pos + 1 < len(words)
                 else (opcode >> 24) & 0x7f)
        if width < (2 if op == 53 else 1) or pos + width > len(words):
            raise ValueError("Invalid executable instruction boundary")
        if op in UNSUPPORTED_RESOURCES:
            raise ValueError("Unsupported compiled resource declaration")
        if op in DECLARATIONS:
            kind, operand_type, required_width = DECLARATIONS[op]
            if width != required_width or opcode >> 31:
                raise ValueError("Unexpected resource declaration encoding")
            operand = words[pos + 1]
            if (operand >> 31 or ((operand >> 12) & 255) != operand_type or
                    ((operand >> 20) & 3) != 1 or ((operand >> 22) & 7) != 0):
                raise ValueError("Unsupported register indexing declaration")
            slot = _bounded_slot(words[pos + 2])
            if slot in result[kind]:
                raise ValueError("Duplicate compiled resource register")
            control = (opcode >> 11) & (15 if kind == "sampler" else 31)
            if kind == "sampler" and control not in (0, 1, 2):
                raise ValueError("Invalid compiled sampler mode")
            if kind != "sampler" and control == 0:
                raise ValueError("Invalid compiled texture/UAV dimension")
            result[kind][slot] = control
        pos += width
    return result


def serialized_slots(program: dict) -> dict:
    """Read original Unity index rows, plus texture-associated sampler slots."""
    common = program.get("m_CommonParameters") if isinstance(program, dict) else None
    if not isinstance(common, dict):
        raise ValueError("Missing original Unity common resource metadata")
    result = {kind: set() for kind in SLOTS}
    implicit_samplers = set()
    for kind, aliases in SLOTS.items():
        hits = [key for key in aliases if key in common]
        if len(hits) != 1:
            raise ValueError("Missing or ambiguous serialized resource table")
        entries = common[hits[0]]
        if not isinstance(entries, list) or len(entries) > MAX_SLOTS:
            raise ValueError("Malformed serialized resource rows")
        for item in entries:
            if not isinstance(item, dict):
                raise ValueError("Malformed serialized resource entry")
            index = _bounded_slot(item.get("m_Index"))
            if index in result[kind]:
                raise ValueError("Duplicate serialized resource slot")
            result[kind].add(index)
            if kind == "texture" and "m_SamplerIndex" in item:
                sampler = item["m_SamplerIndex"]
                if type(sampler) is not int or sampler < -1:
                    raise ValueError("Invalid original texture sampler index")
                if 0 <= sampler < 65535:
                    implicit_samplers.add(_bounded_slot(sampler))
    result["sampler"].update(implicit_samplers)
    return result


def compare_program(program: dict, compiled: bytes, stage: int) -> dict:
    declared = compiled_declarations(compiled, stage)
    serialized = serialized_slots(program)
    return {
        "stage": stage,
        "compiled_counts": {k: len(declared[k]) for k in SLOTS},
        "serialized_counts": {k: len(serialized[k]) for k in SLOTS},
        "numeric_slot_parity": {k: set(declared[k]) == serialized[k] for k in SLOTS},
        "compiled_sampler_modes": sorted(declared["sampler"].values()),
        "names_or_material_sampler_states_verified": False,
    }


def inspect(source: Path) -> dict:
    if source.is_symlink() or not source.is_dir() or (source / OWNER).is_symlink():
        raise ValueError("Unsafe original source path")
    verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    _, object_sha, tree, attestation = _selected_original(source)
    tables = [(plat, records(chunks)) for plat, chunks in decoded_platforms(tree) if plat == 4]
    if len(tables) != 1:
        raise ValueError("Missing unique pinned original D3D11 platform")
    entries = tables[0][1]
    passes = tree["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"]
    if len(passes) != 7:
        raise ValueError("Pinned original Spectrum passes drifted")
    per_pass = []
    parity_all = True
    for index, shader_pass in enumerate(passes):
        by_stage = {}
        for name, stage in STAGES.items():
            program = shader_pass.get(name)
            if not isinstance(program, dict):
                raise ValueError("Missing original program stage")
            rows = {}
            for _, _, meta in stage_variants(program):
                key = _variant_key(meta)
                if key in rows:
                    raise ValueError("Duplicated source variant permutation")
                code, link = linked_program(meta, entries, stage)
                row = compare_program(program, code, stage)
                row["original_blob_index"] = link["blob_index"]
                rows[key] = row
            if len(rows) != 2:
                raise ValueError("Original stage permutation count drifted")
            by_stage[name] = rows
        if by_stage["progVertex"].keys() != by_stage["progFragment"].keys():
            raise ValueError("Unpaired original Spectrum permutation keys")
        samples = []
        for key in sorted(by_stage["progVertex"]):
            v, f = by_stage["progVertex"][key], by_stage["progFragment"][key]
            parity_all &= all(v["numeric_slot_parity"].values()) and all(f["numeric_slot_parity"].values())
            samples.append({
                "permutation_sha256": hashlib.sha256(key.encode("utf-8")).hexdigest(),
                "vertex": v, "fragment": f,
            })
        per_pass.append({"index": index, "variants": samples})
    return {
        "source_verified": True, "original_object_sha256": object_sha,
        "verified_original_topology": attestation["authenticated_original_passes"],
        "original_passes": len(per_pass),
        "program_pairs": sum(len(p["variants"]) for p in per_pass),
        "compiled_vs_serialized_numeric_register_parity": parity_all,
        "per_pass_numeric_evidence": per_pass,
        "original_program_names_verified": False,
        "shaderlab_reconstructed": False, "unity_import_or_device_verified": False,
        "original_program_bytes_disclosed": False, "ready_for_build": False,
    }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    args = cli.parse_args()
    try:
        report = inspect(args.source)
        if args.out.exists() or args.out.is_symlink():
            raise ValueError("Refuse to overwrite report")
        args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("RAFT_B17_COMPILED_BINDINGS " + json.dumps({
            "source_verified": True, "passes": report["original_passes"],
            "pairs": report["program_pairs"],
            "numeric_slot_parity": report["compiled_vs_serialized_numeric_register_parity"],
            "game_assets_modified": False, "device_verified": False}, sort_keys=True))
        return 0 if report["compiled_vs_serialized_numeric_register_parity"] else 3
    except (ValueError, TypeError, KeyError, OSError, struct.error) as error:
        # Only fixed, source-free parser diagnostics. Never display unknown
        # serializer metadata, program strings, paths or exception tracebacks.
        safe_codes = {
            "Unbounded or noninteger resource register": "BAD_SLOT",
            "Unique aligned executable shader stage required": "EXEC_STAGE",
            "Compiled shader stage/version/length mismatch": "EXEC_VERSION",
            "Invalid executable instruction boundary": "EXEC_BOUNDARY",
            "Unsupported compiled resource declaration": "EXEC_EXTRA_RESOURCE",
            "Unexpected resource declaration encoding": "EXEC_DECLARATION",
            "Unsupported register indexing declaration": "EXEC_INDEX_FORM",
            "Duplicate compiled resource register": "EXEC_DUPLICATE",
            "Invalid compiled sampler mode": "EXEC_SAMPLER_MODE",
            "Invalid compiled texture/UAV dimension": "EXEC_DIMENSION",
            "Missing original Unity common resource metadata": "UNITY_COMMON",
            "Missing or ambiguous serialized resource table": "UNITY_TABLE",
            "Malformed serialized resource rows": "UNITY_ROWS",
            "Malformed serialized resource entry": "UNITY_ROW",
            "Duplicate serialized resource slot": "UNITY_DUPLICATE",
            "Invalid original texture sampler index": "UNITY_SAMPLER",
            "Unsafe original source path": "SOURCE_PATH",
            "Missing unique pinned original D3D11 platform": "SOURCE_PLATFORM",
            "Pinned original Spectrum passes drifted": "SOURCE_PASSES",
            "Missing original program stage": "SOURCE_STAGE",
            "Duplicated source variant permutation": "SOURCE_VARIANT_DUPLICATE",
            "Original stage permutation count drifted": "SOURCE_VARIANT_COUNT",
            "Unpaired original Spectrum permutation keys": "SOURCE_PAIRING",
            "Refuse to overwrite report": "REPORT_EXISTS",
        }
        print("RAFT_B17_COMPILED_BINDINGS " + json.dumps({
            "status": "REJECTED",
            "reason_code": safe_codes.get(str(error), "UPSTREAM_OR_UNMODELED"),
            "exception_class": type(error).__name__,
            "private_content_disclosed": False,
            "numeric_register_parity_verified": False}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
