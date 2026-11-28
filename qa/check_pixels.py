import json
import pathlib
from PIL import Image

directory = pathlib.Path("evidence")
results = {}
for name, order in [("baseline", ("red", "green")), ("tapped", ("green", "red"))]:
    with Image.open(directory / f"{name}.png") as raw:
        img = raw.convert("RGB")
        points = [img.getpixel((img.width * i // 4, img.height // 2)) for i in (1, 3)]
    def color(rgb):
        r, g, b = rgb
        return "red" if r > 200 and g < 45 and b < 45 else "green" if g > 200 and r < 45 and b < 45 else "other"
    results[name] = {"rgb": points, "expected": order, "observed": list(map(color, points))}
    with (directory / "pixel-check.json").open("w") as fp:
        json.dump(results, fp, indent=2)
    if tuple(results[name]["observed"]) != order:
        raise SystemExit(f"Unexpected shader framebuffer: {name}, {points}")
