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
SKIN_ROUTES = (8, 13, 2)
BILLBOARD_ROUTES = (4, 5)
NEXT_30_MATERIAL_ROUTES = (8, 13, 8, 2)


def expected_routes_for_shader(name):
    return {"Skin_Amplify": SKIN_ROUTES, "BillboardFade": BILLBOARD_ROUTES}.get(name, EXPECTED_ROUTES)

# ShaderLab injects the pass macro. ForwardBase uses a directional light
# even when Unity does not expose DIRECTIONAL as a separate variant keyword.
ENGINE_FIXED_KEYWORDS = (
    frozenset({"DIRECTIONAL"}), frozenset(), frozenset(),
    frozenset({"UNITY_PASS_SHADOWCASTER"}),
)
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
PACKOFFSET = re.compile(r"packoffset\(c([0-9]+)(?:\.([xyzw]))?\)")


def ordered_buffer(definition):
    lines = definition.splitlines()
    members = []
    for line in lines[1:-1]:
        if not line.strip():
            continue
        offset = PACKOFFSET.search(line)
        if offset is None:
            return definition
        lane = int(offset[1]) * 4 + "xyzw".index(offset[2] or "x")
        members.append((lane, line))
    if len({lane for lane, _ in members}) != len(members):
        raise ValueError("original_921_duplicate_uniform_offset")
    return "\n".join([lines[0], *(line for _, line in sorted(members)), lines[-1]])


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
                    common[name]=ordered_buffer("\n".join([old[0],*declarations,old[-1]]))
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
        source = re.sub(r"\.gt_(?:vs|fs)_raft921_cb[0-9]+_pad([0-9]+)\b",
                        r".gt_struct_pad\1", source)
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
    buffer_declarations = [
        ordered_buffer(MEMBER.sub(lambda m: "" if m["var"] in globals_ else m[0], value))
        if value.startswith("cbuffer ") else value
        for value in common.values()
    ]
    return "\n".join([*type_declarations, *buffer_declarations, *globals_.values(), vertex, fragment])


def engine_route_keys(row, pass_index, pass_modes=PASS_MODES):
    # The original one-Pass source can have an explicit Always tag or no
    # LightMode. Neither has synthetic engine-fixed keywords.
    mode = pass_modes[pass_index]
    fixed_bank = (ENGINE_FIXED_KEYWORDS[PASS_MODES.index(mode)]
                  if mode in PASS_MODES else frozenset()
                  if mode in ("Always", "Untagged") else None)
    if fixed_bank is None:
        raise ValueError("original_921_unproved_source_pass_mode")
    fixed = fixed_bank & {
        name for route in row["routes"] for name in route["enabled"]
    }
    result = []
    for route in row["routes"]:
        names = frozenset(route["enabled"])
        if not fixed <= names:
            raise ValueError("original_921_expected_engine_pass_keyword_missing")
        result.append(tuple(sorted(names - fixed)))
    if len(set(result)) != len(result):
        raise ValueError("original_921_engine_keyword_route_collision")
    return result


def pass_modes_for_routes(counts):
    if counts == EXPECTED_ROUTES:
        return PASS_MODES
    if counts == SKIN_ROUTES:
        return ("ForwardBase", "ForwardAdd", "ShadowCaster")
    if counts == BILLBOARD_ROUTES:
        return ("ForwardBase", "ForwardAdd")
    if counts == NEXT_30_MATERIAL_ROUTES:
        return PASS_MODES
    raise ValueError("original_921_unexpected_shaderlab_routes")


NEXT_SEVEN_7P11_ORIGINAL_ROUTES = (4, 5, 2)
# Original post14 six-Material Shader48 source topology is one Pass and two
# VS/FS keyword pairs. Never infer the Pass LightMode from its route count.
NEXT_SIX_ORIGINAL_ROUTES = (2,)


