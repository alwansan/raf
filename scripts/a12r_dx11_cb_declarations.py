"""Bounded DXBC SHDR/SHEX dcl_constantbuffer decoder (SM4/5), no RDEF needed.

Decodes only declaration register slots and 16-byte element counts, following
D3D10_SB_OPCODE_DCL_CONSTANT_BUFFER and immediate-32 2D operand layout.
Private original program bytecode is never printed or published.
"""
import struct

OPCODE_DCL_CONSTANT_BUFFER = 89
OPCODE_CUSTOMDATA = 53
OPERAND_CONSTANT_BUFFER = 8


def u32(data, pos):
    if pos < 0 or pos + 4 > len(data):
        raise ValueError("dxbc_dcl_truncated")
    return struct.unpack_from("<I", data, pos)[0]


def declarations(dxbc):
    if not isinstance(dxbc, bytes) or len(dxbc) < 40 or dxbc[:4] != b"DXBC":
        raise ValueError("dxbc_dcl_bad_container")
    if u32(dxbc, 24) != len(dxbc):
        raise ValueError("dxbc_dcl_bad_total_size")
    chunks = u32(dxbc, 28)
    if not 1 <= chunks <= 128 or 32 + chunks * 4 > len(dxbc):
        raise ValueError("dxbc_dcl_bad_chunks")
    shaders = []
    for i in range(chunks):
        start = u32(dxbc, 32 + 4 * i)
        if start < 32 + chunks * 4 or start + 8 > len(dxbc):
            raise ValueError("dxbc_dcl_bad_chunk_offset")
        end = start + 8 + u32(dxbc, start + 4)
        if end > len(dxbc):
            raise ValueError("dxbc_dcl_bad_chunk_range")
        if dxbc[start:start + 4] in (b"SHDR", b"SHEX"):
            shaders.append(dxbc[start + 8:end])
    if len(shaders) != 1:
        raise ValueError("dxbc_dcl_missing_unique_shader")
    shader = shaders[0]
    if len(shader) < 8 or len(shader) % 4 or len(shader) > 8 * 1024 * 1024:
        raise ValueError("dxbc_dcl_bad_token_stream")
    tokens = struct.unpack("<" + "I" * (len(shader) // 4), shader)
    if tokens[1] != len(tokens):
        raise ValueError("dxbc_dcl_bad_declared_tokens")
    i, result = 2, {}
    while i < len(tokens):
        header = tokens[i]
        opcode = header & 0x7ff
        length = (header >> 24) & 0x7f
        if not length and opcode == OPCODE_CUSTOMDATA and i + 1 < len(tokens):
            length = tokens[i + 1]
        if not 1 <= length <= 0x10000 or i + length > len(tokens):
            raise ValueError("dxbc_dcl_bad_instruction_size")
        if opcode == OPCODE_DCL_CONSTANT_BUFFER:
            if length != 4 or header >> 31:
                raise ValueError("dxbc_dcl_unsupported_cb_encoding")
            operand, slot, registers = tokens[i + 1:i + 4]
            if (operand >> 31 or ((operand >> 12) & 255) != OPERAND_CONSTANT_BUFFER
                    or ((operand >> 20) & 3) != 2 or ((operand >> 22) & 7) != 0
                    or ((operand >> 25) & 7) != 0):
                raise ValueError("dxbc_dcl_unsupported_cb_operand")
            if slot > 255 or registers == 0 or registers > 131072 or slot in result:
                raise ValueError("dxbc_dcl_unsafe_cb_declaration")
            result[slot] = registers * 16
        i += length
    if not result:
        raise ValueError("dxbc_dcl_no_constant_buffers")
    return result
