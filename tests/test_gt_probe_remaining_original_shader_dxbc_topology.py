"""Synthetic source-ranking tests: no original shader programs or private IDs."""
import unittest
from scripts.gt_probe_remaining_original_shader_dxbc_topology import ranked_candidates


class OriginalRemainingD3D11QueueTests(unittest.TestCase):
    def test_rank_only_authenticated_unique_source_shader_targets(self):
        sources={
            ("resources.assets",10):"a"*64,
            ("resources.assets",11):"b"*64,
            ("sharedassets0.assets",12):"b"*64,
            ("level0",1):"c"*64,
        }
        usage={"a"*64:48,"b"*64:30,"c"*64:26,"d"*64:229}
        queue=ranked_candidates(sources,usage,top=4)
        self.assertEqual([row[0] for row in queue],[229,48,30,26])
        self.assertEqual(queue[0][1],None)
        self.assertEqual(queue[0][2],0)
        self.assertEqual(queue[1][2],1)
        self.assertEqual(queue[2][2],2)
        self.assertEqual(queue[2][1],None)
        self.assertEqual(queue[3][2],1)

    def test_post14_actual_216_dummy_materials_ranked_without_name_guid_equivalence(self):
        sources={
            ("resources.assets",11):"a"*64,
            ("sharedassets2.assets",21):"b"*64,
            ("sharedassets3.assets",22):"b"*64,
            ("sharedassets4.assets",23):"c"*64,
        }
        usage={"a"*64:23,"b"*64:23,"c"*64:18,"d"*64:152}
        result=ranked_candidates(sources,usage,top=4,
                                 expected_dummy_materials=216)
        self.assertEqual([row[0] for row in result],[152,23,23,18])
        self.assertEqual(result[0][1],None)
        self.assertEqual(result[1][2],1)
        self.assertEqual(result[2][2],2)
        self.assertEqual(result[2][1],None)
        self.assertEqual(result[3][2],1)
        with self.assertRaisesRegex(ValueError,"unverified_remaining_source_D3D11_probe_scope"):
            ranked_candidates(sources,usage,expected_dummy_materials=246)
        with self.assertRaisesRegex(ValueError,"unverified_remaining_source_D3D11_probe_scope"):
            ranked_candidates(sources,usage,expected_dummy_materials=217)

    def test_wrong_material_population_cannot_select_any_raw_program(self):
        with self.assertRaisesRegex(ValueError,"unverified_remaining_source_D3D11_probe_scope"):
            ranked_candidates({("resources.assets",1):"a"*64},{"a"*64:334})
        with self.assertRaisesRegex(ValueError,"unverified_remaining_source_D3D11_probe_scope"):
            ranked_candidates({("resources.assets",1):"a"*64},{"a"*64:333},top=33)


if __name__=="__main__":
    unittest.main()
