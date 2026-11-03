# A6 — LOCAL-005 Unity Assets root symlink guard (3 November 2026)

**Scope:** original source staging helpers only. This report does **not** establish successful gameplay/world initialization or original `.rgd` save/load on Android.

## Executable fault reproduction

The original `scripts/adapt_original_save_paths.apply()` and `scripts/adapt_android_offline_startup.apply()` selected original C# source under `project/Assets` using `Path.rglob`, then rejected only leaf-file symlinks. Python on Linux **does traverse a symlink when it is itself the root passed to `rglob`**. Synthetic POSIX fixture: `project/Assets` is a symlink to a separate temporary `external-originals` directory containing ordinary `Assembly-CSharp/SaveAndLoad.cs` or `Settings.cs`. Before guards, both adapters accepted these external sources and could rewrite the external test file. No original Raft source was mutated by the fixtures.

Test-only commit [d2db847142f0a1bb316434aa4c5f86fe5f9a4a8d](https://github.com/alwansan/raf/commit/d2db847142f0a1bb316434aa4c5f86fe5f9a4a8d) added two regression fixtures to existing test files, checking rejection **before** any backup creation and byte-for-byte preservation of external source and synthetic `.meta`. Intentional RED runs:

- [Save-path CPU CI 41644077257](https://github.com/alwansan/raf/actions/runs/41644077257): **FAILED** specifically at `test_symlinked_assets_root_is_rejected_before_original_save_source_is_touched`; `ValueError not raised`, 1/5 save tests failed.
- [Original Android startup CPU CI 41644077268](https://github.com/alwansan/raf/actions/runs/41644077268): **FAILED** specifically at `test_symlinked_assets_root_cannot_redirect_original_offline_source`; `ValueError not raised`, 1/9 adapter tests failed.

## Source correction and green evidence

- [Original save path source commit 33afc2ac8f7868f4ed74bff00208d2711a9c43f9](https://github.com/alwansan/raf/commit/33afc2ac8f7868f4ed74bff00208d2711a9c43f9) refuses `Assets.is_symlink()` and non-directory roots before the original filename scan. [Save-path CI 41644415213](https://github.com/alwansan/raf/actions/runs/41644415213) **COMPLETED SUCCESS**: 5/5 save portability tests and 4/4 existing A10 selector tests; independently SHA-pinned private decompilation of original SaveAndLoad, 16 expression rewrites, 14 Unix/Windows .NET path checks, diagnostic no Unity.
- [Original local startup source commit da4b98a63cf008c05249046595fee10fb2976d09](https://github.com/alwansan/raf/commit/da4b98a63cf008c05249046595fee10fb2976d09) adds the same guarded Assets-root validation before scanning the 12 original game source classes. [Original offline integration CI 41644473219](https://github.com/alwansan/raf/actions/runs/41644473219) **COMPLETED SUCCESS** at exact source `da4b98a6`: 9/9 offline adapter tests including the new negative, 5/5 save tests, further source-contract tests; authenticated original private managed compilation exited `0`, `errorCodes={}`, without publishing game source. [Reconstruction preflight 41644472847](https://github.com/alwansan/raf/actions/runs/41644472847) also **COMPLETED SUCCESS** on the same source SHA.
- Only two source helper scripts and two test scripts were modified by A6. Previous A10 original-source transaction code, A9 local profile, A8 world probe and all other agents' source were not touched.

## Exact limits

These checks protect only a pre-existing symlinked `Assets` directory root, not a transaction/no-follow guarantee for adversarial concurrent filesystem mutation or a global audit of every ancestor symlink. The original game `.rgd` serialization and original assets, `.meta`/GUIDs remain untouched; `SaveAndLoad.cs` private original SHA pin still applies. A green source compile is not an Android Unity build or device gameplay test. The real pre-Unity builtin shader no-match failure [41624581951](https://github.com/alwansan/raf/actions/runs/41624581951) remains a separate unresolved blocker. **LOCAL-005 original game create/load/resume is still open; WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; NOT_READY, 0/3 full independent candidate reviews.** No native/Unity/APK/OBB/XAPK build, LFS transfer, Release, native request, schedule, CL write, or protected branch mutation by A6.