def verified_source_next_six_pass_modes(manifest):
    """Derive a one-Pass LightMode ONLY from the SHA-original serialized tags.

    An absent original LightMode is preserved as untagged (Unity default),
    and an explicit original Always pass is not reclassified as ForwardBase.
    The single original owner/pass and tag lane are fail-closed verified.
    """
    rows = manifest.get("original_passes")
    if (type(rows) is not list or len(rows) != 1
            or type(rows[0]) is not dict
            or rows[0].get("subshader") != 0
            or rows[0].get("pass") != 0):
        raise ValueError("source_6_ambiguous_original_single_Pass_ownership")
    state = rows[0].get("original_state")
    if type(state) is not dict:
        raise ValueError("source_6_missing_original_render_state")
    tags = state.get("m_Tags")
    entries = tags.get("tags") if type(tags) is dict else None
    if type(entries) is not list:
        raise ValueError("source_6_missing_original_serialized_Pass_tags")
    modes = []
    valid = {mode.upper(): mode for mode in PASS_MODES}
    valid["ALWAYS"] = "Always"
    for entry in entries:
        if type(entry) not in (list, tuple) or len(entry) != 2:
            raise ValueError("source_6_malformed_original_Pass_tags")
        key, value = entry
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError("source_6_invalid_original_Pass_tag_values")
        if key.upper() == "LIGHTMODE":
            modes.append(valid.get(value.upper()))
    if not modes:
        return ("Untagged",)
    if len(modes) != 1 or modes[0] is None:
        raise ValueError("source_6_unknown_or_ambiguous_original_LightMode")
    return (modes[0],)



def verified_source_next_seven_pass_modes(manifest):
    """Use exact original 7-Material Shader48 m_State.m_Tags, not route-count guesses.

    This source-only bridge is deliberately restricted to a proven three-pass
    profile. It rejects an absent/ambiguous LightMode rather than silently
    substituting a mobile fallback, GUID, or approximated original pass.
    """
    rows = manifest.get("original_passes")
    if type(rows) is not list or len(rows) != 3:
        raise ValueError("source_7p11_missing_exact_three_original_passes")
    canonical = {name.upper(): name for name in PASS_MODES}
    selected = []
    for index, row in enumerate(rows):
        if (type(row) is not dict or row.get("subshader") != 0
                or row.get("pass") != index):
            raise ValueError("source_7p11_ambiguous_SubShader_Pass_ownership")
        state = row.get("original_state")
        if type(state) is not dict:
            raise ValueError("source_7p11_missing_original_render_state")
        tags = state.get("m_Tags")
        entries = tags.get("tags") if type(tags) is dict else None
        if type(entries) is not list:
            raise ValueError("source_7p11_missing_serialized_pass_tags")
        lightmode = []
        for entry in entries:
            if type(entry) not in (list, tuple) or len(entry) != 2:
                raise ValueError("source_7p11_malformed_serialized_pass_tags")
            key, value = entry
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("source_7p11_invalid_serialized_pass_tag_values")
            if key.upper() == "LIGHTMODE":
                lightmode.append(canonical.get(value.upper()))
        if len(lightmode) != 1 or lightmode[0] is None:
            raise ValueError("source_7p11_unknown_original_LightMode")
        selected.append(lightmode[0])
    if tuple(selected) != ("ForwardBase", "ForwardAdd", "ShadowCaster"):
        raise ValueError("source_7p11_original_Pass_LightMode_contract_not_proven")
    return tuple(selected)



