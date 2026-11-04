"""B49 strict water ShaderLab source-contract controls (synthetic, no game data)."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.b49_shaderlab_pass_contract import pass_coverage, remove_comments
from scripts.verify_water_render_contract import inspect, REQUIRED_PASS_COUNT


def shader(passes):
    return 'Shader "Fixture" { SubShader {\n' + ''.join('Pass { ' + p + ' }\n' for p in passes) + '} }'


GOOD = 'CGPROGRAM\nfloat4 f() { return 0; }\nENDCG'
HLSL = 'HLSLPROGRAM\nvoid main() {}\nENDHLSL'


class B49WaterProgramCoverage(unittest.TestCase):
    def test_two_real_passes_mixed_languages(self):
        actual = pass_coverage(shader([GOOD, HLSL]))
        self.assertEqual(actual['pass_count'], 2)
        self.assertEqual(actual['passes_with_complete_program'], 2)
        self.assertTrue(actual['all_passes_programmed'])

    def test_valid_pass_cannot_cover_empty_pass(self):
        actual = pass_coverage(shader([GOOD, '/* fake CGPROGRAM ENDCG */']))
        self.assertEqual(actual['pass_count'], 2)
        self.assertEqual(actual['passes_with_complete_program'], 1)
        self.assertFalse(actual['all_passes_programmed'])

    def test_comment_string_and_unclosed_program_rejected(self):
        source = '/* Pass { CGPROGRAM ENDCG } */\n' + shader(
            [GOOD, '"Pass { HLSLPROGRAM ENDCG }"', 'CGPROGRAM\nvoid main() {}'])
        actual = pass_coverage(source)
        self.assertEqual(actual['pass_count'], 3)
        self.assertEqual(actual['passes_with_complete_program'], 1)
        self.assertFalse(actual['all_passes_programmed'])

    def test_empty_program_and_unbalanced_braces_rejected(self):
        self.assertFalse(pass_coverage(shader(['CGPROGRAM ENDCG']))['all_passes_programmed'])
        self.assertFalse(pass_coverage('Pass { CGPROGRAM\nvoid f() {}\nENDCG')[
            'pass_braces_balanced'])

    def test_shader_declaration_in_comment_masked(self):
        text = '/* Shader "Bad" {} */ Shader "Good" { SubShader {} }'
        self.assertNotIn('Shader "Bad"', remove_comments(text))
        self.assertIn('Shader "Good"', remove_comments(text))

    def test_gate_rejects_full_count_with_programless_pass(self):
        with TemporaryDirectory() as temp:
            assets = Path(temp) / 'Assets'
            assets.mkdir()
            name, minimum = next(iter(REQUIRED_PASS_COUNT.items()))
            path = assets / 'water.shader'
            contents = 'Shader "' + name + '" { SubShader {\n'
            contents += 'Pass { ' + GOOD + ' }\n'
            contents += 'Pass { /* no executable program */ }\n' * (minimum - 1)
            path.write_text(contents + '} }', encoding='utf-8')
            Path(str(path) + '.meta').write_text('guid: ' + 'f' * 32)
            row = inspect(Path(temp))['shader_contracts'][name]
            self.assertEqual(row['observed']['pass_count'], minimum)
            self.assertEqual(row['observed']['passes_with_complete_program'], 1)
            self.assertFalse(row['observed']['all_passes_programmed'])
            self.assertFalse(row['contract_satisfied'])


    def test_alternate_subshaders_are_not_one_runtime_pass_sequence(self):
        first = 'SubShader { ' + ''.join('Pass { ' + GOOD + ' } ' for _ in range(2)) + ' }'
        second = 'SubShader { ' + ''.join('Pass { ' + GOOD + ' } ' for _ in range(4)) + ' }'
        profile = pass_coverage('Shader "Fixture" { ' + first + second + ' }')
        self.assertEqual(profile['pass_count'], 6)  # diagnostic only
        self.assertEqual(profile['subshader_pass_counts'], [2, 4])
        self.assertEqual(profile['subshader_programmed_pass_counts'], [2, 4])
        self.assertTrue(profile['all_subshaders_programmed'])
        self.assertFalse(profile['active_subshader_runtime_verified'])

    def test_unprogrammed_alternative_is_reported_per_subshader(self):
        profile = pass_coverage(
            'Shader "Fixture" { SubShader { Pass { ' + GOOD + ' } } '
            'SubShader { Pass { /* deliberately blank */ } } }')
        self.assertEqual(profile['subshader_pass_counts'], [1, 1])
        self.assertEqual(profile['subshader_programmed_pass_counts'], [1, 0])
        self.assertFalse(profile['all_subshaders_programmed'])


if __name__ == '__main__':
    unittest.main()
