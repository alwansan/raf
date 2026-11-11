"""Stage the 15 authentic M02 pose samples for the GLES3 readback probe."""
import argparse
import hashlib
import json
from pathlib import Path

from gfxlab.tools.gfx109_gpu_skin_payload import write_case
from gfxlab.tools.gfx111_m02_clip_pose import run
from gfxlab.tools.original_model_probe import stage_originals

EXPECTED = tuple(f"C{clip}P{sample}" for clip in range(3) for sample in range(5))


def main():
    parser = argparse.ArgumentParser()
    for name in ("zip2", "stage", "assets", "safe"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    args.assets.mkdir(parents=True, exist_ok=True)
    samples = {}

    def consume(clip, sample, time, positions, weights, world, bindposes, reference):
        if len(positions) != 1666 or len(world) != 8:
            raise ValueError("M02 source shape changed")
        name = f"C{clip}P{sample}"
        payload = args.assets / (name + ".bin")
        write_case(payload, positions, weights, world, bindposes, reference)
        samples[name] = {"clip_index": clip, "sample_index": sample, "time_s": time,
                         "sha256": hashlib.sha256(payload.read_bytes()).hexdigest()}

    report = run(stage_originals(args.zip2, args.stage), consume)
    if tuple(samples) != EXPECTED:
        raise ValueError("Missing or reordered M02 pose samples")
    hashes = [row["sha256"] for row in samples.values()]
    if len(set(hashes[:5])) != 1 or any(len(set(hashes[i:i+5])) != 5 for i in (5, 10)):
        raise ValueError("Constant and animated sample distinctions do not match GFX111")
    report.update(experiment="GFX112", sample_payloads=samples, expected_gpu_positions=24990)
    args.safe.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
