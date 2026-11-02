"""Bounded, metadata-only DXBC/DXIL and SPIR-V container inspection.

Use for privately recovered, authenticated source buffers, not untrusted
binary execution. This does not reverse engineer Unity shader serialization,
recover original HLSL, certify vendor identity, or validate GPU behaviour.
No executable bytecode, shader names, instructions or source are logged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

MAX_SHADER_BYTES = 16 * 1024 * 1024
MAX_DXBC_CHUNKS = 96
MAX_SPIRV_INSTRUCTIONS = 200_000
SPIRV_MAGIC = 0x07230203


def inspect_dxbc(data):
    if len(data) < 36 or data[:4] != b"DXBC":
        raise ValueError("Not a complete DXBC container")
    marker, declared, count = struct.unpack_from("<III", data, 20)
    if marker != 1 or declared != len(data) or not 1 <= count <= MAX_DXBC_CHUNKS:
        raise ValueError("Malformed DXBC header, size or chunk count")
    table_end = 32 + 4 * count
    if len(data) < table_end:
        raise ValueError("Truncated DXBC chunk directory")
    offsets = struct.unpack_from("<" + "I" * count, data, 32)
    spans, tags = [], []
    for offset in offsets:
        if offset % 4 or offset < table_end or offset + 8 > len(data):
            raise ValueError("DXBC chunk offset outside payload")
        size = struct.unpack_from("<I", data, offset + 4)[0]
        end = offset + 8 + size
        if end > len(data):
            raise ValueError("DXBC chunk extends outside payload")
        tag = data[offset:offset + 4]
        if any(c < 32 or c > 126 for c in tag):
            raise ValueError("Unexpected DXBC chunk identifier")
        spans.append((offset, end))
        tags.append(tag.decode("ascii"))
    for previous, following in zip(sorted(spans), sorted(spans)[1:]):
        if previous[1] > following[0]:
            raise ValueError("Overlapping DXBC chunks")
    count_by_tag = {}
    for tag in tags:
        count_by_tag[tag] = count_by_tag.get(tag, 0) + 1
    return {
        "container": "DXIL" if "DXIL" in tags else "DXBC",
        "chunk_tags": count_by_tag,
        "executable_shader_chunk": any(t in ("SHEX", "SHDR", "DXIL") for t in tags),
        "claimed_sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "shader_source_recovered": False,
        "gpu_compatibility_verified": False,
        "code_emitted": False,
    }


def inspect_spirv(data):
    if len(data) < 20 or len(data) % 4 or data[:4] != struct.pack("<I", SPIRV_MAGIC):
        raise ValueError("Not a complete little-endian SPIR-V module")
    magic, version, generator, bound, schema = struct.unpack_from("<5I", data)
    if (version >> 16) != 1 or (version & 0xff) != 0 or ((version >> 8) & 0xff) > 6:
        raise ValueError("Unexpected SPIR-V version")
    if schema != 0 or bound == 0:
        raise ValueError("Malformed SPIR-V header")
    offset, instructions = 20, 0
    counts = {}
    stages = {}
    local_sizes = []
    while offset < len(data):
        word = struct.unpack_from("<I", data, offset)[0]
        width, op = word >> 16, word & 0xffff
        if width == 0 or offset + width * 4 > len(data):
            raise ValueError("Truncated SPIR-V instruction")
        instructions += 1
        if instructions > MAX_SPIRV_INSTRUCTIONS:
            raise ValueError("SPIR-V instruction count exceeds bound")
        # Count selected structural opcodes only. Never print string operands
        # from OpEntryPoint, OpName or OpString (may contain original names).
        if op == 15:
            if width < 4: raise ValueError("Malformed OpEntryPoint")
            stage = struct.unpack_from("<I", data, offset + 4)[0]
            stages[stage] = stages.get(stage, 0) + 1
        elif op == 16 and width >= 6:
            mode = struct.unpack_from("<I", data, offset + 8)[0]
            if mode == 17:
                x, y, z = struct.unpack_from("<3I", data, offset + 12)
                local_sizes.append([x, y, z])
        elif op in (17, 14, 54, 55, 59, 71, 72, 248, 253):
            counts[op] = counts.get(op, 0) + 1
        offset += width * 4
    return {
        "container": "SPIR-V",
        "version": [version >> 16, (version >> 8) & 0xff],
        "instruction_count": instructions,
        "entrypoint_execution_models": dict(sorted(stages.items())),
        "declared_local_workgroup_sizes": local_sizes[:16],
        "selected_instruction_counts": dict(sorted(counts.items())),
        "claimed_sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "shader_source_recovered": False,
        "gpu_compatibility_verified": False,
        "code_emitted": False,
    }


def inspect(data):
    if not isinstance(data, bytes) or not 20 <= len(data) <= MAX_SHADER_BYTES:
        raise ValueError("Shader binary absent or exceeds size bound")
    if data.startswith(b"DXBC"):
        return inspect_dxbc(data)
    if data.startswith(struct.pack("<I", SPIRV_MAGIC)):
        return inspect_spirv(data)
    raise ValueError("Unsupported direct shader container, not DXBC/DXIL/SPIR-V")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, required=True,
                        help="Private, locally authenticated shader binary")
    args = parser.parse_args()
    if args.file.is_symlink() or not args.file.is_file() or args.file.stat().st_size > MAX_SHADER_BYTES:
        raise ValueError("Unsafe or oversized shader file")
    result = inspect(args.file.read_bytes())
    print("RAFT_SHADER_BRIDGE_CONTRACT " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
