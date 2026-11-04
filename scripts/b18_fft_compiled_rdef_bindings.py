"""B18: SHA-authenticated original FFT typed metadata vs compiled DXBC RDEF binding parity.

No proprietary names or shader bytes are emitted. Serialized compiled slot is not
a Unity runtime FindKernel index, and reflection is not GPU/pixel proof.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from scripts.probe_directx_shader_bridge import inspect_dxbc, MAX_SHADER_BYTES
from scripts.probe_original_fft_resource_bindings import resource_rows
from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_fft_variant_table import (
    correlate_original_variant_bytecode, EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT,
)
from scripts.verify_targeted_lfs_compute_sources import EXPECTED as ORIGINAL_OWNERS, verify_sources
from scripts.probe_authentic_fft_dxbc_translation import OWNER, PATH_ID, ORIGINAL_OBJECT_SHA256

ROLE_KEYS = {("input", 0), ("input", 1), ("output", 0)}


def _rdef(data: bytes) -> bytes:
    inspect_dxbc(data)
    count = struct.unpack_from("<I", data, 28)[0]
    offsets = struct.unpack_from("<" + "I" * count, data, 32)
    chunks = []
    for off in offsets:
        if data[off:off + 4] == b"RDEF":
            size = struct.unpack_from("<I", data, off + 4)[0]
            chunks.append(data[off + 8:off + 8 + size])
    if len(chunks) != 1:
        raise ValueError("Original DXBC must contain exactly one RDEF")
    return chunks[0]


def compiled_binding_hashes(data: bytes) -> dict:
    """RDEF SM5 binding records: uint32[8], names only processed as hashes."""
    if not isinstance(data, bytes) or not 36 <= len(data) <= MAX_SHADER_BYTES:
        raise ValueError("Invalid compiled DXBC size")
    blob = _rdef(data)
    if len(blob) < 28:
        raise ValueError("Truncated RDEF")
    cb_count, _, count, begin = struct.unpack_from("<4I", blob)
    if cb_count != 0 or count != 3 or begin < 28 or begin + 32 * count > len(blob):
        raise ValueError("Unexpected compiled FFT binding table")
    entries = {}
    string_start = begin + 32 * count
    for n in range(count):
        name_off, kind, _, dimension, _, reg, bind_count, _ = struct.unpack_from("<8I", blob, begin + 32 * n)
        if kind not in (2, 4) or dimension != 4 or bind_count != 1 or reg > 1024:
            raise ValueError("Original DXBC image type/count/dimension/register differs")
        role = ("input" if kind == 2 else "output", reg)
        if role in entries:
            raise ValueError("Original DXBC resource register duplicated")
        if not string_start <= name_off < len(blob):
            raise ValueError("RDEF name pointer outside declared string region")
        end = blob.find(b"\x00", name_off, min(len(blob), name_off + 257))
        if end <= name_off:
            raise ValueError("RDEF name absent, invalid or unbounded")
        try:
            name = blob[name_off:end].decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValueError("RDEF name invalid encoding") from exc
        entries[role] = hashlib.sha256(name.encode("utf-8")).hexdigest()
    if set(entries) != ROLE_KEYS:
        raise ValueError("Compiled DXBC binding register layout changed")
    return entries



def compiled_shex_registers(data: bytes) -> tuple[dict, list]:
    """Read bounded executable SM5 DXBC dcl_resource/dcl_uav_typed declarations.

    Official D3D11 token format: opcodes 88, 156 and 155; operand types 7/30;
    Texture2D resource dimension 3. The instruction stream has no authored
    resource-name strings. Only numeric register ownership can be proven.
    """
    inspect_dxbc(data)
    chunks = []
    for off in struct.unpack_from("<" + "I" * struct.unpack_from("<I", data, 28)[0], data, 32):
        size = struct.unpack_from("<I", data, off + 4)[0]
        if data[off:off + 4] in (b"SHEX", b"SHDR"):
            chunks.append(data[off + 8:off + 8 + size])
    if len(chunks) != 1:
        raise ValueError("Exactly one tokenized DXBC executable chunk required")
    blob = chunks[0]
    if len(blob) < 8 or len(blob) % 4:
        raise ValueError("Invalid tokenized executable alignment")
    tokens = struct.unpack("<" + "I" * (len(blob) // 4), blob)
    if tokens[1] != len(tokens) or (tokens[0] >> 16) != 5 or (tokens[0] >> 4) & 0xf != 5:
        raise ValueError("Not a complete SM5 compute shader token stream")
    result = {}
    group = []
    offset = 2
    while offset < len(tokens):
        op = tokens[offset]
        code = op & 0x7ff
        width = tokens[offset + 1] if code == 53 and offset + 1 < len(tokens) else (op >> 24) & 0x7f
        # CustomData has its own DWORD count; unrelated instructions may carry
        # extended-opcode tokens and remain safely skippable by declared length.
        if width < (2 if code == 53 else 1) or offset + width > len(tokens):
            raise ValueError("Unknown extended/invalid DXBC instruction")
        if code in (88, 156):
            if width != 4 or ((op >> 11) & 31) != 3:
                raise ValueError("Unexpected typed Texture2D declaration")
            operand = tokens[offset + 1]
            expected_type = 7 if code == 88 else 30
            if (operand >> 31 or ((operand >> 12) & 255) != expected_type
                    or ((operand >> 20) & 3) != 1 or ((operand >> 22) & 7) != 0):
                raise ValueError("Unrecognized DXBC resource operand representation")
            register = tokens[offset + 2]
            kind = "input" if code == 88 else "output"
            if register > 1024 or (kind, register) in result:
                raise ValueError("Duplicate/out-of-range DXBC declaration register")
            result[(kind, register)] = True
        elif code == 155:
            if width != 4 or group:
                raise ValueError("Ambiguous compute workgroup declaration")
            group = list(tokens[offset + 1:offset + 4])
        elif code in (89, 90, 157, 158, 161, 162):
            raise ValueError("Unexpected extra DXBC resource/sampler/CB declaration")
        offset += width
    if set(result) != ROLE_KEYS or not all(1 <= d <= 1024 for d in group):
        raise ValueError("Compiled DXBC declaration layout/workgroup incomplete")
    return result, group


def compiled_resource_evidence(data: bytes) -> tuple[dict, str, list | None]:
    """Prefer name-preserving RDEF; accept name-free executable declarations."""
    inspect_dxbc(data)
    tags = []
    for off in struct.unpack_from("<" + "I" * struct.unpack_from("<I", data, 28)[0], data, 32):
        tags.append(data[off:off + 4])
    rdef_count = tags.count(b"RDEF")
    if rdef_count > 1:
        raise ValueError("Ambiguous RDEF chunks cannot be bypassed")
    if rdef_count == 1:
        return compiled_binding_hashes(data), "rdef", None
    roles, group = compiled_shex_registers(data)
    return roles, "shex", group

def compare(tree: dict) -> dict:
    rows = resource_rows(tree)
    kernels = tree["variants"][0]["kernels"]
    if len(rows) != len(kernels) or len(rows) != 20:
        raise ValueError("Original serialized compiled slot count changed")
    rdef_count = 0
    shex_count = 0
    for row, kernel in zip(rows, kernels):
        vm = kernel.get("variantMap")
        if not isinstance(vm, list) or len(vm) != 1 or not isinstance(vm[0], (list, tuple)) or len(vm[0]) != 2:
            raise ValueError("Original typed program map invalid")
        fields = vm[0][1]
        if not isinstance(fields, dict):
            raise ValueError("Original typed program fields invalid")
        binaries = []
        for value in fields.values():
            if (isinstance(value, (tuple, list)) and 36 <= len(value) <= MAX_SHADER_BYTES
                    and all(type(v) is int and 0 <= v <= 255 for v in value[:4])
                    and bytes(value[:4]) == b"DXBC"):
                if not all(type(v) is int and 0 <= v <= 255 for v in value):
                    raise ValueError("Invalid original byte array")
                binaries.append(bytes(value))
        if len(binaries) != 1:
            raise ValueError("Ambiguous original per-slot DXBC")
        actual, mode, group = compiled_resource_evidence(binaries[0])
        if mode == "rdef":
            expected = {
                ("input", 0): row["source_image_name_sha256"],
                ("input", 1): row["butterfly_image_name_sha256"],
                ("output", 0): row["target_image_name_sha256"],
            }
            if actual != expected:
                raise ValueError("Compiled DXBC RDEF disagrees with original serialized Unity resource roles")
            rdef_count += 1
        else:
            # SHEX/SHDR declarations carry bind slots but NOT original names.
            # A match here must not be reported as an RDEF/name match.
            if set(actual) != ROLE_KEYS or group != row["workgroup_xyz"]:
                raise ValueError("Executable DXBC declarations disagree with original Unity metadata")
            shex_count += 1
    return {
        "original_compiled_fft_rdef_slots_correlated": rdef_count,
        "original_compiled_fft_shex_slots_correlated": shex_count,
        "rdef_to_unity_t0_t1_u0_identity_matched": rdef_count == 20,
        "shex_resource_registers_and_workgroup_match_unity_metadata": shex_count > 0,
        "compiled_resource_names_proven_from_binary_when_no_rdef": False,
        "runtime_unity_findkernel_slot_mapping_verified": False,
        "android_unity_import_verified": False,
        "android_device_pixels_verified": False,
        "private_names_or_bytecode_published": False,
    }


def inspect(root: Path) -> dict:
    verify_sources(root, expected={OWNER: ORIGINAL_OWNERS[OWNER]})
    import UnityPy
    env = UnityPy.load(str(root / OWNER))
    objs = [o for o in env.file.objects.values() if o.type.name == "ComputeShader" and int(o.path_id) == PATH_ID]
    if len(objs) != 1:
        raise ValueError("Original FFT object absent or ambiguous")
    raw = objs[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original FFT object authentication failed")
    typed = objs[0].read_typetree()
    authenticated = correlate_original_variant_bytecode(
        typed, scan_blob(raw)["valid_dxbc_containers"], EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT
    )
    if authenticated.get("authentic_compiled_variants_verified_in_original_order") != 20:
        raise ValueError("Compiled original DXBC order authentication failed")
    return {
        "original_object_sha256": ORIGINAL_OBJECT_SHA256,
        "pinned_zip2_commit": "15964ea8f246b6e076ce26b60931ee2e1a9a2385",
        **compare(typed),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    try:
        result = inspect(args.source)
    except (ValueError, TypeError, KeyError, OSError, struct.error) as exc:
        # Never log unknown exceptions or dynamic private names/paths.
        safe_codes = {
            "Original DXBC must contain exactly one RDEF": "RDEF_ABSENT_OR_DUPLICATE",
            "Truncated RDEF": "RDEF_TRUNCATED",
            "Unexpected compiled FFT binding table": "RDEF_TABLE_SHAPE",
            "Original DXBC image type/count/dimension/register differs": "RDEF_RESOURCE_TYPE_OR_DIMENSION",
            "Original DXBC resource register duplicated": "RDEF_DUPLICATE_REGISTER",
            "RDEF name pointer outside declared string region": "RDEF_NAME_OFFSET",
            "RDEF name absent, invalid or unbounded": "RDEF_NAME_UNTERMINATED",
            "RDEF name invalid encoding": "RDEF_NAME_ENCODING",
            "Compiled DXBC binding register layout changed": "RDEF_REGISTER_LAYOUT",
            "Compiled DXBC RDEF disagrees with original serialized Unity resource roles": "RDEF_UNITY_MISMATCH",
            "Ambiguous original per-slot DXBC": "ORIGINAL_DXBC_AMBIGUOUS",
            "Original FFT object authentication failed": "ORIGINAL_OBJECT_SHA",
            "Exactly one tokenized DXBC executable chunk required": "SHEX_ABSENT_OR_DUPLICATE",
            "Invalid tokenized executable alignment": "SHEX_ALIGNMENT",
            "Not a complete SM5 compute shader token stream": "SHEX_VERSION_OR_LENGTH",
            "Unknown extended/invalid DXBC instruction": "SHEX_INSTRUCTION_ENCODING",
            "Unexpected typed Texture2D declaration": "SHEX_DIMENSION_OR_LENGTH",
            "Unrecognized DXBC resource operand representation": "SHEX_OPERAND",
            "Duplicate/out-of-range DXBC declaration register": "SHEX_DUPLICATE_REGISTER",
            "Ambiguous compute workgroup declaration": "SHEX_THREAD_GROUP_DUPLICATE",
            "Unexpected extra DXBC resource/sampler/CB declaration": "SHEX_UNEXPECTED_EXTRA_RESOURCE",
            "Compiled DXBC declaration layout/workgroup incomplete": "SHEX_MISSING_RESOURCES_OR_GROUP",
            "Executable DXBC declarations disagree with original Unity metadata": "SHEX_SERIALIZED_MISMATCH",
            "Ambiguous RDEF chunks cannot be bypassed": "RDEF_DUPLICATE",
        }
        print("RAFT_B18_FFT_RDEF " + json.dumps({
            "status": "REJECTED",
            "reason_code": safe_codes.get(str(exc), type(exc).__name__),
            "original_parity_proven": False,
        }, sort_keys=True))
        return 2
    print("RAFT_B18_FFT_RDEF " + json.dumps({"status": "PASS", **result}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
