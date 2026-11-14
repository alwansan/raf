import unittest

from scripts.gt_original_921_shaderlab import (
    EXPECTED_ROUTES, paired_uniform_layouts, unity_resource_bindings, unity_varying_semantics,
)
from scripts.gt_verify_921_shader_bundle import verify_routes


class Original921BundleTests(unittest.TestCase):
    def test_engine_routes_require_compiled_entries_and_exact_keyword_combinations(self):
        keywords = [f"KEY_{index}" for index in range(13)]
        passes = []
        expected_keys = []
        for count in EXPECTED_ROUTES:
            rows = [{"m_KeywordIndices": [index], "m_BlobIndex": index}
                    for index in range(count)]
            passes.append({stage: {"m_PlayerSubPrograms": [list(rows)]}
                           for stage in ("progVertex", "progFragment")})
            expected_keys.append({frozenset({keywords[index]}) for index in range(count)})
        shader = {"m_KeywordNames": keywords, "m_SubShaders": [{"m_Passes": passes}]}
        entries = [(0, b"compiled")] * len(keywords)
        result = verify_routes(shader, entries, expected_keys)
        self.assertTrue(result["compiled_program_table_verified"])
        self.assertEqual(result["fragment_routes_by_pass"], list(EXPECTED_ROUTES))

        rows = passes[1]["progFragment"]["m_PlayerSubPrograms"][0]
        rows[-1] = {"m_KeywordIndices": [11, 12], "m_BlobIndex": 12}
        with self.assertRaisesRegex(ValueError, "engine_routes_missing.*pass=1"):
            verify_routes(shader, entries, expected_keys)
        rows[-1] = {"m_KeywordIndices": [12], "m_BlobIndex": 13}
        with self.assertRaisesRegex(ValueError, "route_blob_missing.*pass=1"):
            verify_routes(shader, entries, expected_keys)

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
        self.assertIn("cbuffer Material { float4 _Color; };", converted)
        self.assertIn("cbuffer gt_fs_raft921_cb0_Globals", converted)
        self.assertIn("_Diffuse.Sample(sampler_Diffuse, uv) * _Color * gt_fs_raft921_cb0_pad3;", converted)

    def test_shared_material_uniforms_preserve_both_stage_offsets(self):
        base = {"name": "BlockPaint", "variant_size_bytes": 16, "structs": []}
        scalar = {"columns": 1, "rows": 1, "matrix": False,
                  "type": 0, "array_size": 0}
        vertex = dict(base, members=[dict(scalar, name="_Wave", index=0)])
        fragment = dict(base, members=[dict(scalar, name="_ColorWeight", index=8)])
        records = [{"source_constant_buffer_layouts": [value]}
                   for value in (vertex, fragment)]
        (vs,), (fs,) = paired_uniform_layouts(records)
        self.assertEqual(vs["original_named_lanes"], fs["original_named_lanes"])
        self.assertEqual(vs["original_named_lanes"][0]["path"], ["_Wave"])
        self.assertEqual(fs["original_named_lanes"][2]["path"], ["_ColorWeight"])
        fragment["members"][0].update(name="_Wave")
        with self.assertRaisesRegex(ValueError, "conflicting_shared_uniform_member"):
            paired_uniform_layouts(records)

    def test_unity_varying_keeps_original_register_and_interpolation(self):
        self.assertEqual(
            unity_varying_semantics("    [[vk::location(7)]] nointerpolation uint v7 : TEXCOORD7;"),
            "    nointerpolation uint v7 : TEXCOORD7;",
        )
        with self.assertRaisesRegex(ValueError, "varying_semantic_location_mismatch"):
            unity_varying_semantics("    [[vk::location(6)]] nointerpolation uint v7 : TEXCOORD7;")
