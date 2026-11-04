"""B20: authenticated two-pass Foam integration-input packet (private only).

Never publishes original DXBC/HLSL/ShaderLab, guesses CB0 aliases, installs a
Unity shader or asserts pixel/device equivalence.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

from scripts.b24_original_foam_stage_translation import (
    OWNER, OBJECT_ID, ORIGINAL_OBJECT_SHA256, inspect as translate_original_stages,
)
from scripts.b25_foam_pass_state import inspect as inspect_states, save_private
from scripts.b25_foam_cb_namebridge import inspect_parsed as inspect_cb
from scripts.w1_recover_graphics_programs import decoded_platforms, records
from scripts.w1_stage_zip2_owners import PINS, fingerprint

ORIGINAL_STAGE_SHA = {
    (0, 1): "77ffe091c60430461b9c125b2d839fedd04982a66a1f7e55331a26536f9e9522",
    (0, 0): "abcee848cbe73e0d16054844473cf7df7f0c9ae6cc62bc6a47dba9848aae4b69",
    (1, 1): "22b508edfeb543931fb649ddbbebe55248da2a4766e6ed066dc5c604428a57b5",
    (1, 0): "f8342b875524cc4b214a59dbcdc609e24c9477416c562af53003e6b04b1e5291",
}
ORIGINAL_STATE_SHA = "19b4753ccc0393a8ebe4f804aded5e5c8363d9b641cac1870d2d6d0c73b50170"
ORIGINAL_STATE_BYTES = 247


def _physical(path):
    return not any(p.is_symlink() for p in (path, *path.parents))


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def stage_verified(parsed, entries, private, *, stages=translate_original_stages,
                   states=inspect_states, bridge=inspect_cb):
    """Stage only source-authenticated inputs, not a plausible fake ShaderLab."""
    private = Path(private)
    if not private.is_dir() or not _physical(private):
        raise ValueError("Private scratch directory unsafe")
    state_report, state_texts = states(parsed)
    cb = bridge(parsed)
    if (state_report.get("original_passes") != 2
            or len(state_report.get("states", [])) != 2
            or len(state_texts) != 2
            or cb.get("original_passes") != 2
            or cb.get("authenticated_stage_count") != 4
            or cb.get("matched_constant_buffer_bindings") != 8
            or cb.get("referenced_cb_names_requiring_alias") != 4
            or cb.get("shaderlab_cb_rebinding_installed") is not False
            or cb.get("unity_or_android_verified") is not False):
        raise ValueError("Original Foam pass/CB source binding incomplete")
    for index, (row, text) in enumerate(zip(state_report["states"], state_texts)):
        data = text.encode("utf-8")
        if (row.get("index") != index or row.get("sha256") != ORIGINAL_STATE_SHA
                or row.get("bytes") != ORIGINAL_STATE_BYTES
                or _sha(data) != ORIGINAL_STATE_SHA or len(data) != ORIGINAL_STATE_BYTES):
            raise ValueError("Original Foam render-state fingerprint changed")
    stage_rows = stages(parsed, entries, private)
    if not isinstance(stage_rows, list) or len(stage_rows) != 4:
        raise ValueError("Original Foam four-stage program packet incomplete")
    safe_stages = []
    for index, row in enumerate(stage_rows):
        key = (index // 2, 1 if index % 2 == 0 else 0)
        if (not isinstance(row, dict)
                or (row.get("pass"), row.get("stage_code")) != key
                or row.get("original_program_sha256") != ORIGINAL_STAGE_SHA[key]
                or row.get("original_spirv_valid") is not True
                or row.get("private_hlsl_recovered") is not True
                or row.get("rebuilt_spirv_valid") is not True):
            raise ValueError("Foam stage SHA/order/roundtrip authentication failed")
        hlsl = private / ("pass%d-stage%d" % key) / "private.hlsl"
        if (not _physical(hlsl) or not hlsl.is_file()
                or not 0 < hlsl.stat().st_size <= 1024 * 1024):
            raise ValueError("Original translated HLSL missing or unsafe")
        safe_stages.append({
            "pass": key[0], "stage_code": key[1],
            "original_dxbc_sha256": ORIGINAL_STAGE_SHA[key],
            "hlsl_sha256": _sha(hlsl.read_bytes()),
            "hlsl_bytes": hlsl.stat().st_size,
        })
    save_private(private, state_texts)
    for index in range(2):
        state_file = private / ("foam-pass-%02d-state.txt" % index)
        if (not _physical(state_file) or state_file.stat().st_size != ORIGINAL_STATE_BYTES
                or _sha(state_file.read_bytes()) != ORIGINAL_STATE_SHA):
            raise ValueError("Private render-state file changed")
    return {
        "status": "private_two_pass_inputs_staged",
        "original_owner_sha256": PINS[OWNER][1],
        "original_object_sha256": ORIGINAL_OBJECT_SHA256,
        "original_passes": 2, "original_stage_programs": 4,
        "original_cb_name_slot_links_verified": 8,
        "opaque_cb0_aliases_still_require_authentication": 4,
        "render_state_sha256": ORIGINAL_STATE_SHA,
        "original_state_bytes_each": ORIGINAL_STATE_BYTES,
        "stage_hashes": safe_stages,
        "private_packet_staged": True,
        "private_original_program_published": False,
        "shaderlab_constructed": False,
        "unity_or_device_verified": False,
        "water_ready": False,
    }


def stage(source, repo, private, report):
    source, repo, private, report = map(lambda x: Path(x).absolute(),
                                       (source, repo, private, report))
    if (not all(_physical(p) for p in (source, repo, private, report))
            or not source.is_dir() or not repo.is_dir()
            or not private.parent.is_dir() or not report.parent.is_dir()
            or private.exists() or report.exists()
            or source.is_relative_to(repo) or private.is_relative_to(repo)
            or report.is_relative_to(repo) or private.is_relative_to(source)
            or report.is_relative_to(source)):
        raise ValueError("Unsafe original source/private output path")
    owner_file = source / OWNER
    if (not _physical(owner_file) or not owner_file.is_file()
            or fingerprint(owner_file) != PINS[OWNER]):
        raise ValueError("Original Foam ZIP2 provider SHA/size mismatch")
    import UnityPy
    env = UnityPy.load(str(owner_file))
    objs = [o for o in env.file.objects.values()
            if o.type.name == "Shader" and int(o.path_id) == OBJECT_ID]
    if len(objs) != 1:
        raise ValueError("Original Foam object missing/ambiguous")
    obj = objs[0]
    if _sha(obj.get_raw_data()) != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original Foam object SHA changed")
    tree = obj.read_typetree()
    tables = [records(parts) for platform, parts in decoded_platforms(tree) if platform == 4]
    if len(tables) != 1:
        raise ValueError("Original Foam D3D11 table missing/ambiguous")
    tmp_report = None
    with tempfile.TemporaryDirectory(prefix="b20-private-foam-", dir=private.parent) as folder:
        staged = Path(folder) / "packet"
        staged.mkdir()
        result = stage_verified(tree.get("m_ParsedForm"), tables[0], staged)
        try:
            with tempfile.NamedTemporaryFile(
                    mode="w", encoding="utf-8", prefix=".b20-foam-safe-",
                    dir=report.parent, delete=False) as handle:
                tmp_report = Path(handle.name)
                handle.write(json.dumps(result, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            if private.exists() or private.is_symlink():
                raise ValueError("Private destination unexpectedly appeared")
            os.rename(staged, private)
            try:
                os.replace(tmp_report, report)
                tmp_report = None
            except BaseException:
                shutil.rmtree(private)
                raise
        finally:
            if tmp_report is not None:
                tmp_report.unlink(missing_ok=True)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--repo", type=Path, required=True)
    p.add_argument("--private", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    try:
        result = stage(a.source, a.repo, a.private, a.out)
    except BaseException as exc:
        print("B20_FOAM_PACKET " + json.dumps({
            "status": "blocked", "failure_type": type(exc).__name__,
            "private_program_published": False}))
        return 2
    print("B20_FOAM_PACKET " + json.dumps({
        "status": result["status"], "original_stage_programs": 4,
        "cb0_alias_verified": False, "shaderlab_constructed": False,
        "private_program_published": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
