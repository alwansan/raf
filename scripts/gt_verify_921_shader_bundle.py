"""Verify the private Unity bundle retains every requested original 921 route."""
import argparse
import json
from pathlib import Path
import struct
import subprocess

from scripts.gt_original_921_shaderlab import EXPECTED_ROUTES
from scripts.restore_builtin_shaders import exported_shader_identity
from scripts.w1_recover_depth_passes import stage_variants
from scripts.w1_recover_graphics_programs import decoded_platforms, records


def spirv_execution_models(data):
    if len(data) < 20 or len(data) % 4 or data[:4] != b"\x03\x02\x23\x07":
        raise ValueError("original_921_invalid_spirv_module")
    words = struct.unpack(f"<{len(data) // 4}I", data)
    models = set()
    index = 5
    while index < len(words):
        count, opcode = divmod(words[index], 1 << 16)
        if not count or index + count > len(words):
            raise ValueError("original_921_invalid_spirv_instruction")
        if opcode == 15:
            if count < 4:
                raise ValueError("original_921_invalid_spirv_entrypoint")
            models.add(words[index + 1])
        index += count
    return models


def vulkan_blob_header_counts(entries, rows):
    indices = {row.get("m_BlobIndex") for _, _, row in rows}
    if any(type(index) is not int or not 0 <= index < len(entries) for index in indices):
        raise ValueError("original_921_invalid_vulkan_blob_index")
    counts = {}
    for index in indices:
        _, bytecode = entries[index]
        count = bytecode.count(b"LOMS") + bytecode.count(b"\x03\x02\x23\x07")
        counts[count] = counts.get(count, 0) + 1
    return dict(sorted(counts.items()))


def unity_vulkan_modules(blob):
    """Read the serialized Unity 2021 subprogram and its Vulkan snippet table."""
    if len(blob) < 32 or struct.unpack_from("<I", blob)[0] < 202012090:
        raise ValueError("original_921_unknown_vulkan_program_header")
    offset = 28
    keywords = struct.unpack_from("<I", blob, 24)[0]
    if keywords > 256:
        raise ValueError("original_921_oversized_vulkan_keyword_table")
    for _ in range(keywords):
        if offset + 4 > len(blob):
            raise ValueError("original_921_truncated_vulkan_keyword")
        size = struct.unpack_from("<I", blob, offset)[0]
        offset += 4 + (size + 3) // 4 * 4
    if offset + 4 > len(blob):
        raise ValueError("original_921_truncated_vulkan_program")
    size = struct.unpack_from("<I", blob, offset)[0]
    program = blob[offset + 4:offset + 4 + size]
    if len(program) != size:
        raise ValueError("original_921_truncated_vulkan_program")
    boundary = len(program)
    for entry_offset in range(4, 52, 8):
        if entry_offset + 8 > boundary:
            break
        start, length = struct.unpack_from("<II", program, entry_offset)
        if not length:
            continue
        if start < entry_offset + 8 or start + length > len(program):
            raise ValueError("original_921_vulkan_module_range")
        boundary = min(boundary, start)
        yield program[start:start + length]


def vulkan_execution_models(blob, decoder):
    models = set()
    for module in unity_vulkan_modules(blob):
        if module[:4] == b"LOMS":
            result = subprocess.run([decoder], input=module, capture_output=True, timeout=15)
            if result.returncode:
                raise ValueError("original_921_smolv_decode_failed")
            module = result.stdout
        models.update(spirv_execution_models(module))
    return models


def inspect(bundle, source, receipt, engine_route_manifest=None, smolv_decoder=None):
    import UnityPy

    expected_name = exported_shader_identity(source.read_text(encoding="utf-8"))
    unity = json.loads(receipt.read_text(encoding="utf-8"))
    if (unity.get("privateBundleCompiled") is not True
            or unity.get("androidVulkanOnly") is not True
            or unity.get("registeredRoutes") != sum(EXPECTED_ROUTES)):
        raise ValueError("original_921_unity_bundle_unverified")
    trees = [obj.read_typetree() for obj in UnityPy.load(str(bundle)).objects
             if obj.type.name == "Shader"]
    matches = [tree for tree in trees if tree["m_ParsedForm"]["m_Name"] == expected_name]
    if len(matches) != 1 or list(matches[0]["platforms"]) != [18]:
        raise ValueError("original_921_vulkan_shader_missing_or_ambiguous")
    tree = matches[0]
    [(platform, segments)] = list(decoded_platforms(tree))
    if platform != 18:
        raise ValueError("original_921_bundle_platform_table_mismatch")
    engine_routes = None
    if engine_route_manifest is not None:
        packet = json.loads(engine_route_manifest.read_text(encoding="utf-8"))
        engine_routes = [{frozenset(row["keywords"]) for row in item["variants"]}
                         for item in packet["passes"]]
        if tuple(map(len, engine_routes)) != EXPECTED_ROUTES:
            raise ValueError("original_921_engine_route_contract_mismatch")
    return verify_routes(tree["m_ParsedForm"], records(segments), engine_routes, smolv_decoder)


