"""Stage/run a fresh authored Unity material/alpha scene; never stage game data.

The pixel gate independently checks all 120 synthetic readback pixels. Source
tests and a missing Unity executable cannot produce a raster PASS receipt.
"""
import argparse
from hashlib import sha256
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import uuid

EDITOR_VERSION = "2021.3.45f2"
ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "tools/synthetic_material_alpha"
ASSETS = {
    "Assets/SyntheticMaterialAlpha.shader": "SyntheticMaterialAlpha.shader",
    "Assets/Editor/SyntheticMaterialAlphaValidation.cs": "SyntheticMaterialAlphaValidation.cs",
}
WIDTH, HEIGHT = 6, 4
TOLERANCE, MINIMUM_MISMATCH = 0.002, 0.05
BACKGROUND = (0.125, 0.25, 0.5, 1.0)
TINT = (0.5, 0.75, 0.25, 1.0)
COLUMNS = ((0., 0., 0., 0.), (1., .25, 0., .5), (.25, 1., .5, 1.),
           (.75, .125, 1., 1.), (.125, .5, .75, .5), (0., 0., 0., 0.))
CASES = ("opaque_texture_tint", "straight_alpha", "missing_texture_binding",
         "missing_tint_binding", "disabled_blending")
SETTINGS = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 26
  companyName: SyntheticValidation
  productName: SyntheticMaterialAlpha
  m_ColorSpace: 1
