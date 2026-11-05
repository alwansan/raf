"""Compare bounded pass-zero traces, publishing only per-site counts."""
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

CAPACITY = 512
RECORD = struct.Struct("<Iiii4I")
SIZE = 4 + CAPACITY * RECORD.size


def decode(data):
    if len(data) != SIZE:
        raise ValueError("Incorrect private trace size")
    (count,) = struct.unpack_from("<I", data)
    if not 0 < count <= CAPACITY:
        raise ValueError("Empty or overflowed private trace")
    sites = [{}, {}, {}]
    for site, x, y, mip, *bits in RECORD.iter_unpack(data[4:4 + count * RECORD.size]):
        if site >= len(sites):
            raise ValueError("Invalid private trace site")
        coordinates = sites[site]
        coordinates.setdefault((x, y, mip), Counter())[tuple(bits)] += 1
    if not all(sites):
        raise ValueError("Missing private trace site")
    return sites


def compare(reference, observed):
    reports = []
    for left, right in zip(decode(reference), decode(observed)):
        missing = extra = differing = comparable = 0
        for coordinate in left.keys() | right.keys():
            a, b = left.get(coordinate, Counter()), right.get(coordinate, Counter())
            na, nb = sum(a.values()), sum(b.values())
            missing += max(na - nb, 0)
            extra += max(nb - na, 0)
            # At unequal multiplicity, report coordinate drift without claiming
            # which fetched value differs from which invocation.
            if na == nb:
                comparable += na
                differing += sum((a - b).values())
        reports.append({"missing_coordinate_records": missing, "extra_coordinate_records": extra,
                        "value_records_compared": comparable, "value_bit_mismatches": differing})
    return {"sites": reports, "match": all(
        not any(row[key] for key in ("missing_coordinate_records", "extra_coordinate_records",
                                     "value_bit_mismatches")) for row in reports)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("observed", type=Path)
    args = parser.parse_args()
    try:
        buffers = []
        for path in (args.reference, args.observed):
            with path.open("rb") as stream:
                buffers.append(stream.read(SIZE + 1))
        result = compare(*buffers)
    except (OSError, ValueError):
        parser.exit(2, "Invalid private paired trace\n")
    print("RAFT_T1_FFT_TRACE_COMPARE " + json.dumps(result, sort_keys=True))
    if not result["match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
