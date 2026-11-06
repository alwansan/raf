"""Source-free HLSL Vertex output field parsing and anonymous width-origin controls."""
import unittest

from scripts.t3_particle108_hlsl_output_width_origin import (
    COUNTERS, classify, extract_output_struct,
)

def source_stage(outputs):
    return {"inputs":[],"outputs":[{"location":loc,"type":typ} for loc,typ in outputs],"resource_slots":{}}

def raw_named(outputs):
    return {"outputs":[{"location":loc,"type":typ,"name":name} for loc,typ,name in outputs]}

class HLSLVertexWidthOriginTests(unittest.TestCase):
    def check(self,source,roundtrip,fields,raw=None):
        return classify(source_stage(source),source_stage(roundtrip),
                        raw_named([] if raw is None else raw),fields)

    def test_generated_output_struct_fields_and_builtins(self):
        hlsl=("struct SPIRV_Cross_Output {\n"
              "    float4 out_color : TEXCOORD0;\n"
              "    float2 out_uv : TEXCOORD1;\n"
              "    float4 gl_position : SV_Position;\n};\n")
        fields=extract_output_struct(hlsl)
        self.assertEqual(len(fields),3)
        d=self.check([(0,"vec4"),(1,"vec2")],
                     [(0,"vec4"),(1,"vec2")],fields,
                     [(0,"vec4","out_color"),(1,"vec2","out_uv")])
        self.assertEqual(d["generated_hlsl_output_user_fields"],2)
        self.assertEqual(d["generated_hlsl_output_builtin_fields"],1)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_source"],1)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_roundtrip"],1)
        self.assertEqual(d["source_to_hlsl_exact_name_matches"],2)
        self.assertEqual(d["source_to_hlsl_exact_name_type_equal"],2)
        self.assertEqual(set(d),set(COUNTERS))

    def test_output_struct_missing_returns_conservative_counts(self):
        fields=extract_output_struct("struct Other { float4 x : TEXCOORD0; };")
        self.assertIsNone(fields)
        d=self.check([(0,"vec4")],[(0,"vec2")],fields)
        self.assertEqual(d["generated_hlsl_output_struct_not_found"],1)
        self.assertEqual(d["source_to_hlsl_exact_name_matches"],0)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_source"],0)

    def test_duplicate_struct_does_not_guess(self):
        hlsl="struct SPIRV_Cross_Output { float4 x : TEXCOORD0; };"
        self.assertIsNone(extract_output_struct(hlsl+"\n"+hlsl))

    def test_hlsl_field_narrowed_before_compilation(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float2 same : TEXCOORD0; };")
        d=self.check([(0,"vec4")],[(0,"vec2")],fields,[(0,"vec4","same")])
        self.assertEqual(d["source_to_hlsl_exact_name_type_narrowing"],1)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_source"],0)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_roundtrip"],1)

    def test_recompiler_narrowing_if_hlsl_still_matches_source_shape(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float4 same : TEXCOORD0; };")
        d=self.check([(0,"vec4")],[(0,"vec2")],fields,[(0,"vec4","same")])
        self.assertEqual(d["source_to_hlsl_exact_name_type_equal"],1)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_source"],1)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_roundtrip"],0)

    def test_multiset_match_does_not_require_name_or_semantic_identity(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float2 different : COLOR7; float4 other : TEXCOORD2; };")
        d=self.check([(0,"vec4"),(1,"vec2")],[(0,"vec4"),(1,"vec2")],fields,
                     [(0,"vec4","authored0"),(1,"vec2","authored1")])
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_source"],1)
        self.assertEqual(d["source_to_hlsl_exact_name_matches"],0)

    def test_vector_widening_exact_name(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float4 same : TEXCOORD0; };")
        d=self.check([(0,"vec2")],[(0,"vec4")],fields,[(0,"vec2","same")])
        self.assertEqual(d["source_to_hlsl_exact_name_type_widening"],1)

    def test_class_and_width_mismatch_exact_name_other(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { int3 same : TEXCOORD0; };")
        d=self.check([(0,"vec4")],[(0,"ivec3")],fields,[(0,"vec4","same")])
        self.assertEqual(d["source_to_hlsl_exact_name_type_other"],1)

    def test_unsupported_field_yields_inconclusive_multiset_not_false_mismatch(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { half4 same : TEXCOORD0; };")
        d=self.check([(0,"vec4")],[(0,"vec4")],fields,[(0,"vec4","same")])
        self.assertEqual(d["generated_hlsl_output_unsupported_user_types"],1)
        self.assertEqual(d["hlsl_user_output_type_multiset_differs_source"],0)
        self.assertEqual(d["hlsl_user_output_type_multiset_equals_source"],0)

    def test_unparsed_output_field_not_silently_counted_as_mismatch(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float4 bad[2] : TEXCOORD0; };")
        d=self.check([(0,"vec4")],[(0,"vec4")],fields)
        self.assertEqual(d["generated_hlsl_output_unparsed_fields"],1)
        self.assertEqual(d["hlsl_user_output_type_multiset_differs_source"],0)

    def test_source_reflection_type_must_match_sanitized_location(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float4 v : TEXCOORD0; };")
        with self.assertRaisesRegex(ValueError,"unverified_named_source_location_type"):
            self.check([(0,"vec4")],[(0,"vec4")],fields,[(0,"vec2","v")])

    def test_duplicate_source_names_rejected(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float4 v : TEXCOORD0; };")
        with self.assertRaisesRegex(ValueError,"duplicate_original_output_reflection_name"):
            self.check([(0,"vec4"),(1,"vec4")],[(0,"vec4"),(1,"vec4")],fields,
                       [(0,"vec4","same"),(1,"vec4","same")])

    def test_duplicate_generated_hlsl_output_field_rejected(self):
        fields=extract_output_struct("struct SPIRV_Cross_Output { float4 v : TEXCOORD0; float2 v : TEXCOORD1; };")
        with self.assertRaisesRegex(ValueError,"duplicate_private_HLSL_output_field"):
            self.check([(0,"vec4"),(1,"vec2")],[(0,"vec4"),(1,"vec2")],fields)

    def test_hlsl_name_and_semantic_never_in_public_report(self):
        private_name="DO_NOT_LEAK_SOURCE_SYMBOL"
        fields=extract_output_struct(
            f"struct SPIRV_Cross_Output {{ float4 {private_name} : TEXCOORD379; }};")
        d=self.check([(0,"vec4")],[(0,"vec4")],fields,
                     [(0,"vec4",private_name)])
        self.assertNotIn(private_name,str(d))
        self.assertNotIn("TEXCOORD379",str(d))
        self.assertEqual(d["source_to_hlsl_exact_name_type_equal"],1)

    def test_size_limit_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"invalid_private_generated_hlsl_scope"):
            extract_output_struct("x"*(1024*1024+1))

if __name__=="__main__":
    unittest.main()
