"""T5 source-only, fail-closed milestones for an immutable GitHub native run.

Consume filtered official run/jobs/steps/artifact metadata, not raw Unity logs.
A successful source gate, APK step, artifact name or workflow never proves an
authentic signed release, installability, GPU visuals or playable Android world.
"""
import argparse
import json
from pathlib import Path
import re

_SHA = re.compile(r"^[a-f0-9]{40}$")
_MILESTONES = (
    ("mesh", 15, "Restore every pinned external Mesh buffer while retaining original serialized identities"),
    ("scenes", 19, "Export 40 scenes into a Unity Editor project with correct MonoScript metadata"),
    ("water_ack", 43, "Authentic water gate (strict) or exact documented trial limitation"),
    ("guid", 59, "Validate reconstructed editor project structure and GUID references"),
    ("unity", 62, "Unity Editor 2021.3.45f2 Android import and compile"),
    ("apk_audit", 65, "Audit private native APK payload and ARM64 IL2CPP structure"),
    ("signature_step", 67, "Verify actual APK signature before any early device-test delivery"),
    ("package_step", 69, "Package complete owner-authorized APK OBB and XAPK delivery"),
    ("retention_step", 71, "Retain complete owner-authorized install packages for release delivery"),
)
_FINAL = {"success", "failure", "cancelled", "timed_out", "skipped", "neutral", "action_required"}
_LIVE = {"in_progress", "pending", "queued", "waiting", "requested"}
_STATES = {"completed"} | _LIVE


def _obj(value, name):
    if type(value) is not dict:
        raise ValueError(name + ": expected object")
    return value


def _state(value, name):
    value = _obj(value, name)
    status, conclusion = value.get("status"), value.get("conclusion")
    if status not in _STATES:
        raise ValueError(name + ": unknown status")
    if status == "completed" and conclusion not in _FINAL:
        raise ValueError(name + ": missing terminal conclusion")
    if status != "completed" and conclusion is not None:
        raise ValueError(name + ": nonterminal conclusion")
    return status, conclusion


def classify(snapshot, *, expected_id, expected_sha):
    snap = _obj(snapshot, "snapshot")
    run = _obj(snap.get("run"), "run")
    if type(expected_id) is not int or type(run.get("id")) is not int:
        raise ValueError("Invalid immutable run id")
    if run["id"] != expected_id:
        raise ValueError("Immutable run id mismatch")
    sha = run.get("head_sha")
    if not isinstance(sha, str) or not _SHA.fullmatch(sha):
        raise ValueError("Missing or invalid immutable source SHA")
    if not isinstance(expected_sha, str) or not _SHA.fullmatch(expected_sha):
        raise ValueError("Invalid expected source SHA")
    if sha != expected_sha:
        raise ValueError("Immutable source SHA mismatch")
    run_status, run_conclusion = _state(run, "run")

    jobs = _obj(snap.get("jobs"), "jobs").get("jobs")
    if type(jobs) is not list:
        raise ValueError("Missing official jobs list")
    indexed = {}
    for job in jobs:
        job = _obj(job, "job")
        name = job.get("name")
        if name not in {
            "native-request-gate", "unity-license-preflight",
            "reconstruct", "delivery-result", "publish-early-test",
        }:
            continue
        if name in indexed:
            raise ValueError("Duplicate native job")
        _state(job, "job " + name)
        indexed[name] = job
    required = {"native-request-gate", "unity-license-preflight", "reconstruct"}
    if not required.issubset(indexed):
        raise ValueError("Incomplete native job snapshot")
    steps = indexed["reconstruct"].get("steps")
    if type(steps) is not list:
        raise ValueError("Missing native milestone steps")
    step_index = {}
    for row in steps:
        row = _obj(row, "milestone")
        name = row.get("name")
        if name in step_index:
            raise ValueError("Duplicate milestone")
        if type(row.get("number")) is not int:
            raise ValueError("Milestone step number must be integer")
        _state(row, "milestone " + str(name))
        step_index[name] = row
    if len(step_index) != len(_MILESTONES):
        raise ValueError("Missing or additional source milestones")
    flags = {}
    outcomes = {}
    for key, number, name in _MILESTONES:
        row = step_index.get(name)
        if row is None or row["number"] != number:
            raise ValueError("Missing or renumbered verified milestone")
        flags[key] = row["conclusion"] == "success"
        outcomes[key] = row["status"] if row["status"] != "completed" else row["conclusion"]
    # A later necessary milestone cannot pass while an earlier required one
    # still fails or remains pending. Future steps are not proof of a build.
    for index, (key, _, _) in enumerate(_MILESTONES):
        if flags[key] and not all(flags[prev] for prev, _, _ in _MILESTONES[:index]):
            raise ValueError("Contradictory later milestone success")
    artifacts = _obj(snap.get("artifacts"), "artifacts").get("artifacts")
    if type(artifacts) is not list or len(artifacts) > 100:
        raise ValueError("Missing or unbounded artifact list")
    names = set()
    for art in artifacts:
        art = _obj(art, "artifact")
        name, size = art.get("name"), art.get("size_in_bytes")
        if (not isinstance(name, str) or not (1 <= len(name) <= 256)
                or type(size) is not int or size < 0
                or type(art.get("expired")) is not bool):
            raise ValueError("Malformed artifact metadata")
        if name in names:
            raise ValueError("Duplicate artifact name")
        names.add(name)

    native_result = indexed["reconstruct"].get("conclusion")
    if run_status == "completed" and run_conclusion == "success":
        if native_result != "success" or not flags["retention_step"]:
            raise ValueError("Workflow success without completed native delivery milestones")

    first_failure = next((
        key for key, _, _ in _MILESTONES
        if outcomes[key] in {"failure", "timed_out"}
    ), None)
    if first_failure is not None:
        phase = first_failure + "_failed"
    elif native_result == "cancelled" or run_conclusion == "cancelled":
        phase = "cancelled_source_cause_unresolved"
    elif not flags["unity"]:
        phase = (
            "unity_editor_in_progress"
            if outcomes["unity"] == "in_progress"
            else "pre_unity_or_unity_pending"
        )
    elif not flags["signature_step"]:
        phase = "unity_import_passed_signature_unverified"
    elif not flags["package_step"]:
        phase = "signature_step_passed_package_unverified"
    elif not flags["retention_step"]:
        phase = "package_step_passed_retention_unverified"
    else:
        phase = "retention_step_passed_external_release_unverified"

    return {
        "run_id": expected_id,
        "source_sha": expected_sha,
        "run_status": run_status,
        "run_conclusion": run_conclusion,
        "native_conclusion": native_result,
        "phase": phase,
        "milestones": outcomes,
        "request_gate_passed": indexed["native-request-gate"]["conclusion"] == "success",
        "unity_license_preflight_passed": indexed["unity-license-preflight"]["conclusion"] == "success",
        "water_documented_trial_gate_passed": flags["water_ack"],
        "authentic_original_water_fft_verified": False,
        "artifact_records": len(artifacts),
        "signed_apk_bytes_digest_verified": False,
        "obb_contents_digest_verified": False,
        "xapk_contents_digest_verified": False,
        "published_release_asset_digest_verified": False,
        "android_device_offline_world_save_reopen_verified": False,
    }


def _read(path):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 1_000_000:
        raise ValueError("Missing or oversized safe metadata fixture")
    return json.loads(p.read_text(encoding="utf-8"))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot", required=True)
    p.add_argument("--id", required=True, type=int)
    p.add_argument("--sha", required=True)
    args = p.parse_args(argv)
    result = classify(_read(args.snapshot), expected_id=args.id, expected_sha=args.sha)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
