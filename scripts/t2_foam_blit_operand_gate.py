"""Source-FREE, fail-closed model for exactly two typed Graphics.Blit calls.

This validates bounded NORMALIZED, straight-line IL fixtures, **not** arbitrary
Mono.Cecil bytecode or original Raft method bodies. A caller supplying a typed
method descriptor is not evidence the descriptor came from an authentic DLL.
Use a separately authenticated, private original-IL extractor before attaching
any original-source provenance claim. No proprietary operands are emitted.
"""
from dataclasses import dataclass


class Unresolved(ValueError):
    """Ambiguous or unsupported IL: no guessed source/destination roles."""


@dataclass(frozen=True)
class Value:
    kind: str
    origin: str
    literal: int | None = None


MAX_STEPS = 128
MAX_STACK = 32
MAX_INDEX = 65535
# Exact four-parameter, static Graphics.Blit overload. Constructor/alias calls
# and other overloads are intentionally NOT accepted by this source-only gate.
BLIT_SIGNATURE = (
    "UnityEngine.Graphics",
    "Blit",
    ("UnityEngine.Texture", "UnityEngine.RenderTexture", "UnityEngine.Material", "System.Int32"),
    True,
)
ARG_TYPES = {"Texture", "RenderTexture", "Material"}


def _index(value):
    return type(value) is int and 0 <= value <= MAX_INDEX


def _origin(value):
    return value.origin.split(":", 1)[0]


def classify_two_pass_blits(instructions):
    """Return sanitized source/destination *type* roles only for pass 0 and 1.

    Normalized instructions are exactly (opcode, operand) pairs. Accepted:
    ldarg=(index, type), ldloc/stloc=index, ldnull=None, ldc.i4=signed int,
    dup/pop/nop=None, call=the exact BLIT_SIGNATURE tuple.
    Reject all field access, instance calls, branching/exception flow, casts,
    unknown aliases, source/destination type uncertainty and stack underflow.
    """
    if type(instructions) not in (list, tuple) or len(instructions) > MAX_STEPS:
        raise Unresolved("invalid or oversized IL sequence")
    stack, locals_, arg_types, sites = [], {}, {}, {}
    for instruction in instructions:
        if type(instruction) not in (list, tuple) or len(instruction) != 2:
            raise Unresolved("malformed normalized instruction")
        op, operand = instruction
        if type(op) is not str:
            raise Unresolved("invalid opcode")
        if op == "ldarg":
            if (type(operand) not in (list, tuple) or len(operand) != 2
                    or not _index(operand[0]) or type(operand[1]) is not str
                    or operand[1] not in ARG_TYPES):
                raise Unresolved("untyped source argument")
            idx, kind = operand
            if idx in arg_types and arg_types[idx] != kind:
                raise Unresolved("conflicting argument types")
            arg_types[idx] = kind
            stack.append(Value(kind, "arg:" + str(idx)))
        elif op == "ldnull":
            if operand is not None:
                raise Unresolved("invalid null")
            stack.append(Value("NULL", "null"))
        elif op == "ldc.i4":
            if type(operand) is not int or not -(2**31) <= operand < 2**31:
                raise Unresolved("invalid i4 literal")
            stack.append(Value("Int32", "literal", operand))
        elif op == "stloc":
            if not _index(operand) or not stack:
                raise Unresolved("invalid local store")
            locals_[operand] = stack.pop()
        elif op == "ldloc":
            if not _index(operand) or operand not in locals_:
                raise Unresolved("uninitialized local")
            stack.append(locals_[operand])
        elif op == "dup":
            if operand is not None or not stack:
                raise Unresolved("invalid dup")
            stack.append(stack[-1])
        elif op == "pop":
            if operand is not None or not stack:
                raise Unresolved("invalid pop")
            stack.pop()
        elif op == "nop":
            if operand is not None:
                raise Unresolved("invalid nop")
        elif op == "call":
            if (type(operand) is not tuple or len(operand) != 4
                    or type(operand[0]) is not str or type(operand[1]) is not str
                    or type(operand[2]) is not tuple or type(operand[3]) is not bool
                    or operand != BLIT_SIGNATURE):
                raise Unresolved("non-exact typed static Graphics.Blit overload")
            if len(stack) < 4:
                raise Unresolved("Blit argument stack underflow")
            source, destination, material, pass_value = stack[-4:]
            del stack[-4:]
            if (source.kind not in ("Texture", "RenderTexture")
                    or destination.kind not in ("RenderTexture", "NULL")
                    or material.kind != "Material"
                    or pass_value.kind != "Int32" or pass_value.literal not in (0, 1)):
                raise Unresolved("unproved Blit source/destination/material/pass")
            p = pass_value.literal
            if p in sites:
                raise Unresolved("duplicate explicit Foam pass")
            sites[p] = {"pass": p,
                        "source": source.kind,
                        "destination": "null" if destination.kind == "NULL" else destination.kind,
                        "source_producer": _origin(source),
                        "destination_producer": _origin(destination)}
        else:
            raise Unresolved("unsupported or control-flow IL operation")
        if len(stack) > MAX_STACK:
            raise Unresolved("IL stack budget exceeded")
    if set(sites) != {0, 1} or stack:
        raise Unresolved("require exactly two pass literals and empty final stack")
    return {
        "sites": [sites[0], sites[1]],
        "normalized_fixture_only": True,
        "original_assembly_authenticated": False,
        "original_texture_instance_identity_proven": False,
        "Unity_or_Android_pixels_verified": False,
    }
