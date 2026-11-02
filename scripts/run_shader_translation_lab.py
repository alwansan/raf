"""No-Unity, no-LFS shader translation exercise on authored synthetic code.

This deliberately does NOT run or package the Windows game, invoke DXVK/FEX,
decode commercial shaders, launch Vulkan on a GPU or change Unity assets.
The compiler output is confined to a temporary directory and not uploaded.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from scripts.probe_directx_shader_bridge import inspect


def execute(command, *, timeout=90):
    try:
        return subprocess.run(command, check=False, capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Compiler operation timed out") from exc


def lab(shader_source):
    if (shader_source.is_symlink() or not shader_source.is_file()
            or shader_source.stat().st_size > 16 * 1024):
        raise ValueError("Use only the small authored synthetic HLSL fixture")
    source = shader_source.read_text()
    if "[numthreads(8, 8, 1)]" not in source or "RWStructuredBuffer" not in source:
        raise ValueError("Unexpected original synthetic fixture")
    needed = ("glslangValidator", "spirv-val", "vkd3d-compiler")
    for binary in needed:
        if not shutil.which(binary):
            raise RuntimeError("Shader bridge lab dependency unavailable: " + binary)
    with tempfile.TemporaryDirectory(prefix="raft-public-shader-test-") as temp:
        root = Path(temp)
        generated_spirv = root / "public_hlsl.spv"
        command = [
            "glslangValidator", "-V", "-D", "-S", "comp",
            "-e", "main", "-o", str(generated_spirv), str(shader_source),
        ]
        result = execute(command)
        if result.returncode:
            raise RuntimeError("Synthetic HLSL -> SPIR-V compiler failed (code=" + str(result.returncode) + ")")
        result = execute(["spirv-val", "--target-env", "vulkan1.0", str(generated_spirv)])
        if result.returncode:
            raise RuntimeError("Synthetic SPIR-V validation failed (code=" + str(result.returncode) + ")")
        spirv_report = inspect(generated_spirv.read_bytes())
        if not spirv_report["declared_local_workgroup_sizes"] or [
            8, 8, 1
        ] not in spirv_report["declared_local_workgroup_sizes"]:
            raise RuntimeError("Synthetic shader workgroup dimensions changed after translation")
        if spirv_report["entrypoint_execution_models"].get(5) != 1:
            raise RuntimeError("Synthetic compute entrypoint absent")

        # Ubuntu 24.04's VKD3D 1.2 CLI may not support compiling all
        # modern HLSL profiles to DXBC. Probe actual capabilities; never
        # report a synthetic DXBC translation that did not happen.
        capability = execute(["vkd3d-compiler", "-x", "dxbc-tpf", "--print-target-types"])
        target_types = capability.stdout.lower()
        vkd3d_target_query_accepted = capability.returncode == 0
        directx = root / "public_compute.dxbc"
        candidate_spirv = root / "public_dxbc.spv"
        compile_result = execute([
            "vkd3d-compiler", "-x", "hlsl", "-p", "cs_5_0",
            "-b", "dxbc-tpf", "-o", str(directx), str(shader_source),
        ])
        dxbc_created = compile_result.returncode == 0 and directx.is_file()
        dxbc_probe = None
        dxbc_to_spirv = False
        dxbc_spirv_validated = False
        if dxbc_created:
            dxbc_probe = inspect(directx.read_bytes())
            if dxbc_probe["container"] != "DXBC" or not dxbc_probe["executable_shader_chunk"]:
                raise RuntimeError("Compiler did not produce a valid DXBC shader container")
            convert = execute([
                "vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                "-o", str(candidate_spirv), str(directx),
            ])
            dxbc_to_spirv = convert.returncode == 0 and candidate_spirv.is_file()
            if dxbc_to_spirv:
                candidate_probe = inspect(candidate_spirv.read_bytes())
                if candidate_probe["container"] != "SPIR-V":
                    raise RuntimeError("VKD3D conversion produced non-SPIR-V output")
                dxbc_spirv_validated = execute([
                    "spirv-val", "--target-env", "vulkan1.0", str(candidate_spirv)
                ]).returncode == 0
        return {
            "lab": "public-authored-HLSL-compute-only",
            "synthetic_hlsl_to_spirv": True,
            "spirv_validator_passed": True,
            "spirv_compute_local_size": [8, 8, 1],
            "vkd3d_dxbc_target_query_accepted": vkd3d_target_query_accepted,
            "vkd3d_lists_spirv_target": "spirv" in target_types,
            "vkd3d_hlsl_to_dxbc": dxbc_created,
            "vkd3d_dxbc_to_spirv": dxbc_to_spirv,
            "vkd3d_dxbc_spirv_validator_passed": dxbc_spirv_validated,
            "dxbc_chunks_if_compiled": dxbc_probe["chunk_tags"] if dxbc_probe else {},
            "game_assets_downloaded": False,
            "original_raft_shader_recovered": False,
            "original_raft_shader_translated": False,
            "unity_player_compiled": False,
            "vulkan_gpu_execution": False,
            "android_gpu_tested": False,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--synthetic-hlsl", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_SHADER_TRANSLATION_LAB " + json.dumps(lab(args.synthetic_hlsl), sort_keys=True))


if __name__ == "__main__":
    main()
