"""Synthetic Unity main/patch OBB GUID log categorization controls."""
import unittest

from scripts.t5_classify_obb_guid_logs import classify_line, classify_streams

PACKAGE = "com.alwansan.raft.androidtest"
CODE = "89"
MAIN = "main." + CODE + "." + PACKAGE + ".obb"
PATCH = "patch." + CODE + "." + PACKAGE + ".obb"
ROOT = "/storage/emulated/0/Android/obb/" + PACKAGE + "/"
FIXTURE = {
    "package": PACKAGE,
    "version_code": CODE,
    "files": [
        {"name": "Raft-Android-Test.apk"},
        {"name": MAIN},
        {"name": "Raft-Android-Test.xapk"},
    ],
}


def warning(name, parent=PACKAGE):
    return "2026-11-05 23:01:38.651630 E Unity: Unable to load GUID for '" + (
        "/storage/emulated/0/Android/obb/" + parent + "/" + name) + "'\n"


class ObbGuidTests(unittest.TestCase):
    def category(self, line, files=None):
        return classify_line(line, code=CODE, logical_files=set(files or (
            "Raft-Android-Test.apk", MAIN, "Raft-Android-Test.xapk")))

    def test_actual_warning_shape_patch_not_shipped(self):
        self.assertEqual(self.category(warning(PATCH)), "optional_patch_probe_not_packaged")

    def test_main_is_a_real_guid_warning(self):
        self.assertEqual(self.category(warning(MAIN)), "declared_main_obb_guid_warning")

    def test_declared_patch_is_not_optional_unshipped(self):
        self.assertEqual(self.category(warning(PATCH), files=(MAIN, PATCH)),
                         "declared_patch_obb_guid_warning")

    def test_foreign_version_is_not_our_optional_patch(self):
        self.assertEqual(self.category(warning("patch.88."+PACKAGE+".obb")),
                         "foreign_or_different_version_obb_guid_warning")

    def test_foreign_filename_package_is_not_our_patch(self):
        self.assertEqual(self.category(warning("patch.89.com.other.game.obb")),
                         "foreign_or_different_version_obb_guid_warning")

    def test_foreign_parent_is_not_our_patch(self):
        self.assertEqual(self.category(warning(PATCH, parent="com.other.app")),
                         "foreign_or_different_version_obb_guid_warning")

    def test_arbitrary_guid_error_is_not_an_android_obb(self):
        self.assertEqual(self.category("Unity: Unable to load GUID for '/data/local/tmp/test.asset'\n"),
                         "other_guid_warning")

    def test_other_unity_render_error_ignored(self):
        self.assertIsNone(self.category("Unity: Shader missing pass for UltimateWater\n"))

    def test_three_original_shapes_in_two_sessions(self):
        summary = classify_streams([[warning(PATCH)], [warning(PATCH), warning(PATCH)]],
                                   delivery=FIXTURE)
        self.assertEqual(summary["total_guid_warning_lines"], 3)
        self.assertEqual(summary["log_segments_processed"], 2)
        self.assertEqual(summary["main_obb_guid_warning_count"], 0)
        self.assertEqual(summary["optional_patch_lookup_not_packaged_count"], 3)
        self.assertFalse(summary["actual_device_main_obb_mount_verified"])
        self.assertFalse(summary["patch_file_physically_absent_on_device_proven"])

    def test_main_warning_is_never_suppressed(self):
        summary = classify_streams([[warning(MAIN), warning(PATCH)]], delivery=FIXTURE)
        self.assertEqual(summary["main_obb_guid_warning_count"], 1)
        self.assertEqual(summary["total_guid_warning_lines"], 2)
        self.assertFalse(summary["unity_warning_suppressed"])

    def test_manifest_must_contain_main(self):
        data = dict(FIXTURE, files=[{"name": "Raft-Android-Test.apk"}])
        with self.assertRaisesRegex(ValueError, "required MAIN"):
            classify_streams([[warning(PATCH)]], delivery=data)

    def test_manifest_must_match_package(self):
        data = dict(FIXTURE, package="com.other")
        with self.assertRaisesRegex(ValueError, "Invalid original"):
            classify_streams([[]], delivery=data)

    def test_repeated_logical_file_rejected(self):
        data = dict(FIXTURE, files=[{"name": MAIN}, {"name": MAIN}])
        with self.assertRaisesRegex(ValueError, "Unsafe or repeated"):
            classify_streams([[]], delivery=data)

    def test_traversal_delivery_filename_rejected(self):
        data = dict(FIXTURE, files=[{"name": MAIN}, {"name": "../secret"}])
        with self.assertRaisesRegex(ValueError, "Unsafe or repeated"):
            classify_streams([[]], delivery=data)

    def test_invalid_version_code_rejected(self):
        data = dict(FIXTURE, version_code="../89")
        with self.assertRaisesRegex(ValueError, "Invalid original"):
            classify_streams([[]], delivery=data)

    def test_wrong_raw_line_type_rejected(self):
        with self.assertRaisesRegex(ValueError, "Log line must be text"):
            self.category(None)


if __name__ == "__main__":
    unittest.main()
