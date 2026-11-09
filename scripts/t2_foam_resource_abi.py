"""T2 WATER-001: private original Foam texture/sampler interface evidence.

Uses B20 authenticated 4-stage Foam packet plus exact B25 original object and
B17's bounded original numeric descriptor parser. Reports only original numeric
table field counts/digests and Vulkan descriptor category/slot numbers.
Does NOT infer Unity material bindings or synthesize a ShaderLab program.
"""
import argparse
import json
from pathlib import Path

from scripts.b17_spectrum_stage_descriptors import RESOURCE_FIELDS, stage_profile
from scripts.b20_foam_cb_descriptor_lineage import SOURCE_SLOTS, probe as b20_probe, reflect
from scripts.t2_foam_member_abi import STAGES, original_source_tree, _physical
from scripts.b25_foam_cb_namebridge import inspect_parsed as b25_inspect
from scripts.b24_original_foam_stage_translation import TARGET, validate_stage

# SPIRV-Cross --reflect keys; not the original source's authored HLSL semantics.
SPV_RESOURCE_CATEGORIES = (
    "textures", "images", "separate_images", "separate_samplers",
    "subpass_inputs", "ssbos", "atomic_counters", "acceleration_structures",
)
MAX_RESOURCE_ROWS = 128
MAX_BOUND_INDEX = 255


def safe_compiled_resources(reflection):
    """Extract only descriptor type-category/set/binding, never private symbols."""
    if not isinstance(reflection, dict):
        raise ValueError("Malformed translated reflection root")
    rows = []
    for category in SPV_RESOURCE_CATEGORIES:
        obj = reflection.get(category, [])
        if not isinstance(obj, list) or len(obj) > MAX_RESOURCE_ROWS:
            raise ValueError("Invalid translated resource list")
        seen = set()
        for resource in obj:
            if not isinstance(resource, dict):
                raise ValueError("Non-record translated resource binding")
            dset, binding = resource.get("set"), resource.get("binding")
            if (type(dset) is not int or type(binding) is not int or
                    not (0 <= dset <= MAX_BOUND_INDEX) or
                    not (0 <= binding <= MAX_BOUND_INDEX) or
                    (dset, binding) in seen):
                raise ValueError("Invalid or duplicate translated resource slot")
            seen.add((dset, binding))
            rows.append({"category": category, "set": dset, "binding": binding})
    return sorted(rows, key=lambda r: (r["category"], r["set"], r["binding"]))


def original_stage_resource_profiles(parsed):
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original Foam identity mismatch")
    evidence = b25_inspect(parsed)
    if (evidence.get("original_passes") != 2 or
            evidence.get("authenticated_stage_count") != 4 or
            evidence.get("matched_constant_buffer_bindings") != 8):
        raise ValueError("Original Foam CB/stage provenance absent")
    passes = parsed["m_SubShaders"][0]["m_Passes"]
    result = {}
    for pi, stage in STAGES:
        prog = passes[pi]["progVertex" if stage == 1 else "progFragment"]
        validate_stage(prog, stage, {"original_pass": pi})
        result[(pi, stage)] = stage_profile(prog)
    if set(result) != set(STAGES):
        raise ValueError("Original Foam resource stage coverage missing")
    return result


