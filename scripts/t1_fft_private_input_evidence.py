"""Private, non-logged source/butterfly image input attestation for T1 FFT.

Only used inside the SHA-pinned Vulkan runner; the resulting JSON contains
private shader/input/trace hashes and MUST NOT be printed or uploaded. It is
deleted along with private runner scratch. Public paired report shows booleans
and aggregate counts only.
"""
import hashlib
import json
from pathlib import Path

from scripts.t1_fft_trace_compare import INVOCATION_SIZE, decode_invocations
from scripts.t1_fft_vulkan_roundtrip_isolation import HEIGHT, WIDTH
from scripts.t1_fft_readback_parity import read_image

SCHEMA = "t1-fft-private-input-contract-v1"
BYTES = WIDTH * HEIGHT * 16
DISPATCH = {
    "width": WIDTH, "height": HEIGHT, "input_seed": 19,
    "dispatch_groups_x": 1, "dispatch_groups_y": 1, "dispatch_groups_z": 1,
    "texture_format": "rgba32f", "pass": 0,
}
STAGES = {"original_spirv", "hlsl_roundtrip_spirv"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def input_hash(source, butterfly):
    return sha(len(source).to_bytes(8, "little") + source +
               len(butterfly).to_bytes(8, "little") + butterfly)


def capture_evidence(work, shader, trace, stage):
    if stage not in STAGES or len(trace) != INVOCATION_SIZE:
        raise ValueError("Invalid private source stage or trace size")
    work = Path(work)
    source = read_image(work / "t1-source-input.rgba32f", BYTES)
    butterfly = read_image(work / "t1-butterfly-input.rgba32f", BYTES)
    shader_bytes = Path(shader).read_bytes()
    if not 20 <= len(shader_bytes) <= 1024*1024:
        raise ValueError("Private instrumented shader size invalid")
    records = decode_invocations(trace)
    return {
        "schema": SCHEMA,
        "stage": stage,
        "input_sha256": input_hash(source, butterfly),
        "dispatch_sha256": sha(json.dumps(DISPATCH, sort_keys=True).encode("ascii")),
        "shader_sha256": sha(shader_bytes),
        "trace_sha256": sha(trace),
        "records_by_site": [len(group) for group in records],
    }


def save_private_evidence(path, report):
    if set(report) != {"schema", "stage", "input_sha256", "dispatch_sha256",
                        "shader_sha256", "trace_sha256", "records_by_site"}:
        raise ValueError("Invalid private attestation metadata")
    with Path(path).open("x", encoding="utf-8") as out:
        json.dump(report, out, sort_keys=True)
        out.write("\n")
