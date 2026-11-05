"""Fail-closed classification of the T1 Unity import CI boundary from GitHub jobs JSON.

A failed activation step is not evidence about shader compilation or kernels.
"""
import argparse
import json
from pathlib import Path

ACTIVATION = "Verify real Unity activation on tiny source-free project BEFORE acquiring game data"
IMPORT = "Invoke isolated Unity 2021 Editor; keep all compiler logs private"


def classify(payload):
    jobs = payload.get("jobs")
    if not isinstance(jobs, list) or len(jobs) != 1:
        raise ValueError("expected exactly one isolated Unity import job")
    job = jobs[0]
    if job.get("name") != "unity-private-compute-import":
        raise ValueError("unexpected job identity")
    steps = job.get("steps")
    if not isinstance(steps, list):
        raise ValueError("missing steps")
    by_name = {}
    for step in steps:
        name = step.get("name")
        if name in by_name:
            raise ValueError("duplicate step identity")
        by_name[name] = step
    if ACTIVATION not in by_name or IMPORT not in by_name:
        raise ValueError("required gate missing")
    activation_step = by_name[ACTIVATION]
    import_step = by_name[IMPORT]
    activation = activation_step.get("conclusion")
    imported = import_step.get("conclusion")
    # A conclusion without a started_at timestamp is insufficient to prove that
    # the import command actually ran. GitHub step JSON includes started_at.
    import_started = bool(import_step.get("started_at"))
    if steps.index(activation_step) >= steps.index(import_step):
        raise ValueError("import gate precedes activation")
    if activation != "success":
        return {"boundary": "unity_activation", "activation": activation, "import": imported,
                "shader_import_attempted": False, "unity_runtime_proven": False}
    if imported != "success":
        return {"boundary": "unity_import", "activation": activation, "import": imported,
                "shader_import_attempted": import_started and imported not in ("skipped", None), "unity_runtime_proven": False}
    return {"boundary": "unity_import_completed", "activation": activation, "import": imported,
            "shader_import_attempted": import_started, "unity_runtime_proven": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("jobs_json", type=Path)
    args = p.parse_args()
    print(json.dumps(classify(json.loads(args.jobs_json.read_text())), sort_keys=True))


if __name__ == "__main__":
    main()
