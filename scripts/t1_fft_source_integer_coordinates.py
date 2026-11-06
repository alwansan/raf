"""Rewrite one private FFT source fetch to use proven integer lanes."""
import argparse
from pathlib import Path

from scripts.t1_fft_spirv_read_provenance import ROOT_EDGES, lane_input, lane_count, numeric_kind


def integer_origin(value, lane, values, types):
    for _ in range(13):
        op, type_id, args = values[value]
        if op == "OpBitcast":
            if numeric_kind(type_id, types) != "float32" or len(args) != 1:
                raise ValueError("Unexpected intermediate bitcast")
            source = args[0]
            if (numeric_kind(values[source][1], types) != "sint32"
                    or lane_count(source, values, types) != lane_count(value, values, types)):
                raise ValueError("Expected equal-width signed integer carrier")
            return source, lane
        width = lane_count(value, values, types)
        if not 0 <= lane < width:
            break
        next_value = lane_input(op, args, lane, width, values, types)
        if next_value is None:
            break
        value, lane = next_value
    raise ValueError("Unresolved private coordinate lane")


def rewrite(assembly):
    types, values, decorations, fetches = {}, {}, {}, []
    lines = assembly.splitlines(keepends=True)
    for index, line in enumerate(lines):
        parts = line.split(";", 1)[0].split()
        if len(parts) == 4 and parts[0] == "OpDecorate" and parts[2] in ("DescriptorSet", "Binding"):
            decorations[parts[1], parts[2]] = parts[3]
        if len(parts) < 3 or parts[1] != "=":
            continue
        result, _, op, *args = parts
        if op.startswith("OpType"):
            types[result] = (op, args)
        elif args:
            values[result] = (op, args[0], args[1:])
        if op == "OpImageFetch" and len(args) >= 3:
            fetches.append((index, parts, args[1], args[2]))

    def source_fetch(image):
        seen = set()
        while image in values and values[image][0] in ROOT_EDGES:
            if image in seen:
                raise ValueError("Cyclic image provenance")
            seen.add(image)
            image = values[image][2][0]
        return (decorations.get((image, "DescriptorSet")),
                decorations.get((image, "Binding"))) == ("0", "0")

    candidates = [row for row in fetches if source_fetch(row[2])]
    if len(candidates) != 1 or "%t1_integer_" in assembly:
        raise ValueError("Expected one unmodified source fetch")
    index, parts, _, coordinate = candidates[0]
    op, coord_type, args = values[coordinate]
    if (op != "OpBitcast" or numeric_kind(coord_type, types) != "sint32"
            or lane_count(coordinate, values, types) != 2 or len(args) != 1
            or numeric_kind(values[args[0]][1], types) != "float32"
            or lane_count(args[0], values, types) != 2):
        raise ValueError("Expected signed int2 fetch coordinate bitcast")
    scalar_type = types[coord_type][1][0]
    inserts, components = [], []
    for axis, lane in enumerate((0, 1)):
        origin, component = integer_origin(args[0], lane, values, types)
        origin_type = values[origin][1]
        if origin_type == scalar_type:
            components.append(origin)
            continue
        if types[origin_type][0] != "OpTypeVector" or types[origin_type][1][0] != scalar_type:
            raise ValueError("Coordinate lane scalar type mismatch")
        name = f"%t1_integer_lane_{axis}"
        inserts.append(f"{name} = OpCompositeExtract {scalar_type} {origin} {component}\n")
        components.append(name)
    inserts.append(f"%t1_integer_coord = OpCompositeConstruct {coord_type} {' '.join(components)}\n")
    parts[5] = "%t1_integer_coord"
    lines[index:index + 1] = [*inserts, " ".join(parts) + "\n"]
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if not 0 < args.input.stat().st_size <= 2 * 1024 * 1024:
            raise ValueError("Private assembly outside size limit")
        result = rewrite(args.input.read_text(encoding="utf-8"))
        with args.output.open("x", encoding="utf-8") as output:
            output.write(result)
    except (OSError, ValueError, KeyError, IndexError):
        parser.exit(2, "Private source-coordinate rewrite could not be proven\n")
    print("RAFT_T1_SOURCE_INTEGER_COORDINATES source_fetch_rewritten=1")


if __name__ == "__main__":
    main()
