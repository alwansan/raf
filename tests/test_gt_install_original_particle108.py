import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import gt_install_original_particle108 as install


class Particle108InstallerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        self.assets = root / "Project/Assets"
        self.assets.mkdir(parents=True)
        self.shader = self.assets / "Exported.shader"
        self.original = b'Shader "Fixture/Particle" {\n//DummyShaderTextExporter\n}\n'
        self.shader.write_bytes(self.original)
        self.meta = self.assets / "Exported.shader.meta"
        self.guid = "1" * 32
        self.metadata = f"fileFormatVersion: 2\nguid: {self.guid}\nShaderImporter: {{}}\n".encode()
        self.meta.write_bytes(self.metadata)
        self.source_key = ("sharedassets0.assets", 17)
        self.trace = {
            "schema_version": 1,
            "export_instance": "2" * 32,
            "objects": [{
                "class_id": 48,
                "source": {"owner": self.source_key[0], "path_id": self.source_key[1]},
                "export": {"file_id": 4800000, "guid": self.guid, "type": 3},
            }],
        }
        self.candidate = root / "Candidate.shader"
        self.candidate.write_text(
            'Shader "Fixture/Particle" {\nSubShader {\nPass {\nHLSLPROGRAM\n'
            '#pragma multi_compile __ KEY_A\n#pragma multi_compile __ KEY_B\n'
            '#pragma vertex main\n#pragma fragment main\nENDHLSL\n}\n}\n}\n'
        )
        self.source = root / "Source.json"
        self.unity = root / "Unity.json"
        self.trace_file = root / "W1.json"
        self.backup = root / "Backup"
        self.trace_file.write_text(json.dumps(self.trace))
        self.digest = hashlib.sha256(self.candidate.read_bytes()).hexdigest()
        self.source.write_text(json.dumps(
            dict(install.SOURCE_PROOF, candidate_shader_sha256=self.digest)
        ))
        self.unity.write_text(json.dumps(dict(
            install.UNITY_PROOF, candidateShaderSha256=self.digest, privateBundleBytes=128
        )))

    def test_guid_alias_to_another_asset_is_rejected(self):
        (self.assets / "Other.asset.meta").write_bytes(self.metadata)
        with self.assertRaisesRegex(ValueError, "does_not_identify_one_exported_shader"):
            install.traced_shader(self.assets, self.trace, self.source_key)

    def test_unity_proof_must_cover_exact_candidate_bytes(self):
        self.candidate.write_text(self.candidate.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "candidate_proof_digest_mismatch"):
            install.candidate_bytes(self.candidate, self.source, self.unity)

    def test_preflight_then_apply_preserves_guid_and_keeps_rollback_bytes(self):
        args = (Path("Original"), Path("Manifest"), self.assets.parent, self.trace_file,
                self.candidate, self.source, self.unity, self.backup)
        with (patch.object(install, "load_original"), patch.object(
                install, "select", return_value=self.source_key)):
            before = install.stage(*args)
            self.assertTrue(before["status"].endswith("PREFLIGHT"))
            self.assertEqual(self.shader.read_bytes(), self.original)
            self.assertFalse(self.backup.exists())
            result = install.stage(*args, apply=True)
            self.assertTrue(result["status"].endswith("INSTALLED"))
            self.assertEqual(self.shader.read_bytes(), self.candidate.read_bytes())
            self.assertEqual(self.meta.read_bytes(), self.metadata)
            self.assertEqual((self.backup / "original.shader").read_bytes(), self.original)
            again = install.stage(*args, apply=True)
            self.assertTrue(again["status"].endswith("ALREADY_INSTALLED"))
