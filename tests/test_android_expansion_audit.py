"""Synthetic APK/OBB validation without game assets or LFS."""
from pathlib import Path
import tempfile
import struct
import unittest
from zipfile import ZipFile
from scripts.audit_android_expansion import audit_companion


def make(path, files):
    with ZipFile(path, "w") as archive:
        for name, value in files.items():
            archive.writestr(name, value)


class ExpansionAuditTests(unittest.TestCase):
    def test_requires_both_parts_and_original_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            with self.assertRaises(FileNotFoundError):
                audit_companion(apk, obb)
            make(obb, {"assets/bin/Data/level1": b"original-scene-data", "assets/bin/Data/StreamingAssets/a.bank": b"bank"})
            result = audit_companion(apk, obb)
            self.assertEqual(result["obbUnityDataMembers"], 2)
            self.assertTrue(result["companionRequired"])
            self.assertEqual(len(result["obbSha256"]), 64)
            self.assertNotIn("original-scene-data", str(result))
            self.assertFalse(result["deviceMountedVerified"])

    def test_rejects_missing_original_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            make(obb, {"metadata": b"no data"})
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False)

    def test_identity_mismatch_and_matching_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first", "assets/unity_obb_guid": b"A"})
            make(obb, {"assets/bin/Data/level1": b"data", "assets/unity_obb_guid": b"B"})
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False)
            make(obb, {"assets/bin/Data/level1": b"data", "assets/unity_obb_guid": b"A"})
            self.assertEqual(audit_companion(apk, obb, digest=False)["expansionIdentityCheck"], "verified")

    def test_reports_obb_size_and_member_limits_without_asset_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            make(obb, {"assets/bin/Data/level1": b"original-scene-data",
                       "assets/bin/Data/StreamingAssets/a.bank": b"bank"})
            normal = audit_companion(apk, obb, digest=False)
            self.assertFalse(normal["obbPlayLimitExceeded"])
            self.assertEqual(normal["obbPlayLimitBytes"], 2_000_000_000)
            self.assertEqual(normal["obbUnityLargestMemberBytes"], len(b"original-scene-data"))
            self.assertEqual(normal["obbUnityCompressedBytes"], len(b"original-scene-data") + len(b"bank"))
            self.assertEqual(normal["obbUnityMembersOverJavaArray"], 0)
            constrained = audit_companion(apk, obb, digest=False,
                                          play_limit_bytes=obb.stat().st_size - 1,
                                          java_array_limit_bytes=4)
            self.assertTrue(constrained["obbPlayLimitExceeded"])
            self.assertEqual(constrained["obbUnityMembersOverJavaArray"], 1)
            self.assertNotIn("level1", str(constrained))
            self.assertNotIn("a.bank", str(constrained))

    def test_crc_checks_detect_modified_payload_without_leaking_member_names(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"initial-scene"})
            make(obb, {"assets/bin/Data/level1": b"original-data"})
            self.assertTrue(audit_companion(apk, obb, digest=False,
                                            verify_crc=True)["zipCrcVerified"])
            self.assertFalse(audit_companion(apk, obb, digest=False)["zipCrcVerified"])

            def damage(path):
                with ZipFile(path) as archive:
                    item = archive.infolist()[0]
                with path.open("r+b") as stream:
                    stream.seek(item.header_offset + 26)
                    name_len, extra_len = struct.unpack("<HH", stream.read(4))
                    stream.seek(item.header_offset + 30 + name_len + extra_len)
                    first = stream.read(1)
                    self.assertTrue(first)
                    stream.seek(-1, 1)
                    stream.write(bytes([first[0] ^ 1]))

            damage(obb)
            with self.assertRaisesRegex(ValueError, "CRC") as caught:
                audit_companion(apk, obb, digest=False, verify_crc=True)
            self.assertNotIn("level1", str(caught.exception))
            make(obb, {"assets/bin/Data/level1": b"original-data"})
            damage(apk)
            with self.assertRaisesRegex(ValueError, "CRC") as caught:
                audit_companion(apk, obb, digest=False, verify_crc=True)
            self.assertNotIn("first", str(caught.exception))

    def test_reports_lossless_compression_feasibility_without_claiming_compatibility(self):
        from zipfile import ZIP_DEFLATED
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            with ZipFile(obb, "w", compression=ZIP_DEFLATED) as archive:
                archive.writestr("assets/bin/Data/level1", b"x" * 4096)
            report = audit_companion(apk, obb, digest=False)
            self.assertEqual(report["obbUnityStoredMembers"], 0)
            self.assertEqual(report["obbUnityDeflatedMembers"], 1)
            self.assertEqual(report["obbUnityStoredBytes"], 0)
            self.assertGreater(report["obbZipContainerOverheadBytes"], 0)
            self.assertEqual(report["obbPlayExcessBytes"], 0)

    def test_rejects_unsafe_obb_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb = Path(tmp) / "a.apk", Path(tmp) / "a.main.obb"
            make(apk, {"assets/bin/Data/first": b"first"})
            make(obb, {"assets/bin/Data/level1": b"data", "../outside": b"unsafe"})
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False)


