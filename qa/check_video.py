"""Verify decoded video pixels, not just the existence of an MP4."""
import json
import pathlib
import subprocess
import tempfile
from PIL import Image

directory = pathlib.Path("evidence")
video = directory / "fixture.mp4"
metadata = json.loads(subprocess.check_output([
    "ffprobe", "-v", "error", "-select_streams", "v:0",
    "-show_streams", "-show_format", "-of", "json", str(video)
], text=True))
(directory / "video-metadata.json").write_text(json.dumps(metadata, indent=2))
streams = metadata["streams"]
if len(streams) != 1 or streams[0]["codec_type"] != "video":
    raise SystemExit("No valid video stream")
duration = float(metadata["format"]["duration"])
if not 4 <= duration <= 20:
    raise SystemExit(f"Unexpected capture duration: {duration}")

def label(rgb):
    r, g, b = rgb
    if r > 180 and g < 70 and b < 70:
        return "red"
    if g > 180 and r < 70 and b < 70:
        return "green"
    return "other"

results = []
before = False
after = False
with tempfile.TemporaryDirectory() as temp:
    subprocess.run([
        "ffmpeg", "-v", "error", "-nostdin", "-i", str(video),
        "-vf", "fps=2", "-frames:v", "40", str(pathlib.Path(temp) / "%04d.png")
    ], check=True)
    for path in sorted(pathlib.Path(temp).glob("*.png")):
        with Image.open(path) as raw:
            img = raw.convert("RGB")
            pixels = [img.getpixel((img.width * i // 4, img.height // 2)) for i in (1, 3)]
        colors = list(map(label, pixels))
        results.append({"sample": path.stem, "rgb": pixels, "colors": colors})
        if colors == ["green", "red"]:
            before = True
        if before and colors == ["red", "green"]:
            after = True
report = {"duration_seconds": duration, "codec": streams[0]["codec_name"],
          "samples": results, "ordered_color_change": after}
(directory / "video-check.json").write_text(json.dumps(report, indent=2))
if not after:
    raise SystemExit("Video lacks expected ordered green/red to red/green transition")
print(f"VIDEO_DECODED_PIXEL_PASS samples={len(results)} duration={duration:.2f}s")
