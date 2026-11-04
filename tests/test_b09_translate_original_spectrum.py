"""B09 private Spectrum 7-pass stage translation safety tests (synthetic only)."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.b09_translate_original_spectrum import translate_packet, validate_packet
from scripts.b09_spectrum_topology_contract import OWNER, PATH_ID, PASSES, BLOB_SEQUENCES
from scripts.verify_targeted_lfs_compute_sources import EXPECTED


def fixture(root):
    root = Path(root)
    repo = root / "checkout"
    packet = root / "private"
    repo.mkdir()
    packet.mkdir()
    rows = []
    for pi in range(PASSES):
        folder = packet / f"s00-p{pi:02d}"
        folder.mkdir()
        pairs = []
        for vi in range(2):
            stages = {}
            for stage, name in ((0, "progFragment"), (1, "progVertex")):
                blob = BLOB_SEQUENCES[name][2*pi+vi]
                code = f"synthetic-DXBC-stage{stage}-blob{blob}".encode()
                (folder / f"pair{vi:03d}-stage{stage}.dxbc").write_bytes(code)
                stages[str(stage)] = {"original_blob_index": blob, "sha256": hashlib.sha256(code).hexdigest(),
                                      "bytes": len(code)}
            pairs.append({"pair_index": vi, "stages": stages})
        rows.append({"subshader": 0, "pass_index": pi, "variant_pairs": pairs})
    source = {"original_owner": OWNER, "original_owner_sha256": EXPECTED[OWNER][1],
              "original_object_path_id": PATH_ID, "original_object_sha256": "a" * 64,
              "original_subshader_pass_counts": [PASSES], "private_packet_staged": True,
              "source_topology_attestation": {"authenticated_variant_stage_programs": 28},
              "stages": rows}
    manifest = root / "stage.json"
    manifest.write_text(json.dumps(source))
    return repo, packet, source, manifest, root / "translation.json"


def pass_translator(data, stage, dest):
    return {"dxbc_sha256": hashlib.sha256(data).hexdigest(),
            "vulkan11_valid": True, "hlsl_recovered": True,
            "roundtrip_vulkan11_valid": True}


class TestB09SpectrumTranslation(unittest.TestCase):
    def test_28_source_references_translate_18_original_blob_slots(self):
        with tempfile.TemporaryDirectory() as td:
            repo, packet, src, manifest, out = fixture(td)
            result = translate_packet(packet, manifest, repo, out, translator=pass_translator)
            self.assertEqual(result["original_pass_count"], 7)
            self.assertEqual(result["stage_references_verified"], 28)
            self.assertEqual(result["original_stage_blob_slots"], 18)
            self.assertEqual(result["stage_roundtrips_verified"], 18)
            self.assertFalse(result["shaderlab_reconstructed"])
            self.assertFalse(result["unity_gpu_or_device_verified"])
            self.assertNotIn("synthetic-DXBC-", out.read_text())

    def test_bad_stage_sha_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo, packet, src, manifest, out = fixture(td)
            (packet / "s00-p00/pair000-stage0.dxbc").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "size changed|SHA mismatch"):
                translate_packet(packet, manifest, repo, out, translator=pass_translator)
            self.assertFalse(out.exists())

    def test_missing_original_stage_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            _, packet, src, _, _ = fixture(td)
            (packet / "s00-p00/pair000-stage1.dxbc").unlink()
            with self.assertRaisesRegex(ValueError, "missing/size"):
                validate_packet(packet, src)

    def test_duplicate_blob_with_different_bytes_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            _, packet, src, _, _ = fixture(td)
            path = packet / "s00-p01/pair000-stage1.dxbc"
            changed = b"synthetic-different-stage"
            path.write_bytes(changed)
            stage = src["stages"][1]["variant_pairs"][0]["stages"]["1"]
            stage["bytes"], stage["sha256"] = len(changed), hashlib.sha256(changed).hexdigest()
            with self.assertRaisesRegex(ValueError, "Reused original stage blob"):
                validate_packet(packet, src)

    def test_invalid_original_blob_slot_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            _, packet, src, _, _ = fixture(td)
            src["stages"][3]["variant_pairs"][0]["stages"]["0"]["original_blob_index"] = 999
            with self.assertRaisesRegex(ValueError, "blob index"):
                validate_packet(packet, src)

    def test_missing_original_variant_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            _, packet, src, _, _ = fixture(td)
            src["stages"][0]["variant_pairs"].pop()
            with self.assertRaisesRegex(ValueError, "variant pairing"):
                validate_packet(packet, src)

    def test_source_owner_change_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            _, packet, src, _, _ = fixture(td)
            src["original_owner_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "attestation"):
                validate_packet(packet, src)

    def test_fake_stage_roundtrip_rejected_without_success_report(self):
        with tempfile.TemporaryDirectory() as td:
            repo, packet, src, manifest, out = fixture(td)
            def broken(data, stage, dest):
                return {"dxbc_sha256": hashlib.sha256(data).hexdigest(),
                        "vulkan11_valid": True, "hlsl_recovered": True,
                        "roundtrip_vulkan11_valid": False}
            with self.assertRaisesRegex(ValueError, "translation failed"):
                translate_packet(packet, manifest, repo, out, translator=broken)
            self.assertFalse(out.exists())

    def test_source_inside_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo, packet, src, manifest, out = fixture(td)
            with self.assertRaisesRegex(ValueError, "outside git checkout"):
                translate_packet(packet, manifest, repo, repo / "unsafe.json", translator=pass_translator)

    def test_symlinked_stage_packet_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo, packet, src, manifest, out = fixture(td)
            path = packet / "s00-p00/pair000-stage1.dxbc"
            real = path.with_suffix(".real")
            path.rename(real)
            path.symlink_to(real)
            with self.assertRaisesRegex(ValueError, "symlink"):
                translate_packet(packet, manifest, repo, out, translator=pass_translator)
