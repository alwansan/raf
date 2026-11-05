"""T2: compile original Foam's paired VS+PS HLSL for each of its two passes.

Requires the SHA-original B20 private four-stage/two-state packet. Combines
original translated vertex+fragment *within the same program text*, as Unity
ShaderLab HLSLPROGRAM would require. This is NOT an authored ShaderLab,
CB0/material upload, Unity compilation, or Adreno output verification.

Private shader inputs/output are NEVER logged, committed, or uploaded.
Only bounded booleans and stage counts may leave the runner scratch.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from scripts.b20_private_foam_packet import (
    ORIGINAL_OBJECT_SHA256, ORIGINAL_STAGE_SHA, ORIGINAL_STATE_SHA,
    ORIGINAL_STATE_BYTES, _physical,
)
from scripts.w1_stage_zip2_owners import PINS
from scripts.b24_original_foam_stage_translation import OWNER
from scripts.w1_depth_shaderlab import stage_body

MAX_HLSL = 1024 * 1024
MAX_SPV = 8 * 1024 * 1024
EXPECTED = ((0, 1), (0, 0), (1, 1), (1, 0))


def _sha(blob):
    return hashlib.sha256(blob).hexdigest()


def _exact_manifest(packet, manifest):
    """Fail closed on a swapped, stale or incomplete original B20 packet."""
    packet, manifest = Path(packet).absolute(), Path(manifest).absolute()
    if (not packet.is_dir() or not manifest.is_file()
            or not _physical(packet) or not _physical(manifest)
            or manifest.is_relative_to(packet) or manifest.stat().st_size > 65536):
        raise ValueError("private_source_path_invalid")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if (data.get("status") != "private_two_pass_inputs_staged"
            or data.get("original_owner_sha256") != PINS[OWNER][1]
            or data.get("original_object_sha256") != ORIGINAL_OBJECT_SHA256
            or data.get("original_passes") != 2
            or data.get("original_stage_programs") != 4
            or data.get("original_cb_name_slot_links_verified") != 8
            or data.get("opaque_cb0_aliases_still_require_authentication") != 4
            or data.get("render_state_sha256") != ORIGINAL_STATE_SHA
            or data.get("original_state_bytes_each") != ORIGINAL_STATE_BYTES
            or data.get("private_packet_staged") is not True
            or data.get("shaderlab_constructed") is not False
            or data.get("unity_or_device_verified") is not False
            or data.get("water_ready") is not False
            or data.get("private_original_program_published") is not False):
        raise ValueError("original_source_manifest_invalid")
    rows = data.get("stage_hashes")
    if not isinstance(rows, list) or len(rows) != 4:
        raise ValueError("original_stage_count_invalid")
    stages = {}
    for expected, row in zip(EXPECTED, rows):
        if (not isinstance(row, dict)
                or set(row) != {"pass", "stage_code", "original_dxbc_sha256",
                               "hlsl_sha256", "hlsl_bytes"}
                or (row["pass"], row["stage_code"]) != expected
                or row["original_dxbc_sha256"] != ORIGINAL_STAGE_SHA[expected]
                or type(row["hlsl_bytes"]) is not int
                or not 0 < row["hlsl_bytes"] <= MAX_HLSL
                or not isinstance(row["hlsl_sha256"], str)
                or len(row["hlsl_sha256"]) != 64):
            raise ValueError("source_stage_identity_invalid")
        stage_file = packet / ("pass%d-stage%d" % expected) / "private.hlsl"
        if (not _physical(stage_file) or not stage_file.is_file()
                or stage_file.stat().st_size != row["hlsl_bytes"]):
            raise ValueError("staged_original_hlsl_invalid")
        blob = stage_file.read_bytes()
        if _sha(blob) != row["hlsl_sha256"] or b"\x00" in blob:
            raise ValueError("original_stage_hlsl_digest_mismatch")
        stages[expected] = blob.decode("utf-8")
    for index in range(2):
        original = packet / ("foam-pass-%02d-state.txt" % index)
        if (not _physical(original) or not original.is_file()
                or original.stat().st_size != ORIGINAL_STATE_BYTES
                or _sha(original.read_bytes()) != ORIGINAL_STATE_SHA):
            raise ValueError("original_render_state_digest_mismatch")
    return stages


def _tool(argv):
    try:
        completed = subprocess.run(
            argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL, check=False, timeout=100,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def compile_pairs(packet, manifest, *, scratch, invoke=_tool):
    packet, manifest, scratch = (
        Path(packet).absolute(), Path(manifest).absolute(), Path(scratch).absolute()
    )
    if (not scratch.is_dir() or not _physical(scratch)
            or scratch.is_relative_to(packet)):
        raise ValueError("unsafe_private_compile_scratch")
    stages = _exact_manifest(packet, manifest)
    validated = []
    # No original HLSL/SPV is ever placed in the checkout or uploaded.
    with tempfile.TemporaryDirectory(prefix="t2-foam-vf-pair-", dir=scratch) as temp:
        temp = Path(temp)
        for pass_id in range(2):
            pair = stage_body(stages[(pass_id, 1)], stages[(pass_id, 0)])
            if not 0 < len(pair.encode("utf-8")) <= 2 * MAX_HLSL + 4096:
                raise ValueError("private_pair_text_budget")
            merged = temp / ("paired-pass-%d.hlsl" % pass_id)
            merged.write_text(pair, encoding="utf-8")
            for stage, macro in ((1, "VERTEX"), (0, "FRAGMENT")):
                output = temp / ("pass-%d-stage-%d.spv" % (pass_id, stage))
                cmd = [
                    "glslangValidator", "-V", "-D",
                    "-DSHADER_STAGE_" + macro + "=1",
                    "-S", "vert" if stage == 1 else "frag",
                    "-e", "main", "-o", str(output), str(merged),
                ]
                if not invoke(cmd):
                    return {"status": "blocked_pair_stage_compile",
                            "validated_count": len(validated),
                            "failed_pass": pass_id,
                            "failed_stage_code": stage,
                            "private_source_published": False}
                if (not _physical(output) or not output.is_file()
                        or not 20 <= output.stat().st_size <= MAX_SPV
                        or not invoke(["spirv-val", "--target-env", "vulkan1.1",
                                       str(output)])):
                    return {"status": "blocked_pair_spirv_validation",
                            "validated_count": len(validated),
                            "failed_pass": pass_id,
                            "failed_stage_code": stage,
                            "private_source_published": False}
                validated.append((pass_id, stage))
    return {"status": "original_foam_two_pairs_compiled_vulkan11",
            "original_passes": 2,
            "compiled_stage_pairs": 2,
            "compiled_stage_variants": len(validated),
            "stage_order_exact": validated == list(EXPECTED),
            "reused_original_247_byte_render_states": True,
            "original_cb0_alias_or_data_upload_verified": False,
            "original_material_and_sampler_upload_verified": False,
            "shaderlab_constructed_or_installed": False,
            "unity_2021_import_or_android_pixels_verified": False,
            "source_program_numeric_pixel_equivalence_verified": False,
            "private_source_published": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--packet", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--scratch", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    out = a.out.absolute()
    status = None
    try:
        # The safe JSON is expected inside RUNNER_TEMP, alongside but not
        # inside the private original packet. It contains no shader bytes.
        if (not out.parent.is_dir() or not _physical(out)
                or out.exists() or out.is_relative_to(a.packet.absolute())):
            raise ValueError("unsafe_safe_output")
        status = compile_pairs(a.packet, a.manifest, scratch=a.scratch)
        code = 0 if status["status"] == "original_foam_two_pairs_compiled_vulkan11" else 2
    except BaseException as exc:
        # Never echo source method/shader names, HLSL, paths or tool stderr.
        status = {"status": "blocked", "error_type": type(exc).__name__,
                  "private_source_published": False}
        code = 2
    if out.parent.is_dir() and _physical(out) and not out.exists():
        out.write_text(json.dumps(status, sort_keys=True) + "\n", encoding="utf-8")
    print("T2_FOAM_PAIRED_SHADER_STAGE_SAFE " + json.dumps(status, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
