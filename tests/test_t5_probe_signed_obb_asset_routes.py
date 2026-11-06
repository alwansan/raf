"""T5 source-free original signed OBB jar-path identity negative and positive cases."""
import io
import struct
import unittest
import warnings
import zipfile

from scripts.t5_probe_github_artifact_zip_range import LimitedRangeIO, ProbeError
from scripts.t5_probe_signed_obb_asset_routes import (
    BANK_TOTAL, ORIGINAL_WAV_TOTAL_BYTES, BANK_SIZES,
    classify_signed_obb_routes, inspect_original_checkpoint, pinned_haptic_lengths,
)

BANKS = {"MasterBank.bank": 7, "MasterBank.strings.bank": 3}
WAVS = {"Dynamite.wav": 2, "SharkBiteRaftHaptics.wav": 4}
PKG = "com.alwansan.raft.androidtest"


def archive(rows, compress=zipfile.ZIP_STORED):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=compress, allowZip64=True) as z:
        for name, data in rows:
            z.writestr(name, data)
    return stream.getvalue()


def original_shape(*, banks=BANKS, wavs=WAVS, extras=(), unity=True, compress=zipfile.ZIP_STORED):
    content = [
        ("assets/" + name, bytes([4]) * n) for name, n in banks.items()
    ] + [
        ("assets/Haptics/" + name, bytes([5]) * n) for name, n in wavs.items()
    ]
    if unity:
        content.append(("assets/bin/Data/resources", b"synthetic-Unity-payload"))
    return archive(content + list(extras), compress=compress)


def prove_obb(data, *, banks=BANKS, wavs=WAVS):
    with zipfile.ZipFile(io.BytesIO(data)) as inner:
        return classify_signed_obb_routes(inner, haptics=wavs, banks=banks)


def simulated_checkpoint(apk=b"temporary-APK-unity-core", obb=None,
                         compress=zipfile.ZIP_STORED):
    if obb is None:
        obb = original_shape()
    stream = archive([
        ("Raft-Android-Test.apk", apk),
        ("main.89." + PKG + ".obb", obb),
    ], compress=compress)
    parent = LimitedRangeIO(
        len(stream), lambda offset, length: stream[offset:offset + length],
        budget=1024 * 1024)
    return parent, len(apk), len(obb)


