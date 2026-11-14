"""Assemble the recovered four-pass shader for a private Unity compiler check."""
import argparse
import json
import re
import tempfile
from pathlib import Path

from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_original_921_keyword_routes import routed_stage
from scripts.gt_original_921_cb_layout import constant_buffer_lanes
from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers
from scripts.gt_original_921_semantics import pin_varying_locations, restore_vertex_inputs


PASS_MODES = ("ForwardBase", "ForwardAdd", "Deferred", "ShadowCaster")
EXPECTED_ROUTES = (8, 13, 8, 4)
VULKAN_LOCATION = re.compile(
    r"(?m)^( +)\[\[vk::location\(([0-9]+)\)\]\] ([^\n]+ : TEXCOORD([0-9]+);)$"
)


def unity_varying_semantics(source):
    # Unity 2021's graphics shader compiler rejects DXC's Vulkan attribute.
    # The same register is already encoded in the matching HLSL semantic.
    def use_semantic(match):
        if match[2] != match[4]:
            raise ValueError("original_921_varying_semantic_location_mismatch")
        return match[1] + match[3]

    source = VULKAN_LOCATION.sub(use_semantic, source)
    if "[[vk::location" in source:
        raise ValueError("original_921_unmapped_vulkan_location")
    return source


def unity_resource_bindings(source, stage):
    # The translated descriptor ordinals share one Vulkan namespace, whereas
    # Unity's graphics compiler has separate, smaller HLSL sampler slots.
    # Bind textures and samplers by their recovered Unity property names.
    source = re.sub(r" : register\([ts][0-9]+\)(?=;)", "", source)
    for name in re.findall(r"(?m)^cbuffer ((?!gt_|raft921_cb)[A-Za-z_]\w*) ", source):
        pattern = re.compile(r"cbuffer " + name + r" : register\(b[0-9]+\) \{[^{}]*\};")
        block = pattern.search(source)
        if block is None:
            continue
        pads = {pad: f"gt_{name}_pad{lane}" for pad, lane in
                re.findall(r"\b(raft921_cb[0-9]+_pad([0-9]+))\b", block[0])}
        source = source[:block.start()] + re.sub(
            r" : register\(b[0-9]+\)", "", block[0], count=1) + source[block.end():]
        if pads:
            source = re.sub(r"\b(?:" + "|".join(pads) + r")\b",
                            lambda match: pads[match[0]], source)
    # These names are generated for padding, with no original Unity binding.
    # They must not alias a different stage's unrelated padding or globals.
    return re.sub(r"\braft921_cb[0-9]+_(?:pad[0-9]+|Globals|type[0-9]+)\b",
                  lambda match: f"gt_{stage}_{match[0]}", source)


def paired_uniform_layouts(stage_records):
    stages = [record["source_constant_buffer_layouts"] for record in stage_records]
    canonical = {}
    matched = {buffer["name"] for buffer in stages[0]} & {buffer["name"] for buffer in stages[1]}
    for name in sorted(matched - {"$Globals"}):
        members = {}
        layouts = [buffer for stage in stages for buffer in stage if buffer["name"] == name]
        if len(layouts) != 2:
            continue
        for buffer in layouts:
            if buffer["structs"] != layouts[0]["structs"] or buffer["variant_size_bytes"] != layouts[0]["variant_size_bytes"]:
                raise ValueError("original_921_incompatible_shared_uniform_block")
            for member in buffer["members"]:
                previous = members.setdefault(member["name"], member)
                if previous != member:
                    raise ValueError("original_921_conflicting_shared_uniform_member")
        canonical[name] = sorted(members.values(), key=lambda member: member["index"])

    merged = []
    for stage in stages:
        buffers = []
        for buffer in stage:
            if buffer["name"] in canonical:
                buffer = dict(buffer, members=canonical[buffer["name"]])
                buffer["original_named_lanes"] = constant_buffer_lanes(buffer)
            buffers.append(buffer)
        merged.append(buffers)
    return merged


TOP_LEVEL = re.compile(
    r"(?m)^(?P<kind>cbuffer|struct) (?P<name>[A-Za-z_]\w*)[^\n{]*\{(?P<body>[^{}]*)\};"
    r"|^(?P<decl>(?:Texture\w*(?:<[^;>]+>)?|Sampler\w*) (?P<resource>[A-Za-z_]\w*)[^;\n]*;)"
)
HELPER = re.compile(
    r"\b(?:SPIRV_Cross_(?:Input|Output)|spirv_cross_main|raft921_cb[0-9]+_read|"
    r"SPIRV_Cross_(?:VertexInfo|BaseVertex|BaseInstance)|in_[A-Za-z_0-9]+|out_[A-Za-z_0-9]+)\b"
)
GLOBAL = re.compile(r"(?m)^(?:static(?: const)? )[^{};\n]+;")
MEMBER = re.compile(
    r"(?m)^(?P<type>(?:column_major |row_major )?[A-Za-z_]\w*) "
    r"(?P<var>[A-Za-z_]\w*)(?P<array>\[[0-9]+\])? : packoffset\([^)]*\);$"
)


