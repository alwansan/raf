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


def compare(tree: dict) -> dict:
    rows = resource_rows(tree)
    kernels = tree["variants"][0]["kernels"]
    if len(rows) != len(kernels) or len(rows) != 20:
        raise ValueError("Original serialized compiled slot count changed")
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
        actual = compiled_binding_hashes(binaries[0])
        expected = {
            ("input", 0): row["source_image_name_sha256"],
            ("input", 1): row["butterfly_image_name_sha256"],
            ("output", 0): row["target_image_name_sha256"],
        }
        if actual != expected:
            raise ValueError("Compiled DXBC RDEF disagrees with original serialized Unity resource roles")
    return {
        "original_compiled_fft_rdef_slots_correlated": 20,
        "rdef_to_unity_t0_t1_u0_identity_matched": True,
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