def verify_routes(parsed, entries=None, engine_routes=None, smolv_decoder=None):
    keywords = parsed["m_KeywordNames"]
    subshaders = parsed["m_SubShaders"]
    if len(subshaders) != 1 or len(subshaders[0]["m_Passes"]) != len(EXPECTED_ROUTES):
        raise ValueError("original_921_bundle_pass_topology_mismatch")
    verified = {}
    decoded = {}
    for stage in ("progVertex", "progFragment"):
        counts = []
        for index, (shader_pass, expected) in enumerate(
            zip(subshaders[0]["m_Passes"], EXPECTED_ROUTES)
        ):
            prefix = f"GT_ORIGINAL_921_P{index}_V"
            expected_keys = engine_routes[index] if engine_routes is not None else None
            engine_names = set().union(*expected_keys) if expected_keys is not None else set()
            rows = stage_variants(shader_pass[stage])
            if entries is not None and stage == "progFragment" and not rows:
                rows = stage_variants(shader_pass["progVertex"])
                if smolv_decoder is None:
                    raise ValueError(
                        f"original_921_fragment_table_empty pass={index} "
                        f"vertexRows={len(rows)} moduleHeadersByBlob={vulkan_blob_header_counts(entries, rows)}"
                    )
            routes = set()
            for _, _, row in rows:
                if entries is not None:
                    blob_index = row.get("m_BlobIndex")
                    if type(blob_index) is not int or not 0 <= blob_index < len(entries):
                        raise ValueError(
                            f"original_921_bundle_route_blob_missing stage={stage} pass={index}"
                        )
                    if smolv_decoder is not None:
                        if blob_index not in decoded:
                            decoded[blob_index] = vulkan_execution_models(entries[blob_index][1], smolv_decoder)
                        if (0 if stage == "progVertex" else 4) not in decoded[blob_index]:
                            continue
                indices = row["m_KeywordIndices"]
                if any(type(key) is not int or not 0 <= key < len(keywords) for key in indices):
                    raise ValueError("original_921_bundle_keyword_index_invalid")
                names = {keywords[key] for key in indices}
                if expected_keys is not None:
                    routes.add(frozenset(names & engine_names))
                    continue
                active = {name for name in names if name.startswith(prefix)}
                if len(active) > 1:
                    raise ValueError("original_921_bundle_route_conflict")
                routes.update(active or {""})
            required = {""} | {prefix + str(variant) for variant in range(1, expected)}
            if expected_keys is not None:
                missing_count = len(expected_keys - routes)
                if missing_count:
                    missing_instanced = sum("INSTANCING_ON" in key for key in expected_keys - routes)
                    raise ValueError(
                        f"original_921_engine_routes_missing stage={stage} pass={index} "
                        f"missing={missing_count} missingInstanced={missing_instanced} entries={len(rows)}"
                    )
                counts.append(len(expected_keys))
                continue
            if routes != required:
                missing = [variant for variant in range(expected)
                           if (prefix + str(variant) if variant else "") not in routes]
                gpu_types = sorted({row.get("m_GpuProgramType", -1) for _, _, row in rows})
                raise ValueError(
                    "original_921_bundle_route_population_mismatch "
                    f"stage={stage} pass={index} missingRoutes={missing} "
                    f"entries={len(rows)} shaderKeywords={len(keywords)} gpuTypes={gpu_types}"
                )
            counts.append(len(routes))
        verified[stage] = counts
    return {"vulkan_platform_only": True, "compiled_program_table_verified": entries is not None,
            "vertex_routes_by_pass": verified["progVertex"],
            "fragment_routes_by_pass": verified["progFragment"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("bundle", "source", "receipt", "out"):
        parser.add_argument("--" + option, required=True, type=Path)
    parser.add_argument("--engine-route-manifest", type=Path)
    parser.add_argument("--smolv-decoder", type=Path)
    args = parser.parse_args()
    result = inspect(args.bundle, args.source, args.receipt, args.engine_route_manifest, args.smolv_decoder)
    args.out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    print("GT_ORIGINAL_921_BUNDLE_ROUTES " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
