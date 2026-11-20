"""Guard the isolated probe's publication and one-variant/seven-pass contract."""
from pathlib import Path
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]

class UnityProbeContract(unittest.TestCase):
    def test_probe_keeps_one_actual_keyword_variant_and_no_player_build(self):
        source=(ROOT/'android-port/Experiments/GT/Editor/FFTUtilitiesShaderValidation.cs').read_text()
        for required in ('result.passCount != 7','result.registeredKeywordVariants != 1',
                         'PassType.Normal, Array.Empty<string>()',
                         'ForceRebuildAssetBundle | BuildAssetBundleOptions.StrictMode',
                         'result.errors == 0 && !ShaderUtil.ShaderHasError(shader)',
                         'SourceReceiptCandidateMismatch','2021.3.45f2'):
            self.assertIn(required,source)
        self.assertNotIn('BuildPlayer(',source)
        self.assertNotIn('registeredRoutes =',source)
        self.assertNotIn('error.Message',source)

    def test_only_safe_receipts_are_uploaded_and_bundle_decoder_is_mandatory(self):
        path=ROOT/'.github/workflows/raft-gt-fft-utilities-source.yml'
        workflow=yaml.safe_load(path.read_text())
        steps=workflow['jobs']['source-recovery']['steps']
        uploads=[s for s in steps if s.get('uses','').startswith('actions/upload-artifact@')]
        self.assertEqual(len(uploads),1)
        paths=uploads[0]['with']['path'].splitlines()
        self.assertEqual(len(paths),3)
        self.assertTrue(all(p.endswith('-safe.json') and '*' not in p for p in paths))
        proof=next(s['run'] for s in steps if '--smolv-decoder' in s.get('run',''))
        self.assertIn('--fft-utilities',proof)
        self.assertIn("bundle['vertex_routes_by_pass']==bundle['fragment_routes_by_pass']==[1]*7",proof)
        self.assertIn("source['candidate_shader_sha256']",proof)
