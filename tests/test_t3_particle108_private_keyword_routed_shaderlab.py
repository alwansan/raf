"""Synthetic-only controls: source-index order into private four-way Shader48."""
from pathlib import Path
import json
import tempfile
import unittest
from scripts import t3_particle108_private_keyword_routed_shaderlab as router

def original(keys=None,names=None,flags=None):
    variants=[[],[1],[0],[0,1]] if keys is None else keys
    def program():
        return {"m_SubPrograms":[{"m_KeywordIndices":list(v),
                   "m_GlobalKeywordIndices":[],"m_LocalKeywordIndices":[]}
                  for v in variants],"m_PlayerSubPrograms":[]}
    return {"m_SubShaders":[{"m_Passes":[{"m_Type":0,
               "progVertex":program(),"progFragment":program()}]}],
            "m_KeywordNames":["SYNTH_A","SYNTH_B"] if names is None else names,
            "m_KeywordFlags":[0,0] if flags is None else flags}

def fake(i):
    return ('Shader "Synthetic" {\nProperties {}\nSubShader {\nPass {\n'
            'HLSLPROGRAM\n#pragma target 5.0\n#pragma vertex main\n'
            '#pragma fragment main\n#if defined(SHADER_STAGE_VERTEX)\n'
            'float4 main() : SV_Position { return float4('+str(i)+',0,0,1); }\n'
            '#elif defined(SHADER_STAGE_FRAGMENT)\n'
            'float4 main() : SV_Target { return float4(0,'+str(i)+',0,1); }\n'
            '#else\n#error Unsupported_stage\n#endif\nENDHLSL\n}\n}\n}\n')

def stage(root):
    for i in range(4):
        (root/("keyword-%d-private.shader"%i)).write_text(fake(i),encoding="utf-8")

class RoutedKeywordSynthetic(unittest.TestCase):
    def test_original_stage_order_mapped_not_keyword_sort(self):
        chosen,routes=router.source_routes(original())
        self.assertEqual(chosen,("SYNTH_A","SYNTH_B"))
        self.assertEqual(routes,{(0,0):0,(0,1):1,(1,0):2,(1,1):3})

    def test_one_provisional_shader_four_branches_eight_stage_attempts(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);stage(root)
            observed=[]
            def compiler(source,stage_index,names,bits,dir):
                observed.append((bits,stage_index))
                self.assertIn("main()",source)
                self.assertEqual(names,("SYNTH_A","SYNTH_B"))
                return True
            report=router.verify(root,original(),compiler=compiler)
            self.assertEqual(report["status"],router.STATUS)
            self.assertEqual(report["original_keyword_pair_routes"],4)
            self.assertEqual(report["private_combination_stage_Vulkan11_SPIRV_valid"],8)
            self.assertEqual(len(set(observed)),8)
            combined=(root/"keyword-routed-private.shader").read_text()
            self.assertEqual(combined.count("HLSLPROGRAM"),1)
            self.assertEqual(combined.count("ENDHLSL"),1)
            self.assertIn("#pragma multi_compile __ SYNTH_A",combined)
            self.assertIn("#pragma multi_compile __ SYNTH_B",combined)
            self.assertFalse(report["Unity_ShaderLab_import_or_actual_variant_selection_proven"])
            self.assertFalse(report["original_keyword_flags_pragma_scope_proven"])

    def test_bad_source_keyword_mappings_fail_closed(self):
        variants=[
            original(names=["DUP","DUP"]),
            original(names=["BAD NAME","SYNTH_B"]),
            original(flags=[0]),
            original(keys=[[],[0],[1],[2]]),
            original(keys=[[2],[1,2],[0,2],[0,1,2]]),
            original(names=["SHADER_STAGE_VERTEX","SYNTH_B"]),
            original(names=["GL_UNSAFE","SYNTH_B"]),
        ]
        for index,p in enumerate(variants):
            with self.subTest(index=index),self.assertRaises(ValueError):
                router.source_routes(p)

    def test_missing_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);stage(root)
            (root/"keyword-3-private.shader").unlink()
            with self.assertRaises(ValueError):router.compose(root,original())

    def test_modified_envelope_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);stage(root)
            file=root/"keyword-2-private.shader"
            file.write_text(file.read_text().replace("Properties {}",'Properties { _A ("A",Float)=0 }'))
            with self.assertRaisesRegex(ValueError,"envelope"):
                router.compose(root,original())

    def test_extra_pragma_in_private_branch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);stage(root)
            file=root/"keyword-0-private.shader"
            file.write_text(file.read_text().replace("#pragma vertex main",
                                 "#pragma vertex main\n#pragma multi_compile UNSAFE"))
            with self.assertRaises(ValueError):router.compose(root,original())

    def test_compiler_shortfall_never_green(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);stage(root)
            report=router.verify(root,original(),compiler=lambda *args:False)
            self.assertEqual(report["status"],"INCONCLUSIVE")
            self.assertEqual(report["private_combination_stage_Vulkan11_SPIRV_valid"],0)

    def test_private_output_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);stage(root)
            target=root/"keyword-routed-private.shader"
            target.write_text("preserve")
            with self.assertRaisesRegex(ValueError,"overwrite"):
                router.verify(root,original(),compiler=lambda *args:True)
            self.assertEqual(target.read_text(),"preserve")

    def test_report_never_contains_original_name(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);stage(root)
            secrets=["PRIVATE_AUTHORED_LEFT","PRIVATE_AUTHORED_RIGHT"]
            report=router.verify(root,original(names=secrets),compiler=lambda *args:True)
            text=json.dumps(report)
            for secret in secrets:
                self.assertNotIn(secret,text)
            self.assertFalse(report["original_keyword_names_indices_shader_code_or_errors_published"])

if __name__=="__main__":
    unittest.main()
