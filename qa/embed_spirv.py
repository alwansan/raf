"""Embed exact little-endian SPIR-V words in a C header."""
import pathlib
import struct
import sys

out, vertex, fragment = map(pathlib.Path, sys.argv[1:])
lines = ["#include <stdint.h>"]
for name, path in (("probe_vertex_spv", vertex), ("probe_fragment_spv", fragment)):
    data = path.read_bytes()
    assert len(data) >= 20 and len(data) % 4 == 0
    words = struct.unpack("<" + "I" * (len(data) // 4), data)
    assert words[0] == 0x07230203
    lines.append("static const uint32_t " + name + "[] = {")
    for i in range(0, len(words), 8):
        lines.append("    " + ", ".join(f"0x{x:08x}u" for x in words[i:i+8]) + ",")
    lines.append("};")
out.write_text("\n".join(lines) + "\n")
