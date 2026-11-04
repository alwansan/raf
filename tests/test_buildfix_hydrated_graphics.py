import hashlib
from pathlib import Path
import tempfile
import unittest
from scripts.hydrate_render_payloads import missing_payloads

class HydratedGraphicsTests(unittest.TestCase):
    def test_verified_and_same_size_tampered(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'owner'
            p.write_bytes(b'original')
            row=(str(p),hashlib.sha256(b'original').hexdigest(),8)
            self.assertEqual(missing_payloads([row]),[])
            p.write_bytes(b'tampered')
            self.assertEqual(missing_payloads([row]),[row])

    def test_missing_truncated_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'owner'
            row=(str(p),hashlib.sha256(b'original').hexdigest(),8)
            self.assertEqual(missing_payloads([row]),[row])
            p.write_bytes(b'x')
            self.assertEqual(missing_payloads([row]),[row])
            target=Path(tmp)/'target'
            target.write_bytes(b'original')
            p.unlink()
            p.symlink_to(target)
            with self.assertRaises(ValueError):
                missing_payloads([row])
