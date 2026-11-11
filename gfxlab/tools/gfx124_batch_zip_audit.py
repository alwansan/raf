"""Verify one GFX124 batch export against the packaged Mesa readbacks."""
import argparse
import json
from zipfile import ZipFile

from gfxlab.tools.gfx120_owner_zip_audit import audit_capture
from gfxlab.tools.gfx124_batch_pack import CONTROLS, POSES, SHADOW_CONTROLS


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
        baselines = {}
        for test, run in zip(tests, runs, strict=True):
            merged = "secondary" in test
            additive = "forward_add" in test
            animated = "animation" in test
            shadow = "shadow" in test
            controls = SHADOW_CONTROLS if shadow else POSES if animated else ("lit", "off", "reject") if additive else ("combined",) if merged else CONTROLS
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
                folder = test["primary"]
                ref = control
                if animated:
                    folder = test["animation"]
                if shadow:
                    folder = test["shadow"]
                if additive:
                    folder = test["forward_add"] if control == "lit" else folder
                    ref = "combined" if control == "lit" else "light"
                reference = package.read(f"assets/{folder}/{ref}.rgba")
                pixels[control], metrics[control] = audit_capture(row, name, logs.read(name), reference, allow_empty=shadow)
            checked = {"id": run["id"], "draw_completed": completed, "captures": metrics}
            if completed and not merged and not additive and not animated and not shadow:
                light = pixels["light"]
                baselines[test["primary"]] = light
                checked["control_rgb_changed_pixels"] = {
                    control: sum(light[i:i+3] != pixels[control][i:i+3] for i in range(0, len(light), 4))
                    for control in CONTROLS[1:]
                }
            if additive and completed and test["primary"] in baselines:
                base = baselines[test["primary"]]
                checked["controls_preserved_forward"] = {
                    control: pixels[control] == base for control in ("off", "reject")
                }
                checked["additional_light_changed_pixels"] = sum(
                    base[i:i+3] != pixels["lit"][i:i+3] for i in range(0, len(base), 4))
            if animated and completed:
                checked["unique_images_per_clip"] = [
                    len({pixels[f"C{clip}P{pose}"] for pose in range(5)}) for clip in range(3)]
            if shadow and completed:
                checked["shadow_controls"] = {
                    "native_has_depth": metrics["native"]["covered_pixels"] > 0,
                    "solid_has_depth": metrics["solid"]["covered_pixels"] > 0,
                    "transparent_has_no_depth": metrics["transparent"]["covered_pixels"] == 0,
                    "depth_write_off_has_no_depth": metrics["depth-off"]["covered_pixels"] == 0,
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
