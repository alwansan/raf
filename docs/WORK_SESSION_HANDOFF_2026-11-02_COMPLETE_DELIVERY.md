# Raft Android — complete APK/OBB/XAPK delivery, 2026-11-02

## Owner direction supersedes older standalone/OBB restrictions
Owner explicitly accepts large packages, OBB and multiple delivery files, authorizes APK+OBB/XAPK Release publication and prioritizes complete content over size-driven reduction. Older standalone-only/no-OBB-publication instructions are historical. Raw reconstructed project, loose original sources/assets and secrets remain unpublished. Only feature/android-native-port writable.

Entry HEAD367eabdc8d0d7456c4fcd2393637b962e3a9a7ca. Current native41400935501/source1246571d/job125132421758 is IN_PROGRESS with immutable older standalone/colour-compression settings; do not cancel or duplicate. These updates apply to the NEXT native after the active result is inspected.

## Research
XAPK is ZIP with APK/manifest/optional OBB. A compatible installer must install APK and copy OBB; Android15 storage/ZIP64 compatibility is not proven by an extension.
Official APKS is bundletool APK-set output with its own metadata; renamed ZIP(APK+OBB) is NOT a genuine APKS and will not solve OBB copying.
GitHub allows each Release asset UNDER2GiB, but no total-release size cap. Prior OBB2287764013bytes exceeds that transport limit. This is separate from historical Play distribution limits and does not prove sideload failure.
Splitting Unity data into arbitrary OBB files is not a valid automatic runtime partition. Transport chunks are reassembled to EXACT original files before installation, without altering Unity data.

References:
https://developer.android.com/tools/bundletool
https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
https://mas.owasp.org/MASTG/techniques/android/MASTG-TECH-0145/
Schema example (not installer compatibility certification): https://github.com/CodeMasterYi/XAPKTools/blob/master/README.md

## Implemented
- Defaults: split package + fidelity texture profile. Existing size-driven2048 cap and extra ASTC conversions run ONLY with explicit -raftTextureProfile mobile. Normal Android platform import format selection remains; source images/settings/metas/GUIDs/scenes/save unchanged.
- All40scene,SDK,histogramkernel,FMOD exact36originalStreamingAssets/nativeJava/ELF/signature gates remain required.
- Package script checks real aapt package/version/SDK identity and input ZIP CRC, preserves APK/OBB bytes/signature, names OBB main.<versionCode>.com.alwansan.raft.androidtest.obb, writes ZIP_STORED XAPK with expansions manifest. APK+OBB and XAPK are ALTERNATIVES.
- Complete direct files when below GitHub per-asset limit. Larger files delivered as1GiB parts with delivery.json and SHA256SUMS. XAPK streams directly to segmented sink with ZIP64 as needed, avoiding an extra full XAPK staging copy. Free disk and size bounds checked before packaging.
- Reassembler verifies part+whole sizes/SHA256 and rejects missing/corrupt/unsafe names/duplicates/overwrites. Termux Python3.11+ command: python reassemble.py Raft-Android-Test.xapk. docs/ANDROID_INSTALL_AR.md explains alternatives, exact OBB path, ZIP64/Android15 caveats and wirelessADB fallback without PC.
- Publisher verifies both part and complete logical hashes after artifact transport, then uploads complete authorized install files/transport parts. Still requires explicit native+device markers, successful reconstruction and allowed branch. Replaces old unconditional OBB publication block; no source/loose assets/secrets uploaded.
- No arbitrary product APK size cap; GitHub per-DOWNLOAD-PART cap stays. No audio recompression or Unity data member edits.
- APKS intentionally omitted because no legitimate AAB/APK-set output exists in this path. Add only if useful and valid, not as renamed XAPK.

## Validation
8local packaging fixtures pass: exact original APK/OBB bytes, manifest total/version/path, stored ZIP/CRC, direct small standalone, parts+full reassembly, source/part corruption, bad identity, missing required file, existing destination, unsafe part names, forced ZIP64 streaming, and execution of actual publisher block with missing-part rejection.
6updated distribution policy and9scene/fidelity source tests pass. These are synthetic/source tests, not actual large-file installer, Unity/device gameplay or OBB mount verification.
First commit requests cheap CI only. Existing41400935501 stays untouched. After it ends, inspect actual result and submit ONE future split/fidelity native+device request for complete delivery. Continue water/input/audio/save restoration; do not call byte completeness full gameplay restoration.
