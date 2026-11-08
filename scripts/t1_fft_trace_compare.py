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


# Site, dispatch ID (xyz), per-site occurrence, Load coordinate (xyz), value bits.
INVOCATION_RECORD = struct.Struct("<5I3i4I")
INVOCATION_SIZE = 4 + CAPACITY * INVOCATION_RECORD.size


def decode_invocations(data):
    if len(data) != INVOCATION_SIZE:
        raise ValueError("Incorrect invocation trace size")
    (count,) = struct.unpack_from("<I", data)
    if not 0 < count <= CAPACITY:
        raise ValueError("Empty or overflowed invocation trace")
    sites = [{}, {}, {}]
    end = 4 + count * INVOCATION_RECORD.size
    for site, x, y, z, occurrence, *sample in INVOCATION_RECORD.iter_unpack(data[4:end]):
        key = (x, y, z, occurrence)
        if site >= len(sites) or key in sites[site]:
            raise ValueError("Invalid or duplicate invocation trace key")
        sites[site][key] = (tuple(sample[:3]), tuple(sample[3:]))
    if not all(sites):
        raise ValueError("Missing invocation trace site")
    return sites


def axis_mapping(pairs):
    """Classify address mappings without exposing coordinates or offsets."""
    varied_reference = len({before for before, _ in pairs}) >= 2
    # An identity mapping is not evidence of a shifted or reflected address.
    changed = any(before != after for before, after in pairs)
    return {
        "varied_reference": varied_reference,
        "constant_observed": varied_reference and len({after for _, after in pairs}) == 1,
        "uniform_translation": varied_reference and changed and len({after - before for before, after in pairs}) == 1,
        "uniform_reflection": varied_reference and changed and len({after + before for before, after in pairs}) == 1,
    }


def compare_invocations(reference, observed):
    """Compare corresponding reads without exposing invocation IDs or samples."""
    reports = []
    for left, right in zip(decode_invocations(reference), decode_invocations(observed)):
        shared = left.keys() & right.keys()
        coordinate_mismatches = same_coordinate_value_mismatches = changed_coordinate_value_mismatches = 0
        axis_mismatches = [0, 0, 0]
        axis_pairs = [[], [], []]
        for key in shared:
            left_coord, left_value = left[key]
            right_coord, right_value = right[key]
            for axis, pair in enumerate(zip(left_coord, right_coord)):
                axis_pairs[axis].append(pair)
            if left_coord == right_coord:
                same_coordinate_value_mismatches += left_value != right_value
            else:
                coordinate_mismatches += 1
                for axis, (before, after) in enumerate(zip(left_coord, right_coord)):
                    axis_mismatches[axis] += before != after
                changed_coordinate_value_mismatches += left_value != right_value
        reports.append({
            "missing_reads": len(left.keys() - right.keys()),
            "extra_reads": len(right.keys() - left.keys()),
            "paired_reads": len(shared),
            "coordinate_mismatches": coordinate_mismatches,
            "coordinate_axis_mismatches": dict(zip(("x", "y", "mip"), axis_mismatches)),
            "coordinate_axis_mapping": {axis: axis_mapping(pairs)
                                        for axis, pairs in zip(("x", "y", "mip"), axis_pairs)},
            "same_coordinate_value_mismatches": same_coordinate_value_mismatches,
            "changed_coordinate_value_mismatches": changed_coordinate_value_mismatches,
        })
    return {"sites": reports, "match": all(
        not any(row[key] for key in ("missing_reads", "extra_reads", "coordinate_mismatches",
                                     "same_coordinate_value_mismatches")) for row in reports)}


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
