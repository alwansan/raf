"""Source-owned one-Pass LightMode for original ZIP2 6-Material Shader48.

Strictly require the immutable source's one original pass and serialized tags.
No guessed pass, shader GUID, source name, or Android visual claims.
"""
import unittest
from scripts.gt_original_921_shaderlab import (
    NEXT_SIX_ORIGINAL_ROUTES, pass_modes_for_routes,
    verified_source_next_six_pass_modes, engine_route_keys,
)


def original_single_pass(tags):
    return {"original_passes": [
        {"subshader": 0, "pass": 0,
         "original_state": {"m_Tags": {"tags": tags}}}
    ]}


class OnePassSourceOriginalShader48(unittest.TestCase):
    def test_source_owned_lightmode_can_be_proven_without_route_guess(self):
        self.assertEqual(NEXT_SIX_ORIGINAL_ROUTES, (2,))
        for source, expected in (
            ([["LIGHTMODE", "FORWARDBASE"]], ("ForwardBase",)),
            ([["LightMode", "ALWAYS"]], ("Always",)),
            ([], ("Untagged",)),
        ):
            self.assertEqual(
                verified_source_next_six_pass_modes(original_single_pass(source)),
                expected,
            )
        with self.assertRaisesRegex(ValueError, "unexpected_shaderlab_routes"):
            pass_modes_for_routes((2,))

    def test_original_single_pass_ownership_must_be_exact(self):
        for modification in ("wrong_owner", "wrong_pass", "two_passes", "empty"):
            source = original_single_pass([])
            if modification == "wrong_owner":
                source["original_passes"][0]["subshader"] = 1
            if modification == "wrong_pass":
                source["original_passes"][0]["pass"] = 1
            if modification == "two_passes":
                source["original_passes"].append(source["original_passes"][0])
            if modification == "empty":
                source["original_passes"].clear()
            with self.assertRaisesRegex(ValueError, "ambiguous_original_single_Pass"):
                verified_source_next_six_pass_modes(source)

    def test_missing_or_unknown_original_source_tags_fail_closed(self):
        source = original_single_pass([])
        del source["original_passes"][0]["original_state"]["m_Tags"]
        with self.assertRaisesRegex(ValueError, "missing_original_serialized_Pass_tags"):
            verified_source_next_six_pass_modes(source)
        for tags in (
            [["LIGHTMODE", "SYNTHETIC"]],
            [["LIGHTMODE", "FORWARDBASE"], ["LightMode", "Always"]],
            [["LightMode", 123]],
            [["LightMode"]],
        ):
            with self.assertRaisesRegex(ValueError, "original_"):
                verified_source_next_six_pass_modes(original_single_pass(tags))

    def test_engine_route_keys_never_introduce_fake_fixed_keywords(self):
        row={"routes": [
            {"enabled": []},
            {"enabled": ["ORIGINAL_KEYWORD_0"]},
        ]}
        self.assertEqual(
            engine_route_keys(row, 0, ("Untagged",)),
            [(), ("ORIGINAL_KEYWORD_0",)],
        )
        self.assertEqual(
            engine_route_keys(row, 0, ("Always",)),
            [(), ("ORIGINAL_KEYWORD_0",)],
        )
        with self.assertRaisesRegex(ValueError, "unproved_source_pass_mode"):
            engine_route_keys(row, 0, ("Invented",))


if __name__ == "__main__":
    unittest.main()
