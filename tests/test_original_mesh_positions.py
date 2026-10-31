import unittest
from scripts.audit_original_mesh_positions import position_metrics


class OriginalMeshPositionTests(unittest.TestCase):
    def test_empty_original_is_distinct_from_missing_payload(self):
        self.assertEqual(position_metrics(None, 0), 'empty-original')
        self.assertEqual(position_metrics(None, 3), 'vertex-count-mismatch')

    def test_finite_and_nonfinite_positions(self):
        self.assertEqual(position_metrics([(0., 1., 2.)], 1), 'finite')
        self.assertEqual(position_metrics([(0., float('nan'), 2.)], 1), 'nonfinite-or-invalid-position')
        self.assertEqual(position_metrics([(0., 1.)], 1), 'nonfinite-or-invalid-position')
