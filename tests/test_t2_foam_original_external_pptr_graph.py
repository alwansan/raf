"""Source-free adversarial Material.m_Shader external graph gates for T2."""
import unittest

from scripts.t2_foam_original_external_pptr_graph import (
    FOAM_OWNER, FOAM_PATHID, OWNERS, OWNER_TAGS,
    classify_owner_graph, external_provider_key,
)


def fixture():
    return {
        name: {
            "shaders": {FOAM_PATHID, 34} if name == FOAM_OWNER else {50},
            "materials": [],
            "unparsed": 0,
            "externals": [],
            "object_count": 10,
        } for name in OWNERS
    }


class OriginalFoamExternalGraphTests(unittest.TestCase):
    def test_all_four_source_owners_explicit_and_unique(self):
        self.assertEqual(len(OWNERS), 4)
        self.assertEqual(set(OWNERS), set(OWNER_TAGS))
        self.assertEqual(FOAM_PATHID, 2420)

    def test_basename_to_known_provider_only_not_alias(self):
        self.assertEqual(
            external_provider_key("archive:/Raft_Data/sharedassets0.assets"),
            FOAM_OWNER,
        )
        self.assertEqual(
            external_provider_key(r"another\folder\sharedassets0.assets"),
            FOAM_OWNER,
        )
        self.assertIsNone(external_provider_key("sharedassets777.assets"))
        self.assertIsNone(external_provider_key(""))
        self.assertIsNone(external_provider_key("a" * 1025))
        self.assertIsNone(external_provider_key("unsafe" + chr(0) + "path"))

    def test_local_foreign_same_pathid_never_claims_original_foam(self):
        graph = fixture()
        graph[FOAM_OWNER]["materials"] = [(0, FOAM_PATHID)]
        other = next(k for k in OWNERS if k != FOAM_OWNER)
        graph[other]["materials"] = [(0, FOAM_PATHID)]
        result = classify_owner_graph(graph)
        self.assertEqual(result["same_owner_Foam_shader_direct_refs"], 1)
        self.assertEqual(result["other_owner_local_same_PathID_not_Foam_count"], 1)
        self.assertEqual(result["external_basename_and_PathID_Foam_candidates"], 0)

    def test_external_fileID_is_one_based_and_pathid_requires_exact_object(self):
        graph = fixture()
        other = next(k for k in OWNERS if k != FOAM_OWNER)
        graph[other]["externals"] = [
            "another-owner.assets",
            "archive:/Raft_Data/sharedassets0.assets",
            "archive:/Raft_Data/resources.assets",
        ]
        graph[other]["materials"] = [
            (1, FOAM_PATHID), (2, FOAM_PATHID),
            (2, 34), (2, 50), (3, FOAM_PATHID),
            (99, FOAM_PATHID), (0, 0),
        ]
        result = classify_owner_graph(graph)
        self.assertEqual(result["external_basename_and_PathID_Foam_candidates"], 1)
        self.assertEqual(result["external_known_pinned_typed_Shader_PPtr_candidates"], 2)
        self.assertEqual(result["external_malformed_fileID_count"], 1)
        self.assertEqual(result["material_null_Shader_pointer_count"], 1)
        self.assertEqual(result["external_unresolved_or_unpinned_target_count"], 2)
        self.assertFalse(result["external_file_basename_is_actual_Shader_GUID_identity_verified"])

    def test_unparsed_materials_are_counted_never_excluded_from_denominator(self):
        graph = fixture()
        graph[FOAM_OWNER]["materials"] = [(0, 0), None]
        graph[FOAM_OWNER]["unparsed"] = 1
        result = classify_owner_graph(graph)
        self.assertEqual(result["material_objects_examined"], 2)
        self.assertEqual(result["material_pointer_unparsed"], 1)
        self.assertEqual(result["material_null_Shader_pointer_count"], 1)
        self.assertFalse(result["material_PPtr_runtime_resolution_verified"])

    def test_original_foam_object_required_in_correct_owner(self):
        graph = fixture()
        graph[FOAM_OWNER]["shaders"].remove(FOAM_PATHID)
        with self.assertRaises(ValueError):
            classify_owner_graph(graph)

    def test_bounded_shape_and_invalid_external_are_rejected(self):
        for alter in (
            lambda d: d.pop(next(iter(OWNERS))),
            lambda d: d[FOAM_OWNER].update(unparsed=1),
            lambda d: d[FOAM_OWNER].update(externals=[11]),
            lambda d: d[FOAM_OWNER].update(shaders={True}),
            lambda d: d[FOAM_OWNER].update(materials=[(-1, 2420)]),
            lambda d: d[FOAM_OWNER].update(materials=[(0, 1, 3)]),
            lambda d: d[FOAM_OWNER].update(object_count=0),
        ):
            g = fixture()
            alter(g)
            with self.assertRaises(ValueError):
                classify_owner_graph(g)

    def test_no_dynamic_source_symbols_or_external_paths_in_safe_result(self):
        graph = fixture()
        foreign = next(k for k in OWNERS if k != FOAM_OWNER)
        graph[foreign]["externals"] = ["private/owner/NOT_A_PINNED_FILE"]
        graph[foreign]["materials"] = [(1, 2420)]
        safe = classify_owner_graph(graph)
        self.assertNotIn("NOT_A_PINNED_FILE", str(safe))
        self.assertNotIn("private/owner", str(safe))
        self.assertEqual(safe["external_unresolved_or_unpinned_target_count"], 1)


if __name__ == "__main__":
    unittest.main()
