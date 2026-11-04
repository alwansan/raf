"""B24: SHA-locked parity between native world tracing and cheap managed CI."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from scripts.adapt_android_offline_startup import fingerprint
from scripts.verify_android_offline_candidate import (
    include_original_trace_only_sources, install_adapted_originals,
)


class OriginalWorldTraceParityTests(unittest.TestCase):
    def test_manifest_pins_original_world_callback(self):
        from scripts.b07_probe_original_world_callbacks import ORIGINAL_GAME_MANAGER_SHA256
        manifest = json.loads(Path("config/runtime-operation-traces.json").read_text())
        original = manifest["sources"]["GameManager"]
        self.assertEqual(original["sha256"], ORIGINAL_GAME_MANAGER_SHA256)
        self.assertEqual([x["name"] for x in original["methods"]], ["OnWorldRecieved"])

    def test_trace_only_source_selected_while_preserving_adapted_and_sdk_sources(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "Assembly-CSharp" / "GameManager.cs"
            sdk = root / "SDK" / "GameManager.cs"
            game.parent.mkdir()
            sdk.parent.mkdir()
            original = "class GameManager { void OnWorldRecieved() {} }"
            game.write_text(original)
            sdk.write_text("class GameManager { void VendorMethod() {} }")
            previous = {"SaveAndLoad": (root / "SaveAndLoad.cs", "adapted save")}
            traces = {"sources": {"GameManager": {"sha256": fingerprint(original)}}}
            selected = include_original_trace_only_sources(root, previous, traces)
            self.assertEqual(selected["GameManager"], (game, original))
            self.assertIs(selected["SaveAndLoad"], previous["SaveAndLoad"])
            self.assertNotIn("VendorMethod", selected["GameManager"][1])

    def test_missing_or_duplicate_authentic_game_manager_rejected_without_partial_selection(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            root.joinpath("A").mkdir()
            root.joinpath("B").mkdir()
            content = "class GameManager {}"
            traces = {"sources": {"GameManager": {"sha256": fingerprint(content)}}}
            previous = {"SaveAndLoad": (root / "SaveAndLoad.cs", "save")}
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                include_original_trace_only_sources(root, previous, traces)
            self.assertEqual(list(previous), ["SaveAndLoad"])
            root.joinpath("A", "GameManager.cs").write_text(content)
            root.joinpath("B", "GameManager.cs").write_text(content)
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                include_original_trace_only_sources(root, previous, traces)
            self.assertEqual(list(previous), ["SaveAndLoad"])

    def test_trace_only_install_instruments_original_and_preserves_meta(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "GameManager.cs"
            original = "class GameManager { void OnWorldRecieved() { SaveGame(); } }"
            game.write_text(original)
            meta = root / "GameManager.cs.meta"
            meta.write_bytes(b"guid: original-and-preserved\n")
            traces = {"sources": {"GameManager": {"sha256": fingerprint(original)}}}
            changed = include_original_trace_only_sources(root, {}, traces)
            with patch.dict("scripts.verify_android_offline_candidate.PINS", {}, clear=True):
                with patch("scripts.verify_android_offline_candidate.instrument",
                           side_effect=lambda name, text, manifest: text + "\n// traced world"):
                    install_adapted_originals(changed, traces)
            self.assertIn("// traced world", game.read_text())
            self.assertEqual(meta.read_bytes(), b"guid: original-and-preserved\n")

    def test_changed_trace_only_source_refused_before_any_write(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            game = root / "GameManager.cs"
            game.write_text("class GameManager { void OnWorldRecieved() {} }")
            old = game.read_text()
            traces = {"sources": {"GameManager": {"sha256": fingerprint(old)}}}
            changed = include_original_trace_only_sources(root, {}, traces)
            game.write_text("class GameManager { void OnWorldRecieved() { Bad(); } }")
            with patch.dict("scripts.verify_android_offline_candidate.PINS", {}, clear=True):
                with self.assertRaisesRegex(ValueError, "changed after SHA selection"):
                    install_adapted_originals(changed, traces)
            self.assertIn("Bad();", game.read_text())

    def test_unregistered_trace_only_source_must_not_be_installed(self):
        with TemporaryDirectory() as temp:
            path = Path(temp) / "GameManager.cs"
            path.write_text("class GameManager {}")
            with patch.dict("scripts.verify_android_offline_candidate.PINS", {}, clear=True):
                with self.assertRaisesRegex(ValueError, "Unregistered original trace-only"):
                    install_adapted_originals({"GameManager": (path, "replacement")}, {"sources": {}})
            self.assertEqual(path.read_text(), "class GameManager {}")


if __name__ == "__main__":
    unittest.main()
