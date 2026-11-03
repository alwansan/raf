"""Unity 2021.3 Shader ParameterBlob parser, retaining only structural evidence.

This byte reader follows the public ReadParameters method in SHA-pinned
nowl-it/AssetRipperCLI ShaderSubProgram.cs. It validates full consumption and
does not guess what nonempty parameters mean for ShaderLab runtime binding.
Names are *never* retained or emitted. Source layout/schema counts only.
"""
from collections import Counter
import hashlib
import struct

VERSION_2021 = 202012090
MAX_RECORD_BYTES = 2 * 1024 * 1024
MAX_ELEMENTS = 512
MAX_GROUPS = 32
MAX_STRING_BYTES = 2048


class Reader:
    def __init__(self, raw):
        if not isinstance(raw, bytes) or not 8 <= len(raw) <= MAX_RECORD_BYTES:
            raise ValueError("Invalid original Shader parameter record bytes")
        self.raw = raw
        self.pos = 0

    def int(self):
        if self.pos + 4 > len(self.raw):
            raise ValueError("Truncated original parameter record integer")
        value = struct.unpack_from("<i", self.raw, self.pos)[0]
        self.pos += 4
        return value

    def uint(self):
        if self.pos + 4 > len(self.raw):
            raise ValueError("Truncated original unsigned parameter field")
        value = struct.unpack_from("<I", self.raw, self.pos)[0]
        self.pos += 4
        return value

    def number(self, limit=MAX_ELEMENTS):
        value = self.int()
        if not 0 <= value <= limit:
            raise ValueError("Original parameter array count out of bounds")
        return value

    def string(self):
        length = self.number(MAX_STRING_BYTES)
        if self.pos + length > len(self.raw):
            raise ValueError("Truncated original shader parameter string")
        # Do not print or retain the original source name/identifier anywhere.
        self.raw[self.pos:self.pos + length].decode("utf-8")
        self.pos += length
        end = (self.pos + 3) & ~3
        if end > len(self.raw) or any(self.raw[self.pos:end]):
            raise ValueError("Original parameter string padding drift")
        self.pos = end

    def finish(self):
        if self.pos != len(self.raw):
            raise ValueError("Original Shader parameter record has trailing bytes")


