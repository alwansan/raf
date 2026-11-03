import unittest
from scripts.probe_original_fft_software_vulkan import validate_requested_workload

class RequestedWorkloadTests(unittest.TestCase):
    def test_requested_workload_and_canary_required(self):
        r=dict(extent_width=1024,extent_height=1024,synthetic_canary_verified=False,input_seed=19,dispatch_group_y=1)
        self.assertEqual(validate_requested_workload(r,19,1),r)
        for k,v in [('extent_width',8),('extent_height',1),('synthetic_canary_verified',True),('input_seed',0),('dispatch_group_y',2)]:
            with self.subTest(field=k), self.assertRaises(ValueError):
                validate_requested_workload(dict(r,**{k:v}),19,1)
