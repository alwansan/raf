"""Source-free conservative alias lattice for T2 Foam CIL experiment.

A token is a *single proven runtime value*, not a field name, call signature,
allocation site, or RenderTexture type. Synthetic control only; no original
Raft code or Unity runtime equivalence is established by this module.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Value:
    tokens: frozenset[str]
    may_be_null: bool = False
    unknown: bool = False

    def __post_init__(self):
        if not isinstance(self.tokens, frozenset) or any(
            not isinstance(t, str) or not t for t in self.tokens
        ):
            raise ValueError("Invalid provenance tokens")
        if type(self.may_be_null) is not bool or type(self.unknown) is not bool:
            raise ValueError("Invalid provenance flags")

def fresh_value(token: str) -> Value:
    if not isinstance(token, str) or not token:
        raise ValueError("Fresh value requires an actual SSA identity token")
    return Value(frozenset((token,)))

NULL = Value(frozenset(), may_be_null=True)
UNKNOWN = Value(frozenset(), unknown=True)

def join(*values: Value) -> Value:
    """CFG phi join; missing/unknown input never becomes proven."""
    if not values or any(not isinstance(v, Value) for v in values):
        raise ValueError("Join requires typed nonempty predecessors")
    return Value(frozenset().union(*(v.tokens for v in values)),
                 any(v.may_be_null for v in values),
                 any(v.unknown for v in values))

def same_instance_proven(a: Value, b: Value) -> bool:
    """Only a shared, single *value identity* proves aliasing.

    Equal member names, method signatures and allocation sites must never be
    passed as identities. Caller must prove SSA provenance and loop freshness.
    """
    if not isinstance(a, Value) or not isinstance(b, Value):
        raise ValueError("Values required")
    return (not a.unknown and not b.unknown and
            not a.may_be_null and not b.may_be_null and
            len(a.tokens) == len(b.tokens) == 1 and a.tokens == b.tokens)

def different_instance_proven(a: Value, b: Value) -> bool:
    """Disjoint single proven identities (never a claim about null/unknown)."""
    if not isinstance(a, Value) or not isinstance(b, Value):
        raise ValueError("Values required")
    return (not a.unknown and not b.unknown and
            not a.may_be_null and not b.may_be_null and
            len(a.tokens) == len(b.tokens) == 1 and a.tokens.isdisjoint(b.tokens))
