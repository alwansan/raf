"""A3 isolated CPU-only audit tests for exact ZIP member spellings in APK/OBB.

Only synthetic APK/OBB fixtures. The Android ZIP URL lookup is an exact
member-name operation; PurePosixPath canonicalization is not an adequate
validator of the original raw ZIP filename.
"""
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from scripts.audit_android_expansion import audit_companion


def zip_with_members(path, members):
    with ZipFile(path, "w") as archive:
        for name, data in members:
            archive.writestr(name, data)


class A3ZipExactMemberPathTests(unittest.TestCase):
    def base(self, root, apk_extras=(), obb_extras=()):
        apk, obb = root / "game.apk", root / "main.obb"
        apk_members = [("assets/bin/Data/first", b"synthetic-APK-data"), *apk_extras]
        obb_members = [("assets/bin/Data/level1", b"synthetic-OBB-data"), *obb_extras]
        zip_with_members(apk, apk_members)
        zip_with_members(obb, obb_members)
        return apk, obb

    def test_normal_exact_member_names_still_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = self.base(Path(tmp))
            report = audit_companion(apk, obb, digest=False)
            self.assertEqual(report["obbUnityDataMembers"], 1)
            self.assertEqual(report["expansionIdentityCheck"], "unavailable")
            self.assertFalse(report["deviceMountedVerified"])

    def test_explicit_directory_entries_ending_slash_remain_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            dirs = (("assets/", b""), ("assets/bin/", b""),
                    ("assets/bin/Data/", b""))
            apk, obb = self.base(Path(tmp), apk_extras=dirs, obb_extras=dirs)
            result = audit_companion(apk, obb, digest=False)
            self.assertEqual(result["obbUnityDataMembers"], 1)

    def test_obb_dot_component_is_not_a_valid_exact_android_zip_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = self.base(Path(tmp), obb_extras=(
                ("assets/bin/Data/./level2", b"ignored-unity-scene"),))
            with self.assertRaisesRegex(ValueError, "Unsafe or duplicate"):
                audit_companion(apk, obb, digest=False)

    def test_obb_empty_component_is_not_a_valid_exact_android_zip_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = self.base(Path(tmp), obb_extras=(
                ("assets/bin/Data//level2", b"ignored-unity-scene"),))
            with self.assertRaisesRegex(ValueError, "Unsafe or duplicate"):
                audit_companion(apk, obb, digest=False)

    def test_apk_dot_component_rejected_before_unity_resource_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = self.base(Path(tmp), apk_extras=(
                ("assets/bin/Data/./unexpected", b"ignored-unity-asset"),))
            with self.assertRaisesRegex(ValueError, "Unsafe or duplicate"):
                audit_companion(apk, obb, digest=False)

    def test_apk_repeated_separator_rejected_even_with_valid_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = self.base(Path(tmp), apk_extras=(
                ("assets//bin/Data/other", b"ignored-unity-asset"),))
            with self.assertRaisesRegex(ValueError, "Unsafe or duplicate"):
                audit_companion(apk, obb, digest=False)

    def test_non_unity_zip_member_is_also_strictly_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = self.base(Path(tmp), obb_extras=(
                ("other/./member", b"unrelated-synthetic"),))
            with self.assertRaisesRegex(ValueError, "Unsafe or duplicate"):
                audit_companion(apk, obb, digest=False)

    def test_existing_traversal_rejection_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = self.base(Path(tmp), obb_extras=(
                ("assets/bin/Data/../wrong", b"bad"),))
            with self.assertRaisesRegex(ValueError, "Unsafe or duplicate"):
                audit_companion(apk, obb, digest=False)


if __name__ == "__main__":
    unittest.main()