def verified_source_next23b_pass_modes(manifest):
    """Read source tags only after exact NEXT23b topology/provenance checks.

    SHA authentication and bytecode stage verification happen upstream. Require
    their preserved per-variant link records here, never infer modes from counts.
    """
    rows, pairs = manifest.get('original_passes'), manifest.get('paired')
    if (type(rows) is not list or len(rows) != 4
            or type(pairs) is not list or len(pairs) != 1156
            or manifest.get('unpaired') != []):
        raise ValueError('source_next23b_exact_original_topology_required')
    by_pass = [0] * 4
    refs = {'vs': set(), 'fs': set()}
    for pair in pairs:
        if (type(pair) is not dict or type(pair.get('subshader')) is not int
                or pair['subshader'] != 0 or type(pair.get('pass')) is not int
                or not 0 <= pair['pass'] < 4):
            raise ValueError('source_next23b_ambiguous_pair_ownership')
        by_pass[pair['pass']] += 1
        for stage in ('vs', 'fs'):
            row = pair.get(stage)
            if type(row) is not dict:
                raise ValueError('source_next23b_missing_original_stage')
            ref = row.get('program_ref')
            metadata, link = row.get('original_variant_metadata'), row.get('original_D3D11_link')
            if (not isinstance(ref, str) or not re.fullmatch(r'program-[0-9]{3}', ref)
                    or type(row.get('bucket_ordinal')) is not int or row['bucket_ordinal'] < 0
                    or (row.get('player_bucket') is not None and
                        (type(row['player_bucket']) is not int or row['player_bucket'] < 0))
                    or type(metadata) is not dict or type(link) is not dict
                    or type(metadata.get('m_BlobIndex')) is not int
                    or metadata['m_BlobIndex'] < 0
                    or link.get('blob_index') != metadata['m_BlobIndex']
                    or type(link.get('segment_index')) is not int or link['segment_index'] < 0
                    or any(not isinstance(link.get(k), str) or not re.fullmatch(r'[0-9a-f]{64}', link[k])
                           for k in ('metadata_sha256', 'entry_sha256'))):
                raise ValueError('source_next23b_missing_original_D3D11_stage_provenance')
            refs[stage].add(ref)
    if (refs['vs'] & refs['fs'] or len(refs['vs'] | refs['fs']) != 134
            or refs['vs'] | refs['fs'] != {f'program-{i:03d}' for i in range(134)}):
        raise ValueError('source_next23b_original_134_stage_identity_drift')
    selected = []
    canonical = {name.upper(): name for name in (*PASS_MODES, 'Always')}
    for index, row in enumerate(rows):
        if (type(row) is not dict or type(row.get('subshader')) is not int
                or row['subshader'] != 0 or type(row.get('pass')) is not int
                or row['pass'] != index or type(row.get('matched_pairs')) is not int
                or row['matched_pairs'] != by_pass[index] or by_pass[index] == 0
                or type(row.get('unmatched_vertex')) is not int or row['unmatched_vertex'] != 0
                or type(row.get('unmatched_fragment')) is not int or row['unmatched_fragment'] != 0):
            raise ValueError('source_next23b_original_pass_population_drift')
        state = row.get('original_state')
        tags = state.get('m_Tags') if type(state) is dict else None
        entries = tags.get('tags') if type(tags) is dict else None
        if type(entries) is not list:
            raise ValueError('source_next23b_missing_original_pass_tags')
        modes = []
        for entry in entries:
            if (type(entry) not in (list, tuple) or len(entry) != 2
                    or any(not isinstance(v, str) for v in entry)):
                raise ValueError('source_next23b_malformed_original_pass_tags')
            if entry[0].upper() == 'LIGHTMODE':
                modes.append(canonical.get(entry[1].upper()))
        if len(modes) > 1 or modes and modes[0] is None:
            raise ValueError('source_next23b_unknown_or_duplicate_original_LightMode')
        selected.append(modes[0] if modes else 'Untagged')
    return tuple(selected)


def compose(private, engine_keywords=False, *, original_array_padding_zero=False):
    layout = (private / "original-private-layout.txt").read_text(encoding="utf-8")
    routes = json.loads((private / "original-private-keyword-routes.json").read_text())
    manifest = json.loads((private / "original-private-variant-manifest.json").read_text())
    counts = tuple(len(row["routes"]) for row in routes)
    pass_modes = (verified_source_next23b_pass_modes(manifest)
                  if len(counts) == 4 and sum(counts) == 1156 else
                  verified_source_next_six_pass_modes(manifest)
                  if counts == NEXT_SIX_ORIGINAL_ROUTES else
                  verified_source_next_seven_pass_modes(manifest)
                  if counts == NEXT_SEVEN_7P11_ORIGINAL_ROUTES
                  else pass_modes_for_routes(counts))
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
                (directory / "resource-bound.hlsl").read_text(encoding="utf-8"),
                layouts[offset],
                original_array_padding_zero=original_array_padding_zero)
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
    if len(blocks) != len(pass_modes) + 1:
        raise ValueError("original_921_shaderlab_layout_has_wrong_pass_count")
    parts = [blocks[0].replace('"LIGHTMODE" = "FORWARDBASE"', '"LightMode" = "ForwardBase"')]
    for index, row in enumerate(routes):
        engine_keys = engine_route_keys(row, index, pass_modes)
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
        if engine_keywords:
            names = sorted({name for key in engine_keys for name in key})
            clauses = [{"enabled": key, "program": number}
                       for number, key in enumerate(engine_keys)]
            pragmas = ["#pragma multi_compile __ " + name
                       for name in names if name != "INSTANCING_ON"]
            if "INSTANCING_ON" in names:
                pragmas.append("#pragma multi_compile_instancing")
            # Import needs a valid default even when the original pass
            # contains no empty-keyword permutation (e.g. ShadowCaster).
            code = routed_stage(clauses, names, programs).replace(
                "#error Unmapped_original_keyword_set", programs[0], 1)
        else:
            pragmas = ["#pragma multi_compile __ " + " ".join(names)]
            code = routed_stage(clauses, names, programs)
        program = ["HLSLPROGRAM", "#pragma target 5.0",
                   "#pragma vertex gt_vs_main", "#pragma fragment gt_fs_main",
                   "#pragma use_dxc vulkan", *pragmas,
                   code, "ENDHLSL"]
        remainder = blocks[index + 1]
        if index + 1 < len(pass_modes):
            mode = pass_modes[index + 1]
            remainder = remainder.replace(f'"LIGHTMODE" = "{mode.upper()}"', f'"LightMode" = "{mode}"')
        parts.extend(("\n".join(program), remainder))
    shader = "".join(parts)
    result = pass_coverage(shader)
    if (result["subshader_pass_counts"] != [len(pass_modes)]
            or result["passes_with_complete_program"] != len(pass_modes)):
        raise ValueError("original_921_incomplete_shaderlab")
    return shader


