"""Synthetic public controls for the two-pass original Foam private pair probe."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.b20_private_foam_packet import (
    ORIGINAL_OBJECT_SHA256, ORIGINAL_STAGE_SHA, ORIGINAL_STATE_SHA,
    ORIGINAL_STATE_BYTES,
)
from scripts.b24_original_foam_stage_translation import OWNER
from scripts.w1_stage_zip2_owners import PINS
from scripts.t2_foam_original_pair_compile import (
    _exact_manifest, compile_pairs, EXPECTED,
)


def fixture(root):
    packet = root / "packet"
    packet.mkdir()
    stages = []
    for pi, sc in EXPECTED:
        directory = packet / ("pass%d-stage%d" % (pi, sc))
        directory.mkdir()
        text = "float4 main() : SV_Target { return float4(1,0,0,1); }\n"
        blob = text.encode()
        (directory / "private.hlsl").write_bytes(blob)
        stages.append({
            "pass": pi, "stage_code": sc,
            "original_dxbc_sha256": ORIGINAL_STAGE_SHA[(pi, sc)],
            "hlsl_sha256": hashlib.sha256(blob).hexdigest(),
            "hlsl_bytes": len(blob),
        })
    # The correct authenticated source-state content is deliberately not
    # available in public fixtures. Tests cannot counterfeit its digest.
    manifest = {
        "status": "private_two_pass_inputs_staged",
        "original_owner_sha256": PINS[OWNER][1],
        "original_object_sha256": ORIGINAL_OBJECT_SHA256,
        "original_passes": 2, "original_stage_programs": 4,
        "original_cb_name_slot_links_verified": 8,
        "opaque_cb0_aliases_still_require_authentication": 4,
        "render_state_sha256": ORIGINAL_STATE_SHA,
        "original_state_bytes_each": ORIGINAL_STATE_BYTES,
        "private_packet_staged": True,
        "shaderlab_constructed": False,
        "unity_or_device_verified": False,
        "water_ready": False,
        "private_original_program_published": False,
        "stage_hashes": stages,
    }
    m = root / "safe.json"
    m.write_text(json.dumps(manifest))
    return packet, m


class FoamPairedProgramControls(unittest.TestCase):
    def test_source_free_fixture_cannot_forge_original_render_state(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            with self.assertRaises(ValueError):
                _exact_manifest(packet, manifest)

    def test_missing_source_stage_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            (packet / "pass0-stage1" / "private.hlsl").unlink()
            with self.assertRaises(ValueError):
                _exact_manifest(packet, manifest)

    def test_swapped_source_stage_order_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            obj = json.loads(manifest.read_text())
            obj["stage_hashes"][0], obj["stage_hashes"][1] = (
                obj["stage_hashes"][1], obj["stage_hashes"][0]
            )
            manifest.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                _exact_manifest(packet, manifest)

    def test_wrong_original_shader_object_sha_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            obj = json.loads(manifest.read_text())
            obj["original_object_sha256"] = "0" * 64
            manifest.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                _exact_manifest(packet, manifest)

    def test_modified_hlsl_digest_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            (packet / "pass0-stage1" / "private.hlsl").write_text("tampered")
            with self.assertRaises(ValueError):
                _exact_manifest(packet, manifest)

    def test_untrusted_shaderlab_claim_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            obj = json.loads(manifest.read_text())
            obj["shaderlab_constructed"] = True
            manifest.write_text(json.dumps(obj))
            with self.assertRaises(ValueError):
                _exact_manifest(packet, manifest)

    def test_symlink_original_stage_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            stage = packet / "pass0-stage1" / "private.hlsl"
            dst = Path(d) / "public.txt"
            dst.write_bytes(stage.read_bytes())
            stage.unlink()
            stage.symlink_to(dst)
            with self.assertRaises(ValueError):
                _exact_manifest(packet, manifest)

    def test_nonexistent_compiler_cannot_claim_success(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            # Path validation occurs before running any compiler, so not even
            # a malicious always-successful fake can bypass original state SHA.
            called = []
            def fake(cmd):
                called.append(cmd)
                return True
            with self.assertRaises(ValueError):
                compile_pairs(packet, manifest, scratch=Path(d), invoke=fake)
            self.assertEqual(called, [])

    def test_scratch_inside_packet_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            packet, manifest = fixture(Path(d))
            with self.assertRaises(ValueError):
                compile_pairs(packet, manifest, scratch=packet)

    def test_public_two_pass_selector_has_four_ordered_stages(self):
        self.assertEqual(EXPECTED, ((0, 1), (0, 0), (1, 1), (1, 0)))


if __name__ == "__main__":
    unittest.main()
