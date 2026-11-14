"""Assemble the recovered four-pass shader for a private Unity compiler check."""
import argparse
import json
import re
from pathlib import Path

from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_original_921_keyword_routes import routed_stage
from scripts.gt_original_921_cb_layout import constant_buffer_lanes
from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers
from scripts.gt_original_921_semantics import pin_varying_locations, restore_vertex_inputs
from scripts.w1_depth_shaderlab import stage_body

PASS_MODES = ("ForwardBase", "ForwardAdd", "Deferred", "ShadowCaster")
EXPECTED_ROUTES = (8, 13, 8, 4)
SHARED_UNIFORMS = ("BlockPaint", "UnityDrawCallInfo", "UnityPerDraw", "UnityPerCamera")
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
    for name in SHARED_UNIFORMS:
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
    for name in SHARED_UNIFORMS:
        members = {}
        layouts = [buffer for stage in stages for buffer in stage if buffer["name"] == name]
        if len(layouts) != 2:
            continue
        for buffer in layouts:
            if buffer["structs"] or buffer["variant_size_bytes"] != layouts[0]["variant_size_bytes"]:
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
        stages = {}
        # A private per-pass keyword dimension lets Unity compile every
        # recovered program without assuming production keyword selection.
        names = [f"GT_ORIGINAL_921_P{index}_V{variant}"
                 for variant in range(1, len(row["routes"]))]
        for stage in ("vs", "fs"):
            programs = {}
            clauses = []
            for number, route in enumerate(row["routes"]):
                order = tuple(sorted(indices[name] for name in route["enabled"]))
                key = (row["subshader"], row["pass"], stage, route[stage], order)
                programs[number] = stage_sources[key]
                clauses.append({"enabled": [names[number - 1]] if number else [],
                                "program": number})
            stages[stage] = routed_stage(clauses, names, programs)
        pragmas = ["#pragma multi_compile __ " + " ".join(names)]
        program = ["HLSLPROGRAM", "#pragma target 5.0",
                   "#pragma vertex gt_vs_main", "#pragma fragment gt_fs_main",
                   "#pragma use_dxc vulkan", *pragmas,
                   stage_body(stages["vs"], stages["fs"]), "ENDHLSL"]
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--shader", type=Path, required=True)
    args = parser.parse_args()
    with args.shader.open("x", encoding="utf-8") as target:
        target.write(compose(args.private))


if __name__ == "__main__":
    main()
