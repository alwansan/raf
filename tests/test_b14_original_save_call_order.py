"""Synthetic-only controls for B14's private original-save call ordering probe."""
import unittest

from scripts.b07_probe_original_world_callbacks import fingerprint
from scripts.b14_original_save_call_order import inspect_original_text, require_authenticated_baseline


SAMPLE = """
public class SaveAndLoad {
    public void SaveGame(bool sendRemoteMessage) {
        // SteamUserStats.StoreStats(); SaveUser();
        string marker = "SaveWorld(); SteamUserStats.StoreStats();";
        SaveUser();
        SteamUserStats.StoreStats();
        SaveWorld();
    }
    private void SaveUser() { Save("private-user", new RGD()); }
    private void SaveWorld() { Save("private-world", new RGD()); }
    private void Save(string filename, RGD raftgamedata) { FileManager.CreateFile(filename); }
}
"""


class OriginalSaveCallOrderTests(unittest.TestCase):
    def inspect(self, text):
        return inspect_original_text(text, expected_sha=fingerprint(text))

    def test_original_mock_save_order_and_stats_only_guard(self):
        report = self.inspect(SAMPLE)
        self.assertEqual(report["savegame_direct_order"],
                         ["save_user", "steam_store_stats", "save_world"])
        self.assertEqual(report["savegame_user_save_calls"], 1)
        self.assertEqual(report["savegame_world_save_calls"], 1)
        self.assertEqual(report["original_user_method_save_calls"], 1)
        self.assertEqual(report["original_world_method_save_calls"], 1)
        self.assertTrue(report["original_save_uses_file_manager"])
        self.assertTrue(report["android_save_calls_preserved_in_order"])
        self.assertEqual(report["other_direct_platform_calls"],
                         {"SaveGame": 0, "SaveUser": 0, "SaveWorld": 0})
        self.assertFalse(report["rgd_written_or_reloaded"])

    def test_unknown_source_hash_fails_without_test_override(self):
        with self.assertRaisesRegex(ValueError, "SHA"):
            inspect_original_text(SAMPLE)

    def test_unexpected_extra_stats_call_fails(self):
        changed = SAMPLE.replace("SteamUserStats.StoreStats();\n        SaveWorld();",
                                 "SteamUserStats.StoreStats();\n        SteamUserStats.StoreStats();\n        SaveWorld();")
        with self.assertRaisesRegex(ValueError, "one stats"):
            self.inspect(changed)

    def test_missing_world_or_user_save_fails(self):
        for victim in ("SaveWorld();", "SaveUser();"):
            changed = SAMPLE.replace("\n        " + victim + "\n", "\n")
            with self.subTest(victim=victim), self.assertRaisesRegex(ValueError, "persistence"):
                self.inspect(changed)

    def test_order_is_observed_not_assumed(self):
        changed = SAMPLE.replace(
            "SaveUser();\n        SteamUserStats.StoreStats();\n        SaveWorld();",
            "SaveWorld();\n        SaveUser();\n        SteamUserStats.StoreStats();"
        )
        report = self.inspect(changed)
        self.assertEqual(report["savegame_direct_order"],
                         ["save_world", "save_user", "steam_store_stats"])
        self.assertTrue(report["android_save_calls_preserved_in_order"])

    def test_direct_platform_calls_outside_stats_remain_visible(self):
        changed = SAMPLE.replace('Save("private-world", new RGD());',
                                 'SteamFriends.GetPersonaName(); Save("private-world", new RGD());')
        self.assertEqual(self.inspect(changed)["other_direct_platform_calls"]["SaveWorld"], 1)

    def test_comment_and_string_platform_markers_are_ignored(self):
        report = self.inspect(SAMPLE)
        self.assertEqual(report["savegame_steam_stats_calls"], 1)
        self.assertEqual(report["other_direct_platform_calls"]["SaveGame"], 0)


    def test_authentic_provider_gate_rejects_wrong_order_or_missing_persistence(self):
        # Only the pinned real original provider must have the independently
        # observed world->user->SteamStats order. Synthetic scan remains generic.
        original = SAMPLE.replace(
            "SaveUser();\n        SteamUserStats.StoreStats();\n        SaveWorld();",
            "SaveWorld();\n        SaveUser();\n        SteamUserStats.StoreStats();"
        )
        baseline = self.inspect(original)
        self.assertTrue(require_authenticated_baseline(baseline))
        for key, value in (
            ("savegame_direct_order", ["save_user", "steam_store_stats", "save_world"]),
            ("original_world_method_save_calls", 0),
            ("original_save_uses_file_manager", False),
            ("android_save_calls_preserved_in_order", False),
        ):
            changed = dict(baseline)
            changed[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, "contract drift"):
                require_authenticated_baseline(changed)
        changed = dict(baseline)
        changed["other_direct_platform_calls"] = dict(baseline["other_direct_platform_calls"])
        changed["other_direct_platform_calls"]["SaveWorld"] = 1
        with self.assertRaisesRegex(ValueError, "contract drift"):
            require_authenticated_baseline(changed)


    def test_wrong_return_or_preprocessor_branch_fails_closed(self):
        bad = SAMPLE.replace("private void SaveWorld()", "private int SaveWorld()")
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            self.inspect(bad)
        bad = SAMPLE.replace("SaveWorld();\n", "#if UNITY_ANDROID\n        SaveWorld();\n#endif\n", 1)
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            self.inspect(bad)


if __name__ == "__main__":
    unittest.main()
