from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from scripts.gt_install_fft_utilities_original import install
from scripts.gt_fft_utilities_restore import STATUS as SOURCE_STATUS, TARGET


class FFTInstallation(unittest.TestCase):
    def fixture(self, root):
        project=root/'project';assets=project/'Assets';assets.mkdir(parents=True)
        target=assets/'Original.shader';meta=assets/'Original.shader.meta'
        target.write_text('Shader "'+TARGET+'" {} // DummyShaderTextExporter\n')
        meta.write_text('fileFormatVersion: 2\nguid: '+'a'*32+'\n')
        (assets/'Unrelated.mat').write_bytes(b'original material')
        (project/'unchanged.txt').write_bytes(b'outside Assets')
        candidate=('Shader "'+TARGET+'" { SubShader {\n'+''.join(
            'Pass {\nHLSLPROGRAM\n#pragma vertex v\n#pragma fragment f\nvoid v(){}\nvoid f(){}\nENDHLSL\n}\n' for _ in range(7))+'}}\n').encode()
        digest=sha256(candidate).hexdigest()
        source=dict(status=SOURCE_STATUS,candidate_shader_sha256=digest,original_SHA_owned_serialized_files=2,
            original_passes=7,original_keyword_pairs=7,original_orphan_stages=0,original_distinct_D3D11_programs=12,
            original_stages_roundtrip_validated=12,named_ShaderLab_entrypoints_compiled=14)
        unity=dict(unityVersion='2021.3.45f2',candidateSha256=digest,passCount=7,registeredKeywordVariants=1,
            errors=0,androidVulkanOnly=True,privateBundleCompiled=True,gamePlayerBuilt=False,devicePixelsProven=False)
        bundle=dict(candidate_sha256=digest,compiled_program_table_verified=True,
            vertex_and_fragment_entrypoints_verified=True,vulkan_platform_only=True,
            engine_keywords_verified=False,vertex_routes_by_pass=[1]*7,fragment_routes_by_pass=[1]*7)
        key=('resources.assets',123)
        trace=dict(schema_version=1,export_instance='b'*32,objects=[dict(class_id=48,
            source=dict(owner=key[0],path_id=key[1]),export=dict(file_id=4800000,guid='a'*32,type=3))])
        return project,target,meta,key,trace,candidate,source,unity,bundle

    def test_installs_only_exact_traced_shader_and_preserves_original_meta(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);project,target,meta,key,trace,candidate,source,unity,bundle=self.fixture(root)
            before={p.relative_to(project):p.read_bytes() for p in project.rglob('*') if p.is_file()}
            result=install(project,trace,key,candidate,source,unity,bundle,root/'backup')
            self.assertTrue(result.get('original_export_guid_preserved'))
            self.assertEqual(target.read_bytes(),candidate)
            for relative,data in before.items():
                if project/relative != target:self.assertEqual((project/relative).read_bytes(),data)
            self.assertEqual((root/'backup/original.shader').read_bytes(),before[target.relative_to(project)])
            self.assertEqual((root/'backup/original.shader.meta').read_bytes(),before[meta.relative_to(project)])

    def test_wrong_candidate_sha_guid_trace_and_source_only_receipt_rejected(self):
        mutations=[lambda x:x[5].update(candidate_sha256='0'*64),
            lambda x:x[5].update(export_guid='c'*32),
            lambda x:x[1]['objects'][0]['source'].update(path_id=456),
            lambda x:x[4].update(privateBundleCompiled=False),
            lambda x:x[5].update(vertex_and_fragment_entrypoints_verified=False)]
        for mutation in mutations:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);project,target,meta,key,trace,candidate,source,unity,bundle=self.fixture(root)
                values=[key,trace,candidate,source,unity,bundle];mutation(values)
                previous=target.read_bytes()
                with self.assertRaises(ValueError):install(project,trace,key,candidate,source,unity,bundle,root/'backup')
                self.assertEqual(target.read_bytes(),previous)
                self.assertFalse((root/'backup').exists())

    def test_duplicate_trace_wrong_meta_and_internal_backup_are_rejected(self):
        for case in ('duplicate','meta','backup'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);project,target,meta,key,trace,candidate,source,unity,bundle=self.fixture(root)
                backup=root/'backup'
                if case=='duplicate':trace['objects'].append(deepcopy(trace['objects'][0]))
                if case=='meta':meta.write_text('guid: '+'d'*32+'\n')
                if case=='backup':backup=project/'backup'
                original=target.read_bytes()
                with self.assertRaises(ValueError):install(project,trace,key,candidate,source,unity,bundle,backup)
                self.assertEqual(target.read_bytes(),original)
                self.assertFalse(backup.exists())

    def test_failed_postwrite_verification_rolls_shader_back(self):
        from unittest.mock import patch
        from scripts import gt_install_fft_utilities_original as impl
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);project,target,meta,key,trace,candidate,source,unity,bundle=self.fixture(root)
            original=target.read_bytes();metadata=meta.read_bytes()
            snapshot=impl.snapshot;calls=[]
            def corrupted_snapshot(path):
                result=snapshot(path);calls.append(1)
                if len(calls)==2:result['unchanged.txt']=(0,'0'*64)
                return result
            with patch.object(impl,'snapshot',side_effect=corrupted_snapshot):
                with self.assertRaisesRegex(ValueError,'unrelated_export'):
                    install(project,trace,key,candidate,source,unity,bundle,root/'backup')
            self.assertEqual(target.read_bytes(),original)
            self.assertEqual(meta.read_bytes(),metadata)
            self.assertEqual((root/'backup/original.shader').read_bytes(),original)