def parse_parameter_blob(raw):
    """Parse byte-for-byte format of ShaderSubProgram.ReadParameters for 2021.3.

    Result is aggregate-only and keeps no original names or values.
    It does *not* claim original HLSL binding equivalence or edit source.
    """
    reader = Reader(raw)
    if reader.int() != VERSION_2021:
        raise ValueError("Unsupported original parameter serializer version")
    groups = reader.number(MAX_GROUPS)
    counts = Counter()
    kinds = Counter()
    for group in range(groups):
        reader.string()
        used_size = reader.number(MAX_RECORD_BYTES)
        counts["all_group_used_bytes"] += used_size
        if group:
            counts["constant_buffer_used_bytes"] += used_size
            counts["nonzero_size_constant_buffers"] += used_size > 0
        count = reader.number()
        if group and not used_size and count:
            # A zero-sized named constant buffer cannot contain numeric values.
            raise ValueError("Original nonempty constant buffer declares zero size")
        counts["groups"] += 1
        if group:
            counts["constant_buffers"] += 1
        counts["numeric_parameter_records"] += count
        for _ in range(count):
            reader.string()
            param_type = reader.int()
            rows = reader.int()
            columns = reader.int()
            matrix_flag = reader.int()
            array_size = reader.int()
            parameter_index = reader.int()
            if (param_type < 0 or not 0 <= rows <= 16 or not 0 <= columns <= 16
                or matrix_flag not in (0, 1) or not 0 <= array_size <= MAX_ELEMENTS
                or parameter_index < 0):
                raise ValueError("Original numeric parameter schema inconsistent")
            counts["matrix_parameters" if matrix_flag else "vector_parameters"] += 1
            kinds["numeric_type_" + str(param_type)] += 1
        # Original 2021.3 always writes structCount, even when zero.
        structs = reader.number()
        counts["structs"] += structs
        for _ in range(structs):
            reader.string()
            index = reader.int()
            array_size = reader.int()
            struct_size = reader.int()
            if index < 0 or not 0 <= array_size <= MAX_ELEMENTS or not 0 <= struct_size <= MAX_RECORD_BYTES:
                raise ValueError("Original struct parameter geometry invalid")
            inner_count = reader.number()
            counts["struct_numeric_members"] += inner_count
            for _ in range(inner_count):
                reader.string()
                param_type = reader.int()
                rows = reader.int()
                columns = reader.int()
                matrix_flag = reader.int()
                array_len = reader.int()
                parameter_index = reader.int()
                if (param_type < 0 or not 0 <= rows <= 16 or not 0 <= columns <= 16
                    or matrix_flag not in (0, 1) or not 0 <= array_len <= MAX_ELEMENTS
                    or parameter_index < 0):
                    raise ValueError("Original struct member schema invalid")
                counts["struct_matrix_members" if matrix_flag else "struct_vector_members"] += 1
    resources = reader.number()
    counts["resource_parameter_records"] = resources
    for _ in range(resources):
        reader.string()
        kind = reader.int()
        index = reader.int()
        extra_value = reader.int()
        if kind not in (0, 1, 2, 3, 4) or index < 0:
            raise ValueError("Unrecognized original Shader resource binding type")
        kinds["resource_kind_" + str(kind)] += 1
        if kind == 0:
            texture_flags = reader.uint()  # Includes dimensionality/multisampling.
            counts["texture_records"] += 1
            if texture_flags >> 1 > 255:
                raise ValueError("Original texture dimension metadata invalid")
        elif kind == 1:
            counts["constant_buffer_bindings"] += 1
        elif kind == 2:
            counts["structured_buffer_bindings"] += 1
        elif kind == 3:
            counts["uav_bindings"] += 1
        else:
            counts["explicit_sampler_bindings"] += 1
    reader.finish()
    return {
        "serializer_version": VERSION_2021,
        "bytes_consumed": len(raw),
        "complete_original_parameter_schema": True,
        "record_sha256": hashlib.sha256(raw).hexdigest(),
        "group_count": counts["groups"],
        "constant_buffer_count": counts["constant_buffers"],
        "constant_buffer_used_bytes": counts["constant_buffer_used_bytes"],
        "all_group_used_bytes": counts["all_group_used_bytes"],
        "nonzero_size_constant_buffers": counts["nonzero_size_constant_buffers"],
        "numeric_parameter_count": counts["numeric_parameter_records"],
        "matrix_parameter_count": counts["matrix_parameters"],
        "vector_parameter_count": counts["vector_parameters"],
        "struct_count": counts["structs"],
        "struct_numeric_member_count": counts["struct_numeric_members"],
        "resource_parameter_count": counts["resource_parameter_records"],
        "texture_count": counts["texture_records"],
        "constant_buffer_binding_count": counts["constant_buffer_bindings"],
        "structured_buffer_binding_count": counts["structured_buffer_bindings"],
        "uav_binding_count": counts["uav_bindings"],
        "explicit_sampler_binding_count": counts["explicit_sampler_bindings"],
        "resource_kind_counts": dict(sorted((k, v) for k, v in kinds.items() if k.startswith("resource_kind_"))),
        "numeric_param_type_counts": dict(sorted((k, v) for k, v in kinds.items() if k.startswith("numeric_type_"))),
        "parameters_empty": (
            counts["numeric_parameter_records"] == 0
            and counts["structs"] == 0
            and counts["resource_parameter_records"] == 0
            and counts["constant_buffers"] == 0
        ),
        # Name-only constant-buffer groups with zero data, and no other
        # parameter bindings, carry zero authored runtime parameter bytes.
        # The original group count stays recorded; not treated as empty.
        "only_zero_size_empty_cb_groups": (
            counts["constant_buffers"] > 0
            and counts["all_group_used_bytes"] == 0
            and counts["numeric_parameter_records"] == 0
            and counts["structs"] == 0
            and counts["resource_parameter_records"] == 0
        ),
        "original_shader_names_published": False,
        "raw_shader_bytes_published": False,
        "shaderlab_binding_verified": False,
    }
