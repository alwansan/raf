# B19 — Original SaveAndLoad hard-link alias safety, 4 November 2026

Session `20261104T2256Z-B19-hl7`; issue `LOCAL-005`. This is a source-stage integrity fix, **not** a world/save/runtime fix.

## Reproduced failure primitive

On Linux, `Path.hardlink_to(source)` creates another regular path referencing the same inode; both `is_symlink()` checks remain false, while `st_nlink == 2`. A test wrote `adapted-source` with `source.write_bytes()` and the unrelated external alias changed from `original-source` to `adapted-source`. Before B19's change, `apply()` tested symlinks but not hardlink counts, then used `path.write_bytes(encoded)`. In a nonstandard/aliased staging tree this could modify data outside Unity Assets; **this is synthetic risk, not evidence of an APK86 incident**.

## Integrated guard and tests

[Source guard commit](https://github.com/alwansan/raf/commit/2d59494d4c77c715ab76ef0b5ac21b566059c6d5) rejects original SaveAndLoad source or sidecar `.meta` with `stat().st_nlink != 1` before the backup/publish/source-write transaction. [Negative controls commit](https://github.com/alwansan/raf/commit/89455426b6a9c1cafd4651e671e558dc12bb80d2) adds independent source-hardlink and metadata-hardlink fixture cases and asserts original/alias bytes untouched and no backup emitted. Existing normal-source positive and rollback paths remain checked.

[Final original-save path CI41929845587](https://github.com/alwansan/raf/actions/runs/41929845587) **SUCCESS** on `89455426b6a9c1cafd4651e671e558dc12bb80d2`: 15/15 save-path synthetic tests including two new hardlink negatives, 11/11 ZIP2-provider checks, 4/4 SaveAndLoad-source selector checks; authenticated pinned original ZIP2 source was decompiled and 16 source path expressions verified idempotent with unchanged non-path content; .NET10 Unix/Windows path checks succeeded. [Earlier source-only CI41929800274](https://github.com/alwansan/raf/actions/runs/41929800274) passed before the two new tests. Test command: `python3 -m unittest discover -s tests -p test_adapt_original_save_paths.py -v`; CI runs the pinned-original validation in `.github/workflows/raft-original-save-path-tests.yml`.

Original private SaveAndLoad source SHA256 `b150dd404da48b8012f6659680b3552c11500c4ec97a64ad9aa12c60094568bb`; ZIP2 provider ref `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. This change does not modify original content, serialized `.rgd`, Steam identity, gameplay flags, `.meta` GUID bytes, FMOD, Settings, deferred touch, Unity build request or APK.

## Limits and follow-up

Hardlink preflight is not a defense against hostile concurrent inode replacement (TOCTOU). No original Raft source file in current Unity stage was shown to be hardlinked; this is a deterministic guard rather than a confirmed user-facing issue. On-phone LOCAL-005 remains OPEN: APK86 logs still show `SteamUserStats.StoreStats -> SaveAndLoad.SaveGame -> WorldHasBeenLoaded` missing `steam_api64`; newer source fixes need an integrated native candidate and phone create/save/reopen verification. The overall project remains NOT_READY (0/3 independent full immutable reviews), WATER-001 and RENDER-002 OPEN. Next B19 cycle should choose another distinct P0 dependency rather than repeat hardlink/symlink safety checks.
