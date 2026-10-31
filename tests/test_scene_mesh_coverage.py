import unittest
from types import SimpleNamespace
from scripts.audit_scene_mesh_coverage import root_objects


class OwnerScopeTests(unittest.TestCase):
    def test_external_objects_are_not_treated_as_owned(self):
        owner, dependency = object(), object()
        env = SimpleNamespace(file=SimpleNamespace(objects={1: owner}), objects=[owner, dependency])
        self.assertEqual(root_objects(env), [owner])
