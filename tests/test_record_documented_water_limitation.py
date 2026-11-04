"""Exact-match tests for the documented experimental water limitation path.

Strict by default: the limitation can only continue when the explicit build
request enumerates exactly the live unmet conditions. No kernels are faked and
the identity flag is never toggled.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.record_documented_water_limitation import check, unmet_conditions
from scripts.verify_water_render_contract import REQUIRED_PASS_COUNT


def write_shader(assets, name, passes):
    filename = 'source_' + str(len(list(assets.rglob('*.shader')))) + '.shader'
    source = 'Shader "' + name + '" { SubShader {\n'
    for _ in range(passes):
        source += 'Pass { CGPROGRAM\nvoid main() {}\nENDCG\n}\n'
    source += '} }\n'
    path = assets / filename
    path.write_text(source)
    Path(str(path) + '.meta').write_text('guid: ' + str(len(list(assets.rglob('*.shader')))).zfill(32))
    return path


def project_with_unmet(root, include_compute=False):
    assets = root / 'Assets'
    assets.mkdir(parents=True)
    for name in REQUIRED_PASS_COUNT:
        write_shader(assets, name, 1)
    if include_compute:
        source = assets / 'FFT.compute'
        source.write_text('#pragma kernel Horizontal\n[numthreads(8,8,1)]\nvoid Horizontal() {}\n')
        Path(str(source) + '.meta').write_text('guid: ' + 'a' * 32)
    return root


def project_with_all_passes(root):
    assets = root / 'Assets'
    assets.mkdir(parents=True)
    for name, count in REQUIRED_PASS_COUNT.items():
        write_shader(assets, name, count)
    source = assets / 'FFT.compute'
    source.write_text('#pragma kernel Horizontal\n[numthreads(8,8,1)]\nvoid Horizontal() {}\n')
    Path(str(source) + '.meta').write_text('guid: ' + 'a' * 32)
    return root


def request_with(root, acknowledged):
    path = root / 'request.json'
    path.write_text(json.dumps({'request_id': 'test-trial', 'documented_water_limitations': acknowledged}))
    return path


class DocumentedWaterLimitationTests(unittest.TestCase):
    def test_exact_live_conditions_allow_documented_trial(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = project_with_unmet(root)
            from scripts.record_documented_water_limitation import unmet_conditions as live
            from scripts.verify_water_render_contract import inspect
            conditions = live(inspect(project))
            self.assertIn('water_compute_source_candidate', conditions)
            self.assertIn('authentic_water_kernel_identity', conditions)
            self.assertEqual(len([c for c in conditions if c.startswith('shader_pass_contract:')]),
                             len(REQUIRED_PASS_COUNT))
            request = request_with(root, conditions)
            out = root / 'limitation.json'
            record = check(project, request, out)
            self.assertTrue(record['experimental'])
            self.assertEqual(record['strict_water_gate'], 'not_passed')
            self.assertEqual(record['unmet_conditions'], sorted(set(conditions)))
            self.assertFalse(record['authentic_water_kernel_identity_verified'])
            self.assertEqual(json.loads(out.read_text())['unmet_conditions'], record['unmet_conditions'])

    def test_missing_or_mismatched_acknowledgement_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = project_with_unmet(root)
            from scripts.record_documented_water_limitation import unmet_conditions as live
            from scripts.verify_water_render_contract import inspect
            conditions = live(inspect(project))
            cases = [
                conditions[:-1],                       # missing one
                conditions + ['water_compute_source_candidate'],  # duplicate
                conditions + ['shader_pass_contract:Unknown/Shader'],  # stale extra
                [],                                    # empty list
            ]
            for acknowledged in cases:
                with self.subTest(acknowledged=acknowledged):
                    request = request_with(root, acknowledged)
                    with self.assertRaises(ValueError):
                        check(project, request, root / 'limitation.json')
            self.assertFalse((root / 'limitation.json').exists())
            bad = root / 'request.json'
            bad.write_text(json.dumps({'request_id': 'test', 'documented_water_limitations': 'not-a-list'}))
            with self.assertRaises(ValueError):
                check(project, bad, root / 'limitation.json')

    def test_all_pass_counts_and_compute_still_require_kernel_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project = project_with_all_passes(root)
            from scripts.verify_water_render_contract import inspect
            report = inspect(project)
            self.assertTrue(report['all_logged_shader_pass_requirements_satisfied'])
            self.assertTrue(report['water_compute_source_candidate_present'])
            self.assertEqual(unmet_conditions(report), ['authentic_water_kernel_identity'])
            request = request_with(root, ['authentic_water_kernel_identity'])
            record = check(project, request, root / 'limitation.json')
            self.assertEqual(record['unmet_conditions'], ['authentic_water_kernel_identity'])
            with self.assertRaises(ValueError):
                check(project, request_with(root, ['authentic_water_kernel_identity', 'water_compute_source_candidate']),
                      root / 'limitation2.json')


if __name__ == '__main__':
    unittest.main()
