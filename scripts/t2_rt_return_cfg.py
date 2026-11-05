"""Fail-closed synthetic IL return provenance; no game source or symbols."""
from collections import deque

UNKNOWN, NULL, CONSTRUCTED = "unknown", "null", "constructed"

def classify(instructions, *, max_states=10000):
    if not instructions:
        return UNKNOWN
    n = len(instructions)
    incoming = {0: ((), ())}
    pending = deque([0])
    returns = []
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
        op, *args = instructions[pc]
        arg = args[0] if args else None
        if op == "ldnull":
            stack += (NULL,)
            successors = [pc+1]
        elif op == "newobj_rt":
            stack += (CONSTRUCTED,)
            successors = [pc+1]
        elif op == "ldloc" and isinstance(arg,int) and arg >= 0:
            stack += (locals_[arg] if arg < len(locals_) else UNKNOWN,)
            successors = [pc+1]
        elif op == "stloc" and isinstance(arg,int) and arg >= 0 and stack:
            value, stack = stack[-1], stack[:-1]
            ls = list(locals_)
            ls.extend([UNKNOWN] * max(0,arg+1-len(ls)))
            ls[arg] = value
            locals_ = tuple(ls)
            successors = [pc+1]
        elif op == "br" and isinstance(arg,int):
            successors = [arg]
        elif op == "brtrue" and isinstance(arg,int) and stack:
            stack = stack[:-1]
            successors = [arg,pc+1]
        elif op == "ldcond":
            stack += (UNKNOWN,)
            successors = [pc+1]
        elif op == "nop":
            successors = [pc+1]
        elif op == "ret":
            returns.append(stack[-1] if len(stack)==1 else UNKNOWN)
            continue
        else:
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
    return returns[0] if returns and all(v == returns[0] for v in returns) else UNKNOWN
