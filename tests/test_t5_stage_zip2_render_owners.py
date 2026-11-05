"""T5 original ZIP2 render owner bridge: independent tiny Git/split fixtures.

Never downloads proprietary files. Real immutable ZIP2 input is checked by
raft-t5-zip2-render-stage.yml separately. No Unity or device proof here.
"""
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import t5_stage_zip2_render_owners as bridge


class ZIP2RenderStageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "zip2"
        self.repo.mkdir()
        self._git("init", "-q")
        self.relative = "Raft_Data/resources.assets"
        self.owner = "Raft/" + self.relative
        self.parts = [b"abcdefgh", b"12345678", b"end"]
        self.original = b"".join(self.parts)
        self.digest = hashlib.sha256(self.original).hexdigest()
        self.source = self.repo / "Raft" / self.relative
        self.source.mkdir(parents=True)
        for index, chunk in enumerate(self.parts):
            (self.source / f"part-{index:05d}").write_bytes(chunk)
        (self.source / "README.txt").write_text("synthetic")
        self.manifest = self.repo / "RAFT_FILE_MANIFEST.tsv"
        self.manifest.write_text(
            "kind\tbytes\tsha256\tmode\trelative_path_under_Raft\n"
            f"split\t{len(self.original)}\t{self.digest}\t660\t{self.relative}\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("-c", "user.name=T5-Synthetic", "-c",
                  "user.email=t5@example.invalid", "commit", "-qm", "fixture")
        self.commit = self._git("rev-parse", "HEAD")
        self.manifest_blob = self._git(
            "hash-object", "--", "RAFT_FILE_MANIFEST.tsv")
        self.output = self.root / "staged"
        self.destination = self.output / self.relative
        self.entries = [(self.owner, self.digest, len(self.original))]
        self.patched_part = mock.patch.object(bridge, "PART", 8)
        self.patched_part.start()
        self.addCleanup(self.patched_part.stop)

    def _git(self, *args):
        return subprocess.check_output(
            ["git", "-C", str(self.repo), *args], text=True,
            stderr=subprocess.DEVNULL,
        ).strip()

    def stage(self, **changes):
        args = dict(owners=[self.relative], entries=self.entries,
                    expected_commit=self.commit,
                    expected_manifest_blob=self.manifest_blob,
                    byte_budget=1024)
        args.update(changes)
        return bridge.stage(self.repo, self.output, **args)

    def no_asset_or_temp(self):
        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.output.rglob(".t5-original-graphics-*.partial"))
                         if self.output.exists() else [], [])

    def test_exact_split_staged_sha_and_repeat_is_read_only(self):
        first = self.stage()
        self.assertEqual(self.destination.read_bytes(), self.original)
        self.assertEqual(first["owners_staged"], 1)
        self.assertEqual(first["owners_cached"], 0)
        self.assertEqual(first["original_bytes_verified"], len(self.original))
        self.assertFalse(first["used_lfs"])
        second = self.stage()
        self.assertEqual(second["owners_staged"], 0)
        self.assertEqual(second["owners_cached"], 1)
        self.assertEqual(self.destination.read_bytes(), self.original)

    def test_verified_stage_replaces_only_exact_feature_lfs_pointer(self):
        from scripts.hydrate_render_payloads import reuse_verified_staged_sources
        self.stage()
        feature = self.root / "feature"
        target = feature / self.owner
        target.parent.mkdir(parents=True)
        target.write_text(
            "version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{self.digest}\nsize {len(self.original)}\n",
            encoding="ascii")
        reused, size = reuse_verified_staged_sources(
            self.entries, self.output / "Raft_Data", feature)
        self.assertEqual((reused, size), (1, len(self.original)))
        self.assertEqual(target.read_bytes(), self.original)
        # An incorrect feature branch pointer is never overwritten.
        target.write_text(
            "version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{'0' * 64}\nsize {len(self.original)}\n",
            encoding="ascii")
        with self.assertRaisesRegex(ValueError, "pointer"):
            reuse_verified_staged_sources(
                self.entries, self.output / "Raft_Data", feature)
        self.assertTrue(target.read_bytes().startswith(b"version https://git-lfs"))

    def install_second_original(self):
        """Second independent synthetic split original and immutable test Git pin."""
        second = "Raft_Data/sharedassets0.assets"
        source = self.repo / "Raft" / second
        source.mkdir(parents=True)
        for i, data in enumerate(self.parts):
            (source / f"part-{i:05d}").write_bytes(data)
        self.manifest.write_text(
            self.manifest.read_text(encoding="utf-8") +
            f"split\t{len(self.original)}\t{self.digest}\t660\t{second}\n",
            encoding="utf-8")
        self._git("add", ".")
        self._git("-c", "user.name=T5-Synthetic", "-c",
                  "user.email=t5@example.invalid", "commit", "-qm", "second fixture")
        options = dict(
            owners=[self.relative, second],
            entries=self.entries + [("Raft/" + second, self.digest, len(self.original))],
            expected_commit=self._git("rev-parse", "HEAD"),
            expected_manifest_blob=self._git(
                "hash-object", "--", "RAFT_FILE_MANIFEST.tsv"),
            byte_budget=1024)
        return second, source, options

    def test_multi_owner_authentic_consumer_shares_one_bounded_batch(self):
        second, _, options = self.install_second_original()
        result = self.stage(**options)
        self.assertEqual(result["owners_verified"], 2)
        self.assertEqual(result["owners_staged"], 2)
        self.assertEqual(result["original_bytes_verified"], 2 * len(self.original))
        self.assertEqual(self.destination.read_bytes(), self.original)
        self.assertEqual((self.output / second).read_bytes(), self.original)

    def test_multi_owner_unsafe_second_preflight_writes_nothing(self):
        second, source, options = self.install_second_original()
        unsafe = source / "part-00001"
        unsafe.unlink()
        external = self.root / "original-source-alias"
        external.write_bytes(self.parts[1])
        unsafe.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "symlinked"):
            self.stage(**options)
        self.assertFalse(self.output.exists())
        self.assertEqual(external.read_bytes(), self.parts[1])

    def test_consumer_two_owner_positive_publishes_both_verified_sources(self):
        from scripts.hydrate_render_payloads import reuse_verified_staged_sources
        second, _, options = self.install_second_original()
        self.stage(**options)
        feature = self.root / "feature"
        for name, digest, size in options["entries"]:
            target = feature / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "version https://git-lfs.github.com/spec/v1\n"
                f"oid sha256:{digest}\nsize {size}\n",
                encoding="ascii",
            )
        reused, count = reuse_verified_staged_sources(
            options["entries"], self.output / "Raft_Data", feature)
        self.assertEqual((reused, count), (2, 2 * len(self.original)))
        self.assertEqual((feature / self.owner).read_bytes(), self.original)
        self.assertEqual((feature / "Raft" / second).read_bytes(), self.original)

    def test_consumer_invalid_later_target_preserves_first_pointer(self):
        from scripts.hydrate_render_payloads import reuse_verified_staged_sources
        second, _, options = self.install_second_original()
        self.stage(**options)
        feature = self.root / "feature"
        first = feature / self.owner
        later = feature / "Raft" / second
        first.parent.mkdir(parents=True, exist_ok=True)
        later.parent.mkdir(parents=True, exist_ok=True)
        first_pointer = (
            "version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{self.digest}\nsize {len(self.original)}\n"
        )
        first.write_text(first_pointer, encoding="ascii")
        later.write_text(
            "version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{'0' * 64}\nsize {len(self.original)}\n",
            encoding="ascii",
        )
        with self.assertRaisesRegex(ValueError, "pointer"):
            reuse_verified_staged_sources(
                options["entries"], self.output / "Raft_Data", feature)
        self.assertEqual(first.read_text(encoding="ascii"), first_pointer)
        self.assertEqual(later.read_text(encoding="ascii").splitlines()[1],
                         "oid sha256:" + "0" * 64)

    def test_consumer_later_same_length_sha_corruption_preserves_first_pointer(self):
        """No first-owner publication before validating a later owner digest."""
        from scripts.hydrate_render_payloads import reuse_verified_staged_sources
        second, _, options = self.install_second_original()
        self.stage(**options)
        feature = self.root / "feature"
        for name, digest, size in options["entries"]:
            target = feature / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "version https://git-lfs.github.com/spec/v1\n"
                f"oid sha256:{digest}\nsize {size}\n",
                encoding="ascii",
            )
        first = feature / self.owner
        later = feature / "Raft" / second
        expected_first = first.read_bytes()
        expected_later = later.read_bytes()
        later_source = self.output / second
        later_source.write_bytes(b"X" * len(self.original))
        self.assertEqual(later_source.stat().st_size, len(self.original))
        self.assertNotEqual(hashlib.sha256(later_source.read_bytes()).hexdigest(),
                            self.digest)
        with self.assertRaisesRegex(ValueError, "SHA verification"):
            reuse_verified_staged_sources(
                options["entries"], self.output / "Raft_Data", feature)
        self.assertEqual(first.read_bytes(), expected_first)
        self.assertEqual(later.read_bytes(), expected_later)
        self.assertEqual(list(feature.rglob(".verified-zip2-graphics-*")), [])

    def test_consumer_later_rename_failure_rolls_back_first_pointer(self):
        """An injected second publication failure restores original pointers."""
        from unittest import mock
        from scripts import hydrate_render_payloads as hyd
        second, _, options = self.install_second_original()
        self.stage(**options)
        feature = self.root / "feature"
        original = {}
        for name, digest, size in options["entries"]:
            target = feature / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "version https://git-lfs.github.com/spec/v1\n"
                f"oid sha256:{digest}\nsize {size}\n", encoding="ascii")
            original[name] = target.read_bytes()
        actual_replace = hyd.os.replace
        calls = 0

        def fail_second(source, target):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected second rename failure")
            return actual_replace(source, target)

        with mock.patch.object(hyd.os, "replace", side_effect=fail_second):
            with self.assertRaisesRegex(OSError, "injected"):
                hyd.reuse_verified_staged_sources(
                    options["entries"], self.output / "Raft_Data", feature)
        for name, _, _ in options["entries"]:
            self.assertEqual((feature / name).read_bytes(), original[name])
        self.assertEqual(list(feature.rglob(".verified-zip2-*")), [])

    def test_consumer_later_symlink_preserves_first_pointer(self):
        from scripts.hydrate_render_payloads import reuse_verified_staged_sources
        second, _, options = self.install_second_original()
        self.stage(**options)
        feature = self.root / "feature"
        first = feature / self.owner
        first.parent.mkdir(parents=True, exist_ok=True)
        first_pointer = (
            "version https://git-lfs.github.com/spec/v1\n"
            f"oid sha256:{self.digest}\nsize {len(self.original)}\n"
        )
        first.write_text(first_pointer, encoding="ascii")
        later_source = self.output / second
        later_source.unlink()
        external = self.root / "unsafe-other"
        external.write_bytes(self.original)
        later_source.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            reuse_verified_staged_sources(
                options["entries"], self.output / "Raft_Data", feature)
        self.assertEqual(first.read_text(encoding="ascii"), first_pointer)
        self.assertEqual(external.read_bytes(), self.original)

    def test_tampered_part_same_size_not_published(self):
        (self.source / "part-00001").write_bytes(b"87654321")
        with self.assertRaisesRegex(ValueError, "sha256"):
            self.stage()
        self.no_asset_or_temp()

    def test_missing_extra_and_wrong_size_part_refused(self):
        part = self.source / "part-00001"
        part.rename(self.root / "taken")
        with self.assertRaisesRegex(ValueError, "parts"):
            self.stage()
        self.no_asset_or_temp()
        part.write_bytes(b"somethingtoo-long")
        with self.assertRaisesRegex(ValueError, "length"):
            self.stage()
        self.no_asset_or_temp()
        part.write_bytes(b"12345678")
        (self.source / "part-00003").write_bytes(b"X")
        with self.assertRaisesRegex(ValueError, "parts"):
            self.stage()
        self.no_asset_or_temp()

    def test_wrong_pinned_commit_or_manifest_rejected(self):
        with self.assertRaisesRegex(ValueError, "commit"):
            self.stage(expected_commit="0" * 40)
        self.manifest.write_text(self.manifest.read_text() + "#touched\n")
        with self.assertRaisesRegex(ValueError, "manifest"):
            self.stage()
        self.no_asset_or_temp()

    def test_disagreeing_feature_lfs_pointer_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "identity_disagree"):
            self.stage(entries=[(self.owner, "0" * 64, len(self.original))])
        with self.assertRaisesRegex(ValueError, "both_immutable"):
            self.stage(owners=["Raft_Data/sharedassets0.assets"])
        self.no_asset_or_temp()

    def test_requested_owner_or_budget_must_be_bounded(self):
        with self.assertRaisesRegex(ValueError, "budget"):
            self.stage(byte_budget=len(self.original) - 1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.stage(owners=[self.relative, self.relative])
        with self.assertRaisesRegex(ValueError, "empty"):
            self.stage(owners=[])
        self.no_asset_or_temp()

    def test_existing_conflicting_destination_not_overwritten(self):
        self.destination.parent.mkdir(parents=True)
        self.destination.write_bytes(b"other_asset")
        with self.assertRaisesRegex(ValueError, "conflicts"):
            self.stage()
        self.assertEqual(self.destination.read_bytes(), b"other_asset")

    def test_symlink_in_original_or_output_cannot_redirect(self):
        external = self.root / "outside"
        external.write_bytes(b"abcdefgh")
        part = self.source / "part-00000"
        part.unlink()
        part.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "symlinked"):
            self.stage()
        self.no_asset_or_temp()
        part.unlink()
        part.write_bytes(self.parts[0])
        self.output.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinked"):
            self.stage()
        self.assertEqual(external.read_bytes(), b"abcdefgh")

    def test_hardlinked_part_rejected_before_copy(self):
        source_part = self.source / "part-00000"
        external = self.root / "alias"
        external.hardlink_to(source_part)
        with self.assertRaisesRegex(ValueError, "hardlinked"):
            self.stage()
        self.no_asset_or_temp()
        self.assertEqual(external.read_bytes(), self.parts[0])

    def test_output_under_original_zip2_source_refused(self):
        with self.assertRaisesRegex(ValueError, "overlapping"):
            bridge.stage(self.repo, self.repo / "Raft" / "staged",
                         owners=[self.relative], entries=self.entries,
                         expected_commit=self.commit,
                         expected_manifest_blob=self.manifest_blob)


if __name__ == "__main__":
    unittest.main()
