"""Synthetic source-only tests for unified Spectrum exact-source keyword staging."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest

from scripts.gt_spectrum_keyword_private_unity_project import prepare


def proof():
    return {
        "status":"PRIVATE_SPECTRUM_ORIGINAL_KEYWORD_INDEX4_SEVEN_PASS_ROUTED_SHADERLAB_CANDIDATE",
        "source_original_pass_count":7,
        "source_original_keyword_index":4,
        "source_original_keyword_variants_per_pass":2,
        "source_program_variant_stage_references":28,
        "source_original_keyword_index_name_authenticated":True,
        "source_original_VS_FS_pair_hashes_authenticated":True,
        "private_seven_program_keyword_pragmas":7,
        "private_uniform_block_stage_aliases_compile_only":True,
        "original_shader_keyword_flags_pragma_scope_proven":False,
        "original_game_ShaderLab_modified":False,
        "Unity_Android_2021_import_or_GPU_proven":False
    }


def shader(count=7):
    parts=['Shader "UltimateWater/Spectrum/Water Spectrum" {',
           "Properties {}", "SubShader {"]
    for i in range(count):
        parts.extend(["Pass {", "HLSLPROGRAM",
                      "#pragma target 5.0","#pragma vertex main",
                      "#pragma fragment main",
                      "#pragma multi_compile __ PRIVATE_KEY",
                      "#if defined(PRIVATE_KEY)",
                      "float4 main():SV_Target{return float4(1,0,0,1);}",
                      "#else",
                      "float4 main():SV_Target{return float4(0,1,0,1);}",
                      "#endif","ENDHLSL","}"])
    parts.extend(["}","}"])
    return "\n".join(parts)+"\n"


class PrivateKeywordUnityStaging(unittest.TestCase):
    def make(self,root,*,text=None,source=None):
        p=Path(root)
        files=p/"private"
        files.mkdir()
        shaderfile=files/"spectrum-keyword-index4-router-private.shader"
        proofpath=files/"safe.json"
        editor=files/"Editor.cs"
        shaderfile.write_text(shader() if text is None else text)
        proofpath.write_text(json.dumps(proof() if source is None else source))
        editor.write_text("class OriginalSpectrumKeywordRouterValidation {}")
        return shaderfile,proofpath,editor,p/"unity",p/"safe.json"

    def test_stages_one_7pass_routed_private_shader_without_meta(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=self.make(tmp)
            result=prepare(*a)
            self.assertEqual(result["source_keyword_passes"],7)
            self.assertFalse(result["original_keyword_scope_flags_proven"])
            self.assertFalse(result["private_Unity2021_import_proven"])
            self.assertFalse(result["original_game_Shader_or_meta_modified"])
            self.assertEqual((a[3]/"GTPrivateOriginalKeyword.txt").read_text(),"PRIVATE_KEY\n")
            self.assertEqual((a[3]/"Assets/GTPrivateSpectrumKeyword.shader").read_text(),shader())
            self.assertFalse(list(a[3].rglob("*.meta")))

    def test_rejects_non_source_keyword_index_or_flags_claim(self):
        for field,value in (("source_original_keyword_index",0),
                            ("source_original_VS_FS_pair_hashes_authenticated",False),
                            ("original_shader_keyword_flags_pragma_scope_proven",True),
                            ("Unity_Android_2021_import_or_GPU_proven",True)):
            with tempfile.TemporaryDirectory() as tmp:
                d=proof();d[field]=value
                a=self.make(tmp,source=d)
                with self.subTest(field=field),self.assertRaisesRegex(
                        ValueError,"source_hash_proof_untrusted"):
                    prepare(*a)

    def test_rejects_six_passes_or_multiple_keyword_names(self):
        for value in (shader(6),
                      shader().replace("PRIVATE_KEY","WRONG_KEY",1)):
            with tempfile.TemporaryDirectory() as tmp:
                a=self.make(tmp,text=value)
                with self.assertRaisesRegex(ValueError,"source_incomplete"):
                    prepare(*a)

    def test_never_overwrite_existing_project_or_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=self.make(tmp)
            a[3].mkdir()
            with self.assertRaisesRegex(ValueError,"path_untrusted"):
                prepare(*a)


if __name__=="__main__":
    unittest.main()
