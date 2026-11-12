"""Independently compare the four Android readbacks to the analytical fixture."""
import argparse
import json
import math
import struct
from zipfile import ZipFile

SIDE = 32
COUNT = SIDE * SIDE
FRAMES = ((0, 0), (0, 1), (0.75, 1), (1.5, 1))


def audit(path):
    names = {"summary.json", *(f"heights-{i}.f32le" for i in range(4))}
    previous = None
    for_output = []
    with ZipFile(path) as archive:
        if set(archive.namelist()) != names or len(archive.namelist()) != len(names):
            raise ValueError("Incomplete or ambiguous export")
        summary = json.loads(archive.read("summary.json"))
        if (summary["experiment"] != "GFX160" or summary["graphicsApi"] != "Vulkan"
                or summary["threadsX"] != 32 or summary["intermediateFormat"] != "R32G32_SFloat"
                or not 0 <= summary["maxImaginary"] <= 3e-5
                or len({summary["horizontalKernel"], summary["verticalKernel"], summary["readbackKernel"]}) != 3 or summary["originalRaftData"] or not summary["passed"]):
            raise ValueError("Unexpected experiment, graphics API or dispatch result")
        for index, (time, scale) in enumerate(FRAMES):
            values = struct.unpack(f"<{COUNT}f", archive.read(f"heights-{index}.f32le"))
            if any(not math.isfinite(value) for value in values):
                raise ValueError(f"Frame {index} has an unwritten or non-finite height")
            errors = []
            for i, value in enumerate(values):
                x, z = i % SIDE, i // SIDE
                angle = math.tau / SIDE
                expected = scale * (0.43 * math.cos(angle * (2 * x + z) - 1.9 * time)
                                    + 0.21 * math.cos(angle * (x + 3 * z) - 2.7 * time))
                errors.append(abs(value - expected))
            error = max(errors)
            delta = max(abs(a - b) for a, b in zip(previous, values)) if previous else 0
            if error > 3e-5 or (index and delta <= 0.1):
                raise ValueError(f"Frame {index}: error={error}, delta={delta}")
            for_output.append({"time": time, "scale": scale, "maximum_error": error, "maximum_delta": delta})
            previous = values
    return {"gpu": summary["gpu"], "cases": for_output, "samples_per_case": COUNT}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive")
    args = parser.parse_args()
    print(json.dumps(audit(args.archive), indent=2))
