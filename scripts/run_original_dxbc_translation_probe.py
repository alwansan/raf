"""Translate one authenticated actual Raft DXBC shader privately, WITHOUT Unity.

Only the specific ordinary-Git original ComputeShader object discovered by
the independent prior source scan is read. Both translators are debug probes,
not Unity asset restorers; their binary outputs remain in an ephemeral CI
temporary folder and are not published, committed or attached as artifacts.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from scripts.probe_original_compute_containers import scan_blob
from scripts.probe_directx_shader_bridge import inspect

ORIGINAL_OWNER = "sharedassets29.assets"
ORIGINAL_PATH_ID = 577
ORIGINAL_OBJECT_SHA256 = "3c4307f852785a8564f90d68256cebfed575876e70c5c5fda8fd7da77d74cfff"
ORIGINAL_DXBC_SHA256 = "93880946974676dee3a7fa4d56246e7f0808874e1ec0327592acfa382950d099"
ORIGINAL_DXBC_BYTES = 460


def authenticate(original_dir: Path) -> tuple:
    source = original_dir / ORIGINAL_OWNER
    if source.is_symlink() or not source.is_file() or source.stat().st_size > 30 * 1024 * 1024:
        raise ValueError("Missing or untrusted original regular-Git DXBC owner")
    with source.open("rb") as file:
        if file.read(48).startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError("Original DXBC owner is an LFS pointer")
    import UnityPy
    env = UnityPy.load(str(source))
    candidates = [
        obj for obj in env.file.objects.values()
        if obj.type.name == "ComputeShader" and int(obj.path_id) == ORIGINAL_PATH_ID
    ]
    if len(candidates) != 1:
        raise ValueError("Original compute owner/pathID changed")
    raw = candidates[0].get_raw_data()
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original authenticated ComputeShader payload changed")
    scan = scan_blob(raw)
    containers = scan["valid_dxbc_containers"]
    if len(containers) != 1 or containers[0]["binary_sha256"] != ORIGINAL_DXBC_SHA256 or containers[0]["bytes"] != ORIGINAL_DXBC_BYTES:
        raise ValueError("Exact original DXBC container identity changed")
    chunk = containers[0]
    data = raw[chunk["offset_in_original_object"]:chunk["offset_in_original_object"] + chunk["bytes"]]
    if inspect(data)["container"] != "DXBC":
        raise ValueError("Original compute bytecode does not have DXBC header")
    return data, chunk


def version_tokens(data):
    if len(data) < 40 or data[:4] != b"DXBC":
        raise ValueError("Not DXBC")
    count = struct.unpack_from("<I", data, 28)[0]
    versions = []
    for index in range(count):
        offset = struct.unpack_from("<I", data, 32 + 4 * index)[0]
        tag = data[offset:offset + 4]
        length = struct.unpack_from("<I", data, offset + 4)[0]
        if tag in (b"SHEX", b"SHDR") and length >= 4:
            token = struct.unpack_from("<I", data, offset + 8)[0]
            kind, major, minor = token >> 16, (token >> 4) & 0xf, token & 0xf
            versions.append({"shader_stage_code": kind, "shader_model": [major, minor]})
    return versions


def execute(args, timeout=120):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Private shader translation exceeded the per-command CPU time bound") from exc


def probe(root: Path, dxbc_compiler: Path):
    if dxbc_compiler.is_symlink() or not dxbc_compiler.is_file():
        raise ValueError("Missing pinned source-built DXBC translator")
    dxbc, context = authenticate(root)
    with tempfile.TemporaryDirectory(prefix="raft-private-dxbc-probe-") as folder:
        temp = Path(folder)
        source = temp / "original.dxbc"
        source.write_bytes(dxbc)
        backends = {}
        for name, command in {
            "vkd3d_1_2": ["vkd3d-compiler", "-x", "dxbc-tpf", "-b", "spirv-binary",
                          "-o", str(temp / "vkd3d.spv"), str(source)],
            "dxbc_spirv": [str(dxbc_compiler), str(source),
                            "--spv", str(temp / "modern.spv")],
        }.items():
            output = temp / ("vkd3d.spv" if name == "vkd3d_1_2" else "modern.spv")
            result = execute(command)
            success = result.returncode == 0 and output.is_file() and output.stat().st_size > 0
            report = {
                "command_completed": result.returncode == 0,
                "produced_spirv": False,
                "structurally_readable_spirv": False,
                "spirv_validator_vulkan_1_1": False,
                "spirv_validator_vulkan_1_3": False,
                "shader_execution_verified": False,
            }
            if success:
                try:
                    reflection = inspect(output.read_bytes())
                except ValueError:
                    reflection = None
                if reflection is not None and reflection["container"] == "SPIR-V":
                    report["produced_spirv"] = True
                    report["structurally_readable_spirv"] = True
                    report["spirv_version"] = reflection["version"]
                    report["execution_models"] = reflection["entrypoint_execution_models"]
                    report["declared_local_workgroup_sizes"] = reflection["declared_local_workgroup_sizes"]
                    for name_ver, env in (("spirv_validator_vulkan_1_1", "vulkan1.1"),
                                          ("spirv_validator_vulkan_1_3", "vulkan1.3")):
                        report[name_ver] = execute(["spirv-val", "--target-env", env, str(output)]).returncode == 0
            backends[name] = report
        return {
            "original_source": ORIGINAL_OWNER,
            "original_compute_path_id": ORIGINAL_PATH_ID,
            "original_compute_object_sha256": ORIGINAL_OBJECT_SHA256,
            "original_dxbc_sha256": ORIGINAL_DXBC_SHA256,
            "original_dxbc_bytes": len(dxbc),
            "original_dxbc_chunks": context["chunk_tags"],
            "shader_version_tokens": version_tokens(dxbc),
            "translation_backends": backends,
            "original_raft_shader_program_published": False,
            "unity_runtime_compiled": False,
            "android_vulkan_gpu_executed": False,
            "original_water_kernel_identity_verified": False,
            "original_assets_modified": False,
        }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--dxbc-compiler", type=Path, required=True)
    a = p.parse_args()
    print("RAFT_ORIGINAL_DXBC_TRANSLATION_PROBE " + json.dumps(
        probe(a.root, a.dxbc_compiler), sort_keys=True))


if __name__ == "__main__":
    main()
