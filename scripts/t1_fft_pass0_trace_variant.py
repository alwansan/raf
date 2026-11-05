"""Compile a private pass-zero HLSL variant with bounded image-read tracing."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile

from scripts.t1_fft_unity_gpu_resource_bridge import IMAGE, translated_image_symbols


def coordinate_end(text, start):
    depth = 1
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if not depth:
                return i
        elif ch == "," and depth == 1:
            break
    raise ValueError("Unexpected private Load argument structure")


def instrument(source):
    clean = re.sub(r"/\*[\s\S]*?\*/|//[^\r\n]*", lambda m: re.sub(r"[^\r\n]", " ", m[0]), source)
    roles = translated_image_symbols(clean)
    if re.search(r"\bT1Trace\w*|\bregister\s*\(\s*u\s*3\b", clean):
        raise ValueError("Private trace binding or identifier collision")
    declarations = list(IMAGE.finditer(clean))
    declared_types = {}
    for decl in declarations:
        typ = re.search(r"<\s*((?:float|int|uint)([234])?)\s*>", decl[0])
        if typ:
            declared_types[decl.group(2)] = (typ.group(1), int(typ.group(2) or "1"))
    wrappers = ["\nRWStructuredBuffer<uint> T1TraceBuffer : register(u3);\n"]
    edits = []
    for role, expected in (("source", 1), ("butterfly", 2)):
        symbol = roles[role]
        if symbol not in declared_types:
            raise ValueError("Unsupported private texture component type")
        typ, channels = declared_types[symbol]
        calls = list(re.finditer(rf"\b{re.escape(symbol)}\s*\.\s*Load\s*\(\s*", clean))
        if len(calls) != expected:
            raise ValueError("Private Load site counts changed")
        for call in calls:
            end = coordinate_end(clean, call.end())
            if not re.match(r"u?int3\s*\(", clean[call.end():end]):
                raise ValueError("Unexpected private Load coordinate type")
            site = len(edits)
            name = f"T1TraceLoad{site}"
            edits.append((call.start(), call.end(), name + "("))
            stores = []
            for lane in range(channels):
                value = "value" if channels == 1 else f"value.{'xyzw'[lane]}"
                bits = value if typ.startswith("uint") else f"asuint({value})"
                stores.append(f"        T1TraceBuffer[base + {4 + lane}u] = {bits};")
            stores.extend(f"        T1TraceBuffer[base + {4 + lane}u] = 0u;" for lane in range(channels, 4))
            wrappers.append(
                f"\n{typ} {name}(int3 coord)\n{{\n"
                f"    {typ} value = {symbol}.Load(coord);\n"
                "    uint index;\n"
                "    InterlockedAdd(T1TraceBuffer[0], 1u, index);\n"
                "    if (index < 256u)\n    {\n"
                "        uint base = 1u + index * 8u;\n"
                f"        T1TraceBuffer[base] = {site}u;\n"
                "        T1TraceBuffer[base + 1u] = asuint(coord.x);\n"
                "        T1TraceBuffer[base + 2u] = asuint(coord.y);\n"
                "        T1TraceBuffer[base + 3u] = asuint(coord.z);\n"
                + "\n".join(stores) + "\n    }\n    return value;\n}\n"
            )
    insert = declarations[-1].end()
    if any(start < insert for start, _, _ in edits):
        raise ValueError("Private Load sites precede declarations")
    for start, end, replacement in sorted(edits, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source[:insert] + "".join(wrappers) + source[insert:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        if args.candidate.stat().st_size > 512 * 1024:
            raise ValueError("Private candidate too large")
        pragma, hlsl = args.candidate.read_text(encoding="utf-8").split("\n", 1)
        if pragma != "#pragma kernel main":
            raise ValueError("Unexpected private entry point")
        with tempfile.TemporaryDirectory(prefix="t1-trace-") as temp:
            root = Path(temp)
            (root / "trace.hlsl").write_text(instrument(hlsl), encoding="utf-8")
            for cmd in (["glslangValidator", "-V", "-D", "-S", "comp", "-e", "main",
                         "-o", "trace.spv", "trace.hlsl"],
                        ["spirv-val", "--target-env", "vulkan1.1", "trace.spv"]):
                subprocess.run(cmd, cwd=root, check=True, capture_output=True, timeout=30)
    except (OSError, ValueError, subprocess.SubprocessError):
        parser.exit(2, "Private trace variant generation or validation failed\n")
    print("RAFT_T1_PASS0_TRACE_VARIANT " + json.dumps({
        "compiled_and_validated": True, "trace_sites": 3, "max_records": 256,
        "runtime_capture": False}))


if __name__ == "__main__":
    main()
