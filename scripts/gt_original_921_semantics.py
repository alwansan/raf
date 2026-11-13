"""Restore Unity mesh vertex attribute semantics using original DXBC signature records."""
import re

from scripts.t3_original_921_dxbc_semantic_join import read_original_dxbc_signatures

FIELD = re.compile(r"\bv([0-9]+)\s*:\s*TEXCOORD([0-9]+)\b")


def restore_vertex_inputs(source, dxbc):
    signature = read_original_dxbc_signatures(dxbc)["input"]
    struct = re.search(r"\bstruct\s+SPIRV_Cross_Input\s*\{([^{}]*)\}", source)
    if struct is None:
        raise ValueError("original_921_missing_translated_vertex_input")

    # vkd3d names vertex input variables after their original register.
    # Unity needs the source attribute names to bind its mesh channels.
    by_register = {}
    for field in signature:
        if not field["system_value"]:
            by_register.setdefault(field["register"], []).append(field)

    restored = 0

    def replace(match):
        nonlocal restored
        matches = by_register.get(int(match[2]), [])
        if match[1] != match[2] or len(matches) != 1:
            raise ValueError("original_921_ambiguous_vertex_input_register")
        field = matches[0]
        restored += 1
        return f"v{match[1]} : {field['semantic']}{field['index']}"

    body = FIELD.sub(replace, struct[1])
    if not restored or re.search(r":\s*TEXCOORD[0-9]+\b", FIELD.sub("", struct[1])):
        raise ValueError("original_921_unmapped_vertex_input_register")
    return source[:struct.start(1)] + body + source[struct.end(1):], restored


def verify_varyings(vertex, fragment):
    """Check the original semantic and register lanes that the fragment reads."""
    vertex_outputs = {
        (field["semantic"], field["index"]): field
        for field in read_original_dxbc_signatures(vertex)["output"]
        if not field["system_value"]
    }
    inputs = [field for field in read_original_dxbc_signatures(fragment)["input"]
              if not field["system_value"]]
    for field in inputs:
        source = vertex_outputs.get((field["semantic"], field["index"]))
        if (source is None or source["register"] != field["register"]
                or source["type"] != field["type"] or field["used_mask"] & ~source["mask"]):
            raise ValueError("original_921_vertex_fragment_varying_mismatch")
    return len(inputs)


def verify_vertex_inputs(bound_stage, program_dir):
    from scripts.w1_recover_graphics_programs import command

    original = (program_dir / "source.dxbc").read_bytes()
    source = (bound_stage / "named-constant-buffers.hlsl").read_text(encoding="utf-8")
    source, restored = restore_vertex_inputs(source, original)
    candidate = bound_stage / "mesh-input-bound.hlsl"
    binary = candidate.with_suffix(".spv")
    candidate.write_text(source, encoding="utf-8")
    if not command(["glslangValidator", "-V", "-D", "-S", "vert", "-e", "main",
                    "-o", str(binary), str(candidate)]):
        raise ValueError("original_921_mesh_input_candidate_compile_failed")
    if not command(["spirv-val", "--target-env", "vulkan1.1", str(binary)]):
        raise ValueError("original_921_mesh_input_candidate_spirv_invalid")
    return restored
