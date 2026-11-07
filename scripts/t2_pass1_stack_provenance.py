"""Fail-closed synthetic IL stack provenance model; NOT a Mono.Cecil/original-game parser.

Input is a bounded straight-line sequence of (opcode, operand) pairs.
Only explicit typed argument/local producers are supported. Any unknown operation,
control flow, or aliasing rejects the entire trace rather than guessing.
"""
from dataclasses import dataclass

class Unresolved(ValueError):
    pass

@dataclass(frozen=True)
class Value:
    kind: str
    origin: str

def trace(instructions, max_steps=128):
    if not isinstance(instructions, (list, tuple)) or len(instructions) > max_steps:
        raise Unresolved("invalid or oversized block")
    stack, locals_ = [], {}
    for index, instruction in enumerate(instructions):
        if not isinstance(instruction, (tuple, list)) or len(instruction) != 2:
            raise Unresolved("malformed instruction")
        op, arg = instruction
        if op == "ldarg":
            if not isinstance(arg, (tuple, list)) or len(arg) != 2 or arg[1] not in ("Texture", "RenderTexture"):
                raise Unresolved("untyped argument")
            stack.append(Value(arg[1], "arg:" + str(arg[0])))
        elif op == "ldnull":
            stack.append(Value("NULL", "null"))
        elif op == "dup":
            if not stack: raise Unresolved("stack underflow")
            stack.append(stack[-1])
        elif op == "stloc":
            if not stack or not isinstance(arg, int) or arg < 0: raise Unresolved("invalid local store")
            locals_[arg] = stack.pop()
        elif op == "ldloc":
            if arg not in locals_: raise Unresolved("uninitialized local")
            stack.append(locals_[arg])
        elif op == "pop":
            if not stack: raise Unresolved("stack underflow")
            stack.pop()
        else:
            # Includes branch targets, call/callvirt, ldfld, castclass, phi/merges.
            raise Unresolved("unsupported instruction: " + str(op))
        if len(stack) > 64: raise Unresolved("stack budget")
    return tuple(stack)