def combine(profiles, compiled):
    """No name/register/upload equivalence claims even if counts match."""
    if set(profiles) != set(STAGES) or set(compiled) != set(STAGES):
        raise ValueError("Foam source/compiled stage coverage mismatch")
    rows = []
    for pi, stage in STAGES:
        original = profiles[(pi, stage)]
        translated = safe_compiled_resources(compiled[(pi, stage)])
        if (not isinstance(original, dict) or
                type(original.get("descriptor_rows")) is not int or
                not isinstance(original.get("table_rows"), dict) or
                not isinstance(original.get("numeric_descriptor_sha256"), str)):
            raise ValueError("Invalid source-authenticated resource descriptor")
        if any(key not in RESOURCE_FIELDS or type(n) is not int or n < 0 or n > 256
               for key, n in original["table_rows"].items()):
            raise ValueError("Unsupported source descriptor table rows")
        if original["descriptor_rows"] != sum(original["table_rows"].values()):
            raise ValueError("Original descriptor census inconsistent")
        rows.append({
            "pass": pi, "stage_code": stage,
            "original_numeric_table_rows": original["table_rows"],
            "original_numeric_descriptor_sha256": original["numeric_descriptor_sha256"],
            "original_descriptor_rows": original["descriptor_rows"],
            "translated_non_cb_resource_count": len(translated),
            "translated_resource_bindings": translated,
            "original_to_translated_texture_sampler_name_binding_verified": False,
            "original_sampler_state_verified": False,
            "unity_shaderlab_or_device_verified": False,
        })
    return {
        "status": "original_foam_resource_interface_observed",
        "original_passes": 2,
        "original_stages": 4,
        "source_stage_descriptor_rows": sum(x["original_descriptor_rows"] for x in rows),
        "compiled_non_cb_descriptors": sum(x["translated_non_cb_resource_count"] for x in rows),
        "rows": rows,
        "shaderlab_or_unity_import_verified": False,
        "original_name_register_join_verified": False,
        "private_shader_symbols_published": False,
        "device_pixels_verified": False,
    }



# Frozen genuine source and current translation interface from CI41939956032;
# proves bounded resource *cardinality*, NOT which original texture is which.
ORIGINAL_TEXTURES_PER_STAGE = {(0, 1): 0, (0, 0): 5, (1, 1): 0, (1, 0): 1}
COMPILED_NUMERIC_RESOURCE_BINDINGS = {
    (0, 1): (),
    (0, 0): (("separate_images", 0, 6), ("separate_images", 0, 7),
             ("separate_images", 0, 8), ("separate_images", 0, 9),
             ("separate_images", 0, 10), ("separate_samplers", 0, 1),
             ("separate_samplers", 0, 2), ("separate_samplers", 0, 3),
             ("separate_samplers", 0, 4), ("separate_samplers", 0, 5)),
    (1, 1): (),
    (1, 0): (("separate_images", 0, 2), ("separate_samplers", 0, 1)),
}


