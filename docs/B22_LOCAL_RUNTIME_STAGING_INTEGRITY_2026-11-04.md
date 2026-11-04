# B22 — Android world/save operation instrumentation staging integrity (2026-11-04)

## Issue and distinction

APK86 still fails local world/save on-device after WorldHasBeenLoaded at a Steam stats boundary. B50's source-stage guard retains the real save and prevents SteamUserStats.StoreStats() native DLL loading for Android local profile, but has not had device retest. B07/B24 improved callback tracing. This B22 track DOES NOT alter the original SaveGame/Steam behavior or make world loading succeed.

The already-integrated [runtime instrumentation adapter](../scripts/instrument_android_runtime_operations.py) had a separate *source staging* correctness risk: apply() checked only whether backup was within project after resolving paths, and checked leaf .cs/.meta symlinks but not linked project/Assets/source parent or backup ancestry. Its backup copy loop ran before the try/rollback and could strand a partial backup on copy failure; on failed original restoration it had no explicit backup-retain guard. This is independent from the earlier B14 patch for adapt_android_offline_startup.py.

## Production source correction

[Fix 2f50776d](https://github.com/alwansan/raf/commit/2f50776dfe51a5d856f3d0484a8b788ee09c04bd) now:
- Preflights physical project, Assets, source/meta and backup ancestry; rejects redirecting symlinks, absent/nonregular metadata and collisions, and backup within project.
- Copies original source and existing metadata into backup before any source mutation, and checks backup bytes against original.
- Treats copy and install as one protected transaction. If install fails, restores original source and checks source/meta bytes; if restoration itself fails, retains the verified backups for recovery rather than destroying them. If originals remain intact or restoration succeeds, removes only this attempt's backup targets, leaving pre-existing unrelated content.
- Keeps unchanged SaveGame operation wrapping, Android offline stats guard, original .rgd serialization and .meta/GUID data; no fake world flags, silent omission of errors, or new external dependency.

## Independent executable evidence

- [Source commit 2f50776d](https://github.com/alwansan/raf/commit/2f50776dfe51a5d856f3d0484a8b788ee09c04bd)
- [14 synthetic staging tests](../tests/test_b22_runtime_stage_integrity.py) and [B22 isolated workflow](../.github/workflows/raft-b22-runtime-stage-integrity.yml)
- [CI run 41920661518](https://github.com/alwansan/raf/actions/runs/41920661518), job126891961921 **COMPLETED SUCCESS**: Python syntax, 14 new tests plus pre-existing tests/test_runtime_operation_traces.py pass. B22 tests include redirected project/source/backup paths, linked metadata, failed backup copy, failed source write with original rollback, failed rollback retaining backup, backup collision, dry-run and normal staging. No original game source file was staged or modified in CI.

The deliberate rollback-failure negative control proves backups are retained even if an original source could not be restored; this is not an invitation to continue automatically in that situation. A real encountered rollback failure requires recovery from the retained authenticated copy before any new import. The tests are synthetic and not an original managed/Unity/phone test.

## Remaining and next step

A subsequent already-justified Unity native import should confirm the staging adapter runs on the actual authenticated source and preserves .meta/GUID, then a new signed APK+OBB/XAPK tested by the owner must prove create/save/.rgd reload into a playable world. The known SteamStoreStats source fix also needs phone verification. This change addresses only safe staging; it does not claim to fix the world connection screen or water/FFT/colors. LOCAL-005, WATER-001, RENDER-002 remain OPEN, NOT_READY and 0/3 full independent reviews. Audio and Settings are owner-confirmed working and untouched, touch/layout deferred; no native build, original game bytes, release, CL data, tasks or protected branches modified.

Final syntactic test cleanup [ee76eeec](https://github.com/alwansan/raf/commit/ee76eeec16575488f529ee5e31df4d20d2742113) removes an inert expression from a test, not production logic. [Latest CI41921049831](https://github.com/alwansan/raf/actions/runs/41921049831) completed SUCCESS on exact cleanup commit, rerunning all new and existing synthetic operation tests; replaces the prior pending test status. No original or device claim.
