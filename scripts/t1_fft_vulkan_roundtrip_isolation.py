"""Compare the exact paired FFT fixture on one Vulkan backend. Publish counts only."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile

from scripts.t1_fft_readback_parity import PIXEL, SENTINEL, compare_pass, read_image
from scripts.t1_fft_vulkan_parity_capture import render_host

WIDTH, HEIGHT = 1024, 32
FILES = ("original0", "original1", "roundtrip0", "roundtrip1")


def capture_host(source: str) -> str:
    source = render_host(source)
    replacements = {
        "VkImageMemoryBarrier,3> postBarriers": "VkImageMemoryBarrier,4> postBarriers",
        "for(int i=0;i<3;i++){\n        postBarriers": "for(int i=0;i<4;i++){\n        postBarriers",
        "images[i==0?2:(i==1?3:5)].image": "images[2+i].image",
        "nullptr,3,postBarriers.data()": "nullptr,4,postBarriers.data()",
        '"source.rgba32f","butterfly.rgba32f","pass0.rgba32f","pass1.rgba32f"':
            ",".join(f'"{name}.rgba32f"' for name in FILES),
        "p=pixel(images[i],x,y,imageFormat)": "p=pixel(images[2+i],x,y,imageFormat)",
    }
    for anchor, replacement in replacements.items():
        if source.count(anchor) != 1:
            raise ValueError("Private capture anchor changed")
        source = source.replace(anchor, replacement)
    return source


def compare_channels(reference: bytes, candidate: bytes) -> dict:
    result = compare_pass(reference, candidate)
    counts = [0, 0, 0, 0]
    for expected, actual in zip(PIXEL.iter_unpack(reference), PIXEL.iter_unpack(candidate)):
        if expected == SENTINEL or actual == SENTINEL or not all(map(math.isfinite, expected + actual)):
            continue
        for i, (a, b) in enumerate(zip(expected, actual)):
            if not math.isclose(a, b, rel_tol=1e-5, abs_tol=1e-4):
                counts[i] += 1
    return {**result, "rgba_outside_tolerance": counts}


def run(args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, timeout=110)


def analyze(project: Path, host: Path) -> dict:
    project = project.resolve()
    with tempfile.TemporaryDirectory(prefix="t1-fft-vulkan-isolation-") as temp:
        work = Path(temp)
        (work / "capture.cpp").write_text(capture_host(host.read_text()))
        run(["g++", "-std=c++17", "-O2", "capture.cpp", "-lvulkan", "-o", "capture"], work)
        modules = []
        for slot in (0, 1):
            candidate = project / "Assets/T1OriginalDerived" / f"FFT_Candidate_{slot:02d}.compute"
            pragma, sep, hlsl = candidate.read_bytes().partition(b"\n")
            if pragma != b"#pragma kernel main" or not sep or not hlsl:
                raise ValueError("Missing expected Unity-only pragma")
            (work / "candidate.hlsl").write_bytes(hlsl)
            compiled = f"slot{slot}-roundtrip.spv"
            run(["glslangValidator", "-V", "-D", "-S", "comp", "-e", "main",
                 "-o", compiled, "candidate.hlsl"], work)
            run(["spirv-val", "--target-env", "vulkan1.1", compiled], work)
            modules.extend([str(project / "_private_vulkan" / f"slot{slot}.spv"), compiled])
        run(["./capture", *modules, str(WIDTH), str(HEIGHT), "19", "1", "rgba32f"], work)
        images = {n: read_image(work / (n + ".rgba32f"), WIDTH * HEIGHT * 16) for n in FILES}
        return {"pass0": compare_channels(images["original0"], images["roundtrip0"]),
                "pass1": compare_channels(images["original1"], images["roundtrip1"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = analyze(args.project, Path("scripts/a1_fft_two_pass_vulkan.cpp"))
    except (ValueError, OSError, subprocess.SubprocessError):
        parser.exit(2, "Private same-Vulkan FFT isolation could not complete\n")
    print("RAFT_T1_VULKAN_ROUNDTRIP " + json.dumps(report, sort_keys=True))
    if not all(row["match"] for row in report.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
