"""A10 synthetic-only SHA-identity regression cases; no original game source or Unity."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.adapt_android_offline_startup import fingerprint
from scripts.verify_android_offline_candidate import select_original_source, install_adapted_originals


class OriginalSourceSelectionTests(unittest.TestCase):
    def test_sdk_homonym_does_not_obscure_game_source(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = "class SaveAndLoad { void Save() {} }\n"
            game = root / "ILSpy" / "SaveAndLoad.cs"
            sdk = root / "Vendor" / "SaveAndLoad.cs"
            game.parent.mkdir()
            sdk.parent.mkdir()
            game.write_text(code)
            sdk.write_text("class SaveAndLoad { void Sdk() {} }")
            self.assertEqual(select_original_source(root, "SaveAndLoad", fingerprint(code)), (game, code))
            self.assertIn("Sdk", sdk.read_text())

    def test_unpinned_candidate_rejected(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SaveAndLoad.cs"
            path.write_text("unrelated source")
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                select_original_source(Path(tmp), "SaveAndLoad", fingerprint("genuine"))
            self.assertEqual(path.read_text(), "unrelated source")

    def test_two_matching_sources_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for directory in ("A", "B"):
                path = root / directory / "SaveAndLoad.cs"
                path.parent.mkdir()
                path.write_text("same original")
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                select_original_source(root, "SaveAndLoad", fingerprint("same original"))

    def test_symlinked_source_is_not_followed(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "external.cs"
            target.write_text("genuine")
            link = root / "SaveAndLoad.cs"
            try:
                link.symlink_to(target)
            except (NotImplementedError, OSError):
                self.skipTest("File symlink unavailable")
            with self.assertRaisesRegex(ValueError, "SHA-pinned original"):
                select_original_source(root, "SaveAndLoad", fingerprint("genuine"))
            self.assertEqual(target.read_text(), "genuine")

    def test_bom_crlf_normalization_does_not_write_source(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "SaveAndLoad.cs"
            raw = b"\xef\xbb\xbfclass SaveAndLoad {\r\n}\r\n"
            path.write_bytes(raw)
            normalized = "class SaveAndLoad {\n}\n"
            self.assertEqual(select_original_source(Path(tmp), "SaveAndLoad", fingerprint(normalized)), (path, normalized))
            self.assertEqual(path.read_bytes(), raw)

    def test_undecodable_sdk_homonym_ignored(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            root.joinpath("Game").mkdir()
            root.joinpath("SDK").mkdir()
            original = root / "Game" / "SaveAndLoad.cs"
            sdk = root / "SDK" / "SaveAndLoad.cs"
            original.write_text("genuine")
            sdk.write_bytes(b"\xff\x80")
            self.assertEqual(select_original_source(root, "SaveAndLoad", fingerprint("genuine")), (original, "genuine"))
            self.assertEqual(sdk.read_bytes(), b"\xff\x80")


class OriginalManagedInstallIntegrityTests(unittest.TestCase):
    """Only artificial source bytes: validate the original-private CI prepare gate."""

    def test_late_harness_failure_never_modifies_original_sources(self):
        """Private ILSpy originals must not change if late RPC extraction fails."""
        from unittest.mock import patch
        from scripts.verify_android_offline_candidate import prepare

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "decompiled"
            runtime = root / "runtime"
            source.mkdir()
            runtime.mkdir()
            original_network = b"// no RPC signature in synthetic source\nclass Raft_Network {}\n"
            original_save = b"\xef\xbb\xbfclass SaveAndLoad {}\r\n"
            network = source / "Raft_Network.cs"
            save = source / "SaveAndLoad.cs"
            network.write_bytes(original_network)
            save.write_bytes(original_save)
            for name in (
                "AndroidStreamingAssets.cs", "TouchPointerGesture.cs",
                "TouchPointerButtons.cs", "AndroidTouchPointer.cs",
                "AndroidTouchUiPanel.cs", "LocalPlayerIdentity.cs",
                "LocalProfileStore.cs", "AndroidTestDiagnostics.cs",
                "AndroidTouchGamepadOverlay.cs", "PersistentDiagnosticLog.cs",
                "AndroidRuntimeLog.cs",
            ):
                (runtime / name).write_text("// synthetic runtime helper")
            pins = {
                "Raft_Network": fingerprint(network.read_text(encoding="utf-8-sig")),
                "SaveAndLoad": fingerprint(save.read_text(encoding="utf-8-sig")),
            }
            with patch.dict("scripts.verify_android_offline_candidate.PINS", pins, clear=True):
                with patch("scripts.verify_android_offline_candidate.adapt", side_effect=lambda name, text: text):
                    with patch("scripts.verify_android_offline_candidate.adapt_paths", side_effect=lambda text: text):
                        with patch("scripts.verify_android_offline_candidate.instrument", side_effect=lambda name, text, manifest: text + "\n// synthetic wrapped"):
                            with self.assertRaises(ValueError):
                                prepare(source, root / "managed", runtime, root / "output")
            self.assertEqual(network.read_bytes(), original_network)
            self.assertEqual(save.read_bytes(), original_save)

    def test_later_instrumentation_failure_preserves_all_source_bytes(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            one, two = root / "One.cs", root / "Two.cs"
            # Use an explicit ordinary second original to model a late guard failure.
            raw_one = b"\xef\xbb\xbfclass One {}\r\n"
            one.write_bytes(raw_one)
            two.write_bytes(b"class Two {}\n")
            original_meta = root / "One.cs.meta"
            original_meta.write_bytes(b"guid: original\n")
            pins = {"One": fingerprint(one.read_text(encoding="utf-8-sig")),
                    "Two": fingerprint(two.read_text())}
            changed = {"One": (one, "class One { /* adapted */ }"),
                       "Two": (two, "class Two { /* adapted */ }")}

            def guard(name, value, manifest):
                if name == "Two":
                    raise ValueError("Synthetic original operation signature drift")
                return value + "\n/* instrumented */"

            with patch.dict("scripts.verify_android_offline_candidate.PINS", pins, clear=True):
                with patch("scripts.verify_android_offline_candidate.instrument", side_effect=guard):
                    with self.assertRaisesRegex(ValueError, "signature drift"):
                        install_adapted_originals(changed, {"sources": {"One": {}, "Two": {}}})
            self.assertEqual(one.read_bytes(), raw_one)
            self.assertEqual(two.read_bytes(), b"class Two {}\n")
            self.assertEqual(original_meta.read_bytes(), b"guid: original\n")

    def test_second_write_error_rolls_back_both_originals(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            first, last = root / "One.cs", root / "Two.cs"
            before_first = b"\xef\xbb\xbfclass One {}\r\n"
            before_last = b"class Two {}\n"
            first.write_bytes(before_first)
            last.write_bytes(before_last)
            changed = {"One": (first, "class One { adapted; }"),
                       "Two": (last, "class Two { adapted; }")}
            pins = {"One": fingerprint(first.read_text(encoding="utf-8-sig")),
                    "Two": fingerprint(last.read_text())}
            real_write = Path.write_bytes

            def fail_mid_write(target, payload):
                if target == last and payload == b"class Two { adapted; }":
                    real_write(target, payload[:4])  # Simulate a truncated write.
                    raise OSError("Synthetic disk write error")
                return real_write(target, payload)

            with patch.dict("scripts.verify_android_offline_candidate.PINS", pins, clear=True):
                with patch.object(Path, "write_bytes", fail_mid_write):
                    with self.assertRaisesRegex(OSError, "disk write error"):
                        install_adapted_originals(changed, {"sources": {}})
            self.assertEqual(first.read_bytes(), before_first)
            self.assertEqual(last.read_bytes(), before_last)

    def test_successful_preflight_replaces_exactly_selected_originals(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            one, two = root / "One.cs", root / "Two.cs"
            one.write_text("original one")
            two.write_text("original two")
            meta = root / "One.cs.meta"
            meta.write_bytes(b"guid: retained\n")
            third = root / "Sdk.cs"
            third.write_text("untouched SDK")
            pins = {"One": fingerprint("original one"),
                    "Two": fingerprint("original two")}
            changed = {"One": (one, "adapted one"), "Two": (two, "adapted two")}
            with patch.dict("scripts.verify_android_offline_candidate.PINS", pins, clear=True):
                install_adapted_originals(changed, {"sources": {}})
            self.assertEqual(one.read_text(), "adapted one")
            self.assertEqual(two.read_text(), "adapted two")
            self.assertEqual(meta.read_bytes(), b"guid: retained\n")
            self.assertEqual(third.read_text(), "untouched SDK")

    def test_original_source_change_after_sha_selection_fails_before_writing(self):
        from unittest.mock import patch
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            one = root / "One.cs"
            one.write_text("unexpected newer source")
            with patch.dict("scripts.verify_android_offline_candidate.PINS",
                            {"One": fingerprint("previous original")}, clear=True):
                with self.assertRaisesRegex(ValueError, "changed after SHA selection"):
                    install_adapted_originals({"One": (one, "adapted")}, {"sources": {}})
            self.assertEqual(one.read_text(), "unexpected newer source")


if __name__ == "__main__":
    unittest.main()
