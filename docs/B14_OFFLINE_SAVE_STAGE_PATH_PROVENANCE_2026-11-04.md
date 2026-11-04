# B14 LOCAL-005 — original offline save-stage root provenance (2026-11-04)

## Observed source-side gap

Both `scripts/adapt_original_save_paths.py` and `scripts/adapt_android_offline_startup.py` verify `Assets.is_symlink()`, but Python follows a symlink in an ancestor path: when the Unity **project root** is linked, `(project / 'Assets').is_symlink()` is false while `is_dir()` is true. Both adapters also test whether a resolved backup is inside the project; a linked backup to a directory outside the project passes this test. On a valid source this permits original-data staging or a backup copy through a redirected path. This is **not** an observed device regression or evidence of an actual symlink in the build.

## Integrated repair

- [Save path adapter 02e7eef](https://github.com/alwansan/raf/commit/02e7eefb614044861eae2cfee32157e50a126378) and [offline adapter cca6e1e](https://github.com/alwansan/raf/commit/cca6e1e8f6c3a07327f811cf788a8d5d6668c099): early fail-closed scan for symlinks at the project/backup roots and their existing ancestors, before adaptation, backup creation, source write, or source/metadata mutation. Preserve all normal source SHA/gates, original .meta, .rgd serialization, offline identity, Steam boundary and Windows game behavior.
- New tests: [SaveAndLoad staging ab77a53](https://github.com/alwansan/raf/commit/ab77a53133c7bb2d2c7e8603bd6afb875d23d0aa) and [offline staging 6b8c7be](https://github.com/alwansan/raf/commit/6b8c7be8fbdafb90121efbefc2550fc4f43bbf6b) each introduce three path-redirection negative controls: linked project root, linked backup root and linked parent of backup. All check no accidental write to synthetic outside directories; existing normal fixtures remain.
- Isolated bounded [workflow 090a03b](https://github.com/alwansan/raf/commit/090a03b34e77ea0817208e7e41ca646286379d63) (Ubuntu 24.04, 5min limit, no LFS/Unity, own concurrency group, `cancel-in-progress:false`). [Run41918579185](https://github.com/alwansan/raf/actions/runs/41918579185) / job126884721688 **SUCCESS**: SaveAndLoad source-only tests **13/13**; offline adapter source-only tests **19/19**, **32/32** total, including six new negative controls. These actually execute the modified production Python adapters under synthetic inputs.
- Local POSIX baseline: project root symlink `is_symlink=True` while descendant `Assets.is_symlink=False` and `Assets.is_dir=True`; externally linked backup resolves outside the project and passed the old containment-only guard. The new source aborts early for these cases.

## Boundaries

This is a source-build staging hardening, **not** a fix for the previously observed APK86 exception `SaveAndLoad.SaveGame -> SteamUserStats.StoreStats -> steam_api64`; B50 already patched that separate gameplay boundary at source level, pending a new phone build. The actual Android world creation, playable scene, persistent `.rgd` roundtrip, IL2CPP, audio/Settings and display/device outcomes were NOT retested by this workflow. No asset/DLL/ZIP2/CL download, original .meta/GUID change or game build/release request was made. The old device evidence remains APK86 / [CI41812889049](https://github.com/alwansan/raf/actions/runs/41812889049).

## Next step

Scoped `LOCAL-005` staging-root safety **SOURCE_FIXED**; parent issue **OPEN**, overall **NOT_READY 0/3**. Next critical work is a coordinated authentic Unity/Android build and device create/save/close/reopen `.rgd` experiment using B50's StoreStats/Cheat and B07/B24 callback instrumentation, after checking current rendering readiness and running jobs. Do not weaken readiness or fake local-world flags to declare success.
