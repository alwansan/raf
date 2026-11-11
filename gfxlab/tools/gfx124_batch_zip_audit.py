"""Verify one GFX124 batch export against the packaged Mesa readbacks."""
import argparse
import json
from zipfile import ZipFile

from gfxlab.tools.gfx120_owner_zip_audit import audit_capture
from gfxlab.tools.gfx124_batch_pack import CONTROLS


def audit(owner_zip, apk):
    with ZipFile(owner_zip) as logs, ZipFile(apk) as package:
        entries = logs.infolist()
        names = {entry.filename for entry in entries}
        if len(entries) != len(names) or "summary.json" not in names or any(
            entry.file_size > 512 * 1024 for entry in entries
        ):
            raise ValueError("Unexpected Android batch archive")
        report = json.loads(logs.read("summary.json"))
        if report["experiment"] != "GFX124" or report["phase_closed"] is not False:
            raise ValueError("Wrong Android batch")
        result = {key: report.get(key) for key in ("experiment", "renderer", "gles", "phase_closed")}
        if "error" in report:
            return {**result, "error": report["error"], "completed_tests": 0}
        tests = json.loads(package.read("assets/batch.json"))["tests"]
        runs = report["tests"]
        if [run["id"] for run in runs] != [test["id"] for test in tests]:
            raise ValueError("Batch case order or identity changed")
        safe = []
        images = set()
        for test, run in zip(tests, runs, strict=True):
            merged = "secondary" in test
            controls = ("combined",) if merged else CONTROLS
            completed = run["draw_completed"] is True
            captures = run["captures"]
            if len(captures) > len(controls) or (completed and len(captures) != len(controls)):
                raise ValueError("Wrong capture count")
            metrics, pixels = {}, {}
            for control, row in zip(controls, captures):
                capture = test["id"] if merged else f'{test["id"]}-{control}'
                if row["name"] != capture:
                    raise ValueError("Wrong Android capture identity")
                name = capture + ".png"
                images.add(name)
                reference = package.read(f'assets/{test["primary"]}/{control}.rgba')
                pixels[control], metrics[control] = audit_capture(row, name, logs.read(name), reference)
            checked = {"id": run["id"], "draw_completed": completed, "captures": metrics}
            if completed and not merged:
                light = pixels["light"]
                checked["control_rgb_changed_pixels"] = {
                    control: sum(light[i:i+3] != pixels[control][i:i+3] for i in range(0, len(light), 4))
                    for control in CONTROLS[1:]
                }
            if not completed:
                checked["error"] = run["error"]
            safe.append(checked)
        completed = sum(case["draw_completed"] for case in safe)
        if names != images | {"summary.json"} or report["completed_tests"] != completed or report["planned_tests"] != len(safe):
            raise ValueError("Batch counts or entries disagree with summary")
        return {**result, "completed_tests": completed, "tests": safe}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args = parser.parse_args()
    print(json.dumps(audit(args.owner_zip, args.signed_apk), indent=2))
