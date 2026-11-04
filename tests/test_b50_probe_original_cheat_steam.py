"""B50 synthetic-only original Steam identity probe guard tests."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.b50_probe_original_cheat_steam import authenticated, probe


def original_fixture():
    return (
        "public class Cheat {\n"
        "  // SteamUser.GetSteamID(); is not an executable native call\n"
        "  private bool AllowCheatsForLocalPlayer() {\n"
        '    string help = "SteamUser.GetSteamID()";\n'
        "    if (CanPlay()) { var user = SteamUser.GetSteamID(); return user.IsValid(); }\n"
        "    return false;\n"
        "  }\n"
        "  private void Other() { SteamUser.GetSteamID(); }\n"
        "}\n"
    )


class B50CheatSteamProbeTests(unittest.TestCase):
    def setup_tree(self, root, source=original_fixture(), managed=b"synthetic-dll"):
        extracted = root / "original"
        extracted.mkdir()
        cheat = extracted / "Cheat.cs"
        cheat.write_text(source)
        original = root / "Assembly-CSharp.dll"
        original.write_bytes(managed)
        return extracted, original, len(managed), hashlib.sha256(managed).hexdigest()

    def test_original_method_only_executable_steam_calls_count(self):
        with tempfile.TemporaryDirectory() as temp:
            source, dll, size, sha = self.setup_tree(Path(temp))
            x = probe(source, dll, expected_bytes=size, expected_sha=sha)
            self.assertTrue(x["method_returns_bool"])
            self.assertEqual(x["direct_steam_getid_calls"], 1)
            self.assertEqual(x["other_steam_named_tokens"], 1)
            self.assertFalse(x["world_load_verified"])
            self.assertFalse(x["source_changed"])
            self.assertNotIn("SteamUser.GetSteamID", str(x))

    def test_authentic_provider_refuses_wrong_length_and_digest(self):
        with tempfile.TemporaryDirectory() as temp:
            source, dll, size, sha = self.setup_tree(Path(temp))
            with self.assertRaisesRegex(ValueError, "exact bytes"):
                authenticated(dll, expected_bytes=size + 1, expected_sha=sha)
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                authenticated(dll, expected_bytes=size, expected_sha="0" * 64)
            dll.unlink()
            with self.assertRaisesRegex(ValueError, "not exact bytes"):
                authenticated(dll, expected_bytes=size, expected_sha=sha)

    def test_ambiguous_or_linked_cheat_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, dll, size, sha = self.setup_tree(root)
            (source / "nested").mkdir()
            (source / "nested" / "Cheat.cs").write_text(original_fixture())
            with self.assertRaisesRegex(ValueError, "unique"):
                probe(source, dll, expected_bytes=size, expected_sha=sha)
            (source / "nested" / "Cheat.cs").unlink()
            (source / "Cheat.cs").unlink()
            try:
                (source / "Cheat.cs").symlink_to(root / "unrelated")
            except (OSError, NotImplementedError):
                self.skipTest("Symlinks unavailable")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                probe(source, dll, expected_bytes=size, expected_sha=sha)

    def test_quoted_or_commented_calls_do_not_count(self):
        empty = original_fixture().replace(
            "var user = SteamUser.GetSteamID(); return user.IsValid();",
            'string line = "SteamUser.GetSteamID()"; return true;')
        with tempfile.TemporaryDirectory() as temp:
            source, dll, size, sha = self.setup_tree(Path(temp), source=empty)
            x = probe(source, dll, expected_bytes=size, expected_sha=sha)
            self.assertEqual(x["direct_steam_getid_calls"], 0)

    def test_duplicate_declared_original_method_refused(self):
        sample = original_fixture().replace(
            "  private void Other()",
            "  private bool AllowCheatsForLocalPlayer() { return true; }\n  private void Other()")
        with tempfile.TemporaryDirectory() as temp:
            source, dll, size, sha = self.setup_tree(Path(temp), source=sample)
            with self.assertRaisesRegex(ValueError, "Expected one original"):
                probe(source, dll, expected_bytes=size, expected_sha=sha)


if __name__ == "__main__":
    unittest.main()
