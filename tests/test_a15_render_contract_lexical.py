"""A15 diagnostic-evidence red/green tests. Only synthetic ShaderLab/compute text.

The original exported game set and the 41624581951 count are NOT reproduced.
"""
import ast
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import re
import tempfile
import unittest

from scripts.audit_render_input_contracts import audit


def run_audit(shaders, computes=()):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "project" / "Assets"
        root.mkdir(parents=True)
        for index, text in enumerate(shaders):
            (root / f"shader{index}.shader").write_text(text, encoding="utf-8")
        for index, text in enumerate(computes):
            (root / f"kernel{index}.compute").write_text(text, encoding="utf-8")
        buffer = StringIO()
        with redirect_stdout(buffer):
            audit(root.parent)
        result = buffer.getvalue()
        assert result.startswith("RAFT_EXPORTED_RENDER_CONTRACT "), result
        def record(name):
            match = re.search(r"\b" + re.escape(name) + r"=(\{[^}]*\})", result)
            if match is None:
                raise AssertionError(f"missing {name} aggregate marker")
            return ast.literal_eval(match[1])
        targeted = result.split(" targeted=", 1)[1].split(" runtimeShaderSupportVerified=", 1)[0]
        return record("source_pass_histogram"), record("source_kernel_histogram"), ast.literal_eval(targeted), result


class A15RenderContractLexicalTests(unittest.TestCase):
    def test_quoted_and_commented_pass_tokens_cannot_inflate_real_passes(self):
        shader = (
            'Shader "Raft/Pass { CGPROGRAM" {\n'
            ' // Pass { HLSLPROGRAM\n'
            ' /* Pass {\nCGPROGRAM\n*/\n'
            ' SubShader { Pass { CGPROGRAM ENDCG } }\n'
            '}'
        )
        passes, _, targeted, _ = run_audit([shader])
        self.assertEqual(passes, {1: 1})
        self.assertEqual(targeted, [])

    def test_fake_program_in_comments_is_not_counted_for_real_target(self):
        shader = (
            '// CGPROGRAM \n'
            'Shader "Hidden/Post FX/Bloom" {\n'
            '  /* HLSLPROGRAM */\n'
            '  SubShader { Pass { } }\n'
            '}'
        )
        passes, _, targeted, _ = run_audit([shader])
        self.assertEqual(passes, {1: 1})
        self.assertEqual(len(targeted), 1)
        self.assertEqual(targeted[0]["shader"], "Hidden/Post FX/Bloom")
        self.assertFalse(targeted[0]["has_program_block"])

    def test_fake_target_shader_name_in_comment_does_not_preempt_real(self):
        shader = (
            '/* Shader "Hidden/Post FX/Bloom" { Pass { CGPROGRAM } } */\n'
            'Shader "Raft/SyntheticPlain" { SubShader { Pass { } } }'
        )
        passes, _, targeted, _ = run_audit([shader])
        self.assertEqual(passes, {1: 1})
        self.assertEqual(targeted, [])

    def test_block_comment_compute_pragma_is_not_a_real_kernel(self):
        compute = (
            '/*\n#pragma kernel FAKE_A\n*/\n'
            '// #pragma kernel FAKE_B\n'
            '#pragma kernel RealFFT\n'
            '/* #pragma kernel FAKE_C */\n'
            '[numthreads(1, 1, 1)] void RealFFT() {}\n'
        )
        passes, kernels, targeted, _ = run_audit([], [compute])
        self.assertEqual(passes, {})
        self.assertEqual(kernels, {1: 1})
        self.assertEqual(targeted, [])

    def test_comments_between_pass_keyword_and_brace_are_ignored(self):
        shader = 'Shader "Raft/Test" { SubShader { Pass /* harmless */ { } } }'
        passes, _, _, _ = run_audit([shader])
        self.assertEqual(passes, {1: 1})

    def test_active_program_and_kernel_controls_remain_visible(self):
        shader = (
            'Shader "Hidden/Post FX/Bloom" {\n'
            '  SubShader { Pass { HLSLPROGRAM ENDHLSL } }\n'
            '}'
        )
        compute = '#pragma kernel RealFFT\n[numthreads(1,1,1)] void RealFFT() {}\n'
        passes, kernels, targeted, _ = run_audit([shader], [compute])
        self.assertEqual(passes, {1: 1})
        self.assertEqual(kernels, {1: 1})
        self.assertEqual(len(targeted), 1)
        self.assertTrue(targeted[0]["has_program_block"])


if __name__ == "__main__":
    unittest.main()