"""


def regular_path(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("symlink_path_not_allowed")
    return path


def source_hashes():
    return {key: sha256((SOURCES / name).read_bytes()).hexdigest()
            for key, name in ASSETS.items()}


def construct(project):
    project = regular_path(project)
    if project.exists() or not project.parent.is_dir():
        raise ValueError("fresh_project_under_existing_parent_required")
    files = {key: (SOURCES / name).read_bytes() for key, name in ASSETS.items()}
    files.update({"Packages/manifest.json": b'{"dependencies":{}}\n',
                  "ProjectSettings/ProjectVersion.txt":
                      ("m_EditorVersion: " + EDITOR_VERSION + "\n").encode(),
                  "ProjectSettings/ProjectSettings.asset": SETTINGS.encode()})
    manifest = {"schema_version": 1, "synthetic_only": True,
                "files": {key: sha256(value).hexdigest() for key, value in files.items()}}
    for key, value in files.items():
        target = project / key
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value)
    (project / "synthetic-alpha-fixture.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {"status": "PREPARED", "Unity_render_executed": False,
            "synthetic_only": True, "fixture_files": len(files), "source_hashes": source_hashes()}


def check_project(project):
    project = regular_path(project)
    manifest = json.loads((project / "synthetic-alpha-fixture.json").read_text())
    required = set(ASSETS) | {"Packages/manifest.json", "ProjectSettings/ProjectVersion.txt",
                              "ProjectSettings/ProjectSettings.asset"}
    if (manifest.get("schema_version") != 1 or manifest.get("synthetic_only") is not True
            or set(manifest.get("files", {})) != required):
        raise ValueError("unexpected_fixture_manifest")
    for key, digest in manifest["files"].items():
        path = regular_path(project / key)
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("fixture_content_changed")
    for key, digest in source_hashes().items():
        if manifest["files"][key] != digest:
            raise ValueError("fixture_source_candidate_changed")
    if json.loads((project / "Packages/manifest.json").read_text()) != {"dependencies": {}}:
        raise ValueError("unexpected_fixture_dependencies")
    for asset in (project / "Assets").rglob("*"):
        regular_path(asset)
        if asset.is_file() and asset.relative_to(project).as_posix() not in ASSETS:
            # An unlaunched fixture has no generated meta files or extra scripts.
            raise ValueError("unexpected_fixture_asset")
    return source_hashes()


def expected_pixel(case, x):
    texel = list(COLUMNS[x])
    if case == "opaque_texture_tint":
        texel[3] = 1.0

    def composite(source, disabled=False):
        a = source[3]
        rgb = source[:3] if disabled else [source[i] * a + BACKGROUND[i] * (1 - a) for i in range(3)]
        return [*rgb, a + BACKGROUND[3] * (1 - a)]

    intended = composite([a * b for a, b in zip(texel, TINT)])
    supplied = (1., 1., 1., 1.) if case == "missing_texture_binding" else texel
    tint = (1., 1., 1., 1.) if case == "missing_tint_binding" else TINT
    actual_expected = composite([a * b for a, b in zip(supplied, tint)], case == "disabled_blending")
    return actual_expected, intended


def finite(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("nonfinite_or_nonnumeric_pixel_evidence")
    return value


def vector(value):
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError("RGBA_evidence_required")
    return [finite(x) for x in value]


def maximum_difference(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


def receipt_identity(report, run_id, hashes):
    return isinstance(report, dict) and report.get("run_id") == run_id and all(
        report.get(key) == hashes[path] for key, path in (
            ("shader_sha256", "Assets/SyntheticMaterialAlpha.shader"),
            ("probe_sha256", "Assets/Editor/SyntheticMaterialAlphaValidation.cs")))


def validate_receipt(report, *, run_id, hashes, exit_code):
    """Return independently recomputed results or raise; no bool-only acceptance."""
    if not isinstance(report, dict):
        raise ValueError("object_receipt_required")
    if type(exit_code) is not int or exit_code != 0:
        raise ValueError("Unity_process_did_not_succeed")
    required = {"schema_version": 1, "run_id": run_id, "status": "PASS",
                "Unity_version": EDITOR_VERSION, "backend": "Vulkan",
                "active_color_space": "Linear", "synthetic_only": True,
                "Unity_render_executed": True, "Android_device": False,
                "production_pixels": False, "XAPK": False,
                "rendered_case_count": 5, "positive_case_count": 2,
                "negative_controls_detected": 3,
                "shader_sha256": hashes["Assets/SyntheticMaterialAlpha.shader"],
                "probe_sha256": hashes["Assets/Editor/SyntheticMaterialAlphaValidation.cs"]}
    for key, expected in required.items():
        value = report.get(key)
        if type(value) is not type(expected) or value != expected:
            raise ValueError("receipt_contract_mismatch:" + key)
    cases = report.get("cases")
    if not isinstance(cases, list) or len(cases) != len(CASES):
        raise ValueError("five_unique_raster_cases_required")
    seen, errors = set(), []
    for row in cases:
        if not isinstance(row, dict):
            raise ValueError("object_case_required")
        name = row.get("name")
        if name not in CASES or name in seen:
            raise ValueError("unexpected_or_duplicate_raster_case")
        seen.add(name)
        positive = name in CASES[:2]
        if (row.get("kind") != ("positive" if positive else "negative")
                or row.get("pass") is not True or type(row.get("checked_pixel_count")) is not int
                or row["checked_pixel_count"] != WIDTH * HEIGHT):
            raise ValueError("case_contract_mismatch")
        samples = row.get("samples")
        if not isinstance(samples, list) or len(samples) != WIDTH * HEIGHT:
            raise ValueError("complete_pixel_readback_required")
        coords, error, mismatch = set(), 0.0, 0.0
        for sample in samples:
            if not isinstance(sample, dict):
                raise ValueError("object_pixel_sample_required")
            x, y = sample.get("x"), sample.get("y")
            if type(x) is not int or type(y) is not int or not 0 <= x < WIDTH or not 0 <= y < HEIGHT or (x, y) in coords:
                raise ValueError("pixel_coordinates_invalid_or_duplicated")
            coords.add((x, y))
            observed = vector(sample.get("observed"))
            expected, intended = expected_pixel(name, x)
            if (maximum_difference(vector(sample.get("expected")), expected) > 1e-6
                    or maximum_difference(vector(sample.get("intended")), intended) > 1e-6):
                raise ValueError("receipt_oracle_differs_from_independent_reference")
            error = max(error, maximum_difference(observed, expected))
            mismatch = max(mismatch, maximum_difference(observed, intended))
        if error > TOLERANCE or (not positive and mismatch < MINIMUM_MISMATCH):
            raise ValueError("pixel_or_negative_control_failed")
        if (abs(finite(row.get("max_error")) - error) > 1e-6
                or abs(finite(row.get("intended_mismatch")) - mismatch) > 1e-6):
            raise ValueError("case_numeric_summary_mismatch")
        errors.append(error)
    if abs(finite(report.get("max_error")) - max(errors)) > 1e-6:
        raise ValueError("receipt_numeric_summary_mismatch")
    return {"validated_cases": len(cases), "validated_pixels": WIDTH * HEIGHT * len(cases),
            "positive_cases": 2, "negative_controls_detected": 3, "max_error": max(errors)}


def execute(project, output, *, unity=None, timeout=600):
    project, output = regular_path(project), regular_path(output)
    hashes = check_project(project)
    raw, log = output.with_suffix(".unity.json"), output.with_suffix(".unity.log")
    for path in (output, raw, log):
        regular_path(path)
        if path.exists() or not path.parent.is_dir() or path.is_relative_to(project):
            raise ValueError("fresh_outside_project_receipt_paths_required")
    run_id = uuid.uuid4().hex
    result = {"schema_version": 1, "status": "NOT_RUN", "reason": "Unity_editor_unavailable",
              "run_id": run_id, "synthetic_only": True, "Unity_render_executed": False,
              "Vulkan_raster_validation_passed": False, "Android_device": False,
              "production_pixels": False, "XAPK": False, "source_hashes": hashes}
    executable = unity or os.environ.get("RAFT_UNITY_EDITOR") or shutil.which("Unity") or shutil.which("unity-editor")
    if executable and Path(executable).is_file() and os.access(executable, os.X_OK):
        command = [str(executable), "-batchmode", "-force-vulkan", "-projectPath", str(project),
                   "-executeMethod", "SyntheticMaterialAlphaValidation.Run", "-logFile", str(log)]
        environment = dict(os.environ, RAFT_SYNTHETIC_ALPHA_REPORT=str(raw),
                           RAFT_SYNTHETIC_ALPHA_RUN_ID=run_id)
        try:
            process = subprocess.run(command, env=environment, timeout=timeout,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            result["process_exit_code"] = process.returncode
            if not raw.is_file() or raw.is_symlink() or raw.stat().st_size > 256 * 1024:
                raise ValueError("fresh_bounded_Unity_receipt_missing")
            report = json.loads(raw.read_text())
            result["Unity_render_executed"] = receipt_identity(report, run_id, hashes) and report.get("Unity_render_executed") is True
            validated = validate_receipt(report, run_id=run_id, hashes=hashes, exit_code=process.returncode)
            result.update(validated, status="PASS", reason="independent_synthetic_pixel_validation_passed",
                          Vulkan_raster_validation_passed=True, Unity_version=report["Unity_version"],
                          backend=report["backend"], receipt_sha256=sha256(raw.read_bytes()).hexdigest())
        except (OSError, ValueError, TypeError, KeyError, subprocess.TimeoutExpired) as exc:
            result.update(status="FAIL", reason=type(exc).__name__ + ": " + str(exc))
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def verify_file(receipt, output, *, run_id, exit_code):
    """Check a fresh CI receipt against this exact source candidate and run."""
    receipt, output = regular_path(receipt), regular_path(output)
    if output.exists() or not output.parent.is_dir():
        raise ValueError("fresh_verification_output_required")
    result = {"schema_version": 1, "status": "NOT_RUN", "reason": "Unity_receipt_missing",
              "run_id": run_id, "synthetic_only": True, "Unity_render_executed": False,
              "Vulkan_raster_validation_passed": False, "Android_device": False,
              "production_pixels": False, "XAPK": False, "source_hashes": source_hashes()}
    try:
        if receipt.is_file():
            if receipt.stat().st_size > 256 * 1024:
                raise ValueError("bounded_receipt_required")
            report = json.loads(receipt.read_text())
            if not isinstance(report, dict):
                raise ValueError("object_receipt_required")
            matching_identity = receipt_identity(report, run_id, source_hashes())
            if matching_identity:
                result.update(Unity_render_executed=report.get("Unity_render_executed") is True,
                              receipt_status=report.get("status"),
                              receipt_reason=str(report.get("reason", ""))[:256])
            if matching_identity and report.get("status") == "NOT_RUN" and report.get("Unity_render_executed") is False:
                result.update(status="NOT_RUN", reason="Unity_prerequisite_unavailable:" + result["receipt_reason"])
            else:
                validated = validate_receipt(report, run_id=run_id, hashes=source_hashes(), exit_code=exit_code)
                result.update(validated, status="PASS", reason="independent_synthetic_pixel_validation_passed",
                              Unity_render_executed=True, Vulkan_raster_validation_passed=True,
                              Unity_version=report["Unity_version"], backend=report["backend"],
                              graphics_device_name=report.get("graphics_device_name", "not_reported"),
                              receipt_sha256=sha256(receipt.read_bytes()).hexdigest())
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result.update(status="FAIL", reason=type(exc).__name__ + ": " + str(exc))
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("stage", "run", "verify"))
    parser.add_argument("--project", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--unity", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--exit-code", type=int)
    args = parser.parse_args()
    if args.action == "verify":
        if args.receipt is None or args.out is None or not args.run_id or args.exit_code is None:
            parser.error("verify requires --receipt, --out, --run-id and --exit-code")
        result = verify_file(args.receipt, args.out, run_id=args.run_id, exit_code=args.exit_code)
    elif args.project is None:
        parser.error("stage/run requires --project")
    elif args.action == "stage":
        result = construct(args.project)
    else:
        if args.out is None:
            parser.error("run requires --out")
        result = execute(args.project, args.out, unity=args.unity)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] in ("PREPARED", "PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
