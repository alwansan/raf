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


## Verified cheap delivery CI and scheduler checkpoint
Source b867fc2901cb94ecaeb46422b104c036d4b670fe. Platform41403797687/job125141186918 COMPLETED SUCCESS: actual embedded publisher/ZIP64/lossless delivery fixtures, source policies, existing exact-data synthetic gates and offline library/smoke passed. No APK/XAPK was built by cheap CI. Original active native41400935501/job125132421758 is IN_PROGRESS at real Unity import/compile on older1246571d; do not cancel/duplicate. New gated41403797736 is a non-opt-in workflow pending behind active concurrency, NOT another full native request.
Updated existing hourly enabled automation6ae68c9d65608191878d7e0c0e40645e with this explicit owner preference and next single split/fidelity native+device request AFTER old build ends and cheap gates pass. No duplicate scheduler created. Current source/history restrictions against OBB publication are superseded by explicit owner authorization; keep source/secrets protections.
Only current multi-hour native wait remains for integration. Next cycle inspect its real result and then build latest split/fidelity complete delivery once, without requiring another owner APK trial. Actual Android15 XAPK installer/OBB mount and game completeness still unverified.


## 2026-11-02 10:10 Baghdad — virtual touch action-resolution audit (independent of active Unity build)
- Latest code/test HEAD before this handoff: `e91dd768c63b88d0f20a2d62511ba0c71bbac3d8`; only `feature/android-native-port` written. Owner-authorized split/fidelity source `b867fc29` and delivery pipeline remain unchanged. Existing native [41400935501](https://github.com/alwansan/raf/actions/runs/41400935501), job `125132421758`, remains IN_PROGRESS at Unity import/compile on immutable older source. Did not cancel or duplicate it. Cheap delivery [41403797687](https://github.com/alwansan/raf/actions/runs/41403797687) platform job SUCCESS.
- New `AndroidTouchGamepadOverlay.AuditVirtualBindings()` reads Input System 1.7.0 `ListEnabledActions(List<InputAction>)` and each active `OnScreenControl.control`, then matches the exact virtual control or its parent (for axis child bindings) against the **currently resolved original enabled action controls**. Logs bounded per-control `touch_binding_audit` and a summary at enable, edit exit and scene transition. Does not alter `PlayerInput`, original action assets, pairing, physical devices, scene or resource data. Zero matches identifies an actionable wiring gap; positive matches are NOT proof that the original gameplay responds to touch on-device.
- Source commits: `b71329f`, `8e36e0c`, `57094b4`, `e835e0e`, `e91dd76`. Updated `tests/test_android_touch_gamepad_policy.py` for read-only audit, child axes and scene refresh. Local literal source-contract smoke: 55 assertions passed, 0 failed; this is NOT a Python/Unity compile or device result. Official Input System 1.7 API documentation checked for `ListEnabledActions(List<InputAction>)` and on-screen control resolution. Wait for triggered cheap CI and next appropriate Unity build; no redundant heavy native run.
- CL historical LF evidence still belongs to prior installed APK; no new device acceptance attributed to these commits. Continue real game action mapping, original `.rgd` roundtrip, water/shaders/FMОD and complete fidelity delivery. No user action required.


## 2026-11-02 11:33 Baghdad — lossless reassembly safety while native build runs
- Verified branch HEAD before change: `efdbba5dd7619a324981cea2deb18371ade7b657`. Older standalone native [41400935501](https://github.com/alwansan/raf/actions/runs/41400935501) remains in progress at Unity Editor Android import/compile; non-opt-in split/fidelity run [41403797736](https://github.com/alwansan/raf/actions/runs/41403797736) is pending behind concurrency. No new heavy native requested or existing job cancelled. Cheap delivery [41403797687](https://github.com/alwansan/raf/actions/runs/41403797687) completed SUCCESS.
- Found an actual Termux reassembly data-loss edge case: when `<name>.assembling` already existed, `open('xb')` raised, but the generic exception cleanup unlinked the *pre-existing* file. Also `Path.exists()` alone did not protect a dangling output symlink. The reassembler now refuses pre-existing temporary files/symlinks, rejects existing/dangling output paths, and cleans up only a temporary it created itself; rechecks the output before final rename. Does not change APK, OBB, XAPK, ZIP64, hashes, resource bytes, signing, Unity scenes or GUIDs.
- Added three synthetic regressions for preserving interrupted partial assembly, refusing dangling output/temp symlinks, and removing a newly created partial file after whole-file SHA mismatch. A local isolated reproduction of these scenarios plus successful reassembly passed 5/5. Full repository CI/Unity/device tests still pending after push. This protects owner downloads and is not a gameplay acceptance claim.
- CL/raft log indexes unchanged: three LF sessions, fifteen screenshots and four logfox files; no newer device evidence. Next inspect existing native completion and cheap CI, then request ONE actual split/fidelity native+device test after old native ends if no equivalent is already running.
