#!/usr/bin/env python3
"""T3 synthetic malformed reflection records; no proprietary inputs."""
import unittest
from t3_dxbc_spirv_contract_join import check_contract

class MalformedReflectionTest(unittest.TestCase):
    def test_unhashable_stage_and_family_fail_closed(self):
        dx = [{"stage":"vertex","family":"texture","register":0,"count":1}]
        spv = [{"stage":"vertex","family":"texture","set":0,"binding":0,"count":1}]
        provenance = [{"stage":"vertex","family":"texture","register":0,"set":0,"binding":0,"count":1}]
        self.assertEqual(check_contract(dx,spv,provenance), [])
        for group_index in range(3):
            for field in ("stage","family"):
                for invalid in ([], {}, 3, None):
                    groups = [[dict(x) for x in group] for group in (dx,spv,provenance)]
                    groups[group_index][0][field] = invalid
                    with self.subTest(group=group_index, field=field, invalid=invalid):
                        self.assertEqual(check_contract(*groups), ["invalid_schema"])

if __name__ == "__main__":
    unittest.main()
