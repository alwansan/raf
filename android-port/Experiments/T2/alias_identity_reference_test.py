"""Source-free conservative alias reference for future Foam CIL analysis.

This is not original CIL analysis, Unity execution or proof of Foam texture identity.
"""
from dataclasses import dataclass
import unittest


@dataclass(frozen=True)
class FieldReference:
    receiver: str | None
    field: str | None
    texture_object: str | None = None


def alias_relation(a: FieldReference, b: FieldReference) -> str:
    """Only proven immutable object identities support SAME/DIFFERENT."""
    # Field token and receiver alone cannot prove alias: fields can be reassigned,
    # and different fields or receivers can point to the same texture.
    if a.texture_object is None or b.texture_object is None:
        return "UNKNOWN"
    return "SAME" if a.texture_object == b.texture_object else "DIFFERENT"


def join_relations(relations: list[str]) -> str:
    """Require all reachable paths to agree, else fail closed."""
    if not relations or any(r not in {"SAME", "DIFFERENT", "UNKNOWN"} for r in relations):
        return "UNKNOWN"
    return relations[0] if len(set(relations)) == 1 else "UNKNOWN"


class ReceiverIdentityFixtures(unittest.TestCase):
    def test_proven_same_object(self):
        self.assertEqual(alias_relation(FieldReference("r1", "foam", "tex1"), FieldReference("r1", "foam", "tex1")), "SAME")

    def test_distinct_proven_allocations(self):
        self.assertEqual(alias_relation(FieldReference("r1", "foam", "tex1"), FieldReference("r2", "foam", "tex2")), "DIFFERENT")

    def test_distinct_fields_with_distinct_objects(self):
        self.assertEqual(alias_relation(FieldReference("r1", "foam", "tex1"), FieldReference("r1", "blur", "tex2")), "DIFFERENT")

    def test_unproven_field_identity(self):
        self.assertEqual(alias_relation(FieldReference("r1", "foam"), FieldReference("r1", "foam")), "UNKNOWN")
        self.assertEqual(alias_relation(FieldReference(None, "foam"), FieldReference("r1", "foam")), "UNKNOWN")

    def test_distinct_receivers_can_alias(self):
        self.assertEqual(alias_relation(FieldReference("r1", "foam", "tex1"), FieldReference("r2", "blur", "tex1")), "SAME")

    def test_conflicting_or_unknown_branch_join(self):
        self.assertEqual(join_relations(["SAME", "DIFFERENT"]), "UNKNOWN")
        self.assertEqual(join_relations(["SAME", "UNKNOWN"]), "UNKNOWN")

    def test_consistent_branch_proofs(self):
        self.assertEqual(join_relations(["SAME", "SAME"]), "SAME")
        self.assertEqual(join_relations(["DIFFERENT", "DIFFERENT"]), "DIFFERENT")

    def test_empty_and_invalid_paths(self):
        self.assertEqual(join_relations([]), "UNKNOWN")
        self.assertEqual(join_relations(["SAME", "INVALID"]), "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
