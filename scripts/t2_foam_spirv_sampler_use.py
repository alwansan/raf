"""T2 WATER-001: original-derived SPIR-V image/sampler *use* by numeric slot.

Read only genuine B20 staged SPIR-V in private scratch. A count or source-name
match is not a use edge. Walk direct OpLoad/OpCopyObject -> OpSampledImage ->
OpImageSample* def-use; reject dynamic/ambiguous provenance rather than making
up a Unity Material texture or original sampler state. Never output SPIR-V IDs,
symbol strings, binary source, HLSL or disassembly.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from scripts.t2_foam_member_abi import STAGES, _physical
from scripts.t2_foam_resource_abi import (
    COMPILED_NUMERIC_RESOURCE_BINDINGS,
    ORIGINAL_TEXTURES_PER_STAGE,
    audit as original_resource_audit,
)

MAX_TEXT = 8 * 1024 * 1024
MAX_LINES = 180_000
MAX_SAMPLES = 4096
MAX_BINDING = 255
MAX_ALIAS_DEPTH = 32
RESULT = re.compile(r"^(%[^\s=]+)\s*=\s*(Op[A-Za-z0-9_]+)(?:\s+(.*))?$")
DIRECT = re.compile(r"^(Op[A-Za-z0-9_]+)(?:\s+(.*))?$")


def numeric_binding(value):
    if not isinstance(value, str) or not value.isdecimal():
        raise ValueError("Non-numeric SPIR-V descriptor binding")
    n = int(value)
    if n > MAX_BINDING:
        raise ValueError("SPIR-V binding outside bounded descriptor range")
    return n


def trace_sampled_pairs(text, expected_image_slots, expected_sampler_slots):
    """Only authentic *used* OpSampledImage chains; public output numeric only."""
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        raise ValueError("Invalid bounded SPIR-V disassembly")
    if not isinstance(expected_image_slots, (list, tuple, set)) or not isinstance(
            expected_sampler_slots, (list, tuple, set)):
        raise ValueError("Invalid typed expected descriptors")
    for slots in (expected_image_slots, expected_sampler_slots):
        if len(slots) > 128:
            raise ValueError("Descriptor limit exceeded")
        for pair in slots:
            if (not isinstance(pair, tuple) or len(pair) != 2 or
                    any(type(x) is not int or x < 0 or x > MAX_BINDING for x in pair)):
                raise ValueError("Expected numeric bindings invalid")
        if len(slots) != len(set(slots)):
            raise ValueError("Duplicate expected descriptor slot")
    images, samplers = set(expected_image_slots), set(expected_sampler_slots)
    if images & samplers:
        raise ValueError("Image/sampler categories overlap numerically")
    bindings, vars_uc, aliases, sampled, sample_ids = {}, set(), {}, {}, []
    line_count = 0
    for line in text.splitlines():
        line_count += 1
        if line_count > MAX_LINES:
            raise ValueError("Unbounded SPIR-V disassembly line count")
        line = line.strip()
        # OpName/OpString may contain private symbols or fake instructions.
        if not line or line.startswith(";") or line.startswith("OpName ") or line.startswith(
                "OpMemberName ") or line.startswith("OpString "):
            continue
        # Other real SPIR-V instructions never require embedded string values
        # for the bindings/SSA operations analyzed below.
        match = RESULT.fullmatch(line) if line.startswith("%") else DIRECT.fullmatch(line)
        if match is None:
            continue
        if line.startswith("%"):
            result, op, raw_args = match.groups()
        else:
            result, (op, raw_args) = None, match.groups()
        args = raw_args.split() if raw_args else []
        if op == "OpDecorate" and len(args) >= 3 and args[1] in (
                "Binding", "DescriptorSet"):
            varid, category = args[:2]
            if not varid.startswith("%"):
                raise ValueError("Decorated descriptor variable invalid")
            value = numeric_binding(args[2])
            key = varid, category
            if key in bindings:
                raise ValueError("Duplicate SPIR-V descriptor decoration")
            bindings[key] = value
        elif op == "OpVariable" and result and len(args) >= 2:
            if args[1] == "UniformConstant":
                vars_uc.add(result)
        elif op == "OpLoad" and result and len(args) >= 2:
            aliases[result] = args[1]
        elif op == "OpCopyObject" and result and len(args) >= 2:
            aliases[result] = args[1]
        elif op in ("OpAccessChain", "OpInBoundsAccessChain", "OpPtrAccessChain",
                    "OpPhi", "OpSelect", "OpFunctionCall") and result:
            # Do not mistake dynamic descriptor indexing or Phi selection
            # for a provably unique resource edge.
            aliases[result] = None
        elif op == "OpSampledImage" and result and len(args) >= 3:
            if result in sampled:
                raise ValueError("Duplicate sampled-image result")
            sampled[result] = (args[1], args[2])
        elif op.startswith("OpImageSample") or op in (
                "OpImageGather", "OpImageDrefGather", "OpImageQueryLod"):
            if len(args) < 2:
                raise ValueError("Sample instruction missing sampled-image operand")
            sample_ids.append(args[1])
            if len(sample_ids) > MAX_SAMPLES:
                raise ValueError("Unbounded shader texture sample calls")

    def follow(identifier):
        seen = set()
        for _ in range(MAX_ALIAS_DEPTH):
            if identifier in seen:
                raise ValueError("Cyclic SPIR-V SSA resource alias")
            seen.add(identifier)
            if identifier not in aliases:
                return identifier
            identifier = aliases[identifier]
            if identifier is None:
                raise ValueError("Ambiguous dynamic SPIR-V resource alias")
        raise ValueError("Excessive SPIR-V SSA alias depth")

    def slot(identifier, category):
        ptr = follow(identifier)
        if ptr not in vars_uc:
            raise ValueError("Used sampler/image cannot be traced to UniformConstant")
        ds, bind = bindings.get((ptr, "DescriptorSet")), bindings.get((ptr, "Binding"))
        if ds is None or bind is None:
            raise ValueError("Used sampler/image descriptor decoration missing")
        pair = ds, bind
        if pair not in (images if category == "image" else samplers):
            raise ValueError("Used sampled descriptor not in pinned source interface")
        return pair

    pairs = []
    for sampled_ref in sample_ids:
        sampled_ref = follow(sampled_ref)
        if sampled_ref not in sampled:
            raise ValueError("Used texture sample has no unambiguous OpSampledImage")
        image_ref, sampler_ref = sampled[sampled_ref]
        pairs.append((*slot(image_ref, "image"), *slot(sampler_ref, "sampler")))
    distinct = sorted(set(pairs))
    return {
        "compiled_sampling_ops": len(sample_ids),
        "used_image_sampler_pairs": [
            {"image_set": a, "image_binding": b, "sampler_set": c,
             "sampler_binding": d} for a, b, c, d in distinct
        ],
        "distinct_used_pair_count": len(distinct),
        "used_image_count": len({(a, b) for a, b, _, _ in distinct}),
        "used_sampler_count": len({(c, d) for _, _, c, d in distinct}),
        "all_declared_resources_used_verified": (
            {(a, b) for a, b, _, _ in distinct} == images and
            {(c, d) for _, _, c, d in distinct} == samplers
        ),
        "original_source_texture_to_compiled_pair_identity_verified": False,
        "unity_material_upload_or_sampler_state_verified": False,
        "device_pixels_verified": False,
        "private_identifiers_published": False,
    }


def audit(source, packet, manifest):
    source, packet, manifest = map(lambda p: Path(p).absolute(),
                                   (source, packet, manifest))
    if not (source.is_dir() and packet.is_dir() and manifest.is_file()
            and all(_physical(p) for p in (source, packet, manifest))):
        raise ValueError("Private original source or SPIR-V packet unsafe")
    prior = original_resource_audit(source, packet, manifest)
    if not (prior.get("original_to_compiled_resource_cardinality_verified")
            and prior.get("authenticated_original_texture_rows") == 6
            and prior.get("authenticated_translated_separate_samplers") == 6):
        raise ValueError("Original Foam interface authentication missing")
    results = []
    for pi, stage in STAGES:
        spv = packet / ("pass%d-stage%d" % (pi, stage)) / "original.spv"
        if not spv.is_file() or not _physical(spv):
            raise ValueError("Authenticated stage SPIR-V missing")
        run = subprocess.run(
            ["spirv-dis", str(spv)], capture_output=True, text=True,
            timeout=40, check=False,
        )
        if run.returncode or len(run.stdout) > MAX_TEXT:
            raise ValueError("Private SPIR-V disassembler rejected stage")
        expected = COMPILED_NUMERIC_RESOURCE_BINDINGS[(pi, stage)]
        images = [(a[1], a[2]) for a in expected if a[0] == "separate_images"]
        samplers = [(a[1], a[2]) for a in expected if a[0] == "separate_samplers"]
        r = trace_sampled_pairs(run.stdout, images, samplers)
        results.append({"pass": pi, "stage_code": stage,
                        "authenticated_original_source_texture_count":
                            ORIGINAL_TEXTURES_PER_STAGE[(pi, stage)], **r})
    if len(results) != 4:
        raise ValueError("Authentic four-stage Foam coverage absent")
    return {
        "status": "original_foam_compiled_sampler_use_observed",
        "source_stage_count": 4,
        "actual_sample_call_count": sum(r["compiled_sampling_ops"] for r in results),
        "actual_distinct_pair_count": sum(r["distinct_used_pair_count"] for r in results),
        "stages": results,
        "source_to_unity_material_binding_verified": False,
        "shaderlab_import_verified": False,
        "adreno_pixels_verified": False,
        "private_shader_data_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("source", "packet", "manifest", "out"):
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args()
    try:
        out = args.out.absolute()
        if (out.exists() or not out.parent.is_dir() or not _physical(out)
                or out.is_relative_to(args.packet.absolute())
                or out.is_relative_to(args.source.absolute())):
            raise ValueError("Unsafe aggregate report output")
        report = audit(args.source, args.packet, args.manifest)
        out.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        print("T2_FOAM_SAMPLED_USE " + json.dumps({
            "status": report["status"],
            "four_original_stages": report["source_stage_count"],
            "sample_calls": report["actual_sample_call_count"],
            "compiled_pairs": report["actual_distinct_pair_count"],
            "shaderlab_or_device_verified": False,
            "source_symbols_published": False,
        }))
        return 0
    except BaseException as exc:
        # Do not reveal source, SPIR-V strings or private paths in failure.
        print("T2_FOAM_SAMPLED_USE " + json.dumps({
            "status": "blocked", "failure_type": type(exc).__name__,
            "shaderlab_or_device_verified": False,
            "source_symbols_published": False,
        }))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
