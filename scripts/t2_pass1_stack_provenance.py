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
    if type(max_steps) is not int or max_steps < 1 or not isinstance(instructions, (list, tuple)) or len(instructions) > max_steps:
        raise Unresolved("invalid or oversized block")
    stack, locals_, arg_types = [], {}, {}
    for index, instruction in enumerate(instructions):
        if not isinstance(instruction, (tuple, list)) or len(instruction) != 2:
            raise Unresolved("malformed instruction")
        op, arg = instruction
        if type(op) is not str:
            raise Unresolved("non-string opcode")
        if op == "ldarg":
            if not isinstance(arg, (tuple, list)) or len(arg) != 2 or type(arg[0]) is not int or not 0 <= arg[0] <= 65535 or type(arg[1]) is not str or arg[1] not in ("Texture", "RenderTexture"):
                raise Unresolved("untyped argument")
            previous_type = arg_types.get(arg[0])
            if previous_type is not None and previous_type != arg[1]:
                raise Unresolved("conflicting argument type")
            arg_types[arg[0]] = arg[1]
            stack.append(Value(arg[1], "arg:" + str(arg[0])))
        elif op == "ldnull":
            if arg is not None: raise Unresolved("invalid null operand")
            stack.append(Value("NULL", "null"))
        elif op == "dup":
            if arg is not None or not stack: raise Unresolved("invalid dup")
            stack.append(stack[-1])
        elif op == "stloc":
            if not stack or type(arg) is not int or not 0 <= arg <= 65535: raise Unresolved("invalid local store")
            locals_[arg] = stack.pop()
        elif op == "ldloc":
            if type(arg) is not int or not 0 <= arg <= 65535 or arg not in locals_: raise Unresolved("uninitialized local")
            stack.append(locals_[arg])
        elif op == "pop":
            if arg is not None or not stack: raise Unresolved("stack underflow")
            stack.pop()
        else:
            # Includes branch targets, call/callvirt, ldfld, castclass, phi/merges.
            raise Unresolved("unsupported instruction: " + str(op))
        if len(stack) > 64: raise Unresolved("stack budget")
    return tuple(stack)
