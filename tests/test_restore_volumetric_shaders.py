import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.restore_volumetric_shaders import (
    COMMIT, REPO, EXPECTED, NOTICE, combined_half_pass, sources, restore_project,
)


class VolumetricTests(unittest.TestCase):
    def fixture(self):
        raw = {}
        for path, (name, count) in EXPECTED.items():
            deps = ('v2fUpsample BilateralUpsample sampler_HalfResColor sampler_HalfResDepthBuffer'
                    if 'Bilateral' in path else 'source *= main.w; source.xyz += main.xyz;')
            raw[path] = ('Shader "' + name + '" { SubShader {\n// ' + deps + '\n'
                         + 'Pass {}\n' * count + '}\n}\n').encode()
        raw['LICENSE'] = b'BSD notice fixture'
        manifest = dict(repository=REPO, commit=COMMIT, files=[dict(
            path=p, bytes=len(b), git_blob=hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()
        ) for p, b in raw.items()])
        return manifest, raw

    def test_changed_bytes_fail_before_restore(self):
        manifest, raw = self.fixture()
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            sources(manifest, lambda p: raw[p] + b'x')

    def test_wrong_repository_or_revision_rejected(self):
        for key in ('repository', 'commit'):
            manifest, raw = self.fixture()
            manifest[key] = 'untrusted'
            with self.assertRaises(ValueError):
                sources(manifest, raw.__getitem__)

    def test_missing_duplicate_or_unsafe_file_rejected(self):
        manifest, raw = self.fixture()
        for rows in (manifest['files'][:-1], manifest['files'] + [manifest['files'][0]],
                     [dict(r, path='../other') if i == 0 else r for i, r in enumerate(manifest['files'])]):
            candidate = copy.deepcopy(manifest)
            candidate['files'] = rows
            with self.assertRaises(ValueError):
                sources(candidate, raw.__getitem__)

    def test_missing_pass_or_changed_composition_rejected(self):
        manifest, raw = self.fixture()
        bilateral = raw['Assets/Shaders/BilateralBlur.shader'].decode()
        blit = raw['Assets/Shaders/BlitAdd.shader'].decode()
        for b, a in ((bilateral.replace('Pass {}', '', 1), blit), (bilateral, blit.replace('main.w', '1'))):
            with self.assertRaises(ValueError):
                combined_half_pass(b, a)

    def test_preserve_all_guids_original_backups_and_binary_notice(self):
        manifest, raw = self.fixture()
        shaders, license = sources(manifest, raw.__getitem__)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            originals = {}
            for i, name in enumerate(shaders):
                path = root / 'project/Assets/Shader' / (str(i) + '.shader')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('Shader "' + name + '" { SubShader { Pass {} } }')
                meta = Path(str(path) + '.meta')
                meta.write_text('guid: original-' + str(i) + '\n')
                originals[path] = (path.read_bytes(), meta.read_bytes())
            self.assertEqual(restore_project(root / 'project', root / 'backup', shaders, license), 3)
            for path, (before, meta) in originals.items():
                self.assertEqual(Path(str(path) + '.meta').read_bytes(), meta)
                self.assertEqual((root / 'backup/Shader' / path.name).read_bytes(), before)
                self.assertIn(path.read_text(), shaders.values())
            self.assertEqual((root / 'project' / NOTICE).read_bytes(), license)

    def test_conflicting_notice_prevents_modification(self):
        manifest, raw = self.fixture()
        shaders, license = sources(manifest, raw.__getitem__)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / 'project' / NOTICE
            path.parent.mkdir(parents=True)
            path.write_bytes(b'other notice')
            with self.assertRaisesRegex(ValueError, 'notice'):
                restore_project(root / 'project', root / 'backup', shaders, license)
            self.assertFalse((root / 'backup').exists())
