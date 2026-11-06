"""T2: fail-closed material-level water pass triage of pinned CL session summaries.

Source-free aggregate only. Never infer pixel parity or device shader correctness.
"""
import argparse
import json
from pathlib import Path

MATERIALS = ("spectrum", "foam_global", "subsurface_blur", "utility_noise", "other_ultimate_water")
MAX_BYTES = 128 * 1024


def classify(summary):
    if not isinstance(summary, dict) or summary.get("schema") != 1:
        raise ValueError("unsupported_session_schema")
    session = summary.get("session")
    if not isinstance(session, str) or not session.startswith("20261105-") or len(session) > 64:
        raise ValueError("unexpected_session_identity")
    stop = summary.get("stop_time_android_process_exit_info")
    if not isinstance(stop, dict):
        raise ValueError("missing_final_game_totals")
    breakdown = stop.get("final_render_failure_breakdown")
    if not isinstance(breakdown, dict):
        raise ValueError("missing_material_breakdown")
    rows = breakdown.get("ultimate_water_invalid_pass_by_material")
    if not isinstance(rows, dict) or set(rows) != set(MATERIALS):
        raise ValueError("unrecognized_material_categories")
    if any(type(v) is not int or v < 0 for v in rows.values()):
        raise ValueError("invalid_material_counts")
    total = stop.get("final_shader_pass_errors_total")
    if type(total) is not int or total < 0 or sum(rows.values()) != total:
        raise ValueError("material_total_inconsistent")
    groups = summary.get("final_error_category_breakdown")
    if (not isinstance(groups, dict) or not isinstance(groups.get("ultimate_water_invalid_pass"), dict)
            or type(groups["ultimate_water_invalid_pass"].get("count")) is not int
            or groups["ultimate_water_invalid_pass"]["count"] != total):
        raise ValueError("root_category_total_inconsistent")
    kernel = stop.get("final_compute_kernel_errors_total")
    if type(kernel) is not int or kernel < 0:
        raise ValueError("kernel_total_invalid")
    return {"session": session, "water_pass_errors": total,
            "by_material": {k: rows[k] for k in MATERIALS},
            "fft_kernel_errors_separate": kernel,
            "foam_share_of_water_pass_errors_pct": round(rows["foam_global"] * 100 / total, 2) if total else None,
            "no_observed_blur_pass_error_is_not_pixel_validation": True,
            "source": "pinned_CL_session_summary_final_game_UID"}


def _reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def read(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_BYTES:
        raise ValueError("invalid_summary_file")
    return classify(json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("summaries", nargs="+", type=Path)
    args = parser.parse_args()
    results = [read(p) for p in args.summaries]
    ids = [r["session"] for r in results]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate_session")
    print(json.dumps({"status": "device_material_error_triage_only",
                      "sessions": results, "shaderlab_or_device_fix_verified": False},
                     sort_keys=True))


if __name__ == "__main__":
    main()
