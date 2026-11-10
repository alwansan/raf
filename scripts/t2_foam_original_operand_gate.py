"""Fail-closed operand provenance gate for T2 Foam original-CIL diagnostics.

Input is a *single producer slice* from a separately validated CFG. This
module does not establish aliasing, a Unity texture instance, or shader parity.
"""
from __future__ import annotations

import re
from typing import Sequence

from t2_foam_rhs_origin_guard import classify_verified_rhs

_SHORT = re.compile(r"^(ldloc|ldarg)\.[0-3]$")
_OPERAND = {"ldloc", "ldarg", "ldloc.s", "ldarg.s"}


def classify_original_operand_rhs(
    opcodes: Sequence[str], *, complete_slice: bool = False,
    receiver_verified: bool = False, call_returns_value: bool = False,
    operand_verified: bool = False,
) -> str:
    """Require resolved Mono.Cecil operands for non-short local/arg loads.

    Bare ldloc/ldarg and their .s forms have an operand outside OpCode.Name.
    A caller must verify the actual VariableDefinition/ParameterDefinition
    before claiming a producer category. Short .0..3 forms are self-contained.
    This gate deliberately refuses mixed/unsupported slices.
    """
    flags = (complete_slice, receiver_verified, call_returns_value,
             operand_verified)
    if any(type(flag) is not bool for flag in flags):
        return "UNKNOWN"
    if not isinstance(opcodes, (tuple, list)) or not opcodes:
        return "UNKNOWN"
    if any(not isinstance(op, str) for op in opcodes):
        return "UNKNOWN"
    ops = [op.strip().lower() for op in opcodes]
    loads = [op for op in ops if op in _OPERAND or _SHORT.fullmatch(op)]
    if len(loads) > 1:
        return "UNKNOWN"
    if any(op in _OPERAND for op in loads):
        if not operand_verified:
            return "UNKNOWN"
        # The legacy helper only understands normalized ldloc/ldarg.
        # The resolved operand is checked by the caller, not represented here.
        ops = [op.split(".")[0] if op in _OPERAND else op for op in ops]
    return classify_verified_rhs(
        ops, complete_slice=complete_slice,
        receiver_verified=receiver_verified,
        call_returns_value=call_returns_value,
    )
