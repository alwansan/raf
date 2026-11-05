"""T5: fail-closed verdict for GitHub native build job metadata.

Use GitHub's official workflow-run, workflow-run-jobs, and artifacts JSON.
Do not infer a successful device install or a signed release from job metadata.
No logs, original assets, or credentials are consumed or emitted.
"""
import argparse
import json
from pathlib import Path
import re

_SHA = re.compile(r"^[0-9a-f]{40}$")
_STEP_TAGS = {
    "Restore every pinned external Mesh buffer while retaining original serialized identities":
        "original_mesh_restoration",
    "Unity Editor 2021.3.45f2 Android import and compile": "unity_editor_import",
    "Package complete owner-authorized APK OBB and XAPK delivery": "delivery_package",
    "Verify actual APK signature before any early device-test delivery": "signature_check",
}


def _object(value, name):
    if not isinstance(value, dict):
        raise ValueError(name + " must be an object")
    return value


def _job_index(jobs):
    records = _object(jobs, "jobs response").get("jobs")
    if not isinstance(records, list):
        raise ValueError("GitHub jobs response must contain jobs array")
    answer = {}
    wanted = {
        "native-request-gate", "unity-license-preflight",
        "reconstruct", "delivery-result", "publish-early-test",
    }
    for item in records:
        item = _object(item, "job")
        name = item.get("name")
        if name in wanted:
            if name in answer:
                raise ValueError("Duplicate native workflow job")
            if item.get("conclusion") not in {
                None, "success", "failure", "cancelled", "skipped",
                "timed_out", "neutral", "action_required",
            }:
                raise ValueError("Unexpected native job conclusion")
            answer[name] = item
    return answer


def _failed_stage(reconstruct):
    if reconstruct is None:
        return "not_started"
    steps = reconstruct.get("steps", [])
    if not isinstance(steps, list):
        raise ValueError("GitHub job steps must be an array")
    interrupted = [x for x in steps if isinstance(x, dict) and
                   x.get("conclusion") in ("cancelled", "failure", "timed_out")]
    if not interrupted:
        return "stage_unknown"
    # Last interrupted step is not evidence of which actor cancelled the job.
    return _STEP_TAGS.get(interrupted[-1].get("name"), "other_or_unknown_stage")


def classify(run, jobs, artifacts, *, expected_id, expected_sha):
    run = _object(run, "workflow run")
    art = _object(artifacts, "artifacts response")
    entries = art.get("artifacts")
    if not isinstance(entries, list):
        raise ValueError("Artifacts must be an explicit list, even when empty")
    sha = run.get("head_sha")
    if not isinstance(sha, str) or not _SHA.fullmatch(sha):
        raise ValueError("Invalid or missing run source SHA")
    if not isinstance(expected_sha, str) or not _SHA.fullmatch(expected_sha):
        raise ValueError("Invalid expected source SHA")
    if type(expected_id) is not int or type(run.get("id")) is not int:
        raise ValueError("Run ID must be an integer")
    if run["id"] != expected_id or sha != expected_sha:
        raise ValueError("Immutable run identity mismatch")

    status, conclusion = run.get("status"), run.get("conclusion")
    if status not in {
        "completed", "in_progress", "queued", "waiting", "pending",
        "requested", "action_required",
    }:
        raise ValueError("Unknown GitHub run status")
    if status == "completed":
        if conclusion not in {
            "success", "failure", "cancelled", "skipped", "timed_out",
            "neutral", "action_required",
        }:
            raise ValueError("A completed run requires a known conclusion")
    elif conclusion is not None:
        raise ValueError("Nonterminal GitHub run cannot have a conclusion")

    lane = _job_index(jobs)
    native = lane.get("reconstruct")
    native_result = native.get("conclusion") if native else None
    result_gate = lane.get("delivery-result")
    downstream_failure = bool(
        native_result == "cancelled" and result_gate and
        result_gate.get("conclusion") == "failure"
    )
    if status != "completed":
        verdict = "awaiting_terminal_workflow"
    elif native_result == "cancelled":
        verdict = "native_job_cancelled_no_source_failure_established"
    elif native_result in {"failure", "timed_out"}:
        verdict = "native_job_failed_or_timed_out"
    elif native_result == "success":
        published = lane.get("publish-early-test")
        verdict = (
            "native_job_passed_publish_job_passed_but_release_unverified"
            if published and published.get("conclusion") == "success"
            else "native_job_passed_delivery_unverified"
        )
    else:
        verdict = "native_job_not_successfully_executed"

    if status == "completed" and native_result == "cancelled" and conclusion == "success":
        raise ValueError("Contradictory completed-success / cancelled native job")
    if status == "completed" and native_result in {"failure", "timed_out"} and conclusion == "success":
        raise ValueError("Contradictory completed-success / failed native job")
    if status == "completed" and conclusion == "success" and native_result != "success":
        raise ValueError("Success requires successful native reconstruct")

    return {
        "run_id": expected_id,
        "source_sha": expected_sha,
        "run_status": status,
        "run_conclusion": conclusion,
        "native_conclusion": native_result,
        "native_stage": _failed_stage(native),
        "verdict": verdict,
        "request_gate_passed": bool(
            lane.get("native-request-gate") and
            lane["native-request-gate"].get("conclusion") == "success"
        ),
        "license_preflight_passed": bool(
            lane.get("unity-license-preflight") and
            lane["unity-license-preflight"].get("conclusion") == "success"
        ),
        "downstream_failure_follows_cancelled_native": downstream_failure,
        "artifact_records": len(entries),
        "delivery_package_sha_verified": False,
        "signed_release_assets_verified": False,
        "android_install_verified": False,
        "cancellation_initiator": "unknown",
    }


def _read_json(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 2_000_000:
        raise ValueError("Invalid or oversized metadata input")
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--jobs", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--id", type=int, required=True)
    parser.add_argument("--sha", required=True)
    args = parser.parse_args(argv)
    result = classify(
        _read_json(args.run), _read_json(args.jobs),
        _read_json(args.artifacts), expected_id=args.id,
        expected_sha=args.sha
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
