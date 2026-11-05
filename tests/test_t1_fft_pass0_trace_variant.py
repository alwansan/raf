import unittest

from scripts.t1_fft_pass0_trace_variant import instrument


HLSL = """
Texture2D<float4> sourceTex : register(t0);
Texture2D<float> lookupTex : register(t1);
RWTexture2D<float4> resultTex : register(u2);
void pass0()
{
    float4 v = sourceTex.Load(int3(int2(1, 2), 0));
    float a = lookupTex.Load(int3(1, 0, 0));
    float b = lookupTex.Load(int3(2, 0, 0));
}
"""


class TraceVariantTests(unittest.TestCase):
    def test_original_load_wrapped_and_bounded(self):
        variant = instrument(HLSL)
        self.assertIn("float T1TraceLoad1(int3 coord)", variant)
        self.assertIn("T1TraceLoad0(int3(int2(1, 2), 0))", variant)
        self.assertIn("if (index < 256u)", variant)
        self.assertEqual(variant.count("lookupTex.Load(coord)"), 2)

    def test_extra_load_parameter_and_binding_collision_rejected(self):
        for value in (HLSL.replace("int3(1, 0, 0))", "int3(1, 0, 0), offset)"),
                      HLSL + "\nRWStructuredBuffer<uint> other : register(u3);"):
            with self.assertRaises(ValueError):
                instrument(value)
