"""B20 read-only original Foam SPIR-V/HLSL numeric CB descriptor probe.

All SPIR-V, HLSL, names and shader bytes stay private. Even numeric slot
coincidence is NOT an authenticated Unity CB0 identifier or runtime upload.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from scripts.b20_private_foam_packet import (
    ORIGINAL_OBJECT_SHA256, ORIGINAL_STAGE_SHA, _physical,
)

# B25 source-confirmed original Unity serialized partial CB registers.
SOURCE_SLOTS = {(0, 1): (0, 1, 2), (0, 0): (0,),
                (1, 1): (0, 1, 2), (1, 0): (0,)}
MAX_HLSL = 1024 * 1024
LEXICAL = re.compile(r'//[^\r\n]*|/\*[\s\S]*?(?:\*/|$)|"(?:\\.|[^"\\])*"')
HLSL_CBUFFER = re.compile(
    r'\bcbuffer\s+[A-Za-z_]\w*\s*:\s*register\s*\(\s*b(\d+)'
    r'(?:\s*,\s*space\d+)?\s*\)\s*\{'
)


def hlsl_cb_slots(body):
    """Only explicit registered cbuffer declarations count; no guessed names."""
    if not isinstance(body, str) or not 0 < len(body.encode("utf-8")) <= MAX_HLSL:
        raise ValueError("Unsafe translated HLSL size")
    masked = LEXICAL.sub(lambda m: re.sub(r"[^\r\n]", " ", m.group()), body)
    slots = [int(m.group(1)) for m in HLSL_CBUFFER.finditer(masked)]
    if any(slot > 31 for slot in slots) or len(set(slots)) != len(slots):
        raise ValueError("Duplicate/unsupported translated HLSL CB registers")
    return tuple(sorted(slots))


def reflected_ubos(reflection):
    """Normalize numeric SPIRV-Cross UBO reflection, never print opaque names."""
    if not isinstance(reflection, dict):
        raise ValueError("Malformed SPIR-V reflection")
    rows = reflection.get("ubos", [])
    if not isinstance(rows, list) or len(rows) > 16:
        raise ValueError("Unbounded translated UBO declarations")
    result = []
    seen = set()
    for obj in rows:
        if not isinstance(obj, dict):
            raise ValueError("Unknown translated UBO row")
        dset, binding, size = (obj.get("set"), obj.get("binding"), obj.get("block_size"))
        if (any(type(v) is not int for v in (dset, binding, size))
                or not 0 <= dset <= 15 or not 0 <= binding <= 31
                or not 0 <= size <= 65536 or (dset, binding) in seen):
            raise ValueError("Ambiguous SPIR-V UBO descriptor")
        seen.add((dset, binding))
        result.append({"set": dset, "binding": binding, "bytes": size})
    return sorted(result, key=lambda x: (x["set"], x["binding"]))


def analyze_pair(hlsl, reflection, *, expected_slots):
    hlsl_slots = hlsl_cb_slots(hlsl)
    ubos = reflected_ubos(reflection)
    spv_slots = tuple(sorted(row["binding"] for row in ubos if row["set"] == 0))
    all_set_zero = all(row["set"] == 0 for row in ubos)
    return {
        "original_source_cb_slots": list(expected_slots),
        "hlsl_explicit_cbuffer_b_slots": list(hlsl_slots),
        "spirv_reflected_ubos": ubos,
        "hlsl_source_slot_set_coincides": hlsl_slots == expected_slots,
        "spirv_set0_binding_set_coincides": all_set_zero and spv_slots == expected_slots,
        "original_name_to_hlsl_cb0_identifier_verified": False,
        "unity_original_constant_buffer_upload_verified": False,
    }


def reflect(spv):
    try:
        proc = subprocess.run(
            ["spirv-cross", str(spv), "--reflect"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, check=False, timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Private SPIR-V reflection tool failed") from None
    if proc.returncode or len(proc.stdout) > 1024 * 1024:
        raise ValueError("Private SPIR-V reflection failed/budget exceeded")
    try:
        return json.loads(proc.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed private reflection JSON") from None


def probe(packet, manifest):
    packet, manifest = Path(packet).absolute(), Path(manifest).absolute()
    if (not _physical(packet) or not _physical(manifest)
            or not packet.is_dir() or not manifest.is_file()
            or manifest.is_relative_to(packet) or manifest.stat().st_size > 65536):
        raise ValueError("Unsafe input packet or safe manifest")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if (data.get("status") != "private_two_pass_inputs_staged"
            or data.get("original_object_sha256") != ORIGINAL_OBJECT_SHA256
            or data.get("original_stage_programs") != 4
            or data.get("original_cb_name_slot_links_verified") != 8
            or data.get("opaque_cb0_aliases_still_require_authentication") != 4
            or data.get("private_original_program_published") is not False
            or data.get("shaderlab_constructed") is not False):
        raise ValueError("Foam source-authentic packet attestation missing")
    records = data.get("stage_hashes")
    if not isinstance(records, list) or len(records) != 4:
        raise ValueError("Original Foam HLSL stage packet manifest incomplete")
    results = []
    for i, item in enumerate(records):
        key = (i // 2, 1 if i % 2 == 0 else 0)
        if (not isinstance(item, dict)
                or (item.get("pass"), item.get("stage_code")) != key
                or item.get("original_dxbc_sha256") != ORIGINAL_STAGE_SHA[key]):
            raise ValueError("Original stage SHA/order changed")
        folder = packet / ("pass%d-stage%d" % key)
        hlsl, spv = folder / "private.hlsl", folder / "original.spv"
        if (not _physical(hlsl) or not _physical(spv)
                or not hlsl.is_file() or not spv.is_file()
                or not 0 < hlsl.stat().st_size <= MAX_HLSL
                or not 0 < spv.stat().st_size <= MAX_HLSL):
            raise ValueError("Original translated private stage source missing")
        content = hlsl.read_bytes()
        if (item.get("hlsl_bytes") != len(content)
                or item.get("hlsl_sha256") != hashlib.sha256(content).hexdigest()):
            raise ValueError("Private HLSL source digest changed since staging")
        row = analyze_pair(content.decode("utf-8"), reflect(spv),
                           expected_slots=SOURCE_SLOTS[key])
        results.append({"pass": key[0], "stage_code": key[1], **row})
    return {
        "status": "genuine_foam_cb_reflection_observed",
        "authenticated_original_foam_stage_count": 4,
        "original_source_cb_links": 8,
        "all_hlsl_b_slots_numerically_coincide": all(
            x["hlsl_source_slot_set_coincides"] for x in results),
        "all_spirv_set0_bindings_numerically_coincide": all(
            x["spirv_set0_binding_set_coincides"] for x in results),
        "stages": results,
        "original_cb0_name_to_hlsl_alias_verified": False,
        "original_material_constant_buffer_upload_verified": False,
        "unity_or_device_pixels_verified": False,
        "private_hlsl_spirv_names_or_binaries_published": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    try:
        output = Path(args.out).absolute()
        if (not _physical(output) or output.exists() or not output.parent.is_dir()
                or output.is_relative_to(Path(args.packet).absolute())):
            raise ValueError("Unsafe safe report location")
        result = probe(args.packet, args.manifest)
        output.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
        print("B20_FOAM_CB_LINEAGE " + json.dumps({
            "status": result["status"],
            "source_authentic_stages": 4,
            "all_hlsl_numeric_slot_candidates": result["all_hlsl_b_slots_numerically_coincide"],
            "all_spirv_numeric_slot_candidates": result["all_spirv_set0_bindings_numerically_coincide"],
            "cb0_alias_verified": False, "unity_device_verified": False}))
        return 0
    except BaseException as exc:
        print("B20_FOAM_CB_LINEAGE " + json.dumps({
            "status": "blocked", "failure_type": type(exc).__name__,
            "cb0_alias_verified": False, "private_code_published": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
