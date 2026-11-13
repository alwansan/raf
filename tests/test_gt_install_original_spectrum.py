"""GT: source-free negative/positive tests for original Spectrum export replacement.

No original game ShaderLab, keywords or real game GUIDs in these fixtures.
"""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.b09_spectrum_topology_contract import TARGET
from scripts.gt_install_original_spectrum import SOURCE_PROOF, inspect, stage


def candidate(*, passes=7):
    parts = ['Shader "'+TARGET+'" {', 'SubShader {']
    for _ in range(passes):
        parts.extend([
            'Pass {', 'HLSLPROGRAM',
            '#pragma target 5.0', '#pragma vertex main', '#pragma fragment main',
            '#pragma multi_compile __ _SYNTHETIC_ONLY_',
            'float4 main() : SV_Target { return float4(1,0,0,1); }',
            'ENDHLSL', '}',
        ])
    return ('\n'.join(parts+['}', '}'])+'\n').encode()


class OriginalSpectrumExportTransactionTests(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root/'unity'
        self.assets = self.project/'Assets'/'Raft'
        self.assets.mkdir(parents=True)
        self.target = self.assets/'OriginalSpectrum.shader'
        self.original = ('Shader "'+TARGET+'" { SubShader { Pass { '
                         '//DummyShaderTextExporter\n } } }\n').encode()
        self.target.write_bytes(self.original)
        self.meta = Path(str(self.target)+'.meta')
        self.meta_bytes=b'fileFormatVersion: 2\nguid: '+b'a'*32+b'\nShaderImporter:\n  userData:\n'
        self.meta.write_bytes(self.meta_bytes)
        self.shader = self.root/'private.shader'
        self.shader.write_bytes(candidate())
        self.report = self.root/'private-proof.json'
        self.report.write_text(json.dumps(SOURCE_PROOF), encoding='utf-8')
        self.backup = self.root/'external-backup'

    def test_exact_identity_preflight_does_not_mutate(self):
        proof = stage(self.project,self.shader,self.report,self.backup,apply=False)
        self.assertEqual(proof['exported_exact_identity_matches'],1)
        self.assertEqual(proof['status'],
                         'SOURCE_AUTHENTIC_SPECTRUM_EXPORTED_IDENTITY_PREFLIGHT')
        self.assertFalse(self.backup.exists())
        self.assertEqual(self.meta.read_bytes(),self.meta_bytes)
        self.assertEqual(self.target.read_bytes(),self.original)
        self.assertFalse(proof['Adreno_water_pixels_proven'])

    def test_install_original_guid_preserved_and_external_backup_verified(self):
        result = stage(self.project,self.shader,self.report,self.backup,apply=True)
        self.assertEqual(result['status'],
                         'SOURCE_AUTHENTIC_SPECTRUM_EXPORTED_GUID_REPLACEMENT_STAGED')
        self.assertTrue(result['original_export_backup_external_verified'])
        self.assertEqual(self.target.read_bytes(),candidate())
        self.assertEqual(self.meta.read_bytes(),self.meta_bytes)
        self.assertEqual((self.backup/'original.shader').read_bytes(),self.original)
        self.assertEqual((self.backup/'original.shader.meta').read_bytes(),self.meta_bytes)
        self.assertFalse(result['actual_Unity2021_compilation_verified'])
        with self.assertRaisesRegex(ValueError,'external_fresh_backup_required'):
            stage(self.project,self.shader,self.report,self.backup,apply=True)

    def test_duplicate_shader_identity_is_rejected_before_writes(self):
        other=self.assets/'Duplicated.shader'
        other.write_bytes(candidate())
        with self.assertRaisesRegex(ValueError,'exactly_one_exported'):
            inspect(self.project,self.shader,self.report)
        self.assertEqual(self.target.read_bytes(),self.original)
        self.assertFalse(self.backup.exists())

    def test_unknown_export_shader_identity_is_not_replaced_or_guessed(self):
        self.target.write_text('Shader "Custom/Not Spectrum" { SubShader {} }')
        with self.assertRaisesRegex(ValueError,'exactly_one_exported'):
            stage(self.project,self.shader,self.report,self.backup,apply=True)
        self.assertFalse(self.backup.exists())

    def test_duplicate_guid_in_other_meta_rejected(self):
        (self.assets/'Other.asset.meta').write_bytes(
            b'fileFormatVersion: 2\nguid: '+b'a'*32+b'\n')
        with self.assertRaisesRegex(ValueError,'GUID_collision'):
            stage(self.project,self.shader,self.report,self.backup,apply=True)
        self.assertEqual(self.target.read_bytes(),self.original)

    def test_corrupt_or_missing_meta_blocks_before_backup(self):
        self.meta.write_bytes(b'fileFormatVersion: 2\n')
        with self.assertRaisesRegex(ValueError,'meta_guid_invalid'):
            stage(self.project,self.shader,self.report,self.backup,apply=True)
        self.assertFalse(self.backup.exists())

    def test_unverified_proof_or_changed_source_counts_fail_closed(self):
        report=json.loads(self.report.read_text())
        report['original_Material_sampler_CB0_RT_GUID_binding_proven']=True
        self.report.write_text(json.dumps(report))
        with self.assertRaisesRegex(ValueError,'source_keyword_evidence_incomplete'):
            inspect(self.project,self.shader,self.report)
        self.assertEqual(self.target.read_bytes(),self.original)

    def test_private_shader_missing_pass_or_no_real_program_is_rejected(self):
        self.shader.write_bytes(candidate(passes=6))
        with self.assertRaisesRegex(ValueError,'not_seven_complete_passes'):
            inspect(self.project,self.shader,self.report)
        self.shader.write_bytes(candidate().replace(b'HLSLPROGRAM',b'//DummyShaderTextExporter'))
        with self.assertRaisesRegex(ValueError,'not_seven_complete_passes'):
            inspect(self.project,self.shader,self.report)

    def test_private_shader_cannot_be_inside_project(self):
        self.shader=self.project/'Assets'/'staged.shader'
        self.shader.write_bytes(candidate())
        with self.assertRaisesRegex(ValueError,'original_candidate_or_proof_inside'):
            inspect(self.project,self.shader,self.report)

    def test_refuse_symlinked_export(self):
        original_target=self.target
        original_target.rename(self.assets/'Source.shader')
        original_target.symlink_to(self.assets/'Source.shader')
        with self.assertRaises(ValueError):
            inspect(self.project,self.shader,self.report)


if __name__=="__main__":
    unittest.main()
