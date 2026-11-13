import unittest

from scripts.gt_original_921_shaderlab import EXPECTED_ROUTES
from scripts.gt_verify_921_shader_bundle import verify_routes


class Original921BundleTests(unittest.TestCase):
    def test_missing_compiled_route_is_rejected(self):
        names, passes = [], []
        for index, expected in enumerate(EXPECTED_ROUTES):
            rows = [{"m_KeywordIndices": []}]
            for variant in range(1, expected):
                rows.append({"m_KeywordIndices": [len(names)]})
                names.append(f"GT_ORIGINAL_921_P{index}_V{variant}")
            passes.append({stage: {"m_PlayerSubPrograms": [rows.copy()]}
                           for stage in ("progVertex", "progFragment")})
        parsed = {"m_KeywordNames": names, "m_SubShaders": [{"m_Passes": passes}]}
        self.assertEqual(verify_routes(parsed)["fragment_routes_by_pass"], list(EXPECTED_ROUTES))
        passes[1]["progFragment"]["m_PlayerSubPrograms"][0].pop()
        with self.assertRaisesRegex(ValueError, "route_population_mismatch"):
            verify_routes(parsed)
