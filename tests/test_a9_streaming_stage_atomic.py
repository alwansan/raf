"""A9 interrupted original asset copy regressions; synthetic temporary Git files only."""
from pathlib import Path
from unittest import mock
import shutil
import unittest
import test_stage_original_streaming_assets as fixtures
from scripts.stage_original_streaming_assets import stage


class AtomicStageTests(unittest.TestCase):
    setUp = fixtures.OriginalStreamingTests.setUp
    git = fixtures.OriginalStreamingTests.git
    commit = fixtures.OriginalStreamingTests.commit

    def assert_no_staged_partials(self):
        if self.project.exists():
            self.assertEqual(
                list(self.project.rglob(".raft-stage-*.partial")), [],
                "Unpublished partial data file survived failed copy",
            )

    def test_mid_copy_os_error_never_exposes_partial_final_and_retry_recovers(self):
        original_copy = shutil.copyfile
        name = "VO_npc_english.bank"
        source = self.source / name
        final = self.project / "Assets/StreamingAssets" / name

        def interrupt_copy(src, dst, *args, **kwargs):
            if Path(src) == source:
                Path(dst).write_bytes(b"PARTIAL BANK BYTES - simulated I/O interruption")
                raise OSError("synthetic interrupted original audio copy")
            return original_copy(src, dst, *args, **kwargs)

        with mock.patch("scripts.stage_original_streaming_assets.shutil.copyfile",
                        side_effect=interrupt_copy):
            with self.assertRaisesRegex(OSError, "interrupted"):
                stage(self.repo, self.project, self.report, apply=True,
                      haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(final.exists(), "Broken final bank must not be visible")
        self.assertFalse(self.report.exists(), "Failed staging cannot publish success report")
        self.assert_no_staged_partials()
        stage(self.repo, self.project, self.report, apply=True,
                      haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertEqual(final.read_bytes(), source.read_bytes())
        self.assert_no_staged_partials()

    def test_corrupted_copy_rejected_before_publishing_final_asset(self):
        original_copy = shutil.copyfile
        name = "VO_logs_english.bank"
        source = self.source / name
        final = self.project / "Assets/StreamingAssets" / name

        def corrupt_copy(src, dst, *args, **kwargs):
            if Path(src) == source:
                Path(dst).write_bytes(b"intentionally corrupted bank bytes")
                return str(dst)
            return original_copy(src, dst, *args, **kwargs)

        with mock.patch("scripts.stage_original_streaming_assets.shutil.copyfile",
                        side_effect=corrupt_copy):
            with self.assertRaisesRegex(ValueError, "verification failed"):
                stage(self.repo, self.project, self.report, apply=True,
                      haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(final.exists(), "Corrupt final bank must not be visible")
        self.assertFalse(self.report.exists())
        self.assert_no_staged_partials()
        stage(self.repo, self.project, self.report, apply=True,
                      haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertEqual(final.read_bytes(), source.read_bytes())
        self.assert_no_staged_partials()


    def test_copy_temporary_path_is_outside_unity_streamingassets(self):
        original_copy = shutil.copyfile
        name = "VO_npc_english.bank"
        source = self.source / name
        assets = self.project / "Assets/StreamingAssets"
        paths = []

        def inspect_copy(src, dst, *args, **kwargs):
            if Path(src) == source:
                paths.append(Path(dst))
                self.assertFalse(
                    Path(dst).is_relative_to(assets),
                    "A crash can leave a temporary file packaged as StreamingAssets",
                )
            return original_copy(src, dst, *args, **kwargs)

        with mock.patch("scripts.stage_original_streaming_assets.shutil.copyfile",
                        side_effect=inspect_copy):
            stage(self.repo, self.project, self.report, apply=True,
                      haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertEqual(len(paths), 1)
        self.assertEqual((assets / name).read_bytes(), source.read_bytes())
        self.assert_no_staged_partials()

    def test_atomic_no_overwrite_if_destination_appears_after_preflight(self):
        from scripts import stage_original_streaming_assets as source_module
        original_link = source_module.os.link
        name = "VO_npc_english.bank"
        final = self.project / "Assets/StreamingAssets" / name
        called = []

        def race_link(src, dst, *args, **kwargs):
            if Path(dst) == final:
                called.append(True)
                final.write_bytes(b"synthetic concurrent owner")
                raise FileExistsError("synthetic cross-job race")
            return original_link(src, dst, *args, **kwargs)

        with mock.patch("scripts.stage_original_streaming_assets.os.link",
                        side_effect=race_link):
            with self.assertRaisesRegex(ValueError, "Existing original StreamingAssets conflict"):
                stage(self.repo, self.project, self.report, apply=True,
                      haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertEqual(len(called), 1)
        self.assertEqual(final.read_bytes(), b"synthetic concurrent owner")
        self.assertFalse(self.report.exists())
        self.assert_no_staged_partials()


    def test_committed_original_bank_coedit_does_not_rebase_trust(self):
        # Both source and mutable HEAD agree; that is not proof of the
        # original ZIP game's audio bytes.
        (self.source / "VO_npc_english.bank").write_bytes(b"synthetic new committed bank")
        self.commit()
        with self.assertRaisesRegex(ValueError, "original root .*identity"):
            stage(self.repo, self.project, self.report, apply=True,
                  haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())
        self.assertFalse(self.report.exists())

    def test_committed_original_data_rgd_coedit_does_not_rebase_trust(self):
        (self.source / "Data.rgd").write_bytes(b"synthetic different save payload")
        self.commit()
        with self.assertRaisesRegex(ValueError, "original root .*identity"):
            stage(self.repo, self.project, self.report, apply=True,
                  haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())
        self.assertFalse(self.report.exists())

    def test_unknown_committed_root_asset_fails_closed(self):
        (self.source / "NotOriginal.data").write_bytes(b"synthetic added root file")
        self.commit()
        with self.assertRaisesRegex(ValueError, "original root .*identity"):
            stage(self.repo, self.project, self.report, apply=True,
                  haptics_manifest_blob_sha=self.haptics_manifest_blob_sha)
        self.assertFalse(self.project.exists())
        self.assertFalse(self.report.exists())


    def test_a9_zip2_override_rejects_unpinned_bank(self):
        # A synthetic file may never masquerade as a ZIP2 replacement if the
        # tracked MasterBank is not the authentic original LFS pointer.
        fake_bank = self.root / "fake-restored.bank"
        fake_bank.write_bytes(b"not an original bank")
        with self.assertRaisesRegex(ValueError, "requires original pinned LFS pointer"):
            stage(self.repo, self.project, self.report, apply=True,
                  haptics_manifest_blob_sha=self.haptics_manifest_blob_sha,
                  verified_external_master_bank=fake_bank)
        self.assertFalse(self.project.exists())
        self.assertFalse(self.report.exists())

    def test_a9_zip2_override_rejects_linked_restored_bank(self):
        from scripts import stage_original_streaming_assets as source_module
        original = self.source / "MasterBank.bank"
        original.write_bytes(
            b"version https://git-lfs.github.com/spec/v1\n"
            + b"oid sha256:" + source_module.MASTER_SHA.encode()
            + b"\nsize 101600960\n"
        )
        self.commit()
        # Fixture-only re-pin of a new synthetic Git blob; production original
        # has an independent immutable OID and SHA256 validator.
        source_module.ORIGINAL_ROOT_BLOB_SHAS["MasterBank.bank"] = self.git(
            "rev-parse", "HEAD:Raft/Raft_Data/StreamingAssets/MasterBank.bank"
        ).decode().strip()
        outside = self.root / "fake-restored.bank"
        outside.write_bytes(b"synthetic, not game audio")
        linked = self.root / "linked-restored.bank"
        linked.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "source link"):
            stage(self.repo, self.project, self.report, apply=True,
                  haptics_manifest_blob_sha=self.haptics_manifest_blob_sha,
                  verified_external_master_bank=linked)
        self.assertEqual(outside.read_bytes(), b"synthetic, not game audio")
        self.assertFalse(self.project.exists())
        self.assertFalse(self.report.exists())


if __name__ == "__main__":
    unittest.main()
