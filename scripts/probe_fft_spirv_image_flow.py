"""Private SPIR-V SSA image operand -> numeric descriptor slot tracing.

Handles bounded direct loads, pointer access chains, image and copy aliases,
phi/select unions. Unresolved/dynamic resource references are explicitly
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
    operations = {"write": [], "fetch": [], "read": []}
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
            if a[1] in variables:
                raise ValueError("Repeated SPIR-V variable ID")
            variables.add(a[1])
        if op in (65, 66, 67, 68) and count >= 4:  # AccessChain pointer alias
            aliases[a[1]] = (a[2],)
        if op == 61 and count >= 4:  # OpLoad result => pointer
            aliases[a[1]] = (a[2],)
        if op in (83, 100) and count >= 4:  # CopyObject, OpImage
            aliases[a[1]] = (a[2],)
        if op == 86 and count >= 5:  # OpSampledImage result => image
            aliases[a[1]] = (a[2],)
        if op == 169 and count >= 6:  # OpSelect result => two candidates
            aliases[a[1]] = (a[4], a[5]) if len(a) >= 6 else (a[3], a[4])
        if op == 245 and count >= 5:  # OpPhi result => alternating value, parent
            aliases[a[1]] = tuple(a[k] for k in range(2, len(a), 2))
        if op == 99 and count >= 4:  # OpImageWrite
            operations["write"].append(a[0])
        if op == 95 and count >= 5:  # OpImageFetch
            operations["fetch"].append(a[2])
        if op == 98 and count >= 5:  # OpImageRead
            operations["read"].append(a[2])
        i += count
    slots = {v: (sets.get(v), bindings[v]) for v in variables if v in bindings}
    def find_slots(value, visited):
        if value in slots:
            return {slots[value]}
        if value in visited:
            return set()
        parent = aliases.get(value)
        if parent is None:
            return set()
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
            if len(parents) == 1:
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
