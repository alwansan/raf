"""Run directly instrumented PRIVATE original FFT SPIR-V with keyed trace buffer.

Only aggregate counts and output invariance are public. The original shader,
injected SPIR-V, readback pixels, source inputs and invocation records remain
private scratch; this does NOT compare against translated candidate reads.
"""
import argparse
import json
from pathlib import Path
import struct
import subprocess
import tempfile

from scripts.t1_fft_original_direct_keyed_recorder import instrument
from scripts.t1_fft_pass0_vulkan_trace import trace_host
from scripts.t1_fft_vulkan_roundtrip_isolation import WIDTH, HEIGHT, run
from scripts.t1_fft_readback_parity import read_image, compare_pass
from scripts.t1_fft_trace_compare import INVOCATION_SIZE, decode_invocations, CAPACITY
from scripts.t1_fft_private_input_evidence import capture_evidence, save_private_evidence

EXPECTED_RECORDS = [64, 256, 64]


def analyze(project, host_file, export=None, *, private_evidence_export=None):
    original = project / "_private_vulkan" / "slot0.spv"
    other = project / "_private_vulkan" / "slot1.spv"
    for x in (original, other):
        if not x.is_file() or not 20 <= x.stat().st_size <= 1024 * 1024:
            raise ValueError("Private original module not available in bound")
    with tempfile.TemporaryDirectory(prefix="t1-original-keyed-vulkan-") as scratch:
        work = Path(scratch)
        print("RAFT_T1_ORIGINAL_KEYED_STAGE disassemble", flush=True)
        dis = subprocess.run(["spirv-dis", "--raw-id", str(original)],
                             check=True, capture_output=True, text=True, timeout=30)
        print("RAFT_T1_ORIGINAL_KEYED_STAGE instrument", flush=True)
        (work / "original-record.spvasm").write_text(instrument(dis.stdout), encoding="utf-8")
        print("RAFT_T1_ORIGINAL_KEYED_STAGE assemble", flush=True)
        run(["spirv-as", "--target-env", "vulkan1.1", "original-record.spvasm",
             "-o", "original-record.spv"], work)
        print("RAFT_T1_ORIGINAL_KEYED_STAGE spirv_validate", flush=True)
        validate = subprocess.run(
            ["spirv-val", "--target-env", "vulkan1.1", "original-record.spv"],
            cwd=work, capture_output=True, text=True, timeout=30)
        if validate.returncode:
            # Private compiler diagnostics may contain original SSA IDs; only
            # fixed instruction/semantic families are allowed in public logs.
            raw_error = (validate.stderr + validate.stdout).lower()
            families = {
                "OpAtomicIAdd": "opatomiciadd",
                "OpAccessChain": "opaccesschain",
                "OpVariable": "opvariable",
                "OpTypeRuntimeArray": "optyperuntimearray",
                "OpTypePointer": "optypepointer",
                "OpTypeStruct": "optypestruct",
                "OpEntryPoint": "opentrypoint",
                "OpStore": "opstore",
                "OpLoad": "opload",
                "OpBitcast": "opbitcast",
                "OpCompositeExtract": "opcompositeextract",
                "OpPhi": "opphi",
                "StorageBuffer": "storagebuffer",
                "Block": "block",
                "ArrayStride": "arraystride",
                "Offset": "offset",
                "dominance": "dominat",
                "variable_scope": "scope",
                "type_mismatch": "type",
                "logical_layout": "layout",
                "memory_semantics": "semantics",
                "atomic": "atomic",
                "capability": "capability",
            }
            detected = sorted(name for name, signature in families.items()
                              if signature in raw_error)
            print("RAFT_T1_ORIGINAL_KEYED_VAL_DIAGNOSTIC " +
                  json.dumps({"families": detected[:16], "classification_only": True,
                              "private_error_text_exported": False}, sort_keys=True),
                  flush=True)
            raise ValueError("Original private SPIR-V validation rejected instrumented module")
        source = trace_host(host_file.read_text(encoding="utf-8"), INVOCATION_SIZE,
                            capture_inputs=private_evidence_export is not None)
        if source.count("traceWrite.dstSet = sets[1];") != 1:
            raise ValueError("Original descriptor set host patch anchor absent")
        source = source.replace("traceWrite.dstSet = sets[1];",
                                "traceWrite.dstSet = sets[0];")
        print("RAFT_T1_ORIGINAL_KEYED_STAGE host_compile", flush=True)
        (work / "trace.cpp").write_text(source, encoding="utf-8")
        run(["g++", "-std=c++17", "-O2", "trace.cpp", "-lvulkan", "-o", "trace"], work)
        print("RAFT_T1_ORIGINAL_KEYED_STAGE vulkan_dispatch", flush=True)
        run(["./trace", "original-record.spv", str(original), str(other), str(other),
             str(WIDTH), str(HEIGHT), "19", "1", "rgba32f"], work)
        print("RAFT_T1_ORIGINAL_KEYED_STAGE readback_decode", flush=True)
        record = read_image(work / "trace.bin", INVOCATION_SIZE)
        (count,) = struct.unpack_from("<I", record)
        if count > CAPACITY:
            raise ValueError("Original keyed capture atomic record capacity overflow")
        sites = decode_invocations(record)
        by_site = [len(s) for s in sites]
        if by_site != EXPECTED_RECORDS:
            raise ValueError("Original keyed capture site coverage unexpected")
        if sum(by_site) != count:
            raise ValueError("Original keyed capture count inconsistent")
        # Both are the ORIGINAL shader: original0 is private instrumented,
        # roundtrip0 is unmodified original, same host/input/dispatch.
        print("RAFT_T1_ORIGINAL_KEYED_STAGE output_compare", flush=True)
        original_image = read_image(work / "original0.rgba32f", WIDTH * HEIGHT * 16)
        baseline_image = read_image(work / "roundtrip0.rgba32f", WIDTH * HEIGHT * 16)
        invariant = compare_pass(baseline_image, original_image)
        if not invariant["match"]:
            raise ValueError("Original traced shader changed output pixels")
        if export is not None:
            with Path(export).open("xb") as destination:
                destination.write(record)
        if private_evidence_export is not None:
            save_private_evidence(private_evidence_export,
                                  capture_evidence(work, work / "original-record.spv",
                                                   record, "original_spirv"))
        return {
            "status": "actual_original_spirv_invocation_keyed_gpu_capture",
            "original_sha_source_staged_privately": True,
            "original_shader_directly_instrumented_no_hlsl_roundtrip": True,
            "records_by_site": by_site, "count": count,
            "duplicate_invocation_occurrence_keys": 0,
            "trace_capacity_limit": CAPACITY,
            "output_invariance_original_traced_vs_untraced": True,
            "output_pixels_compared": invariant["compared_written_pixels"],
            "paired_with_translated_candidate": False,
            "numeric_original_vs_candidate_parity_proven": False,
            "android_water_proven": False,
            "private_shader_or_capture_bytes_exported": False,
        }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True)
    p.add_argument("--export-private-trace", type=Path)
    p.add_argument("--export-private-evidence", type=Path)
    args = p.parse_args()
    try:
        result = analyze(args.project.resolve(), Path("scripts/a1_fft_two_pass_vulkan.cpp"),
                         args.export_private_trace,
                         private_evidence_export=args.export_private_evidence)
    except (OSError, ValueError, UnicodeError, subprocess.SubprocessError):
        p.exit(2, "Private original FFT GPU keyed trace generation failed\n")
    print("RAFT_T1_ORIGINAL_SPIRV_KEYED_GPU_TRACE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
