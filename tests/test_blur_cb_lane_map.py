import unittest
from scripts.blur_cb_lane_map import build, lookup

def member(offset, dim, kind='vector'):
    return dict(serialized_index=offset, serialized_dimension=dim,kind=kind,
                serialized_array_size=0,serialized_type=0)

class SparseLayout(unittest.TestCase):
    def test_original_observed_matrix_gap_preserved(self):
        m=build(dict(allocation_bytes=368,members=[member(272,4,'matrix')]))
        self.assertEqual(m['unmapped_bytes'],304)
        self.assertIsNone(lookup(m,0,0))
        self.assertEqual(lookup(m,17,0),(0,0))
        self.assertEqual(lookup(m,20,3),(0,15))
        self.assertIsNone(lookup(m,21,0))
        self.assertFalse(m['gpu_semantics_verified'])
    def test_fragment_packed_lanes_and_holes(self):
        m=build(dict(allocation_bytes=80,members=[member(32,1),member(48,3)]))
        self.assertEqual(lookup(m,2,0),(0,0))
        self.assertIsNone(lookup(m,2,1))
        self.assertEqual(lookup(m,3,2),(1,2))
        self.assertIsNone(lookup(m,3,3))
        self.assertEqual(m['unmapped_bytes'],64)
    def test_overlap_and_trim_rejected(self):
        for size,members in [(64,[member(64,2)]),(80,[member(32,4),member(36,1)])]:
            with self.assertRaises(ValueError):build(dict(allocation_bytes=size,members=members))
    def test_unknown_array_refused(self):
        x=member(0,4);x['serialized_array_size']=2
        with self.assertRaises(ValueError):build(dict(allocation_bytes=80,members=[x]))