def combine_stages(vertex, fragment):
    """Keep both entries visible to Unity's DXC and share exact uniform declarations."""
    common = {}
    members = {}
    types = {}
    globals_ = {}

    def stage_body(source, stage):
        source = HELPER.sub(lambda match: f"gt_{stage}_{match[0]}", source)

        def extract(match):
            kind = match["kind"]
            if kind == "struct":
                if "raft921_cb" not in match["name"]:
                    return match[0]
                normalized = re.sub(r"gt_(?:vs|fs)_raft921_cb[0-9]+_pad([0-9]+)",
                                    r"gt_struct_pad\1", match["body"])
                key = normalized
                target = types.setdefault(key, f"gt_original_struct{len(types)}")
                type_symbols[match["name"]] = target
                return ""
            name = match["name"] or match["resource"]
            definition = re.sub(r" ?:\s*register\(b[0-9]+\)", "", match[0], count=1)
            if name in common:
                if common[name] != definition:
                    old=common[name].splitlines()
                    new=definition.splitlines()
                    if kind != "cbuffer" or old[0] != new[0]:
                        raise ValueError("original_921_shared_HLSL_declaration_drift")
                    declarations={line.strip() for line in old[1:-1]+new[1:-1]}
                    def offset(line):
                        match = re.search(r"packoffset\(c([0-9]+)(?:\.([xyzw]))?\)", line)
                        return int(match[1]) * 4 + ("xyzw".index(match[2]) if match[2] else 0)
                    common[name]="\n".join([old[0],*sorted(declarations,key=offset),old[-1]])
                return ""
            if kind == "cbuffer":
                for member in MEMBER.finditer(match["body"]):
                    var = member["var"]
                    previous = members.setdefault(var, name)
                    if previous == name:
                        continue
                    if not previous.endswith("_Globals") or not name.endswith("_Globals"):
                        raise ValueError("original_921_uniform_in_multiple_buffers")
                    other = next(m for m in MEMBER.finditer(common[previous]) if m["var"] == var)
                    if (other["type"], other["array"]) != (member["type"], member["array"]):
                        raise ValueError("original_921_uniform_incompatible_type")
                    globals_[var] = f'{member["type"]} {var}{member["array"] or ""};'
            common[name] = definition
            return ""

        type_symbols = {}
        source = TOP_LEVEL.sub(lambda match: extract(match) if match["kind"] == "struct" else match[0], source)
        for old, new in type_symbols.items():
            source = re.sub(r"\b" + old + r"\b", new, source)
        # Translated helpers, including the global stage I/O temporaries, are
        # private to their stage. Recovered engine/material names remain global.
        prefixes = {}
        for decl in GLOBAL.finditer(source):
            match = re.search(r"\b([A-Za-z_]\w*)(?:\[[^]]+\])?\s*(?:=.*)?;$", decl[0])
            if match and not match[1].startswith(f"gt_{stage}_"):
                prefixes[match[1]] = f"gt_{stage}_{match[1]}"
        if prefixes:
            names = re.compile(r"\b(?:" + "|".join(prefixes) + r")\b")
            source = names.sub(lambda match: prefixes[match[0]], source)
        return TOP_LEVEL.sub(extract, source)

    vertex = stage_body(vertex, "vs")
    fragment = stage_body(fragment, "fs")
    type_declarations = [f"struct {name} {{{body}}};" for body, name in types.items()]
    buffer_declarations = [MEMBER.sub(lambda m: "" if m["var"] in globals_ else m[0], value)
                           for value in common.values()]
    return "\n".join([*type_declarations, *buffer_declarations, *globals_.values(), vertex, fragment])


