#!/usr/bin/env python3
"""Opt-in fail-closed publication boundary for aggregate-only Foam reports.

Does not establish integration with any legacy report producer.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
from t2_foam_evidence_gate_20261110 import MAX_BYTES, EvidenceError, parse_aggregate_json


def publish(source: Path, destination: Path):
    source, destination = Path(source).absolute(), Path(destination).absolute()
    if (source == destination or source.is_symlink() or not source.is_file()
            or destination.is_symlink() or not destination.parent.is_dir()):
        raise EvidenceError("unsafe output destination")
    with source.open("rb") as stream:
        safe = parse_aggregate_json(stream.read(MAX_BYTES + 1))
    encoded = (json.dumps(safe, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                                         prefix=".t2-aggregate-", suffix=".tmp",
                                         delete=False) as stream:
            temporary = stream.name
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        if destination.is_symlink():
            raise EvidenceError("unsafe output destination")
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        publish(args.input, args.output)
    except (OSError, ValueError, RecursionError) as exc:
        print("REJECTED: " + type(exc).__name__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
