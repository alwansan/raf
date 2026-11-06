# T5 INTEGRATION-001 — APK/OBB local ZIP-header integrity regression

**Session:** `20261106T1243Z-T5-chat-zip-local-headers-9e2a`, `origin=chat`. **Only writable branch:** `feature/android-native-port`. **Status:** validator source patch integrated, source-only synthetic CI verified; no real signed package or Android phone acceptance claim.

## Why it mattered

Previously `scripts/t5_verify_apk_obb_pair.py` authenticated each *completed* APK/OBB byte stream against the adjacent `delivery.json` SHA/size and verified the ZIP **central directory** names and a few core APK members. It did not compare the local ZIP header for every non-core Unity member. A local filename could be modified, and after the local manifest was regenerated the SHA would still match; `ZipFile.namelist()` showed the safe name while `ZipFile.open()` would raise `BadZipFile` because the local name differed. This prevents a simple manifest-consistent archive from being misidentified as structurally usable. This is **not** a signature or trusted publisher check.

## Actual change

The T5-owned pair checker `scripts/t5_verify_apk_obb_pair.py` now walks every indexed APK and OBB member without extracting compressed game data and validates:

- Positive local ZIP header signature, sensible offset, bounded filename metadata, decoded filename bytes exactly matching the central directory;
- Identical local/central flags and compression method, local CRC and sizes where a data descriptor is **not** used (ZIP64 sentinel sizes respected);
- Compressed byte-range start/end inside the archive payload and no compressed member region overlapping the next local entry;
- Existing filename traversal, duplicate, Unix symlink, encrypted member, ARM64 IL2CPP core, aapt package/version, APK/OBB complete-byte SHA and `delivery.json` checks remain intact.

The metadata-only pass uses O(member-count) memory and O(member-count log member-count) sorting, with one local-header seek/read per entry, no 6GB decompression. `zipfile.ZipInfo` compressed sizes are read from the central directory; data descriptor footprints may sit between regions and do not trigger false overlap claims.

## Tests and exact CI

- First isolated source-only run [42219865068](https://github.com/alwansan/raf/actions/runs/42219865068) passed existing tests on source patch `7839aa9c13ebff573762d8ade1f390fddb0268c0`.
- [42219989211](https://github.com/alwansan/raf/actions/runs/42219989211) **FAILED** with six fixture `AssertionError: -1` from a new test helper's double-escaped `PK\\x03\\x04` Python bytes. The production patch was not the root cause. Fixture literal corrected in `432dc4b7bc819a49b561e948b471664ee88bd085`.
- [42220094481](https://github.com/alwansan/raf/actions/runs/42220094481) **SUCCESS** with **30/30 synthetic tests**, including seven new malformed non-core APK/OBB cases using **recomputed matching delivery.json hashes**: mismatched local member filename (both APK/OBB), flags, compression method, CRC, local signature, and compressed member overlap.
- To guard against rejecting a genuine large native package, added **two positive tests** for ZIP64 local `0xffffffff` size placeholders and nonseekable streamed ZIP data-descriptor flag 8. Final [42220308068](https://github.com/alwansan/raf/actions/runs/42220308068), job `127900400890`, exact SHA `5b700fa6a2fd3f734f0a51ffc70ba2b534db9198`, **COMPLETED SUCCESS, 32/32 synthetic tests**; both legal structures accepted. `python3 -m py_compile` passed.

## Proof limits, team coordination, next step

This is an **implemented source-only pack-verification improvement**, not just a metadata census. No APK/OBB/XAPK original assets, proprietary DLL/shader data or signed delivery archives were downloaded, uploaded or republished in this test. A manifest with SHA values cannot authenticate itself; this checker still does not verify APK cryptographic signature, Unity OBB GUID or actual read/write/load on the phone, and does **not** exhaustively decompress/check CRC for all members. The source-only positive test does **not** validate the actual ~6GB phone artifact.

Original device world/save/reentry remains confirmed only on prior owner-tested [run 42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) under source `e9c358e`; WATER-001/FFT, RENDER-002 shaders/effects/colors and device acceptance remain OPEN, overall game `NOT_READY 0/3`. T1/T2/T3/T4 code, Settings, touch, scene materials, shader, .meta/GUID and Unity build jobs remain untouched. No full native game build requested or cancelled.

**Next:** When the existing signed delivery artifacts are available in an authorized isolated runner with enough disk, verify their **inner actual** `delivery.json`, APK and main OBB after SHA authentication and versionCode/package match with `aapt`. Apply this stricter validator to the real files and independently inspect APK signature / Unity GUID with authorized tools. Correlate installed package and LogRaft data before claiming phone confidence. Avoid duplicating full-size artifact downloads or changing the working Settings and audio.
