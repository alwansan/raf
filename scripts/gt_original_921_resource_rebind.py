"""Build private HLSL texture and sampler declarations from the source slot map."""
import re

from scripts.w1_rebind_depth_resources import IDENT, RESOURCE


def rebind_resources(source, bindings):
    by_slot = {(entry["kind"], entry["slot"]): entry["source_texture_name"]
               for entry in bindings}
    if len(by_slot) != len(bindings):
        raise ValueError("duplicate_original_resource_slot")

    replacements = {}
    for match in RESOURCE.finditer(source):
        symbol, kind = match[2], match[3]
        slot = re.fullmatch(kind + r"(\d+)", symbol)
        key = (kind, int(slot[1])) if slot else None
        name = by_slot.pop(key, None)
        if name is None or not IDENT.fullmatch(name) or symbol in replacements:
            raise ValueError("unresolved_original_resource_name")
        replacements[symbol] = ("sampler" + name) if kind == "s" else name
    if by_slot or len(set(replacements.values())) != len(replacements):
        raise ValueError("original_resource_symbol_collision")
    if not replacements:
        return source

    # The translated register annotations can contain the same spelling as
    # an unrelated declaration. Leave descriptor syntax byte-for-byte intact.
    tokens = re.compile(r"\bregister\s*\([^)]*\)|\b(?:" +
                        "|".join(map(re.escape, replacements)) + r")\b")
    return tokens.sub(lambda match: replacements.get(match[0], match[0]), source)


def verify_rebound_resources(program, stage, bindings, private):
    from scripts.w1_recover_graphics_programs import command

    private.mkdir(mode=0o700)
    hlsl = private / "resource-bound.hlsl"
    hlsl.write_text(rebind_resources((program / "private.hlsl").read_text(), bindings),
                    encoding="utf-8")
    binary = hlsl.with_suffix(".spv")
    suffix = {0: "frag", 1: "vert"}[stage]
    if not command(["glslangValidator", "-V", "-D", "-S", suffix, "-e", "main",
                    "-o", str(binary), str(hlsl)]):
        raise ValueError("original_resource_rebound_compile_failed")
    if not command(["spirv-val", "--target-env", "vulkan1.1", str(binary)]):
        raise ValueError("original_resource_rebound_spirv_invalid")
    normalized = private / "resource-bound-normalized.spv"
    baseline = private / "resource-baseline-normalized.spv"
    for original, output in ((binary, normalized), (program / "roundtrip.spv", baseline)):
        if not command(["spirv-opt", "--strip-debug", str(original), "-o", str(output)]):
            raise ValueError("original_resource_spirv_normalization_failed")
    if normalized.read_bytes() != baseline.read_bytes():
        raise ValueError("original_resource_rebound_changed_spirv")
