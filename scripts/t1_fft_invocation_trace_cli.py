"""Fail-closed invocation-keyed FFT trace comparison (not legacy coordinate histogram).

Only aggregate counts are printed. Input buffers remain private; this tool does
not establish that the captures used identical shaders, resources or dispatch.
"""
import argparse
import json
from pathlib import Path
import sys

from scripts.t1_fft_trace_compare import INVOCATION_SIZE, compare_invocations


def read_capture(path: Path) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(INVOCATION_SIZE + 1)
    if len(data) != INVOCATION_SIZE:
        raise ValueError("Incorrect invocation capture length")
    return data


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("observed", type=Path)
    args = parser.parse_args(argv)
    try:
        result = compare_invocations(read_capture(args.reference),
                                     read_capture(args.observed))
    except (OSError, ValueError, OverflowError):
        print("RAFT_T1_FFT_INVOCATION_TRACE invalid_capture", file=sys.stderr)
        return 2
    print("RAFT_T1_FFT_INVOCATION_TRACE " + json.dumps(result, sort_keys=True))
    return 0 if result["match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
