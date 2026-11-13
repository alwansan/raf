"""Build private, exact per-pass keyword routes from the recovered ZIP2 packet."""
from collections import Counter, defaultdict
import re

from scripts.w1_recover_depth_passes import variant_key
from scripts.t3_particle108_source_propstate import serialize_properties
from scripts.w1_depth_shaderlab import quoted, render_state, tags


def keyword_routes(parsed, pairs, orphans, passes):
    names = parsed["m_KeywordNames"]
    flags = parsed["m_KeywordFlags"]
    if (len(names) != len(flags) or len(names) != len(set(names))
            or any(not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", name) for name in names)
            or any(type(flag) is not int or not 0 <= flag <= 255 for flag in flags)):
        raise ValueError("invalid_original_keyword_declarations")

    def enabled(row):
        metadata = row["original_variant_metadata"]
        if metadata.get("m_GlobalKeywordIndices") or metadata.get("m_LocalKeywordIndices"):
            raise ValueError("original_keyword_scope_requires_explicit_routing")
        indices = metadata.get("m_KeywordIndices", [])
        if (type(indices) is not list or len(indices) != len(set(indices))
                or any(type(index) is not int or not 0 <= index < len(names) for index in indices)):
            raise ValueError("invalid_original_enabled_keyword_set")
        return tuple(sorted(indices))

    routes = {(p["subshader"], p["pass"]): {} for p in passes}
    unmatched = defaultdict(set)
    for pair in pairs:
        vs, fs = pair["vs"], pair["fs"]
        if (vs["player_bucket"] != fs["player_bucket"]
                or variant_key(vs["original_variant_metadata"]) != variant_key(fs["original_variant_metadata"])):
            raise ValueError("original_stage_pair_keyword_mismatch")
        scope = (pair["subshader"], pair["pass"])
        keywords = enabled(vs)
        if keywords in routes[scope]:
            raise ValueError("keyword_route_collision_across_original_tiers_or_buckets")
        routes[scope][keywords] = (vs["program_ref"], fs["program_ref"])

    for orphan in orphans:
        scope = (orphan["subshader"], orphan["pass"])
        keywords = enabled(orphan["variant"])
        if orphan["stage"] != 1 or keywords in routes[scope] or keywords in unmatched[scope]:
            raise ValueError("unmatched_stage_cannot_be_routed_by_original_keywords")
        unmatched[scope].add(keywords)

    packet = []
    flag_counts = Counter()
    for (subshader, shader_pass), variants in routes.items():
        if not variants:
            raise ValueError("missing_original_pass_routes")
        all_indices = sorted({index for key in (*variants, *unmatched[subshader, shader_pass])
                              for index in key})
        flag_counts.update(flags[index] for index in all_indices)
        packet.append({
            "subshader": subshader,
            "pass": shader_pass,
            "keyword_universe": [{"name": names[index], "serialized_flag": flags[index]}
                                 for index in all_indices],
            "routes": [{"enabled": [names[index] for index in key], "vs": vs, "fs": fs}
                       for key, (vs, fs) in sorted(variants.items())],
            "unmatched_vertex_keywords": [[names[index] for index in key]
                                          for key in sorted(unmatched[subshader, shader_pass])],
        })

    return packet, {
        "source_exact_keyword_routes_by_pass": [len(row["routes"]) for row in packet],
        "source_keyword_universe_size_by_pass": [len(row["keyword_universe"]) for row in packet],
        "source_unmatched_vertex_keyword_sets_by_pass": [
            len(row["unmatched_vertex_keywords"]) for row in packet
        ],
        "source_used_flag_byte_population_across_passes": dict(flag_counts),
    }


def shaderlab_layout(parsed, passes):
    properties, counts = serialize_properties(parsed, allow_hidden_and_toggle=True)
    if counts["original_authored_property_count"] != 35:
        raise ValueError("original_921_property_count_drift")
    lines = ["// Private layout fragment. Attach recovered HLSL before import.",
             "Shader " + quoted(parsed["m_Name"]) + " {", properties]
    states = {(row["subshader"], row["pass"]): row["original_state"] for row in passes}
    for sub_index, sub in enumerate(parsed["m_SubShaders"]):
        lines.extend(["SubShader {", "LOD " + str(sub["m_LOD"]), tags(sub["m_Tags"])])
        for pass_index in range(len(sub["m_Passes"])):
            lines.extend(["Pass {",
                          render_state(states[sub_index, pass_index], allow_selective_color_mask=True),
                          "// Original stage programs attach here", "}"])
        lines.append("}")
    for field, directive in (("m_FallbackName", "Fallback"), ("m_CustomEditorName", "CustomEditor")):
        if parsed.get(field):
            lines.append(directive + " " + quoted(parsed[field]))
    lines.append("}")
    return "\n".join(lines) + "\n", {
        **counts,
        "original_property_hide_in_inspector_count": sum(
            prop["m_Flags"] == 1 for prop in parsed["m_PropInfo"]["m_Props"]),
        "original_property_toggle_count": sum(
            prop["m_Attributes"] == ["Toggle"] for prop in parsed["m_PropInfo"]["m_Props"]),
        "original_render_states_serialized": len(states),
    }


def routed_stage(routes, keyword_names, stage_sources):
    """Emit one HLSL branch for each complete keyword set in a pass."""
    lines = []
    for route in routes:
        enabled = set(route["enabled"])
        condition = " && ".join(
            ("" if name in enabled else "!") + f"defined({name})"
            for name in keyword_names
        ) or "1"
        lines.extend([("#elif " if lines else "#if ") + condition,
                      stage_sources[route["program"]]])
    return "\n".join([*lines, "#else", "#error Unmapped_original_keyword_set", "#endif", ""])


def compile_routed_stages(packet, private):
    """Exercise every exact source route with glslang and compare its emitted code."""
    from scripts.w1_recover_graphics_programs import command

    passed = 0
    for row in packet:
        names = [entry["name"] for entry in row["keyword_universe"]]
        for stage, suffix in (("vs", "vert"), ("fs", "frag")):
            programs = {route[stage] for route in row["routes"]}
            sources = {program: (private / program / "private.hlsl").read_text()
                       for program in programs}
            routes = [{"enabled": route["enabled"], "program": route[stage]}
                      for route in row["routes"]]
            source = private / f"route-{row['subshader']}-{row['pass']}.{suffix}.hlsl"
            source.write_text(routed_stage(routes, names, sources), encoding="utf-8")
            binary = source.with_suffix(".spv")
            for route in routes:
                args = ["glslangValidator", "-V", "-D", "-S", suffix, "-e", "main",
                        "-o", str(binary)]
                args.extend("-D" + name + "=1" for name in route["enabled"])
                if not command([*args, str(source)]):
                    raise ValueError("original_921_routed_stage_compile_failed")
                if not command(["spirv-val", "--target-env", "vulkan1.1", str(binary)]):
                    raise ValueError("original_921_routed_stage_validation_failed")
                baseline = private / route["program"] / "roundtrip.spv"
                if binary.read_bytes() != baseline.read_bytes():
                    raise ValueError("original_921_route_binary_differs_from_selected_stage")
                passed += 1
    return passed
