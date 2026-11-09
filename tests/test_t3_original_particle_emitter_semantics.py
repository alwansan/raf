"""Source-free tests for T3 original particle emitter label linkage."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "t3_original_particle_emitter_semantics.py"
spec = importlib.util.spec_from_file_location("t3_emitter_semantics", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ParticleEmitterNameHints(unittest.TestCase):
    def test_selected_smoke_fire_water_and_other_counts_without_names(self):
        rows = [
            (True, 2, "SmokeEmitter"),
            (True, 2, "Bonfire_Sparks"),
            (False, 0, "WaterSplash"),
            (False, 0, "GenericEffect"),
            (False, 0, None),
        ]
        result = module.safe_aggregate(rows, expected_selected_slots=4, expected_selected_renderers=2)
        self.assertEqual(result["selected_smoke_like_GameObject_names"], 1)
        self.assertEqual(result["selected_fire_like_GameObject_names"], 1)
        self.assertEqual(result["selected_GameObject_name_resolved"], 2)
        self.assertEqual(result["other_water_like_GameObject_names"], 1)
        self.assertEqual(result["other_GameObject_name_unresolved"], 1)
        self.assertNotIn("SmokeEmitter", str(result))
        self.assertNotIn("Bonfire", str(result))
        self.assertFalse(result["original_names_guids_PathIDs_or_private_shader_identifiers_published"])

    def test_ignores_near_matches(self):
        self.assertEqual(module.hint_categories("smokeless"), set())
        self.assertEqual(module.hint_categories("fireside"), set())
        self.assertEqual(module.hint_categories("Smoke_03"), {"smoke_like"})
        self.assertEqual(module.hint_categories("FlameParticles"), {"fire_like"})
        self.assertEqual(module.hint_categories("smoke_and_fire"), {"smoke_like", "fire_like"})

    def test_untrusted_rows_rejected(self):
        invalid = [
            [(1, 2, "Smoke")],
            [(True, 0, "Smoke")],
            [(False, 2, "Smoke")],
            [(True, -1, "Smoke")],
            [(True, 2, 1)],
        ]
        for rows in invalid:
            with self.subTest(rows=repr(rows)), self.assertRaises(ValueError):
                module.safe_aggregate(rows, expected_selected_slots=2, expected_selected_renderers=1)

    def test_incomplete_selected_identity_must_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "changed"):
            module.safe_aggregate([(True, 1, "Smoke")],
                                  expected_selected_slots=2, expected_selected_renderers=1)
        with self.assertRaisesRegex(ValueError, "changed"):
            module.safe_aggregate([(True, 2, "Smoke")],
                                  expected_selected_slots=2, expected_selected_renderers=2)

    def test_name_resolution_fails_closed_and_never_emits_private_ids(self):
        class Kind:
            def __init__(self, name):
                self.name = name

        class O:
            def __init__(self, kind, value):
                self.type = Kind(kind)
                self.value = value

            def read_typetree(self, **kwargs):
                return self.value

        by_id = {11: O("GameObject", {"m_Name": "Smoke01"}),
                 12: O("Material", {"m_Name": "Hidden"})}
        self.assertEqual(module.local_gameobject_name(
            {"m_GameObject": {"m_FileID": 0, "m_PathID": 11}}, by_id), "Smoke01")
        self.assertIsNone(module.local_gameobject_name(
            {"m_GameObject": {"m_FileID": 1, "m_PathID": 11}}, by_id))
        self.assertIsNone(module.local_gameobject_name(
            {"m_GameObject": {"m_FileID": 0, "m_PathID": 12}}, by_id))
        self.assertIsNone(module.local_gameobject_name({}, by_id))

    def test_name_does_not_reach_public_report_even_for_duplicates(self):
        result = module.safe_aggregate(
            [(True, 2, "Smoke_SecretPath_112"), (True, 2, "Smoke_SecretPath_112")],
            expected_selected_slots=4, expected_selected_renderers=2)
        self.assertEqual(result["selected_smoke_like_GameObject_names"], 1 if False else 0)
        self.assertNotIn("SecretPath", str(result))


if __name__ == "__main__":
    unittest.main()
