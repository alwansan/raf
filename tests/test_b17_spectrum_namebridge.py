"""B17 source-free Spectrum property binding guards (no game source)."""
import unittest
from scripts.b17_spectrum_namebridge import rebind_resource_symbols

HLSL = ("Texture2D<float4> stage_t0 : register(t0);\n"
        "SamplerState stage_s0 : register(s0);\n"
        "cbuffer cb0 : register(b0) { float4 n; };\n")
NAMES = [("ColorTex", 1)]

def program(slot=0, sampler=0, extra=False):
    return {"m_CommonParameters": {
        "m_TextureParams": [{"m_Index": slot, "m_NameIndex": 1,
                             "m_SamplerIndex": sampler}],
        "m_Samplers": [{"m_Index": 2}] if extra else [],
        "m_UAVParams": [],
        "m_ConstantBuffers": [{"m_Index": 0}],
    }}

class NameBridgeTests(unittest.TestCase):
    def test_named_resource_compile_registers_remain(self):
        output, counts = rebind_resource_symbols(HLSL, program(), NAMES)
        self.assertIn("ColorTex", output)
        self.assertIn("samplerColorTex", output)
        self.assertIn("register(t0)", output)
        self.assertIn("register(s0)", output)
        self.assertIn("cbuffer cb0", output)
        self.assertEqual(counts["renamed_textures"], 1)
        self.assertEqual(counts["renamed_samplers"], 1)
        self.assertFalse(counts["original_cb_names_restored"])

    def test_fail_closed_wrong_original_sampler(self):
        with self.assertRaises(ValueError):
            rebind_resource_symbols(HLSL, program(extra=True), NAMES)

    def test_fail_closed_source_identifier_missing(self):
        with self.assertRaises(ValueError):
            rebind_resource_symbols(HLSL, program(), [("Other", 3)])

    def test_fail_closed_compiler_resource_missing(self):
        with self.assertRaises(ValueError):
            rebind_resource_symbols(HLSL.replace("stage_s0", "unknown"), program(), NAMES)

    def test_fail_closed_compiled_texture_slot_mismatch(self):
        with self.assertRaises(ValueError):
            rebind_resource_symbols(HLSL, program(slot=2), NAMES)

    def test_fail_closed_invalid_source(self):
        with self.assertRaises(ValueError):
            rebind_resource_symbols("", program(), NAMES)

    def test_fail_closed_unmodeled_original_resource(self):
        obj = program()
        del obj["m_CommonParameters"]["m_TextureParams"]
        with self.assertRaises(ValueError):
            rebind_resource_symbols(HLSL, obj, NAMES)

if __name__ == "__main__":
    unittest.main()