def compose(private):
    layout = (private / "original-private-layout.txt").read_text(encoding="utf-8")
    routes = json.loads((private / "original-private-keyword-routes.json").read_text())
    manifest = json.loads((private / "original-private-variant-manifest.json").read_text())
    if tuple(len(row["routes"]) for row in routes) != EXPECTED_ROUTES:
        raise ValueError("original_921_unexpected_shaderlab_routes")
    records = json.loads((private / "original-private-parameter-records.json").read_text())["stage_records"]
    stage_sources = {}
    for index, pair in enumerate(manifest["paired"]):
        layouts = paired_uniform_layouts(records[index * 2:index * 2 + 2])
        for offset, stage in enumerate(("vs", "fs")):
            row = pair[stage]
            key = (pair["subshader"], pair["pass"], stage, row["program_ref"],
                   tuple(sorted(row["original_variant_metadata"]["m_KeywordIndices"])))
            directory = private / f"bound-stage-{index * 2 + offset:03d}"
            source = rebind_constant_buffers(
                (directory / "resource-bound.hlsl").read_text(encoding="utf-8"), layouts[offset])
            if stage == "vs":
                dxbc = (private / row["program_ref"] / "source.dxbc").read_bytes()
                source, _ = restore_vertex_inputs(source, dxbc)
            source = unity_varying_semantics(pin_varying_locations(source, 1 - offset))
            source, entries = re.subn(r"\bmain(?=\s*\()", f"gt_{stage}_main", source)
            if entries != 1:
                raise ValueError("original_921_translated_entrypoint_missing_or_ambiguous")
            stage_sources[key] = unity_resource_bindings(source, stage)
    original_names = manifest["original_shader_ParsedForm_full_private"]["m_KeywordNames"]
    indices = {name: index for index, name in enumerate(original_names)}
    anchor = "// Original stage programs attach here"
    blocks = layout.split(anchor)
    if len(blocks) != len(PASS_MODES) + 1:
        raise ValueError("original_921_shaderlab_layout_has_wrong_pass_count")
    parts = [blocks[0].replace('"LIGHTMODE" = "FORWARDBASE"', '"LightMode" = "ForwardBase"')]
    for index, row in enumerate(routes):
        # A private per-pass keyword dimension lets Unity compile every
        # recovered program without assuming production keyword selection.
        names = [f"GT_ORIGINAL_921_P{index}_V{variant}"
                 for variant in range(1, len(row["routes"]))]
        programs = {}
        clauses = []
        for number, route in enumerate(row["routes"]):
            order = tuple(sorted(indices[name] for name in route["enabled"]))
            pair_sources = [
                stage_sources[row["subshader"], row["pass"], stage, route[stage], order]
                for stage in ("vs", "fs")
            ]
            programs[number] = combine_stages(*pair_sources)
            clauses.append({"enabled": [names[number - 1]] if number else [],
                            "program": number})
        pragmas = ["#pragma multi_compile __ " + " ".join(names)]
        program = ["HLSLPROGRAM", "#pragma target 5.0",
                   "#pragma vertex gt_vs_main", "#pragma fragment gt_fs_main",
                   "#pragma use_dxc vulkan", *pragmas,
                   routed_stage(clauses, names, programs), "ENDHLSL"]
        remainder = blocks[index + 1]
        if index + 1 < len(PASS_MODES):
            mode = PASS_MODES[index + 1]
            remainder = remainder.replace(f'"LIGHTMODE" = "{mode.upper()}"', f'"LightMode" = "{mode}"')
        parts.extend(("\n".join(program), remainder))
    shader = "".join(parts)
    result = pass_coverage(shader)
    if result["subshader_pass_counts"] != [4] or result["passes_with_complete_program"] != 4:
        raise ValueError("original_921_incomplete_shaderlab")
    return shader


def verify_entrypoints(shader, directory):
    """Compile both real entries of every generated ShaderLab route."""
    from scripts.w1_recover_graphics_programs import command
    from scripts.t3_spirv_interface_name_drift import read_reflection

    blocks = re.findall(r"(?ms)^HLSLPROGRAM\n(.*?)^ENDHLSL$", shader)
    if len(blocks) != len(EXPECTED_ROUTES):
        raise ValueError("original_921_entrypoint_pass_count_mismatch")
    with tempfile.TemporaryDirectory(prefix="original-921-entrypoints-", dir=directory) as tmp:
        source = Path(tmp) / "route.hlsl"
        binary = Path(tmp) / "route.spv"
        for index, (block, count) in enumerate(zip(blocks, EXPECTED_ROUTES)):
            code = re.sub(r"(?m)^#pragma [^\n]*\n", "", block)
            source.write_text(code, encoding="utf-8")
            for variant in range(count):
                route = [f"-DGT_ORIGINAL_921_P{index}_V{variant}=1"] if variant else []
                for suffix, macro, entry in (
                    ("vert", "VERTEX", "gt_vs_main"),
                    ("frag", "FRAGMENT", "gt_fs_main"),
                ):
                    args = ["glslangValidator", "-V", "-D", "--target-env", "vulkan1.1",
                            "-S", suffix, "-e", entry, f"-DSHADER_STAGE_{macro}=1"]
                    binary.unlink(missing_ok=True)
                    if not command([*args, *route, "-o", str(binary), str(source)]):
                        raise ValueError("original_921_shaderlab_entrypoint_compile_failed")
                    if not command(["spirv-val", "--target-env", "vulkan1.1", str(binary)]):
                        raise ValueError("original_921_shaderlab_entrypoint_spirv_invalid")
                    if [row["name"] for row in read_reflection(binary)["entryPoints"]] != [entry]:
                        raise ValueError("original_921_shaderlab_entrypoint_missing")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--shader", type=Path, required=True)
    parser.add_argument("--verify-entrypoints", action="store_true")
    args = parser.parse_args()
    shader = compose(args.private)
    if args.verify_entrypoints:
        verify_entrypoints(shader, args.private)
    with args.shader.open("x", encoding="utf-8") as target:
        target.write(shader)


if __name__ == "__main__":
    main()
