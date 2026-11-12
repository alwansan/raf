#!/usr/bin/env python3
"""GT restoration ledger validation: source, export, build and device remain distinct.

Audits only repository-owned safe aggregate JSON. It does NOT reconstruct or
publish game shaders/texture bytes, and does not certify rendered pixels.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

PIN = "15964ea8f246b6e076ce26b60931ee2e1a9a2385"
EXPECTED_WORKSTREAMS = tuple(f"P{i:02d}" for i in range(12))
EXPECTED_MILESTONES = tuple(f"M{i}" for i in range(6))
KNOWN_STATUSES = frozenset(("complete", "active", "blocked", "pending"))
SOURCE_FIELDS = ("source_verified", "export_verified", "unity_verified",
                 "packaged", "device_verified")
MAX_JSON = 256 * 1024


def _object(value, label):
    if not isinstance(value, dict):
        raise ValueError("missing_or_malformed_" + label)
    return value


def _strict_int(value, label, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("bad_" + label)
    return value


def _row(items, expected, kind):
    if not isinstance(items, list):
        raise ValueError("missing_" + kind)
    ids = [row.get("id") if isinstance(row, dict) else None for row in items]
    if tuple(ids) != expected:
        raise ValueError("duplicate_missing_or_reordered_" + kind)
    return {row["id"]: row for row in items}


def _same(actual, expected, key):
    if actual != expected or type(actual) is not type(expected):
        raise ValueError("source_proof_mismatch_" + key)


def check(plan: dict, state: dict, device: dict) -> dict:
    plan = _object(plan, "plan")
    state = _object(state, "state")
    device = _object(device, "device_receipt")
    if (plan.get("schema_version") != 1 or plan.get("agent") != "GT"
            or plan.get("repository") != "alwansan/raf"
            or plan.get("write_branch") != "feature/android-native-port"):
        raise ValueError("untrusted_restoration_plan_identity")
    orig = _object(plan.get("original_source"), "original_source")
    if (orig.get("sha") != PIN or state.get("source", {}).get("sha") != PIN
            or orig.get("git_lfs_allowed") is not False
            or orig.get("original_meta_or_scene_guid_modification_allowed_without_proof")
            is not False):
        raise ValueError("original_source_policy_drift")
    rows = _row(plan.get("workstreams"), EXPECTED_WORKSTREAMS, "workstreams")
    milestones = _row(plan.get("milestones"), EXPECTED_MILESTONES, "milestones")
    for key, row in rows.items():
        for field in ("name_ar", "status", "restored_now", "missing", "next_action"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError("missing_workstream_description_" + key)
        _object(row.get("scope"), "scope_" + key)
        for field in SOURCE_FIELDS:
            value = row.get(field)
            if value is None or (type(value) not in (bool, str)
                                 or (type(value) is str and not value.strip())):
                raise ValueError("missing_stage_proof_" + key + "_" + field)
        if type(row["device_verified"]) is not bool:
            raise ValueError("device_acceptance_must_be_explicit_boolean_" + key)
        if row["device_verified"]:
            # A future verified device claim must have a new device session
            # and strict known-log gate PASS, not the owner failing baseline.
            proof = _object(row.get("device_acceptance"), "device_acceptance_" + key)
            if (proof.get("strict_known_log_gate_passed") is not True
                    or not re.fullmatch(r"[0-9a-f]{64}",
                                        str(proof.get("apk_sha256", "")))
                    or _strict_int(proof.get("phone_render_samples"),
                                   "phone_samples", 1) < 1
                    or proof.get("session_id") == state.get(
                        "proofs_20261112_chat20", {}).get("owner_device_log_session")):
                raise ValueError("unproven_device_acceptance_" + key)
        proof_ids = row.get("evidence")
        if (not isinstance(proof_ids, list) or not proof_ids or
                any(type(n) is not int or n < 100000 for n in proof_ids)):
            raise ValueError("missing_numbered_evidence_" + key)
    for key, row in milestones.items():
        if (row.get("status") not in KNOWN_STATUSES
                or not isinstance(row.get("action_ar"), str)
                or not row["action_ar"].strip()
                or not isinstance(row.get("gate"), str) or not row["gate"].strip()
                or not isinstance(row.get("evidence"), list)
                or not row["evidence"]):
            raise ValueError("incomplete_milestone_" + key)
        if key != "M0" and row["status"] == "complete" and not row.get(
                "acceptance_evidence"):
            raise ValueError("milestone_complete_without_acceptance_" + key)
    inv = _object(state.get("inventory"), "state_inventory")
    totals = _object(inv.get("totals"), "state_totals")
    usage = _object(inv.get("usage"), "state_usage")
    authenticated = _object(inv.get("source_authenticated"), "source_auth")
    original = _object(authenticated.get("full_native_graphics"), "graphics")
    r0 = rows["P00"]["scope"]
    for key, value in [
        ("original_files", original["original_file_count"]),
        ("original_bytes", original["original_bytes"]),
        ("stream_files", original["streams"]),
        ("serialised_owners", authenticated["owners"]),
        ("unity_scenes", usage["source_scenes"])]:
        _same(r0.get(key), value, "P00_"+key)
    for id, field, value in [
        ("P01", "meshes", totals["Mesh"]),
        ("P01", "scenes", usage["source_scenes"]),
        ("P02", "source_texture2d", totals["Texture2D"]),
        ("P02", "external_texture_streams",
         original["external_texture_streams_verified"]),
        ("P03", "arrays", totals["Texture2DArray"]),
        ("P04", "source_materials", totals["Material"]),
        ("P05", "source_shader_objects", totals["Shader"]),
        ("P07", "source_compute_shaders", totals["ComputeShader"]),
        ("P09", "source_particle_system_renderer_components",
         totals["ParticleSystemRenderer"])]:
        _same(rows[id]["scope"].get(field), value, id+"_"+field)
    proof = _object(authenticated["real_assetripper_export"], "export_proof")
    _same(rows["P04"]["scope"].get("exported_material_docs"),
          proof["material_yaml_files"], "P04_exported_materials")
    vendor = _object(proof["vendor_shader_restore"], "vendor")
    _same(rows["P04"]["scope"].get("custom_dummy_after_vendor_restorers"),
          vendor["post_vendor_restorers_dummy_material_docs"], "P04_dummy_docs")
    _same(rows["P04"]["scope"].get("postvendor_custom_non_dummy_docs"),
          vendor["non_dummy_custom_materials_gained"], "P04_vendor_docs")
    arrays = _object(proof["original_texture_arrays"], "arrays")
    for key, value in [
        ("logical_layers", arrays["logical_layers"]),
        ("original_nonempty_bc3_layers", arrays["BC3_layers_with_source_bytes"]),
        ("original_empty_layers", arrays["original_empty_pixel_layers"]),
        ("material_references", arrays["material_refs_class187"]),
        ("original_gpu_bytes", arrays["original_gpu_streamed_bytes"])]:
        _same(rows["P03"]["scope"].get(key), value, "P03_"+key)
    real = _object(state.get("proofs_20261112_chat20"), "chat20")
    r6 = rows["P06"]["scope"]
    r7 = rows["P07"]["scope"]
    r10 = rows["P10"]["scope"]
    for key, val in [
        ("device_invalid_pass_count", real["owner_phone_UltimateWater_invalid_pass_total"]),
        ("device_spectrum_errors", real["owner_phone_spectrum_invalid_pass"]),
        ("device_foam_global_errors", real["owner_phone_foam_global_invalid_pass"])]:
        _same(r6.get(key), val, "P06_"+key)
    _same(r7.get("device_invalid_kernel_index6"),
          real["owner_phone_invalid_compute_kernel_index_6_total"], "P07_kernel")
    _same(r10.get("cursor_rgba32_log_count"),
          real["owner_phone_cursor_RGBA32_warning_total"], "P10_cursor")
    _same(r10.get("obb_guid_load_failures"),
          real["owner_phone_OBB_GUID_load_failures"], "P10_obb")
    counts = _object(device.get("error_counts"), "device_counts")
    for key, val in [
        ("water_invalid_pass", r6["device_invalid_pass_count"]),
        ("water_spectrum_invalid_pass", r6["device_spectrum_errors"]),
        ("water_foam_global_invalid_pass", r6["device_foam_global_errors"]),
        ("invalid_kernel_index_6", r7["device_invalid_kernel_index6"]),
        ("cursor_rgba32_required", r10["cursor_rgba32_log_count"]),
        ("obb_guid_load_failed", r10["obb_guid_load_failures"])]:
        _same(counts.get(key), val, "CL_"+key)
    _same(plan["reference_runs"].get("new_native_active_at_snapshot"),
          state["proofs_20261112_chat19"]["latest_native_full_run"],
          "current_native_run")
    if (any(row["device_verified"] for row in rows.values())
            and device.get("failing_known_device_log_gate") is True):
        # Future successful device sessions need their *own* cited receipts.
        for row in rows.values():
            if (row["device_verified"] and row["device_acceptance"].get(
                    "session_id") == real["owner_device_log_session"]):
                raise ValueError("reused_failing_device_session")
    return {"status": "GT_SOURCE_BACKED_RESTORATION_LEDGER_VALID",
            "original_source_sha_pinned": True,
            "workstreams": len(rows), "milestones": len(milestones),
            "source_owner_count": r0["serialised_owners"],
            "remaining_postvendor_dummy_material_docs":
                rows["P04"]["scope"]["custom_dummy_after_vendor_restorers"],
            "owner_device_water_error_count": r6["device_invalid_pass_count"],
            "device_proof_workstreams": sum(x["device_verified"] for x in rows.values()),
            "native_build_latest_result_unverified": milestones["M1"]["status"] != "complete"}


def _read(path: Path):
    if (not path.is_file() or path.is_symlink()
            or not 0 < path.stat().st_size <= MAX_JSON):
        raise ValueError("unsafe_or_oversized_plan_document")
    def no_duplicate_keys(items):
        data = {}
        for key, value in items:
            if key in data:
                raise ValueError("duplicate_json_key")
            data[key] = value
        return data
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicate_keys)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", type=Path, default=Path("clients/GT/RESTORATION_PLAN.json"))
    ap.add_argument("--state", type=Path, default=Path("clients/GT/state.json"))
    ap.add_argument("--device-receipt", type=Path,
                    default=Path("clients/GT/evidence/20261112_cl_device_graphics_failure_receipt.json"))
    args = ap.parse_args()
    print("GT_RESTORATION_PLAN_CHECK " + json.dumps(
        check(_read(args.plan), _read(args.state), _read(args.device_receipt)),
        sort_keys=True))


if __name__ == "__main__":
    main()