def verify_genuine_texture_sampler_pair_count(report):
    """Fail closed on lost original source textures or compiled descriptor side."""
    if (not isinstance(report, dict) or report.get("status") !=
            "original_foam_resource_interface_observed" or
            report.get("original_stages") != 4 or
            not isinstance(report.get("rows"), list) or len(report["rows"]) != 4):
        raise ValueError("Original resource audit prerequisite absent")
    seen = set()
    for row in report["rows"]:
        if not isinstance(row, dict):
            raise ValueError("Invalid original resource stage")
        # bool and integral floats compare equal to int tuple keys in Python.
        # A report must preserve the exact serialized stage identifier types.
        if type(row.get("pass")) is not int or type(row.get("stage_code")) is not int:
            raise ValueError("Malformed original Foam stage identifier")
        key = row["pass"], row["stage_code"]
        if key not in ORIGINAL_TEXTURES_PER_STAGE or key in seen:
            raise ValueError("Original Foam pass/stage duplicate or unknown")
        seen.add(key)
        fields = row.get("original_numeric_table_rows")
        if (not isinstance(fields, dict) or fields.get("m_TextureParams") !=
                ORIGINAL_TEXTURES_PER_STAGE[key] or
                fields.get("m_Samplers") != 0 or fields.get("m_UAVParams") != 0):
            raise ValueError("Authentic original Foam source resource table drift")
        # A caller may pass a deserialized or mutated report, not combine() output.
        # Revalidate source metadata before accepting the numeric ABI evidence.
        descriptor_rows = row.get("original_descriptor_rows")
        digest = row.get("original_numeric_descriptor_sha256")
        if (set(fields) != {"m_TextureParams", "m_Samplers", "m_UAVParams"} or
                any(type(value) is not int or value < 0 or value > 256
                    for value in fields.values()) or
                type(descriptor_rows) is not int or
                descriptor_rows != sum(fields.values()) or
                not isinstance(digest, str) or len(digest) != 64 or
                any(char not in "0123456789abcdef" for char in digest)):
            raise ValueError("Malformed original Foam source metadata")
        bindings = row.get("translated_resource_bindings")
        if not isinstance(bindings, list):
            raise ValueError("Compiled Foam texture/sampler bindings unavailable")
        # Reports are untrusted even when claiming authenticated sources.
        # Reject malformed or duplicated slots before any parity assertion.
        if any(not isinstance(r, dict) or
               r.get("category") not in ("separate_images", "separate_samplers") or
               type(r.get("set")) is not int or
               type(r.get("binding")) is not int or
               not (0 <= r["set"] <= MAX_BOUND_INDEX) or
               not (0 <= r["binding"] <= MAX_BOUND_INDEX)
               for r in bindings):
            raise ValueError("Malformed translated Foam binding")
        numeric = tuple(sorted(
            (r["category"], r["set"], r["binding"]) for r in bindings
        ))
        if len(set(numeric)) != len(numeric):
            raise ValueError("Duplicate translated Foam binding")
        if numeric != COMPILED_NUMERIC_RESOURCE_BINDINGS[key]:
            raise ValueError("Translated Foam sampled image/sampler numeric ABI drift")
        count = ORIGINAL_TEXTURES_PER_STAGE[key]
        images = sum(r["category"] == "separate_images" for r in bindings)
        samplers = sum(r["category"] == "separate_samplers" for r in bindings)
        if images != count or samplers != count:
            raise ValueError("Missing actual translated image/sampler pair")
    if seen != set(ORIGINAL_TEXTURES_PER_STAGE):
        raise ValueError("Authentic Foam stage coverage incomplete")
    report["authenticated_original_texture_rows"] = 6
    report["authenticated_translated_sampled_images"] = 6
    report["authenticated_translated_separate_samplers"] = 6
    report["original_to_compiled_resource_cardinality_verified"] = True
    report["original_texture_to_hlsl_sampler_identity_verified"] = False
    return report


def audit(source, packet, manifest):
    source, packet, manifest = map(lambda p: Path(p).absolute(), (source, packet, manifest))
    if (not source.is_dir() or not packet.is_dir() or
            not manifest.is_file() or not all(_physical(p) for p in (source, packet, manifest))):
        raise ValueError("Private original/packet path unsafe")
    cb_evidence = b20_probe(packet, manifest)
    if (cb_evidence["authenticated_original_foam_stage_count"] != 4 or
            not cb_evidence["all_spirv_set0_bindings_numerically_coincide"]):
        raise ValueError("Source-authenticated Foam four-stage packet invalid")
    source_profile = original_stage_resource_profiles(original_source_tree(source))
    compiled = {key: reflect(packet / ("pass%d-stage%d" % key) / "original.spv")
                for key in STAGES}
    return verify_genuine_texture_sampler_pair_count(combine(source_profile, compiled))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "packet", "manifest", "out"):
        p.add_argument("--" + name, type=Path, required=True)
    args = p.parse_args()
    try:
        out = args.out.absolute()
        if (out.exists() or not out.parent.is_dir() or not _physical(out)
                or out.is_relative_to(args.packet.absolute())
                or out.is_relative_to(args.source.absolute())):
            raise ValueError("Unsafe aggregate report destination")
        report = audit(args.source, args.packet, args.manifest)
        out.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        print("T2_FOAM_RESOURCE_ABI " + json.dumps({
            "status": report["status"], "original_stages": 4,
            "original_descriptor_rows": report["source_stage_descriptor_rows"],
            "compiled_non_cb_descriptors": report["compiled_non_cb_descriptors"],
            "unity_or_device_verified": False, "private_code_published": False
        }))
        return 0
    except BaseException as exc:
        # No private program, path, name or exception string in logs.
        print("T2_FOAM_RESOURCE_ABI " + json.dumps({
            "status": "blocked", "failure_type": type(exc).__name__,
            "unity_or_device_verified": False, "private_code_published": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
