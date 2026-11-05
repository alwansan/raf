"""Fail-closed synthetic IL return provenance; no game source or symbols."""
from collections import deque

UNKNOWN, NULL, CONSTRUCTED = "unknown", "null", "constructed"

def classify(instructions, *, max_states=10000, max_locals=4096, max_stack=256):
    if (not isinstance(instructions, (list, tuple)) or not instructions
            or any(type(limit) is not int or limit <= 0 for limit in (max_states, max_locals, max_stack))):
        return UNKNOWN
    n = len(instructions)
    incoming = {0: ((), ())}
    pending = deque([0])
    returns = {}
    steps = 0
    def join(a, b):
        sa, la = a
        sb, lb = b
        if len(sa) != len(sb):
            return ((UNKNOWN,), ())
        size = max(len(la), len(lb))
        la += (UNKNOWN,) * (size-len(la))
        lb += (UNKNOWN,) * (size-len(lb))
        merge = lambda x,y: x if x == y else UNKNOWN
        return (tuple(map(merge,sa,sb)), tuple(map(merge,la,lb)))
    while pending:
        steps += 1
        if steps > max_states:
            return UNKNOWN
        pc = pending.popleft()
        stack, locals_ = incoming[pc]
        record = instructions[pc]
        if not isinstance(record, (tuple, list)) or not record or type(record[0]) is not str or len(record) > 2:
            return UNKNOWN
        op, *args = record
        arg = args[0] if args else None
        if op == "ldnull":
            stack += (NULL,)
            successors = [pc+1]
        elif op == "newobj_rt":
            stack += (CONSTRUCTED,)
            successors = [pc+1]
        elif op == "ldloc" and type(arg) is int and 0 <= arg < max_locals:
            stack += (locals_[arg] if arg < len(locals_) else UNKNOWN,)
            successors = [pc+1]
        elif op == "stloc" and type(arg) is int and 0 <= arg < max_locals and stack:
            value, stack = stack[-1], stack[:-1]
            ls = list(locals_)
            ls.extend([UNKNOWN] * max(0,arg+1-len(ls)))
            ls[arg] = value
            locals_ = tuple(ls)
            successors = [pc+1]
        elif op == "br" and type(arg) is int:
            successors = [arg]
        elif op == "brtrue" and type(arg) is int and stack:
            stack = stack[:-1]
            successors = [arg,pc+1]
        elif op == "ldcond":
            stack += (UNKNOWN,)
            successors = [pc+1]
        elif op == "nop":
            successors = [pc+1]
        elif op == "ret":
            returns[pc] = stack[-1] if len(stack)==1 else UNKNOWN
            continue
        else:
            return UNKNOWN
        # Bound straight-line stack growth independently of worklist iteration limits.
        if len(stack) > max_stack:
            return UNKNOWN
        for target in successors:
            if not 0 <= target < n:
                return UNKNOWN
            candidate = (stack,locals_)
            if target in incoming:
                # Inconsistent evaluation-stack heights are invalid at a CIL join.
                # Do not let a later stloc/pop erase this structural violation.
                if len(incoming[target][0]) != len(candidate[0]):
                    return UNKNOWN
                merged = join(incoming[target],candidate)
                if merged != incoming[target]:
                    incoming[target] = merged
                    pending.append(target)
            else:
                incoming[target] = candidate
                pending.append(target)
    values = tuple(returns.values())
    return values[0] if values and all(v == values[0] for v in values) else UNKNOWN
