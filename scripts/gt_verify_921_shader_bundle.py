"""Verify the private Unity bundle retains every requested original 921 route."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess

from scripts.gt_original_921_shaderlab import EXPECTED_ROUTES, NEXT_30_MATERIAL_ROUTES, SKIN_ROUTES, NEXT_SEVEN_7P11_ORIGINAL_ROUTES, expected_routes_for_shader
from scripts.restore_builtin_shaders import exported_shader_identity
from scripts.gt_runtime_keyword_contract import exact_independent_toggle_plan, strict_bundle_route_key
from scripts.gt_next23b_route_provenance import verify_candidate_route_manifest, verify_bundle_metadata
from scripts.gt_next23b_unity_receipt import (
    MAX_SOURCE_BYTES, MAX_RECEIPT_BYTES, MAX_MANIFEST_BYTES, MAX_BUNDLE_BYTES,
    read_snapshot, strict_json, verify_unity_receipt,
)
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


def inspect(bundle, source, receipt, engine_route_manifest=None, smolv_decoder=None, *, next30=False, next17=False, next7p11=False, fft_utilities=False, next23b=False, source_variant_manifest=None):
    import UnityPy

    shader = read_snapshot(source, MAX_SOURCE_BYTES) if next23b else source.read_bytes()
    expected_name = exported_shader_identity(shader.decode("utf-8"))
    if sum(bool(value) for value in (next30, next17, next7p11, fft_utilities, next23b)) > 1:
        raise ValueError("mutually_exclusive_original_shader_source_route_profiles")
    # This profile only validates serialized private candidate routes; never
    # interpret a matching source Shader48 name as an exported GUID.
    counts = ((512, 4, 128, 512) if next23b else
              (1,) * 7 if fft_utilities else
              NEXT_SEVEN_7P11_ORIGINAL_ROUTES if next7p11 else
              SKIN_ROUTES if next17 else
              NEXT_30_MATERIAL_ROUTES if next30 else
              expected_routes_for_shader(expected_name))
    if fft_utilities and expected_name != "UltimateWater/Utilities/FFT Utilities":
        raise ValueError("fft_utilities_exact_original_lookup_name_required")
    if fft_utilities and (smolv_decoder is None or engine_route_manifest is not None):
        raise ValueError("fft_utilities_requires_decoded_empty_keyword_routes")
    if next23b and (engine_route_manifest is None or smolv_decoder is None):
        raise ValueError("next23b_requires_actual_engine_routes_and_decoded_entrypoints")
    if next23b and source_variant_manifest is None:
        raise ValueError("next23b_requires_independent_source_variant_manifest")
    if not next23b and source_variant_manifest is not None:
        raise ValueError("source_variant_manifest_only_supported_for_next23b")
    provenance = {}
    bundle_input = str(bundle)
    if next23b:
        unity = strict_json(read_snapshot(receipt, MAX_RECEIPT_BYTES))
        route_bytes = read_snapshot(engine_route_manifest, MAX_MANIFEST_BYTES)
        source_bytes = read_snapshot(source_variant_manifest, MAX_SOURCE_BYTES)
        bundle_input = read_snapshot(bundle, MAX_BUNDLE_BYTES)
        provenance = verify_unity_receipt(unity, shader, route_bytes, source_bytes, bundle_input)
        packet = strict_json(route_bytes)
        validate_next23b_engine_manifest(packet)
        provenance.update(verify_candidate_route_manifest(source_bytes, shader, packet))
    else:
        unity = json.loads(receipt.read_text(encoding="utf-8"))
    if next23b and (unity.get("unityVersion") != "2021.3.45f2" or
                    unity.get("passCount") != 4 or unity.get("errors") != 0):
        raise ValueError("next23b_exact_unity_four_pass_compilation_required")
    if fft_utilities and (unity.get("passCount") != 7 or unity.get("errors") != 0):
        raise ValueError("fft_utilities_unity_seven_pass_compilation_unverified")
    if (unity.get("privateBundleCompiled") is not True
            or unity.get("androidVulkanOnly") is not True
            or (unity.get("registeredKeywordVariants") != 1 if fft_utilities
                else unity.get("registeredRoutes") != sum(counts))
            or unity.get("candidateSha256") != sha256(shader).hexdigest()):
        raise ValueError("original_921_unity_bundle_unverified")
    trees = [obj.read_typetree() for obj in UnityPy.load(bundle_input).objects
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
        if next23b:
            provenance.update(verify_bundle_metadata(source_bytes, tree["m_ParsedForm"], packet))
        else:
            packet = json.loads(engine_route_manifest.read_text(encoding="utf-8"))
        engine_routes = [{frozenset(row["keywords"]) for row in item["variants"]}
                         for item in packet["passes"]]
        if tuple(map(len, engine_routes)) != counts:
            raise ValueError("original_921_engine_route_contract_mismatch")
    result = verify_routes(tree["m_ParsedForm"], records(segments), engine_routes, smolv_decoder, counts, zero_keywords=fft_utilities, strict_engine=next23b)
    return dict(result, **provenance, candidate_sha256=unity["candidateSha256"],
                engine_keywords_verified=engine_routes is not None,
                vertex_and_fragment_entrypoints_verified=smolv_decoder is not None)


def validate_next23b_engine_manifest(packet):
    passes = packet.get("passes")
    if type(passes) is not list or len(passes) != 4:
        raise ValueError("next23b_exact_engine_passes_required")
    for row, count in zip(passes, (512, 4, 128, 512)):
        if row.get("passType") not in ("Normal", "ForwardBase", "ForwardAdd", "Deferred", "ShadowCaster"):
            raise ValueError("next23b_source_pass_type_required")
        variants = row.get("variants")
        if type(variants) is not list or len(variants) != count:
            raise ValueError("next23b_exact_engine_route_population_required")
        keys = []
        for variant in variants:
            names = variant.get("keywords")
            if (type(names) is not list or any(not isinstance(name, str) or
                    name.startswith("GT_ORIGINAL_921_") for name in names) or len(set(names)) != len(names)):
                raise ValueError("next23b_original_engine_keywords_required")
            keys.append(frozenset(names))
        if len(set(keys)) != count:
            raise ValueError("next23b_engine_route_collision")
        exact_independent_toggle_plan([sorted(key) for key in keys])


def verify_routes(parsed, entries=None, engine_routes=None, smolv_decoder=None, expected_counts=EXPECTED_ROUTES, *, zero_keywords=False, strict_engine=False):
    keywords = parsed["m_KeywordNames"]
    if strict_engine and (engine_routes is None or len(engine_routes) != len(expected_counts)):
        raise ValueError("original_runtime_exact_engine_manifest_required")
    if zero_keywords and (keywords or tuple(expected_counts) != (1,) * 7 or engine_routes is not None):
        raise ValueError("fft_utilities_bundle_requires_seven_zero_keyword_routes")
    subshaders = parsed["m_SubShaders"]
    if len(subshaders) != 1 or len(subshaders[0]["m_Passes"]) != len(expected_counts):
        raise ValueError("original_921_bundle_pass_topology_mismatch")
    verified = {}
    decoded = {}
    for stage in ("progVertex", "progFragment"):
        counts = []
        for index, (shader_pass, expected) in enumerate(
            zip(subshaders[0]["m_Passes"], expected_counts)
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
            strict_blobs = {}
            for _, _, row in rows:
                strict_key = strict_bundle_route_key(keywords, row, expected_keys) if strict_engine else None
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
                if strict_engine:
                    if entries is not None and strict_blobs.setdefault(strict_key, blob_index) != blob_index:
                        raise ValueError("original_runtime_bundle_ambiguous_keyword_program")
                    routes.add(strict_key)
                    continue
                indices = row["m_KeywordIndices"]
                if zero_keywords and (indices or row.get("m_GlobalKeywordIndices") or row.get("m_LocalKeywordIndices")):
                    raise ValueError("fft_utilities_bundle_nonempty_source_keywords")
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
    parser.add_argument("--source-variant-manifest", type=Path)
    parser.add_argument("--smolv-decoder", type=Path)
    variant_profile = parser.add_mutually_exclusive_group()
    variant_profile.add_argument("--next23b", action="store_true", help="Require original 1156 engine routes and decoded VS/FS")
    variant_profile.add_argument("--next30", action="store_true", help="Require verified original 30-material [8,13,8,2] routes")
    variant_profile.add_argument("--next17", action="store_true", help="Require SHA-original 17-material 3-pass [8,13,2] routes")
    variant_profile.add_argument("--next7p11", action="store_true", help="Require SHA-original distinct 7-material 3-pass [4,5,2] routes")
    variant_profile.add_argument("--fft-utilities", action="store_true", help="Require seven source passes with one empty-keyword VSFS route each")
    args = parser.parse_args()
    result = inspect(args.bundle, args.source, args.receipt, args.engine_route_manifest, args.smolv_decoder, next30=args.next30, next17=args.next17, next7p11=args.next7p11, fft_utilities=args.fft_utilities, next23b=args.next23b, source_variant_manifest=args.source_variant_manifest)
    args.out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
    print("GT_ORIGINAL_921_BUNDLE_ROUTES " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
