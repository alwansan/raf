"""Assemble the recovered four-pass shader for a private Unity compiler check."""
import argparse
import json
from pathlib import Path

from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_original_921_keyword_routes import routed_stage
from scripts.w1_depth_shaderlab import stage_body

PASS_MODES = ("ForwardBase", "ForwardAdd", "Deferred", "ShadowCaster")
EXPECTED_ROUTES = (8, 13, 8, 4)


def compose(private):
    layout = (private / "original-private-layout.txt").read_text(encoding="utf-8")
    routes = json.loads((private / "original-private-keyword-routes.json").read_text())
    manifest = json.loads((private / "original-private-variant-manifest.json").read_text())
    if tuple(len(row["routes"]) for row in routes) != EXPECTED_ROUTES:
        raise ValueError("original_921_unexpected_shaderlab_routes")
    stage_sources = {}
    for index, pair in enumerate(manifest["paired"]):
        for offset, stage in enumerate(("vs", "fs")):
            row = pair[stage]
            key = (pair["subshader"], pair["pass"], stage, row["program_ref"],
                   tuple(sorted(row["original_variant_metadata"]["m_KeywordIndices"])))
            stage_sources[key] = (private / f"bound-stage-{index * 2 + offset:03d}"
                                  / "varying-bound.hlsl").read_text(encoding="utf-8")
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
                   "#pragma vertex main", "#pragma fragment main", *pragmas,
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
