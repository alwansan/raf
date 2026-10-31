import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from scripts.stage_fmod_android_runtime import ALLOWED, AAD, unpack, stage


class AuthenticatedRuntimeTests(unittest.TestCase):
    def seal(self, extra=None):
        files = {name: ('fixture:' + name).encode() for name in ALLOWED}
        if extra:
            files[extra] = b'unexpected'
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, data in files.items():
                z.writestr(name, data)
        key = bytes(range(32))  # PUBLIC synthetic test key only.
        nonce = bytes(range(12))
        cipher = b'RFMD1' + nonce + AESGCM(key).encrypt(nonce, stream.getvalue(), AAD)
        manifest = dict(schema=1, version='2.02.15', cipher_bytes=len(cipher),
                        cipher_sha256=hashlib.sha256(cipher).hexdigest(),
                        files={n: dict(bytes=len(d), sha256=hashlib.sha256(d).hexdigest())
                               for n, d in files.items() if n in ALLOWED})
        return cipher, key.hex(), manifest

    def test_exact_scope_roundtrip_and_idempotent_staging(self):
        cipher, key, manifest = self.seal()
        files = unpack(cipher, key, manifest)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.assertEqual(stage(root, files, True)['created_files'], 10)
            self.assertEqual(stage(root, files, True)['created_files'], 0)

    def test_wrong_key_or_tampering_refused(self):
        cipher, key, manifest = self.seal()
        with self.assertRaises(Exception):
            unpack(cipher, 'ff' * 32, manifest)
        with self.assertRaises(ValueError):
            unpack(cipher[:-1] + bytes([cipher[-1] ^ 1]), key, manifest)

    def test_traversal_and_competing_sources_refused(self):
        for extra in ('../escape', 'Assets/Plugins/FMOD/src/fmod.cs'):
            with self.subTest(extra=extra):
                cipher, key, manifest = self.seal(extra)
                with self.assertRaises(ValueError):
                    unpack(cipher, key, manifest)

    def test_manifest_revision_or_file_hash_refused(self):
        cipher, key, manifest = self.seal()
        changed = json.loads(json.dumps(manifest))
        changed['version'] = '2.02.21'
        with self.assertRaises(ValueError):
            unpack(cipher, key, changed)
        changed = json.loads(json.dumps(manifest))
        changed['files'][next(iter(ALLOWED))]['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            unpack(cipher, key, changed)

    def test_original_meta_conflict_prevents_every_write(self):
        cipher, key, manifest = self.seal()
        files = unpack(cipher, key, manifest)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            name = next(n for n in ALLOWED if n.endswith('.meta'))
            target = root / name
            target.parent.mkdir(parents=True)
            target.write_bytes(b'original meta must survive')
            with self.assertRaises(ValueError):
                stage(root, files, True)
            self.assertEqual(target.read_bytes(), b'original meta must survive')
            self.assertEqual(sum(p.is_file() for p in root.rglob('*')), 1)

    def test_outside_symlink_prevents_write(self):
        cipher, key, manifest = self.seal()
        files = unpack(cipher, key, manifest)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project, outside = root / 'project', root / 'outside'
            project.mkdir(); outside.mkdir()
            (project / 'Assets').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                stage(project, files, True)
            self.assertEqual(list(outside.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
