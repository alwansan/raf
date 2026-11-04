"""B20 source-free synthetic packet tests; never use original private shaders."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import b20_private_foam_packet as packet

STATE = "SYNTHETIC FOAM RENDER STATE\n"
STAGE_BYTES = b"// synthetic source, never original\nvoid main() {}\n"


def synthetic_states(_parsed):
    return ({"original_passes": 2, "states": [
        {"index": i, "sha256": hashlib.sha256(STATE.encode()).hexdigest(),
         "bytes": len(STATE.encode())} for i in range(2)
    ]}, [STATE, STATE])


def synthetic_bridge(_parsed):
    return {
        "original_passes": 2, "authenticated_stage_count": 4,
        "matched_constant_buffer_bindings": 8,
        "referenced_cb_names_requiring_alias": 4,
        "shaderlab_cb_rebinding_installed": False,
        "unity_or_android_verified": False,
    }


def synthetic_stages(_parsed, _entries, root):
    result = []
    for index in range(4):
        key = (index // 2, 1 if index % 2 == 0 else 0)
        target = root / ("pass%d-stage%d" % key)
        target.mkdir()
        (target / "private.hlsl").write_bytes(STAGE_BYTES)
        result.append({
            "pass": key[0], "stage_code": key[1],
            "original_program_sha256": packet.ORIGINAL_STAGE_SHA[key],
            "original_spirv_valid": True, "private_hlsl_recovered": True,
            "rebuilt_spirv_valid": True,
        })
    return result


class B20FoamSourcePacketTest(unittest.TestCase):
    def _stage(self, root, *, stages=synthetic_stages, states=synthetic_states,
               bridge=synthetic_bridge):
        with mock.patch.object(packet, "ORIGINAL_STATE_SHA",
                               hashlib.sha256(STATE.encode()).hexdigest()), \
             mock.patch.object(packet, "ORIGINAL_STATE_BYTES", len(STATE.encode())):
            return packet.stage_verified(
                {"test": "synthetic"}, [], root,
                stages=stages, states=states, bridge=bridge,
            )

    def test_four_original_stage_and_two_state_packet_shapes(self):
        with tempfile.TemporaryDirectory() as path:
            result = self._stage(Path(path))
            self.assertEqual(result["original_passes"], 2)
            self.assertEqual(result["original_stage_programs"], 4)
            self.assertEqual(result["opaque_cb0_aliases_still_require_authentication"], 4)
            self.assertFalse(result["shaderlab_constructed"])
            self.assertFalse(result["unity_or_device_verified"])
            self.assertFalse(result["private_original_program_published"])
            for index in range(2):
                self.assertEqual(
                    (Path(path) / ("foam-pass-%02d-state.txt" % index)).read_text(),
                    STATE,
                )
            self.assertEqual(len(result["stage_hashes"]), 4)

    def test_stage_order_swap_rejected(self):
        def bad(parsed, entries, root):
            rows = synthetic_stages(parsed, entries, root)
            rows[0], rows[1] = rows[1], rows[0]
            return rows
        with tempfile.TemporaryDirectory() as path, self.assertRaisesRegex(ValueError, "stage"):
            self._stage(Path(path), stages=bad)

    def test_changed_original_program_digest_rejected(self):
        def bad(parsed, entries, root):
            rows = synthetic_stages(parsed, entries, root)
            rows[0]["original_program_sha256"] = "0" * 64
            return rows
        with tempfile.TemporaryDirectory() as path, self.assertRaises(ValueError):
            self._stage(Path(path), stages=bad)

    def test_invalid_translation_roundtrip_rejected(self):
        def bad(parsed, entries, root):
            rows = synthetic_stages(parsed, entries, root)
            rows[2]["rebuilt_spirv_valid"] = False
            return rows
        with tempfile.TemporaryDirectory() as path, self.assertRaises(ValueError):
            self._stage(Path(path), stages=bad)

    def test_missing_private_hlsl_is_not_staged(self):
        def bad(parsed, entries, root):
            rows = synthetic_stages(parsed, entries, root)
            (root / "pass0-stage0" / "private.hlsl").unlink()
            return rows
        with tempfile.TemporaryDirectory() as path, self.assertRaisesRegex(ValueError, "HLSL"):
            self._stage(Path(path), stages=bad)

    def test_original_opaque_cb0_alias_is_never_synthetically_completed(self):
        def bad(parsed):
            out = synthetic_bridge(parsed)
            out["referenced_cb_names_requiring_alias"] = 0
            return out
        with tempfile.TemporaryDirectory() as path, self.assertRaisesRegex(ValueError, "binding"):
            self._stage(Path(path), bridge=bad)

    def test_forged_unity_binding_status_rejected(self):
        def bad(parsed):
            out = synthetic_bridge(parsed)
            out["shaderlab_cb_rebinding_installed"] = True
            return out
        with tempfile.TemporaryDirectory() as path, self.assertRaises(ValueError):
            self._stage(Path(path), bridge=bad)

    def test_render_state_byte_drift_rejected_before_stage_generation(self):
        def bad(_parsed):
            report, states = synthetic_states(None)
            states[0] = states[0] + "corrupt"
            return report, states
        with tempfile.TemporaryDirectory() as path, self.assertRaises(ValueError):
            self._stage(Path(path), states=bad)
            self.assertFalse((Path(path) / "pass0-stage1").exists())

    def test_unlinked_path_required_for_private_programs(self):
        with tempfile.TemporaryDirectory() as path:
            original = Path(path) / "untrusted.hlsl"
            original.write_bytes(STAGE_BYTES)
            def bad(parsed, entries, root):
                rows = synthetic_stages(parsed, entries, root)
                link = root / "pass0-stage1" / "private.hlsl"
                link.unlink()
                link.symlink_to(original)
                return rows
            packet_dir = Path(path) / "packet"
            packet_dir.mkdir()
            with self.assertRaisesRegex(ValueError, "HLSL"):
                self._stage(packet_dir, stages=bad)

    def test_private_directory_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as path:
            real = Path(path) / "real"
            real.mkdir()
            (Path(path) / "alias").symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "scratch"):
                self._stage(Path(path) / "alias")


if __name__ == "__main__":
    unittest.main()
