"""Source-free GFX142 AES-GCM CMS owner delivery regression tests."""
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest

from gfxlab.tools.gfx142_owner_envelope import encrypt_private_apk, digest


class OwnerEnvelopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.key = cls.root / "test-private.pem"
        cls.cert = cls.root / "test-public.pem"
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-nodes", "-keyout", str(cls.key), "-out", str(cls.cert),
            "-days", "1", "-subj", "/CN=GFX142 Synthetic",
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cls.fake_apk = cls.root / "synthetic.apk"
        cls.fake_apk.write_bytes(os.urandom(1_000_005))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def encrypt(self, name):
        return encrypt_private_apk(self.fake_apk, self.cert, self.root / name)

    def decrypt(self, name, output):
        return subprocess.run([
            "openssl", "cms", "-decrypt", "-inform", "DER",
            "-in", str(self.root / name),
            "-recip", str(self.cert), "-inkey", str(self.key),
            "-out", str(self.root / output),
        ], capture_output=True, check=False)

    def test_authenticated_private_payload_round_trip(self):
        name = "one.cms"
        evidence = self.encrypt(name)
        self.assertEqual(evidence["encrypted_apk_sha256"], digest(self.root / name))
        self.assertTrue(evidence["private_owner_delivery_encrypted_only"])
        self.assertEqual(self.decrypt(name, "one.dec").returncode, 0)
        self.assertEqual(digest(self.root / "one.dec"), digest(self.fake_apk))

    def test_gcm_rejects_modified_encrypted_payload(self):
        name = "tampered.cms"
        self.encrypt(name)
        b = bytearray((self.root / name).read_bytes())
        b[-2] ^= 1
        (self.root / name).write_bytes(b)
        self.assertNotEqual(self.decrypt(name, "tampered.dec").returncode, 0)

    def test_refuses_existing_output(self):
        self.encrypt("repeated.cms")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.encrypt("repeated.cms")

    def test_refuses_missing_certificate(self):
        with self.assertRaisesRegex(ValueError, "certificate"):
            encrypt_private_apk(self.fake_apk, self.root / "missing.pem",
                                self.root / "missing.cms")

    def test_refuses_small_file(self):
        small = self.root / "small.apk"
        small.write_bytes(b"synthetic")
        with self.assertRaisesRegex(ValueError, "small"):
            encrypt_private_apk(small, self.cert, self.root / "small.cms")


if __name__ == "__main__":
    unittest.main()