def verify_entrypoints(shader, directory, routes=None, *, original_hlsl_offsets=False):
    """Compile both real entries of every generated ShaderLab route."""
    from scripts.w1_recover_graphics_programs import command
    from scripts.t3_spirv_interface_name_drift import read_reflection

    blocks = re.findall(r"(?ms)^HLSLPROGRAM\n(.*?)^ENDHLSL$", shader)
    counts = EXPECTED_ROUTES if routes is None else tuple(map(len, routes))
    if len(blocks) != len(counts):
        raise ValueError("original_921_entrypoint_pass_count_mismatch")
    with tempfile.TemporaryDirectory(prefix="original-921-entrypoints-", dir=directory) as tmp:
        source = Path(tmp) / "route.hlsl"
        binary = Path(tmp) / "route.spv"
        for index, (block, count) in enumerate(zip(blocks, counts)):
            code = re.sub(r"(?m)^#pragma [^\n]*\n", "", block)
            source.write_text(code, encoding="utf-8")
            for variant in range(count):
                if routes is not None:
                    route = [f"-D{name}=1" for name in routes[index][variant]]
                else:
                    route = [f"-DGT_ORIGINAL_921_P{index}_V{variant}=1"] if variant else []
                for suffix, macro, entry in (
                    ("vert", "VERTEX", "gt_vs_main"),
                    ("frag", "FRAGMENT", "gt_fs_main"),
                ):
                    args = ["glslangValidator", "-V", "-D", "--target-env", "vulkan1.1"]
                    if original_hlsl_offsets is True:
                        # Source-authenticated NEXT6: the original typed
                        # CBuffer array otherwise gets optimized out.
                        args.extend(["--hlsl-offsets", "-Od"])
                    elif original_hlsl_offsets is not False:
                        raise ValueError("unverified_original_hlsl_offsets_opt_in")
                    args.extend(["-S", suffix, "-e", entry,
                                 f"-DSHADER_STAGE_{macro}=1"])
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
    parser.add_argument("--engine-keywords", action="store_true")
    parser.add_argument("--engine-route-manifest", type=Path)
    args = parser.parse_args()
    shader = compose(args.private, engine_keywords=args.engine_keywords)
    routes = None
    if args.engine_keywords:
        packet = json.loads((args.private / "original-private-keyword-routes.json").read_text())
        pass_modes = pass_modes_for_routes(tuple(len(row["routes"]) for row in packet))
        routes = [engine_route_keys(row, index, pass_modes) for index, row in enumerate(packet)]
    if args.verify_entrypoints:
        verify_entrypoints(shader, args.private, routes)
    if args.engine_route_manifest:
        if routes is None:
            parser.error("--engine-route-manifest requires --engine-keywords")
        with args.engine_route_manifest.open("x", encoding="utf-8") as output:
            json.dump({"passes": [{"variants": [{"keywords": list(key)} for key in keys]}
                                  for keys in routes]}, output)
    with args.shader.open("x", encoding="utf-8") as target:
        target.write(shader)


if __name__ == "__main__":
    main()
