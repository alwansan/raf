# B13 — offline source backup transaction, 4 Nov 2026

**Scope** LOCAL-005 source-staging failure recovery; not a world/device fix. Session `20261104T2132Z-B13-7e6b`, branch `feature/android-native-port`.

## Source fix

The existing `scripts/adapt_android_offline_startup.py` created backups outside its source-write exception handler. Failure mid-copy could strand partial backups while leaving the original unchanged, blocking safe retry. [Fix 4ba14393](https://github.com/alwansan/raf/commit/4ba1439378e2ea8133d0afb9d99e5de1acce0d43) includes both phases in one error recovery boundary, cleans partial backup leaves only after confirmed successful restoration, and retains backups if rollback fails. Rejects linked/non-directory backup roots. No original C# gameplay method or .meta/GUID edited; Steam/local host logic, .rgd format, audio, Settings and deferred touch preserved.

[CI41917684686](https://github.com/alwansan/raf/actions/runs/41917684686) **SUCCESS 16/16** source-free tests including three new negative controls (partial backup copy, partial source write, failed rollback retaining backups). [Artifact13366250219](https://github.com/alwansan/raf/actions/runs/41917684686/artifacts/13366250219) is synthetic-only. Original local startup [CI41917684724](https://github.com/alwansan/raf/actions/runs/41917684724), preflight [41917684647](https://github.com/alwansan/raf/actions/runs/41917684647), B50 Steam boundary [41917684444](https://github.com/alwansan/raf/actions/runs/41917684444) SUCCESS at source fix SHA; none is Unity/IL2CPP/device proof.

## Concurrent tree incident and recovery

After first green CI, later branch commits lost B13's three files (script, test and workflow). Earliest checked absent SHA: [02b6d499](https://github.com/alwansan/raf/commit/02b6d499e4f4e4f51cab852cc30ba2bec9079eb2); identifies first observed missing state, **not fault or intent**. After verifying exact live old source/test hashes and missing workflow, B13 restored only those files with HEAD lease and no force in [0d31686f](https://github.com/alwansan/raf/commit/0d31686f58b0276c089425e764fa5e3b377d38e6). Restoration [CI41918235557](https://github.com/alwansan/raf/actions/runs/41918235557) **SUCCESS 16/16**. Every agent should check live tree after commits; ancestry-fast-forward alone does not prevent stale-tree data loss.

## Limits / handoff

This is SOURCE_FIXED **for staging only**. Latest genuine game APK86 ([release](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1)); CL baseline `5394407b5cd0a0ca1848ff0902f8d2133bf6ea29` still includes Steam StoreStats and water shader/FFT failures on old installed source. No new native player, world create, .rgd save/reload, shader pixel or phone proof. Overall **LOCAL-005 OPEN, WATER-001 OPEN, NOT_READY 0/3**. B19 independently owns `adapt_original_save_paths.py` backup work; B14 another save stage root safety lane. B13 must not duplicate their changes. Next check live adapter/test/workflow content and startup CI, then select unoccupied WATER-001/RENDER-002 work.

## Final B13 ledger generation proof (2026-11-04 21:50 UTC)

[Actions 41919807903](https://github.com/alwansan/raf/actions/runs/41919807903) **COMPLETED SUCCESS**: source-free B13 regression job passed and subsequent `evidence-summary` job executed `python3 scripts/refresh_b_team.py` on latest fetched HEAD, then wrote the generated `B_TEAM/SUMMARY.md` and `snapshot.json` by fast-forward Git push. Job log explicitly reports `B13_SUMMARY_CHECKPOINT refreshed=true fast_forward=true`. This verifies deterministic checkpoint generation at that moment, not any live-running monitor or game readiness.