class OriginalHapticsObbContractTests(unittest.TestCase):
    """Synthetic-only ZIP layout and Git-blob parity negative controls.

    The production manifest is exercised independently in A3 staging and
    A5's authenticated original source reader CI. Fixtures never contain
    proprietary audio or emit member names in diagnostic messages.
    """

    def fixture(self, root):
        import hashlib
        import json

        apk = root / "a.apk"
        obb = root / "a.main.obb"
        manifest = root / "original-haptics.json"
        names = ["SyntheticHaptic%02d.wav" % i for i in range(29)]
        payloads = {name: (b"RIFF-TEST-ONLY-" + name.encode()) for name in names}
        files = {}
        for name, payload in payloads.items():
            oid = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
            files[name] = {"git_blob_sha": oid, "bytes": len(payload)}
        original = {"schema_version": 1,
                    "path_prefix": "Raft/Raft_Data/StreamingAssets/Haptics/",
                    "files": files}
        manifest.write_text(json.dumps(original), encoding="utf-8")
        make(apk, {"assets/bin/Data/first": b"first"})
        entries = {"assets/bin/Data/level1": b"original-data"}
        entries.update({"assets/Haptics/" + name: payload for name, payload in payloads.items()})
        make(obb, entries)
        return apk, obb, manifest, entries, original, names

    def test_exact_29_jar_paths_and_git_blobs_pass_without_original_asset_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb, manifest, _, _, _ = self.fixture(Path(tmp))
            result = audit_companion(apk, obb, digest=False, verify_crc=True,
                                     haptics_manifest=manifest)
            self.assertEqual(result["hapticsOriginalMembers"], 29)
            self.assertGreater(result["hapticsOriginalBytes"], 0)
            self.assertTrue(result["hapticsJarPathsAndOriginalGitBlobsVerified"])
            self.assertFalse(result["originalBytesVerified"])  # other Unity data unverified
            self.assertFalse(result["deviceMountedVerified"])
            self.assertNotIn("SyntheticHaptic", str(result))

    def test_missing_misplaced_and_case_changed_entries_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb, manifest, entries, _, names = self.fixture(Path(tmp))
            original_key = "assets/Haptics/" + names[0]
            scenarios = [
                ("missing", None),
                ("wrong_unity_data_prefix", "assets/bin/Data/StreamingAssets/Haptics/" + names[0]),
                ("case_changed", "assets/Haptics/" + names[0].lower()),
                ("wrong_subdirectory", "assets/Haptics/extra/" + names[0]),
            ]
            for name, replacement in scenarios:
                with self.subTest(name=name):
                    other = dict(entries)
                    value = other.pop(original_key)
                    if replacement is not None:
                        other[replacement] = value
                    make(obb, other)
                    with self.assertRaisesRegex(ValueError, "absent") as error:
                        audit_companion(apk, obb, digest=False,
                                        haptics_manifest=manifest)
                    self.assertNotIn(names[0], str(error.exception))

    def test_valid_zip_same_size_tamper_and_wrong_manifest_sha_fail_closed(self):
        import json

        with tempfile.TemporaryDirectory() as tmp:
            apk, obb, manifest, entries, original, names = self.fixture(Path(tmp))
            target = "assets/Haptics/" + names[0]
            tampered = dict(entries)
            value = tampered[target]
            tampered[target] = value[:-1] + bytes([value[-1] ^ 1])
            make(obb, tampered)
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                audit_companion(apk, obb, digest=False,
                                haptics_manifest=manifest)
            make(obb, entries)
            forged = json.loads(json.dumps(original))
            forged["files"][names[0]]["git_blob_sha"] = "0" * 40
            manifest.write_text(json.dumps(forged), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "identity mismatch"):
                audit_companion(apk, obb, digest=False,
                                haptics_manifest=manifest)

    def test_manifest_must_have_exact_safe_29_original_wav_names(self):
        import json

        with tempfile.TemporaryDirectory() as tmp:
            apk, obb, manifest, _, original, names = self.fixture(Path(tmp))
            candidates = []
            shorter = json.loads(json.dumps(original))
            shorter["files"].pop(names[0])
            candidates.append(shorter)
            alias = json.loads(json.dumps(original))
            alias["files"][names[0].lower()] = alias["files"].pop(names[1])
            candidates.append(alias)
            traversal = json.loads(json.dumps(original))
            traversal["files"]["../outside.wav"] = traversal["files"].pop(names[0])
            candidates.append(traversal)
            wrong_schema = json.loads(json.dumps(original))
            wrong_schema["path_prefix"] = "assets/Haptics/"
            candidates.append(wrong_schema)
            for bad in candidates:
                with self.subTest(case=list(bad["files"])[0]):
                    manifest.write_text(json.dumps(bad), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        audit_companion(apk, obb, digest=False, haptics_manifest=manifest)


    def test_native_obb_audit_wires_manifest_in_same_command(self):
        # Static wiring guard only; does not run a native build.
        workflow = (Path(".github/workflows/raft-unity-editor-android-import.yml")
                    .read_text(encoding="utf-8"))
        start = workflow.find("python3 scripts/audit_android_expansion.py")
        self.assertGreaterEqual(start, 0)
        command = workflow[start: workflow.find("\n          fi", start)]
        self.assertIn('--haptics-manifest "$GITHUB_WORKSPACE/config/original-haptics-manifest.json"',
                      command)
        self.assertIn("--verify-crc", command)

    def test_without_manifest_does_not_claim_haptic_archive_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            apk, obb, manifest, entries, _, names = self.fixture(Path(tmp))
            entries.pop("assets/Haptics/" + names[0])
            make(obb, entries)
            result = audit_companion(apk, obb, digest=False)
            self.assertFalse(result["hapticsJarPathsAndOriginalGitBlobsVerified"])
            with self.assertRaises(ValueError):
                audit_companion(apk, obb, digest=False, haptics_manifest=manifest)


if __name__ == "__main__":
    unittest.main()
