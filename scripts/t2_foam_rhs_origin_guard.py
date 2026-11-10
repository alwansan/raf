"""Source-free conservative CIL RHS origin classifier for T2 Foam diagnostics.

This helper never infers Unity runtime texture identity. The input is a
pre-normalized *single straight-line producer slice*, not arbitrary CIL.
Any control flow, unknown opcode or multiple producers is UNKNOWN.
"""
from __future__ import annotations

from typing import Sequence

_ALLOWED = {"nop", "castclass"}
_ORIGINS = {"ldnull": "NULL", "newobj": "CONSTRUCTOR", "ldfld": "FIELD_READ",
            "ldsfld": "STATIC_FIELD_READ", "call": "CALL_RESULT",
            "callvirt": "CALL_RESULT", "ldloc": "LOCAL_READ",
            "ldarg": "ARGUMENT_READ"}
_BRANCH_PREFIXES = ("br", "beq", "bne", "bge", "bgt", "ble", "blt", "leave")


def classify_rhs(opcodes: Sequence[str], *, call_returns_value: bool = False) -> str:
    """Return an origin *category*, not a proven object identity.

    A caller must separately prove the slice is exact, complete and
    single-producer; otherwise it must not use the result as evidence.
    call/callvirt are UNKNOWN unless the resolved original method signature
    explicitly proves a non-void return (call_returns_value=True).
    """
    if not isinstance(opcodes, (list, tuple)) or not opcodes:
        return "UNKNOWN"
    if any(not isinstance(op, str) for op in opcodes):
        return "UNKNOWN"
    ops = [op.lower().strip() for op in opcodes]
    if any(op.startswith(_BRANCH_PREFIXES) or op in
           {"switch", "ret", "throw", "stfld", "stsfld", "stloc", "pop"}
           for op in ops):
        return "UNKNOWN"
    if not isinstance(call_returns_value, bool):
        return "UNKNOWN"
    if any(op in {"call", "callvirt"} for op in ops) and not call_returns_value:
        return "UNKNOWN"
    producers = [op for op in ops if op in _ORIGINS]
    if len(producers) != 1 or any(op not in _ORIGINS and op not in _ALLOWED
                                  for op in ops):
        return "UNKNOWN"
    # castclass consumes a value: it cannot precede the only producer.
    # dup is deliberately unsupported without explicit stack simulation.
    producer_index = ops.index(producers[0])
    if any(op == "castclass" for op in ops[:producer_index]):
        return "UNKNOWN"
    return _ORIGINS[producers[0]]
