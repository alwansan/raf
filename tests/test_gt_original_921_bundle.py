import unittest

from scripts.gt_original_921_shaderlab import (
    EXPECTED_ROUTES, unity_resource_bindings, unity_varying_semantics,
)
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


class Original921UnityCompilerTests(unittest.TestCase):
    def test_named_sampler_binding_preserves_properties_and_sampling(self):
        source = ("Texture2D<float4> _Diffuse : register(t21);\n"
                  "SamplerState sampler_Diffuse : register(s16);\n"
                  "cbuffer Material : register(b0) { float4 _Color; };\n"
                  "cbuffer raft921_cb0_Globals { float raft921_cb0_pad3; };\n"
                  "_Diffuse.Sample(sampler_Diffuse, uv) * _Color * raft921_cb0_pad3;")
        converted = unity_resource_bindings(source, "fs")
        self.assertIn("Texture2D<float4> _Diffuse;", converted)
        self.assertIn("SamplerState sampler_Diffuse;", converted)
        self.assertNotIn("register(s16)", converted)
        self.assertIn("cbuffer Material : register(b0) { float4 _Color; };", converted)
        self.assertIn("cbuffer gt_fs_raft921_cb0_Globals", converted)
        self.assertIn("_Diffuse.Sample(sampler_Diffuse, uv) * _Color * gt_fs_raft921_cb0_pad3;", converted)

    def test_unity_varying_keeps_original_register_and_interpolation(self):
        self.assertEqual(
            unity_varying_semantics("    [[vk::location(7)]] nointerpolation uint v7 : TEXCOORD7;"),
            "    nointerpolation uint v7 : TEXCOORD7;",
        )
        with self.assertRaisesRegex(ValueError, "varying_semantic_location_mismatch"):
            unity_varying_semantics("    [[vk::location(6)]] nointerpolation uint v7 : TEXCOORD7;")
