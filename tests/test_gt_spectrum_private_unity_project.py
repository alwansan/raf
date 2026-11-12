"""Source-free Spectrum seven-pass Unity project staging negatives."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.gt_spectrum_private_unity_project import prepare


def proof():
    return {
        "status":"PRIVATE_ORIGINAL_SPECTRUM_TWO_SEVEN_PASS_SHADERLAB_CANDIDATES",
        "original_SHA_authenticated":True,
        "original_exact_pass_count":7,
        "private_seven_pass_ShaderLab_candidates":2,
        "private_shaderlab_structural_passes":14,
        "original_stage_variants_included":28,
        "original_per_pass_render_states_source_equal":True,
        "original_game_shader_installed":False,
        "Unity2021_import_or_Adreno_pixels_proven":False,
    }


def shader(pass_count=7):
    passes=[]
    for _ in range(pass_count):
        passes.append("""Pass {
HLSLPROGRAM
#pragma target 5.0
#pragma vertex main
#pragma fragment main
float4 main() : SV_Target { return float4(1, 1, 1, 1); }
ENDHLSL
}""")
    return ('Shader "UltimateWater/Spectrum/Water Spectrum" {\n'
            'Properties {}\nSubShader {\n' + "\n".join(passes) +
            '\n}\n}\n')


class PrivateSpectrumUnityProjectTests(unittest.TestCase):
    def _files(self, root, *, source=None, metadata=None):
        private=Path(root)/"private"
        private.mkdir()
        candidate=private/"original-spectrum-7pass-variant-0.shader"
        manifest=private/"proof.json"
        editor=private/"Editor.cs"
        candidate.write_text(shader() if source is None else source)
        manifest.write_text(json.dumps(proof() if metadata is None else metadata))
        editor.write_text("public static class Editor { }\n")
        return candidate,manifest,editor,Path(root)/"project",Path(root)/"safe.json"

    def test_exact_7pass_project_stages_without_original_meta_or_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate,manifest,editor,project,out=self._files(tmp)
            initial=candidate.read_bytes()
            r=prepare(candidate,manifest,editor,project,out)
            self.assertEqual(r["status"],"PRIVATE_ORIGINAL_SPECTRUM_ISOLATED_UNITY_2021_PROJECT_STAGED")
            self.assertFalse(r["Unity_Editor_2021_compilation_proven"])
            self.assertFalse(r["Adreno_pixels_verified"])
            self.assertFalse(r["original_game_source_or_meta_modified"])
            self.assertEqual(candidate.read_bytes(),initial)
            self.assertEqual((project/"Assets/GTPrivateSpectrum.shader").read_bytes(),initial)
            self.assertEqual((project/"ProjectSettings/ProjectVersion.txt").read_text(),
                             "m_EditorVersion: 2021.3.45f2\n")
            self.assertFalse(list(project.rglob("*.meta")))
            self.assertTrue((project/"Assets/Editor/OriginalSpectrumSevenPassValidation.cs").is_file())

    def test_phone_floor_6_is_not_original_7(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate,manifest,editor,project,out=self._files(tmp,source=shader(6))
            with self.assertRaisesRegex(ValueError, "not_complete"):
                prepare(candidate,manifest,editor,project,out)
            self.assertFalse(project.exists())

    def test_dummy_or_missing_hlsl_program_rejected(self):
        for name,text in (("dummy",shader().replace("Properties {}",
                                  "Properties {}\n//DummyShaderTextExporter")),
                          ("short",shader().replace("HLSLPROGRAM", "CGPROGRAM",1))):
            with tempfile.TemporaryDirectory() as tmp:
                candidate,manifest,editor,project,out=self._files(tmp,source=text)
                with self.subTest(name=name),self.assertRaisesRegex(
                        ValueError,"not_complete"):
                    prepare(candidate,manifest,editor,project,out)

    def test_fake_source_proof_rejected(self):
        for key,value in (("original_SHA_authenticated",False),
                          ("original_exact_pass_count",6),
                          ("original_stage_variants_included",20),
                          ("original_game_shader_installed",True)):
            with tempfile.TemporaryDirectory() as tmp:
                d=proof()
                d[key]=value
                files=self._files(tmp,metadata=d)
                with self.subTest(key=key),self.assertRaisesRegex(
                        ValueError,"proof_not_accepted"):
                    prepare(*files)

    def test_never_overwrites_existing_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            files=self._files(tmp)
            files[3].mkdir()
            with self.assertRaisesRegex(ValueError, "unsafe_private"):
                prepare(*files)


if __name__ == "__main__":
    unittest.main()
