import unittest

from scripts.t1_fft_original_global_id_inject import inject


BASE = """OpCapability Shader
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %entry "main"
OpExecutionMode %entry LocalSize 64 1 1
OpSource HLSL 500
%void = OpTypeVoid
%fn = OpTypeFunction %void
%entry = OpFunction %void None %fn
%start = OpLabel
OpReturn
OpFunctionEnd
"""


class OriginalGlobalDispatchInjectionTests(unittest.TestCase):
    def test_new_builtin_is_inserted_into_input_interface(self):
        p = inject(BASE)
        self.assertIn('OpEntryPoint GLCompute %entry "main" %t1_gid_builtin_input', p)
        self.assertIn("OpDecorate %t1_gid_builtin_input BuiltIn GlobalInvocationId", p)
        self.assertIn("%t1_gid_uint32 = OpTypeInt 32 0", p)
        self.assertIn("%t1_gid_v3uint = OpTypeVector %t1_gid_uint32 3", p)
        self.assertIn("%t1_gid_ptr_input_v3uint = OpTypePointer Input %t1_gid_v3uint", p)
        self.assertIn("%t1_gid_builtin_input = OpVariable %t1_gid_ptr_input_v3uint Input", p)
        self.assertIn("%t1_gid_loaded_id = OpLoad %t1_gid_v3uint %t1_gid_builtin_input", p)
        self.assertLess(p.index("%start = OpLabel"), p.index("%t1_gid_loaded_id = OpLoad"))
        self.assertLess(p.index("%t1_gid_loaded_id = OpLoad"), p.index("OpReturn"))

    def test_reuses_existing_uint32_vector_and_input_pointer(self):
        fixture = BASE.replace("%entry = OpFunction", (
            "%uint = OpTypeInt 32 0\n"
            "%v3 = OpTypeVector %uint 3\n"
            "%inputptr = OpTypePointer Input %v3\n"
            "%entry = OpFunction"))
        p = inject(fixture)
        self.assertEqual(p.count("OpTypeInt 32 0"), 1)
        self.assertEqual(p.count("OpTypeVector %uint 3"), 1)
        self.assertEqual(p.count("OpTypePointer Input %v3"), 1)
        self.assertIn("%t1_gid_builtin_input = OpVariable %inputptr Input", p)
        self.assertIn("%t1_gid_loaded_id = OpLoad %v3 %t1_gid_builtin_input", p)

    def test_global_input_does_not_move_original_function_variables(self):
        fixture = BASE.replace("%entry = OpFunction", (
            "%uint = OpTypeInt 32 0\n"
            "%fnptr = OpTypePointer Function %uint\n"
            "%entry = OpFunction"
        )).replace("OpReturn\nOpFunctionEnd", (
            "%local = OpVariable %fnptr Function\n"
            "OpReturn\nOpFunctionEnd"
        ))
        p = inject(fixture)
        self.assertLess(p.index("%local = OpVariable"), p.index("%t1_gid_loaded_id = OpLoad"))
        self.assertLess(p.index("%t1_gid_loaded_id = OpLoad"), p.index("OpReturn"))

    def test_unused_builtin_injection_does_not_change_original_return(self):
        p = inject(BASE)
        self.assertEqual(p.count("OpReturn"), 1)
        self.assertEqual(p.count("OpFunctionEnd"), 1)
        self.assertEqual(p.count("OpFunction "), 1)

    def test_multiple_entrypoints_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "one compute entry"):
            inject(BASE.replace("OpExecutionMode", 'OpEntryPoint GLCompute %entry "second"\nOpExecutionMode'))

    def test_vertex_entrypoint_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "one compute entry"):
            inject(BASE.replace("GLCompute", "Vertex"))

    def test_missing_shader_capability_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Shader capability"):
            inject(BASE.replace("OpCapability Shader\n", ""))

    def test_wrong_memory_model_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "memory model"):
            inject(BASE.replace("Logical GLSL450", "Physical64 OpenCL"))

    def test_already_present_global_invocation_builtin_rejected(self):
        with self.assertRaisesRegex(ValueError, "already declares"):
            inject(BASE.replace("%void = OpTypeVoid", (
                "OpDecorate %already BuiltIn GlobalInvocationId\n%void = OpTypeVoid")))

    def test_namespace_collision_or_repeat_is_rejected(self):
        p = inject(BASE)
        with self.assertRaises(ValueError):
            inject(p)

    def test_entrypoint_function_missing_rejected(self):
        with self.assertRaisesRegex(ValueError, "entry function ID"):
            inject(BASE.replace("GLCompute %entry", "GLCompute %missing"))

    def test_missing_function_label_rejected(self):
        with self.assertRaisesRegex(ValueError, "function block"):
            inject(BASE.replace("%start = OpLabel\n", ""))

    def test_public_result_is_not_a_capture(self):
        p = inject(BASE)
        self.assertNotIn("OpImageFetch", p)
        self.assertNotIn("T1TraceBuffer", p)
        self.assertNotIn("OpAtomicIAdd", p)

    def test_empty_and_overbound_inputs_fails_closed(self):
        for src in ("", BASE + " " * (2*1024*1024)):
            with self.assertRaises(ValueError):
                inject(src)


if __name__ == "__main__":
    unittest.main()
