"""Bounded SPIR-V direct producer-edge census for original FFT investigations.

Only public opcodes 124/128/132/245 and direct SSA value operands are
considered. Edges to any other producer are deliberately unclassified.
This does not verify full def-use, arithmetic semantics or device execution.
All shader IDs and operand values stay private and are never emitted.
"""
import struct

MAX_BYTES = 1048576
TARGETS = (124, 128, 132, 245)  # bitcast, integer add/mul, phi


def direct_producer_edges(module):
    if type(module) is not bytes or not 20 <= len(module) <= MAX_BYTES or len(module) % 4:
        raise ValueError("Invalid SPIR-V operand-edge module")
    words = struct.unpack("<" + "I" * (len(module) // 4), module)
    bound = words[3]
    if words[0] != 0x07230203 or not bound or words[4] != 0:
        raise ValueError("Invalid SPIR-V operand-edge header")
    definitions = {}
    consumers = []
    counts = {op: 0 for op in TARGETS}
    i = 5
    while i < len(words):
        n, opcode = words[i] >> 16, words[i] & 65535
        if not 1 <= n <= 1024 or i + n > len(words):
            raise ValueError("Invalid SPIR-V operand-edge instruction")
        if opcode in TARGETS:
            if ((opcode == 124 and n != 4) or
                    (opcode in (128, 132) and n != 5) or
                    (opcode == 245 and (n < 5 or (n - 3) % 2))):
                raise ValueError("Malformed tracked SPIR-V operand instruction")
            a = words[i + 1:i + n]
            result_id = a[1]
            # OpPhi's alternating parent-block IDs are labels, not value inputs.
            inputs = (a[2],) if opcode == 124 else (
                (a[2], a[3]) if opcode in (128, 132)
                else tuple(a[k] for k in range(2, len(a), 2)))
            if (not 0 < result_id < bound or result_id in definitions or
                    not 0 < a[0] < bound or
                    any(not 0 < item < bound for item in inputs)):
                raise ValueError("Invalid or duplicate tracked SPIR-V result/value ID")
            definitions[result_id] = opcode
            consumers.append((opcode, inputs))
            counts[opcode] += 1
        i += n
    edges = {}
    untracked = 0
    operand_uses = 0
    for consumer, operands in consumers:
        for value in operands:
            operand_uses += 1
            producer = definitions.get(value)
            if producer is None:
                # This is NOT proof the operand is a constant or external.
                untracked += 1
                continue
            edge = (producer, consumer)
            edges[edge] = edges.get(edge, 0) + 1
    return {
        "tracked_opcode_counts": {str(k): counts[k] for k in TARGETS},
        "direct_tracked_producer_edges": [
            {"producer_opcode": p, "consumer_opcode": c, "uses": edges[(p, c)]}
            for p, c in sorted(edges)
        ],
        "tracked_operand_uses": operand_uses,
        "operand_uses_from_untracked_producers": untracked,
        "direct_tracked_edge_total": operand_uses - untracked,
        "all_dependencies_classified": untracked == 0,
        "bounded_subset_only": True,
        "private_shader_ids_or_values_disclosed": False,
        "numeric_or_device_equivalence_proven": False,
    }


def compare_direct_producer_edges(original, roundtrip):
    for profile in (original, roundtrip):
        if type(profile) is not dict:
            raise ValueError("Invalid SPIR-V producer-edge profile")
        counts = profile.get("tracked_opcode_counts")
        edges = profile.get("direct_tracked_producer_edges")
        if (type(counts) is not dict or set(counts) != {str(k) for k in TARGETS}
                or any(type(v) is not int or v < 0 for v in counts.values())
                or type(edges) is not list or len(edges) > len(TARGETS) ** 2):
            raise ValueError("Invalid SPIR-V producer-edge counters")
        seen = set()
        uses = 0
        for row in edges:
            if (type(row) is not dict or set(row) !=
                    {"producer_opcode", "consumer_opcode", "uses"} or
                    type(row["producer_opcode"]) is not int or
                    type(row["consumer_opcode"]) is not int or
                    row["producer_opcode"] not in TARGETS or
                    row["consumer_opcode"] not in TARGETS or
                    type(row["uses"]) is not int or row["uses"] <= 0):
                raise ValueError("Invalid SPIR-V producer-edge record")
            key = (row["producer_opcode"], row["consumer_opcode"])
            if key in seen:
                raise ValueError("Duplicate SPIR-V producer-edge record")
            seen.add(key)
            uses += row["uses"]
        other = profile.get("operand_uses_from_untracked_producers")
        total = profile.get("tracked_operand_uses")
        if (type(other) is not int or type(total) is not int or other < 0 or
                total < 0 or uses + other != total):
            raise ValueError("Inconsistent SPIR-V operand-use census")
    left = {(r["producer_opcode"], r["consumer_opcode"]): r["uses"]
            for r in original["direct_tracked_producer_edges"]}
    right = {(r["producer_opcode"], r["consumer_opcode"]): r["uses"]
             for r in roundtrip["direct_tracked_producer_edges"]}
    changes = [
        {"producer_opcode": p, "consumer_opcode": c,
         "original": left.get((p, c), 0), "roundtrip": right.get((p, c), 0)}
        for p, c in sorted(set(left) | set(right))
        if left.get((p, c), 0) != right.get((p, c), 0)
    ]
    same_counts = original["tracked_opcode_counts"] == roundtrip["tracked_opcode_counts"]
    same_edges = not changes
    return {
        "same_tracked_opcode_counts": same_counts,
        "same_direct_tracked_producer_edges": same_edges,
        "direct_tracked_edge_differences": changes,
        "original_untracked_operand_uses": original["operand_uses_from_untracked_producers"],
        "roundtrip_untracked_operand_uses": roundtrip["operand_uses_from_untracked_producers"],
        "all_dependencies_compared": False,
        "identical_operands_or_semantic_equivalence_proven": False,
        "device_gpu_execution_proven": False,
    }
