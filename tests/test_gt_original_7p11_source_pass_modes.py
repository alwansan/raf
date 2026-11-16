"""Source-owned LightMode contract for genuine 7-Material Shader48 [4,5,2]."""
import unittest
from scripts.gt_original_921_shaderlab import (
    verified_source_next_seven_pass_modes, NEXT_SEVEN_7P11_ORIGINAL_ROUTES,
    pass_modes_for_routes,
)


def original_manifest(modes=("FORWARDBASE", "FORWARDADD", "SHADOWCASTER")):
    return {"original_passes": [
        {"subshader": 0, "pass": i,
         "original_state": {"m_Tags": {"tags": [["LIGHTMODE", mode]]}}}
        for i, mode in enumerate(modes)
    ]}


class ExactOriginal7P11PassOwnership(unittest.TestCase):
    def test_source_tags_not_route_guess_prove_three_pass_modes(self):
        self.assertEqual(NEXT_SEVEN_7P11_ORIGINAL_ROUTES, (4, 5, 2))
        self.assertEqual(
            verified_source_next_seven_pass_modes(original_manifest()),
            ("ForwardBase", "ForwardAdd", "ShadowCaster"))

    def test_generic_route_mapper_must_not_guess_new_shader(self):
        with self.assertRaisesRegex(ValueError, "unexpected_shaderlab_routes"):
            pass_modes_for_routes((4, 5, 2))

    def test_wrong_source_LightMode_or_pass_order_must_fail(self):
        with self.assertRaisesRegex(ValueError, "original_Pass_LightMode_contract_not_proven"):
            verified_source_next_seven_pass_modes(
                original_manifest(("FORWARDBASE", "SHADOWCASTER", "FORWARDADD")))
        with self.assertRaisesRegex(ValueError, "unknown_original_LightMode"):
            verified_source_next_seven_pass_modes(
                original_manifest(("FORWARDBASE", "FORWARDADD", "INVALID")))

    def test_missing_duplicate_tags_or_wrong_owner_must_fail(self):
        m = original_manifest()
        m["original_passes"][0]["original_state"]["m_Tags"]["tags"] = []
        with self.assertRaisesRegex(ValueError, "unknown_original_LightMode"):
            verified_source_next_seven_pass_modes(m)
        m = original_manifest()
        m["original_passes"][0]["original_state"]["m_Tags"]["tags"].append(
            ["LightMode", "FORWARDBASE"])
        with self.assertRaisesRegex(ValueError, "unknown_original_LightMode"):
            verified_source_next_seven_pass_modes(m)
        m = original_manifest()
        m["original_passes"][1]["subshader"] = 1
        with self.assertRaisesRegex(ValueError, "ambiguous_SubShader_Pass_ownership"):
            verified_source_next_seven_pass_modes(m)


if __name__ == "__main__":
    unittest.main()
