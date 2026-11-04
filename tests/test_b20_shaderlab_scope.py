"""B20: source-only ShaderLab scope checks; synthetic text only, no original shaders."""
import unittest

from scripts.b49_shaderlab_pass_contract import pass_coverage


PROGRAM = "CGPROGRAM\nfloat4 main() { return 0; }\nENDCG"


def shader(body):
    return 'Shader "Synthetic" { ' + body + ' }'


class B20ShaderLabScopeTests(unittest.TestCase):
    def test_authored_pass_belongs_to_subshader(self):
        result = pass_coverage(shader("SubShader { Pass { " + PROGRAM + " } }"))
        self.assertEqual(result["pass_count"], 1)
        self.assertEqual(result["passes_with_complete_program"], 1)
        self.assertTrue(result["all_passes_programmed"])

    def test_orphan_pass_outside_shader_cannot_count(self):
        result = pass_coverage("Pass { " + PROGRAM + " }")
        self.assertEqual(result["pass_count"], 0)
        self.assertFalse(result["all_passes_programmed"])

    def test_subshader_without_shader_cannot_count(self):
        result = pass_coverage("SubShader { Pass { " + PROGRAM + " } }")
        self.assertEqual(result["pass_count"], 0)
        self.assertFalse(result["all_passes_programmed"])

    def test_invalid_properties_pass_does_not_inflate_count(self):
        result = pass_coverage(shader("Properties { Pass { " + PROGRAM
                                      + " } } SubShader { Pass { " + PROGRAM + " } }"))
        self.assertEqual(result["pass_count"], 1)
        self.assertEqual(result["passes_with_complete_program"], 1)

    def test_shader_without_subshader_does_not_count_pass(self):
        result = pass_coverage(shader("Pass { " + PROGRAM + " }"))
        self.assertEqual(result["pass_count"], 0)
        self.assertFalse(result["all_passes_programmed"])

    def test_multiple_genuine_subshaders_count_independently(self):
        body = ("SubShader { Pass { " + PROGRAM + " } } "
                "SubShader { Pass { HLSLPROGRAM\nvoid main(){}\nENDHLSL } }")
        result = pass_coverage(shader(body))
        self.assertEqual(result["pass_count"], 2)
        self.assertEqual(result["passes_with_complete_program"], 2)
        self.assertTrue(result["all_passes_programmed"])

    def test_hlsl_nested_pass_looking_struct_does_not_count(self):
        program = "CGPROGRAM\nvoid main(){ struct Pass { int x; }; }\nENDCG"
        result = pass_coverage(shader("SubShader { Pass { " + program + " } }"))
        self.assertEqual(result["pass_count"], 1)
        self.assertTrue(result["all_passes_programmed"])

    def test_unbalanced_enclosing_shader_prevents_success(self):
        result = pass_coverage('Shader "Synthetic" { SubShader { Pass { '
                               + PROGRAM + " } }")
        self.assertEqual(result["pass_count"], 1)
        self.assertFalse(result["pass_braces_balanced"])
        self.assertFalse(result["all_passes_programmed"])

    def test_extraneous_close_prevents_success(self):
        result = pass_coverage(shader("SubShader { Pass { " + PROGRAM + " } }") + "}")
        self.assertFalse(result["pass_braces_balanced"])
        self.assertFalse(result["all_passes_programmed"])

    def test_comment_and_string_do_not_synthesize_scopes(self):
        result = pass_coverage('/* Shader "False" { SubShader { Pass { '
                               + PROGRAM + ' } } } */ "SubShader { Pass {"')
        self.assertEqual(result["pass_count"], 0)
        self.assertFalse(result["all_passes_programmed"])


if __name__ == "__main__":
    unittest.main()
