"""Check a GFX109 owner export against the exact signed test APK inputs."""
import argparse
import hashlib
import json
import math
from zipfile import ZipFile

from gfxlab.tools.gfx109_gpu_skin_payload import EXPECTED


def audit(owner_zip, apk, *, experiment="GFX109", expected=EXPECTED):
    with ZipFile(owner_zip) as archive:
        entries = archive.infolist()
        if (len(entries) != 1 or entries[0].filename != "summary.json"
                or not 0 < entries[0].file_size < 32768):
            raise ValueError("Unexpected owner export contents")
        report = json.loads(archive.read(entries[0]))
    if (report["experiment"] != experiment or report["phase_closed"] is not False
            or not report.get("renderer") or not report.get("gles")
            or report["absolute_tolerance"] != 0.0001
            or report["relative_tolerance"] != 0.000001):
        raise ValueError("Unexpected probe context")
    cases = report["cases"]
    models = [case["model"] for case in cases]
    if models != list(expected)[:len(models)]:
        raise ValueError("Unexpected model sequence")

    total = failures = 0
    maximum = 0.0
    with ZipFile(apk) as package:
        for case in cases:
            model = case["model"]
            vertices, bones = expected[model]
            payload = package.read(f"assets/{model}.bin")
            if (case["vertices"] != vertices or case["bones"] != bones
                    or case["gpu_vertices_written"] != vertices
                    or case["source_payload_sha256"] != hashlib.sha256(payload).hexdigest()):
                raise ValueError(f"Input or GPU count mismatch for {model}")
            failed, nonfinite = case["failing_vertices"], case["nonfinite_vertices"]
            error = case["max_absolute_error"]
            if (type(failed) is not int or type(nonfinite) is not int
                    or not 0 <= nonfinite <= failed <= vertices
                    or not math.isfinite(error) or error < 0):
                raise ValueError(f"Invalid result for {model}")
            total += vertices
            failures += failed
            maximum = max(maximum, error)
    passed = models == list(expected) and failures == 0 and "error" not in report
    if report["gpu_source_position_match"] is not passed:
        raise ValueError("Summary disagrees with recorded cases")
    return {"experiment": experiment, "models_checked": len(models), "vertices_checked": total,
            "failing_vertices": failures, "max_absolute_error": maximum,
            "gpu_source_position_match": passed, "phase_closed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("owner_zip")
    parser.add_argument("signed_apk")
    args = parser.parse_args()
    print(json.dumps(audit(args.owner_zip, args.signed_apk), indent=2))
