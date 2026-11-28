import unittest
from tools.gt_skybox_compiler_differential import probe as p
class Controls(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(len({p.shader(c) for c in p.CASES}),7)
        self.assertTrue(all("#pragma vertex gt_vert" in p.shader(c) and "#pragma fragment gt_frag" in p.shader(c) for c in p.CASES))
    def test_guard(self):
        self.assertNotIn(p.GUARD,p.shader("common"))
        self.assertIn(p.GUARD,p.shader("guard_common"))
        self.assertEqual(p.shader("guard_common").count("register(b2)"),2)
        self.assertIn("register(b3)",p.shader("guard_different_registers"))
    def test_split(self):
        s=p.shader("split_registers")
        self.assertIn("GTVertex : register(b2)",s)
        self.assertIn("GTFragment : register(b3)",s)
        self.assertNotIn(p.GUARD,s)
    def test_exclusive_entries(self):
        for case in ("guard_entries","guard_entries_offset"):
            s=p.shader(case)
            vs,fs=s.split(p.GUARD,1)[1].split(p.FRAG,1)
            self.assertIn("Vary gt_vert",vs)
            self.assertNotIn("float4 gt_frag",vs)
            self.assertIn("float4 gt_frag",fs)
            self.assertNotIn("Vary gt_vert",fs)
        self.assertIn("packoffset(c1)",p.shader("guard_entries_offset"))
        self.assertIn("register(b3)",p.shader("guard_entries_offset"))
    def test_scoped_decoding_without_console(self):
        good=dict(imported=True,bundleBuilt=True,sourceCopyExact=True,bundle_sha256_matches=True,
                  errorsBefore=0,errorsAfter=0,stageSelectorMessages=0,bindingConflictMessages=0,
                  decoded_vertex_fragment=True,all_spirv_validated=True,referenced_blob_count=1,
                  execution_models=[0,4],log_boundary=False)
        self.assertTrue(p.editor_clean_decoded(good))
        self.assertFalse(p.compiled(good))
        for k,v in (("sourceCopyExact",False),("bundle_sha256_matches",False),("errorsAfter",1),
                    ("stageSelectorMessages",1),("bindingConflictMessages",1),("execution_models",[0])):
            with self.subTest(k=k):self.assertFalse(p.editor_clean_decoded(dict(good,**{k:v})))
    def test_bad_case(self):
        with self.assertRaises(ValueError):p.shader("bad")
    def test_log_scope(self):
        log="GT_STAGE_PROBE_BEGIN common\nvulkan (total internal programs: 2, unique: 2)\nGT_STAGE_PROBE_END common\nGT_STAGE_PROBE_BEGIN guard_common\nShader error: GT_PROBE_STAGE_SELECTION\nGT_STAGE_PROBE_END guard_common\n"
        self.assertEqual(p.log_case(log,"common")["vulkan_internal_program_counts"],[[2,2]])
        self.assertEqual(p.log_case(log,"common")["stage_selection_errors"],0)
        self.assertEqual(p.log_case(log,"guard_common")["stage_selection_errors"],1)
    def test_missing_boundary(self):
        self.assertFalse(p.log_case("GT_STAGE_PROBE_BEGIN common\n","common")["log_boundary"])
    def test_acceptance_mutations(self):
        good=dict(imported=True,bundleBuilt=True,errorsBefore=0,errorsAfter=0,decoded_vertex_fragment=True,all_spirv_validated=True,referenced_blob_count=1,execution_models=[0,4],log_boundary=True,stage_selection_errors=0,shared_uniform_explicit_binding_conflicts=0)
        self.assertTrue(p.compiled(good))
        for k,v in (("bundleBuilt",False),("errorsAfter",1),("decoded_vertex_fragment",False),("all_spirv_validated",False),("referenced_blob_count",0),("execution_models",[0]),("stage_selection_errors",1),("shared_uniform_explicit_binding_conflicts",1),("log_boundary",False)):
            with self.subTest(k=k):self.assertFalse(p.compiled(dict(good,**{k:v})))
if __name__=="__main__":unittest.main()
