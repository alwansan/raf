"""Automate source preparation and GLES rendering for all six calibration samples."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from gfxlab.tools.gfx123_model_forward_prepare import MODEL_IDS, prepare

EXPECTED = {(model, 0) for model in MODEL_IDS} | {("M03", 1)}


def replay(zip2, stage, work, safe):
    work.mkdir(parents=True, exist_ok=False)
    source = prepare(zip2, stage, work, models=MODEL_IDS)
    if {(row["model"], row["slot"]) for row in source["slots"]} != EXPECTED:
        raise ValueError("Original sample scope changed")
    env = {**os.environ, "EGL_PLATFORM": "surfaceless", "LIBGL_ALWAYS_SOFTWARE": "1"}
    rows = []
    portable = work / "portable"
    for row in source["slots"]:
        label = f'{row["model"]}-{row["slot"]}'
        slot = work / label
        report = work / (label + ".json")
        command = [sys.executable, "-m", "gfxlab.tools.gfx119_mesa_forward_draw",
                   "--private", str(slot), "--textures", str(slot), "--safe", str(report),
                   "--portable", str(portable / label)]
        if label == "M03-0":
            command += ["--second-slot", str(work / "M03-1")]
        try:
            subprocess.run(command, env=env, stdout=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError as error:
            raise ValueError(f"Forward GPU validation failed for {label}") from error
        result = json.loads(report.read_text())
        if not result["original_translated_forward_draw_completed"] or not result["baseline_repeat_exact"]:
            raise ValueError(f"Forward GPU result incomplete for {label}")
        rows.append({"source": row, "gpu": result})
    safe.write_text(json.dumps({"experiment": "GFX153", "source_sha": source["source_sha"],
                                "models": len(MODEL_IDS), "gpu_slots": len(rows), "slots": rows,
                                "unity_runtime_state_verified": False, "phase_closed": False}, indent=2)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for key in ("zip2", "stage", "work", "safe"):
        parser.add_argument("--"+key, type=Path, required=True)
    args = parser.parse_args()
    replay(args.zip2, args.stage, args.work, args.safe)
