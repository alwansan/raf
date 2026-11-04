"""B17: privately restore Spectrum fragment texture/sampler names from original Unity.

Checks source DXBC numeric ABI first. No original names, HLSL or binary bytes
leave the temporary runner. Never claims CB names, ShaderLab or device parity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.b09_stage_original_spectrum import _selected_original
from scripts.b17_spectrum_compiled_bindings import compare_program, serialized_slots
from scripts.verify_targeted_lfs_compute_sources import verify_sources, EXPECTED
from scripts.w1_rebind_depth_resources import rebind
from scripts.w1_recover_depth_passes import linked_program, stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate

OWNER = "sharedassets0.assets"


def rebind_resource_symbols(hlsl, program, names):
    """Only rebind original indexed texture and associated sampler symbols."""
    if not isinstance(hlsl, str) or not 0 < len(hlsl) <= 1024 * 1024 or "\x00" in hlsl:
        raise ValueError("Unbounded translated HLSL input")
    common = program.get("m_CommonParameters") if isinstance(program, dict) else None
    if not isinstance(common, dict) or not isinstance(names, list):
        raise ValueError("Missing original per-stage resource names")
    if "m_TextureParams" not in common or not isinstance(common["m_TextureParams"], list):
        raise ValueError("Missing original texture property slots")
    original_slots = serialized_slots(program)
    associated_sampler_slots = set()
    for row in common["m_TextureParams"]:
        if not isinstance(row, dict):
            raise ValueError("Unexpected original texture property")
        sampler = row.get("m_SamplerIndex", 65535)
        if type(sampler) is int and 0 <= sampler < 65535:
            associated_sampler_slots.add(sampler)
    if associated_sampler_slots != original_slots["sampler"]:
        raise ValueError("Explicit original sampler cannot be named by texture association")
    # W1's prior rebinder supports source-indexed texture/sampler names but
    # rejects CBs. Scope to the *texture metadata only*; never alter the
    # original CB source or assert its names have been restored.
    scoped = {"m_CommonParameters": {"m_TextureParams": common["m_TextureParams"]}}
    try:
        renamed, counts = rebind(hlsl, scoped, names)
    except (KeyError, IndexError):
        raise ValueError("Original shader name index unresolved") from None
    if (counts["textures_rebound"] != len(original_slots["texture"]) or
            counts["samplers_rebound"] != len(original_slots["sampler"])):
        raise ValueError("Original per-stage symbol mapping incomplete")
    return renamed, {
        "renamed_textures": counts["textures_rebound"],
        "renamed_samplers": counts["samplers_rebound"],
        "original_cb_names_restored": False,
        "original_sampler_modes_verified": False,
        "original_name_values_disclosed": False,
    }


def inspect(source: Path) -> dict:
    if source.is_symlink() or not source.is_dir() or (source / OWNER).is_symlink():
        raise ValueError("Unsafe source root")
    verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    _, original_object_sha, tree, topology = _selected_original(source)
    tables = [(p, records(parts)) for p, parts in decoded_platforms(tree) if p == 4]
    if len(tables) != 1:
        raise ValueError("Missing source D3D11 platform")
    shader_pass = tree["m_ParsedForm"]["m_SubShaders"][0]["m_Passes"][0]
    program = shader_pass["progFragment"]
    variants = stage_variants(program)
    if len(variants) != 2:
        raise ValueError("Original Spectrum pass fragment variants changed")
    code, link = linked_program(variants[0][2], tables[0][1], 0)
    abi = compare_program(program, code, 0)
    if not all(abi["numeric_slot_parity"].values()):
        raise ValueError("Source executable register ABI differs from Unity metadata")
    # Authenticate/translate only ONE representative original fragment.
    with tempfile.TemporaryDirectory(prefix="b17-spectrum-private-hlsl-") as tmp:
        folder = Path(tmp)
        translated = translate(code, 0, folder)
        if not all(translated.get(x) for x in (
                "vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid")):
            raise ValueError("Private original source translation rejected")
        hlsl = (folder / "private.hlsl").read_text(encoding="utf-8")
        renamed, counts = rebind_resource_symbols(hlsl, program, shader_pass["m_NameIndices"])
        candidate = folder / "source-name-rebound.hlsl"
        target = folder / "source-name-rebound.spv"
        candidate.write_text(renamed, encoding="utf-8")
        for command in (
            ["glslangValidator", "-V", "-D", "-S", "frag", "-e", "main",
             "-o", str(target), str(candidate)],
            ["spirv-val", "--target-env", "vulkan1.1", str(target)],
        ):
            result = subprocess.run(command, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL, timeout=60, check=False)
            if result.returncode:
                raise ValueError("Rebound private HLSL Vulkan1.1 compilation failed")
        return {
            "original_owner_sha256": EXPECTED[OWNER][1],
            "original_object_sha256": original_object_sha,
            "original_passes_attested": topology["authenticated_original_passes"],
            "verified_private_original_fragment_blob_index": link["blob_index"],
            "source_compiled_numeric_register_parity": True,
            "private_symbol_bridge": counts,
            "rebound_hlsl_sha256": hashlib.sha256(renamed.encode("utf-8")).hexdigest(),
            "private_rebound_vulkan11_valid": True,
            "original_names_or_hlsl_disclosed": False,
            "complete_spectrum_shaderlab_or_device_verified": False,
        }


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", required=True, type=Path)
    cli.add_argument("--out", required=True, type=Path)
    args = cli.parse_args()
    try:
        report = inspect(args.source)
        if args.out.exists() or args.out.is_symlink():
            raise ValueError("Output exists")
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print("RAFT_B17_HLSL_NAMEBRIDGE " + json.dumps({
            "status": "PRIVATE_ONE_FRAGMENT_SOURCE_REBOUND",
            "numeric_parity": True,
            "translated_hlsl_recompiled_vulkan11": True,
            "original_names_disclosed": False,
            "unity_or_android_verified": False}, sort_keys=True))
        return 0
    except (ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired):
        print("RAFT_B17_HLSL_NAMEBRIDGE " + json.dumps({
            "status": "REJECTED", "source_or_names_disclosed": False,
            "shaderlab_or_device_verified": False}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
