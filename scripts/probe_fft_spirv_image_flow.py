"""Private SPIR-V SSA image operand -> numeric descriptor slot tracing.

Handles bounded direct loads, pointer access chains, image and copy aliases,
phi/select unions and SPIR-V core/sparse image consumers. Unresolved/dynamic resource references are explicitly
reported, never guessed. No shader identifiers, code or binaries leave CI.
"""
import struct

MAX_WORDS = 262144


def image_slot_dataflow(module):
    if type(module) is not bytes or not 20 <= len(module) <= 1048576 or len(module) % 4:
        raise ValueError("Invalid SPIR-V image-flow module")
    words = struct.unpack("<" + "I" * (len(module) // 4), module)
    if words[0] != 0x07230203 or not words[3] or words[4]:
        raise ValueError("Invalid SPIR-V image-flow header")
    bindings, sets, variables, aliases = {}, {}, set(), {}
    # Numeric descriptor consumers: SPIR-V core image ops, plus sparse variants.
    # Count all supported resource uses; an ignored sample must never
    # accidentally make the global uniqueness flag true.
    operations = {"write": [], "fetch": [], "read": [],
                  "sample": [], "gather": [], "query": [], "texel_pointer": []}

    def record_alias(result_id, parents):
        # A tracked SSA ID has exactly one definition. Overwriting its prior
        # parent silently invents a unique resource lineage for malformed data.
        # This is not a substitute for full spirv-val structural validation.
        if result_id in variables or result_id in aliases:
            raise ValueError("Repeated SPIR-V tracked result ID")
        aliases[result_id] = parents

    i = 5
    while i < len(words):
        count, op = words[i] >> 16, words[i] & 65535
        if not 1 <= count <= 1024 or i + count > len(words):
            raise ValueError("Invalid SPIR-V image-flow instruction")
        a = words[i + 1:i + count]
        if op == 71 and count == 4:
            target, deco, value = a
            if deco in (33, 34):
                record = bindings if deco == 33 else sets
                if target in record:
                    raise ValueError("Ambiguous SPIR-V descriptor decoration")
                record[target] = value
        if op == 59 and count in (4, 5):  # OpVariable
            if a[1] in variables or a[1] in aliases:
                raise ValueError("Repeated SPIR-V tracked result ID")
            variables.add(a[1])
        if op in (65, 66, 67, 70) and count >= 4:  # AccessChain pointer alias
            record_alias(a[1], (a[2],))
        if op == 60 and count >= 6:  # OpImageTexelPointer => image texel pointer
            record_alias(a[1], (a[2],))
            operations["texel_pointer"].append(a[2])
        if op == 61 and count >= 4:  # OpLoad result => pointer
            record_alias(a[1], (a[2],))
        if op in (83, 100) and count >= 4:  # CopyObject, OpImage
            record_alias(a[1], (a[2],))
        if op == 86 and count >= 5:  # OpSampledImage result => image
            record_alias(a[1], (a[2],))
        if op == 169 and count == 6:  # OpSelect result => two candidates
            record_alias(a[1], (a[3], a[4]))
        if op == 245 and count >= 5:  # OpPhi result => alternating value, parent
            record_alias(a[1], tuple(a[k] for k in range(2, len(a), 2)))
        # SPIR-V core Image* opcodes (Khronos unified grammar). The Image or
        # Sampled Image operand is word a[2], except OpImageWrite where it is a[0].
        # Sparse image ops 305-315 and 320 use the same operand position.
        bucket = None
        minimum = 0
        if op == 99:
            bucket, minimum = "write", 4
        elif op in (95, 313):
            bucket, minimum = "fetch", 5
        elif op in (98, 320):
            bucket, minimum = "read", 5
        elif 87 <= op <= 94 or 305 <= op <= 312:
            bucket, minimum = "sample", 5
        elif op in (96, 97, 314, 315):
            bucket, minimum = "gather", 6
        elif 101 <= op <= 107:
            bucket, minimum = "query", 4
        if bucket is not None:
            if count < minimum:
                raise ValueError("Truncated SPIR-V image operation")
            operations[bucket].append(a[0] if op == 99 else a[2])
        if op == 60 and count < 6:
            raise ValueError("Truncated SPIR-V image texel pointer")
        i += count
    slots = {v: (sets.get(v), bindings[v]) for v in variables if v in bindings}
    def find_slots(value, visited):
        if value in slots:
            return {slots[value]} if slots[value][0] is not None else {None}
        if value in visited:
            return {None}
        parent = aliases.get(value)
        if parent is None:
            return {None}
        found = set()
        for item in parent:
            found.update(find_slots(item, visited | {value}))
        return found
    reports = {}
    for operation, ids in operations.items():
        counts = {}
        unresolved = ambiguous = 0
        for ident in ids:
            parents = find_slots(ident, set())
            if None in parents:
                unresolved += 1
            elif len(parents) == 1:
                key = next(iter(parents))
                counts[key] = counts.get(key, 0) + 1
            elif not parents:
                unresolved += 1
            else:
                ambiguous += 1
        reports[operation] = {
            "total": len(ids),
            "resolved_slot_counts": [
                {"descriptor_set": k[0], "binding": k[1], "calls": n}
                for k, n in sorted(counts.items(),
                                   key=lambda entry: (entry[0][0] is None, entry[0][0] or 0,
                                                      entry[0][1]))],
            "unresolved_count": unresolved,
            "ambiguous_count": ambiguous,
        }
    return {
        "image_operand_slot_uses": reports,
        "all_image_operations_uniquely_traced": all(
            row["unresolved_count"] == 0 and row["ambiguous_count"] == 0
            for row in reports.values()),
        "source_semantic_equivalence_or_device_execution_proven": False,
        "private_shader_ids_or_names_disclosed": False,
    }
