"""Validate the *shape* of Unity FFT carrier diagnostics, not GPU authenticity."""
import argparse
import json
from pathlib import Path

EXPECTED = 10
MAX_BYTES = 512
THREADS = 64
POSITIVE_CONTROLS = (0, 3, 4)


def parse_report(data: bytes) -> dict:
    if len(data) > MAX_BYTES or not data:
        raise ValueError("invalid report length")
    try:
        text = data.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("report must be ASCII") from exc
    if "\r" in text or not text.endswith("\n"):
        raise ValueError("report requires LF-terminated lines")
    lines = text.splitlines()
    if len(lines) != EXPECTED:
        raise ValueError("expected exactly ten counters")
    if any(not line or not line.isascii() or not line.isdecimal() or
           (len(line) > 1 and line.startswith("0")) for line in lines):
        raise ValueError("noncanonical decimal counter")
    values = [int(line) for line in lines]
    if any(value > THREADS for value in values):
        raise ValueError("counter exceeds dispatch thread count")
    return {
        "shape_valid": True,
        "positive_controls_pass": all(values[i] == 0 for i in POSITIVE_CONTROLS),
        "noncontrol_mismatch_categories": sum(values[i] != 0 for i in range(EXPECTED)
                                              if i not in POSITIVE_CONTROLS),
        "counters": values,
        "gpu_execution_verified": False,
        "original_kernel_identity_verified": False,
        "android_water_verified": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        if args.report.is_symlink() or not args.report.is_file():
            raise ValueError("report must be a regular non-symlink file")
        if args.report.stat().st_size > MAX_BYTES:
            raise ValueError("report too large")
        result = parse_report(args.report.read_bytes())
    except (OSError, ValueError) as exc:
        print(json.dumps({"shape_valid": False, "error": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["positive_controls_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
