from pathlib import Path
import shutil
import subprocess
import tempfile
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
        self.assertIn("if (index < 512u)", variant)
        self.assertEqual(variant.count("lookupTex.Load(coord)"), 2)

    def test_extra_load_parameter_and_binding_collision_rejected(self):
        for value in (HLSL.replace("int3(1, 0, 0))", "int3(1, 0, 0), offset)"),
                      HLSL + "\nRWStructuredBuffer<uint> other : register(u3);"):
            with self.assertRaises(ValueError):
                instrument(value)

    def test_invocation_layout_reuses_existing_dispatch_semantic(self):
        source = HLSL + "[numthreads(64,1,1)] void main(uint3 id : SV_DispatchThreadID) { pass0(); }"
        variant = instrument(source, keyed=True)
        self.assertEqual(variant.count("SV_DispatchThreadID"), 1)
        self.assertIn("T1TraceDispatchID = id;", variant)
        self.assertIn("index * 12u", variant)
        for site in range(3):
            self.assertIn(f"T1TraceOccurrences[{site}]++", variant)
        self.assertIn("base + 4u] = occurrence", variant)
        self.assertIn("base + 5u] = asuint(coord.x)", variant)
        self.assertIn("base + 8u] = asuint(value.x)", variant)

    def test_invocation_layout_injects_missing_dispatch_semantic(self):
        variant = instrument(HLSL + "void main() { pass0(); }", keyed=True)
        self.assertIn("main(uint3 T1TraceInputID : SV_DispatchThreadID)", variant)
        with self.assertRaises(ValueError):
            instrument(HLSL, keyed=True)

    def test_structured_dispatch_semantic_is_not_duplicated(self):
        source = HLSL + """
struct SPIRV_Cross_Input
{
    uint3 gl_GlobalInvocationID : SV_DispatchThreadID;
};
[numthreads(64,1,1)]
void main(SPIRV_Cross_Input stage_input) { pass0(); }
"""
        variant = instrument(source, keyed=True)
        self.assertEqual(variant.count("SV_DispatchThreadID"), 1)
        self.assertIn("T1TraceDispatchID = stage_input.gl_GlobalInvocationID;", variant)
        if shutil.which("glslangValidator") and shutil.which("spirv-val"):
            with tempfile.TemporaryDirectory() as directory:
                Path(directory, "trace.hlsl").write_text(variant, encoding="utf-8")
                for command in (
                    ["glslangValidator", "-V", "-D", "-S", "comp", "-e", "main",
                     "-o", "trace.spv", "trace.hlsl"],
                    ["spirv-val", "--target-env", "vulkan1.1", "trace.spv"],
                ):
                    subprocess.run(command, cwd=directory, check=True, capture_output=True, timeout=30)
