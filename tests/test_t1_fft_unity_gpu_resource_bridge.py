"""T1 fail-closed original-derived HLSL property binding controls (synthetic only)."""
import unittest
from scripts.t1_fft_unity_gpu_resource_bridge import translated_image_symbols


VALID = """#pragma kernel main
// Generated identifiers are NOT original Unity resource names.
Texture2D<float4> _Source: register(t0);
Texture2D<float4> _Butterfly : register(t1, space0);
RWTexture2D<float4> _Output : register(u2);
[numthreads(64,1,1)]
void main(uint3 i:SV_DispatchThreadID) {
    _Output[i.xy] = _Source.Load(int3(i.xy,0)) + _Butterfly.Load(int3(i.xy,0));
}
"""


class FFTUnityGpuResourceTests(unittest.TestCase):
    def test_exact_private_compiled_resource_roles(self):
        self.assertEqual(translated_image_symbols(VALID),{
            "source":"_Source","butterfly":"_Butterfly","output":"_Output"
        })

    def test_source_and_butterfly_swapped_are_visible_to_caller(self):
        swapped=VALID.replace("register(t0)","register(t9)").replace(
            "register(t1, space0)","register(t0)").replace(
            "register(t9)","register(t1)")
        roles=translated_image_symbols(swapped)
        self.assertEqual(roles["source"],"_Butterfly")
        self.assertEqual(roles["butterfly"],"_Source")

    def test_reject_missing_duplicate_registers(self):
        for changed in (
            VALID.replace("register(t1, space0)","register(t0)"),
            VALID.replace("register(t1, space0)","register(t2)"),
            VALID.replace("register(u2)","register(u1)"),
            VALID.replace("register(t0)","register(t999)"),
            VALID.replace("RWTexture2D<float4>","Texture2D<float4>"),
            VALID.replace("register(u2)","register(t0)"),
        ):
            with self.subTest(hash=hash(changed)):
                with self.assertRaises(ValueError):
                    translated_image_symbols(changed)

    def test_original_dx_u0_is_not_the_translated_hlsl_storage_register(self):
        # The authentic private translation observed a unique generated u2
        # output; original D3D11 executable independently declares u0.
        # These are DIFFERENT interfaces and must never be conflated.
        wrong = VALID.replace("register(u2)", "register(u0)")
        with self.assertRaises(ValueError):
            translated_image_symbols(wrong)

    def test_reject_nonzero_space_and_private_symbol_alias(self):
        for changed in (
            VALID.replace("register(t1, space0)","register(t1, space1)"),
            VALID.replace("_Butterfly", "_Source"),
        ):
            with self.assertRaises(ValueError):
                translated_image_symbols(changed)

    def test_reject_comment_forged_or_extra_texture(self):
        changed=VALID.replace("Texture2D<float4> _Butterfly", "// Texture2D<float4> _Butterfly")
        with self.assertRaises(ValueError):
            translated_image_symbols(changed)
        changed=VALID+"\nTexture2D<float4> _Extra:register(t7);\n"
        with self.assertRaises(ValueError):
            translated_image_symbols(changed)
        changed=VALID.replace("RWTexture2D<float4> _Output : register(u2);",
            "/* RWTexture2D<float4> _Output : register(u2); */")
        with self.assertRaises(ValueError):
            translated_image_symbols(changed)

    def test_reject_missing_or_binary_body(self):
        for value in ("", "bad shader", None, b"not text", "A"*(512*1024+1)):
            with self.assertRaises(ValueError):
                translated_image_symbols(value)

    def test_no_compiled_identifier_publicly_returned_by_errors(self):
        private="SENSITIVE_PRIVATE_IDENTIFIER"
        broken=VALID.replace("register(t0)","register(t4)").replace("_Source",private)
        with self.assertRaises(ValueError) as exc:
            translated_image_symbols(broken)
        self.assertNotIn(private,str(exc.exception))


if __name__=="__main__":
    unittest.main()