class SignedObbRealPathTests(unittest.TestCase):
    def test_exact_synthetic_jar_paths_accepted_for_bank_haptics_unity(self):
        result = prove_obb(original_shape())
        self.assertEqual(result["original_FMOD_bank_exact_runtime_jar_routes_present"], 2)
        self.assertEqual(result["original_haptics_exact_runtime_jar_routes_present"], 2)
        self.assertEqual(result["original_FMOD_bank_total_uncompressed_bytes"], 10)
        self.assertEqual(result["original_haptics_total_uncompressed_bytes"], 6)
        self.assertEqual(result["original_Unity_data_folder_entries"], 1)
        self.assertTrue(result["actual_obb_local_headers_match_central"])
        self.assertFalse(result["original_jar_URL_asset_read_on_phone_proven"])

    def test_missing_bank_is_rejected_before_any_success_claim(self):
        data = original_shape(banks={"MasterBank.bank": 7})
        with self.assertRaisesRegex(ProbeError, "original_fmod_bank_route_absent"):
            prove_obb(data)

    def test_missing_haptic_is_not_saved_by_same_name_in_wrong_location(self):
        data = original_shape(
            wavs={"Dynamite.wav": 2},
            extras=[("assets/bin/Data/StreamingAssets/Haptics/SharkBiteRaftHaptics.wav", b"same")])
        with self.assertRaisesRegex(ProbeError, "original_haptics_route_absent"):
            prove_obb(data)

    def test_bank_and_haptic_length_mismatches_rejected(self):
        with self.assertRaisesRegex(ProbeError, "original_fmod_bank_route_size_or_encoding_drift"):
            prove_obb(original_shape(banks={"MasterBank.bank": 6, "MasterBank.strings.bank": 3}))
        with self.assertRaisesRegex(ProbeError, "original_haptics_route_size_or_encoding_drift"):
            prove_obb(original_shape(wavs={"Dynamite.wav": 3, "SharkBiteRaftHaptics.wav": 4}))

    def test_extra_haptic_and_extra_bank_do_not_hide_shadow_paths(self):
        with self.assertRaisesRegex(ProbeError, "original_audio_extra_or_unexpected_routes"):
            prove_obb(original_shape(extras=[("assets/Haptics/unknown.wav", b"new")]))
        with self.assertRaisesRegex(ProbeError, "original_audio_extra_or_unexpected_routes"):
            prove_obb(original_shape(extras=[("assets/unexpected.bank", b"new")]))

    def test_unity_data_missing_or_empty_rejected(self):
        with self.assertRaisesRegex(ProbeError, "original_unity_data_route_absent"):
            prove_obb(original_shape(unity=False))
        with self.assertRaisesRegex(ProbeError, "original_unity_data_route_absent"):
            prove_obb(original_shape(unity=False, extras=[("assets/bin/Data/empty", b"")]))

    def test_case_sensitive_archive_lookup_requires_exact_runtime_casing(self):
        data = original_shape(
            banks={"masterbank.bank": 7, "MasterBank.strings.bank": 3})
        with self.assertRaisesRegex(ProbeError, "original_fmod_bank_route_absent"):
            prove_obb(data)

    def test_bad_zip_duplicate_member_name_rejected(self):
        rows = [("assets/MasterBank.bank", b"AAAAAAA"),
                ("assets/MasterBank.bank", b"BBBBBBB")]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            bad = original_shape(extras=rows)
        with self.assertRaisesRegex(ProbeError, "signed_obb_duplicate_zip_member"):
            prove_obb(bad)

    def test_unsafe_relative_traversal_entry_rejected(self):
        bad = original_shape(extras=[("assets/../escape.wav", b"unsafe")])
        with self.assertRaisesRegex(ProbeError, "unsafe_zip_member"):
            prove_obb(bad)

    def test_corrupted_local_filename_rejected_before_jar_path_inventory(self):
        src = bytearray(original_shape())
        with zipfile.ZipFile(io.BytesIO(src)) as file:
            entry = file.getinfo("assets/MasterBank.bank")
        name_end = entry.header_offset + 30 + len(entry.filename) - 1
        src[name_end] ^= 1
        with self.assertRaisesRegex(ProbeError, "signed_obb_local_header_inconclusive"):
            prove_obb(bytes(src))

    def test_compressed_members_are_valid_for_source_jar_metadata(self):
        data = prove_obb(original_shape(compress=zipfile.ZIP_DEFLATED))
        self.assertTrue(data["original_FMOD_bank_lengths_match_production_identity"])

    def test_outer_signed_checkpoint_stored_member_range_nested_proof(self):
        parent, a, o = simulated_checkpoint()
        real_like = inspect_original_checkpoint(parent, apk_size=a, obb_size=o,
                                                haptics=WAVS, banks=BANKS)
        self.assertEqual(real_like["original_FMOD_bank_exact_runtime_jar_routes_present"], 2)
        self.assertEqual(real_like["source_original_signed_checkpoint_id"], 13441766832)
        self.assertLess(real_like["real_original_HTTP206_bytes"], 1024 * 1024)
        self.assertFalse(real_like["raw_game_bytes_logged_or_uploaded"])

    def test_outer_signed_checkpoint_bad_size_refused(self):
        parent, a, o = simulated_checkpoint()
        with self.assertRaisesRegex(ProbeError, "original_signed_checkpoint_member_drift"):
            inspect_original_checkpoint(parent, apk_size=a, obb_size=o + 1,
                                        haptics=WAVS, banks=BANKS)

    def test_outer_signed_checkpoint_member_deflate_refused_without_download(self):
        parent, a, o = simulated_checkpoint(compress=zipfile.ZIP_DEFLATED)
        with self.assertRaisesRegex(ProbeError, "outer_signed_member_not_stored"):
            inspect_original_checkpoint(parent, apk_size=a, obb_size=o,
                                        haptics=WAVS, banks=BANKS)

    def test_outer_range_budget_exceeded_refuses_fallback(self):
        parent, a, o = simulated_checkpoint()
        parent.remaining = 12
        with self.assertRaisesRegex(ProbeError, "budget_exhausted"):
            inspect_original_checkpoint(parent, apk_size=a, obb_size=o,
                                        haptics=WAVS, banks=BANKS)

    def test_invalid_expectations_rejected_instead_of_empty_vacuous_pass(self):
        raw = original_shape()
        for kwargs in ({"banks": {}}, {"wavs": {}},
                       {"banks": {"X.bin": 7}}, {"wavs": {"../bad.wav": 3}},
                       {"banks": {"MasterBank.bank": True}}):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ProbeError, "resource_expectations_invalid"):
                prove_obb(raw, **kwargs)

    def test_pinned_original_manifest_real_source_count_without_asset_payload(self):
        lengths = pinned_haptic_lengths()
        self.assertEqual(len(lengths), 29)
        self.assertEqual(sum(lengths.values()), ORIGINAL_WAV_TOTAL_BYTES)
        self.assertEqual(len(BANK_SIZES), 5)
        self.assertEqual(BANK_TOTAL, 123817498)


if __name__ == "__main__":
    unittest.main()
