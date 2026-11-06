import unittest
from scripts.t1_fft_original_existing_gid_audit import analyze

BASE = """OpCapability Shader
OpMemoryModel Logical GLSL450
OpEntryPoint GLCompute %main "main" %gid
OpDecorate %gid BuiltIn GlobalInvocationId
%uint = OpTypeInt 32 0
%v3 = OpTypeVector %uint 3
%ptr = OpTypePointer Input %v3
%gid = OpVariable %ptr Input
%loaded = OpLoad %v3 %gid
"""

def member():
    return (BASE.replace("OpDecorate %gid BuiltIn GlobalInvocationId",
                         "OpMemberDecorate %struct 0 BuiltIn GlobalInvocationId")
                .replace("%ptr = OpTypePointer Input %v3",
                         "%struct = OpTypeStruct %v3\n%ptr = OpTypePointer Input %struct"))

class ExistingGidTests(unittest.TestCase):
    def test_existing_direct_input_is_ready(self):
        x=analyze(BASE)
        self.assertEqual(x["direct_count"], 1)
        self.assertEqual(x["member_count"], 0)
        self.assertTrue(x["already_accessible_as_standard_input"])
        self.assertEqual(x["direct_declarations"][0]["direct_load_user_count"], 1)
        self.assertEqual(x["direct_declarations"][0]["value_type"],
                         {"numeric_kind":"uint32","width":3})
        self.assertFalse(x["original_gpu_invocation_capture_proven"])

    def test_direct_missing_interface_not_ready(self):
        x=analyze(BASE.replace('"main" %gid','"main"'))
        self.assertFalse(x["already_accessible_as_standard_input"])
        self.assertFalse(x["direct_declarations"][0]["in_compute_entry_interface"])

    def test_signed_input_rejected(self):
        x=analyze(BASE.replace("OpTypeInt 32 0","OpTypeInt 32 1"))
        self.assertFalse(x["already_accessible_as_standard_input"])
        self.assertEqual(x["direct_declarations"][0]["value_type"]["numeric_kind"],"sint32")

    def test_wrong_variable_storage_rejected(self):
        x=analyze(BASE.replace("OpTypePointer Input","OpTypePointer Private")
                      .replace("OpVariable %ptr Input","OpVariable %ptr Private"))
        self.assertEqual(x["direct_declarations"][0]["declaration_form"], "other_variable")
        self.assertFalse(x["already_accessible_as_standard_input"])

    def test_struct_member_builtin_accepted(self):
        x=analyze(member())
        self.assertEqual(x["direct_count"],0)
        self.assertEqual(x["member_count"],1)
        self.assertTrue(x["already_accessible_as_standard_input"])
        self.assertEqual(x["member_declarations"][0]["member_type"],
                         {"numeric_kind":"uint32","width":3})

    def test_struct_missing_interface_not_ready(self):
        x=analyze(member().replace('"main" %gid','"main"'))
        self.assertFalse(x["already_accessible_as_standard_input"])

    def test_bad_member_index_fail_closed(self):
        with self.assertRaises(ValueError):
            analyze(member().replace("MemberDecorate %struct 0","MemberDecorate %struct 4"))

    def test_no_builtin_is_not_ready(self):
        x=analyze(BASE.replace("OpDecorate %gid BuiltIn GlobalInvocationId",""))
        self.assertEqual(x["status"],"builtin_not_declared")

    def test_public_report_has_no_original_ssa_ids(self):
        x=analyze(BASE)
        self.assertNotIn("%gid",str(x))
        self.assertNotIn("%loaded",str(x))
        self.assertNotIn("%v3",str(x))
        self.assertFalse(x["private_identifiers_exported"])

if __name__ == "__main__":
    unittest.main()
