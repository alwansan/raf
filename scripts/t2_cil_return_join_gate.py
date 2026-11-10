"""Fail-closed synthetic CIL return-join provenance gate.

Not a Mono.Cecil interpreter. Callers must prove path coverage and receiver identity.
"""
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True)
class Origin:
    kind: str
    token: str

def classify_path(instructions: Sequence[tuple[str, str]]) -> Origin | None:
    stack: list[Origin] = []
    returned = False
    for index, (op, arg) in enumerate(instructions):
        if returned:
            return None
        if op == 'ldarg.receiver' and arg:
            stack.append(Origin('receiver', arg))
        elif op == 'ldfld' and arg and stack:
            receiver = stack.pop()
            if receiver.kind != 'receiver':
                return None
            stack.append(Origin('field', receiver.token + '/' + arg))
        elif op == 'newobj' and arg:
            stack.append(Origin('allocation', arg + '@' + str(index)))
        elif op == 'ldnull' and not arg:
            stack.append(Origin('null', ''))
        elif op == 'castclass' and arg and stack:
            if stack[-1].kind == 'receiver':
                return None
        elif op == 'ret' and not arg and len(stack) == 1:
            returned = True
        else:
            return None
    if not returned or len(stack) != 1 or stack[0].kind == 'receiver':
        return None
    return stack[0]

def classify_join(paths: Sequence[Sequence[tuple[str, str]]], *, complete_cfg: bool) -> Origin | None:
    """Only equal field/null origins join; allocation site never proves identity."""
    if not complete_cfg or not paths:
        return None
    origins = [classify_path(p) for p in paths]
    if any(origin is None for origin in origins):
        return None
    first = origins[0]
    if first.kind == 'allocation':
        return None
    return first if all(origin == first for origin in origins) else None
