import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.fetch_verified_mesh_ranges import validate_manifest, install_range
from scripts.inline_verified_mesh_ranges import prepare_whole_streams
from scripts.mesh_source_files import serialized_sources


class SceneStreamTests(unittest.TestCase):
    def manifest(self):
        raw = b'original'
        chunk = {'offset': 0, 'size': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        return {'format': 1, 'max_chunk_bytes': 1024,
                'streams': {'level29.resS': {'size': len(raw), 'sha256': chunk['sha256'],
                            'restore_whole': True, 'chunks': [chunk]}}}

    def test_whole_scene_refuses_missing_prefix_and_suffix(self):
        for kind in ('prefix', 'suffix'):
            manifest = self.manifest()
            stream = manifest['streams']['level29.resS']
            if kind == 'prefix':
                stream['chunks'][0]['offset'] = 1
                stream['size'] += 1
            else:
                stream['size'] += 1
            with self.assertRaises(ValueError):
                validate_manifest(manifest)

    def test_exact_full_identity_prepared_before_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cache = root / 'cache'
            cache.mkdir()
            manifest = self.manifest()
            validate_manifest(manifest)
            chunk = manifest['streams']['level29.resS']['chunks'][0]
            install_range(cache, 'level29.resS', chunk, b'original')
            pending = []
            self.assertEqual(prepare_whole_streams(root, manifest, cache, pending), 1)
            self.assertFalse((root / 'level29.resS').exists())
            self.assertEqual(pending[0][0].read_bytes(), b'original')

    def test_selector_includes_scenes_and_registries_but_excludes_streams(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('level29', 'resources.assets', 'globalgamemanagers', 'globalgamemanagers.assets', 'level29.resS', 'Raft.exe'):
                (root / name).touch()
            self.assertEqual([p.name for p in serialized_sources(root)], ['globalgamemanagers', 'globalgamemanagers.assets', 'level29', 'resources.assets'])
