# A6 LOCAL-005 — original source backup dangling-link redirect (2026-11-03)

Identity: raft-20261103T145401Z-051434ed; session a6-20261103T145401Z-ba243dcc; resumed_from `raft-20261103T132000Z-a6e7f219`. Write scope only `feature/android-native-port`.

## Bounded defect and evidence

Both original C# source adapters used `Path.exists()` to protect a destination such as `backup/SaveAndLoad.cs` or `backup/Settings.cs` before `shutil.copy2`. A dangling symbolic link has `exists() == False` but `is_symlink() == True`; `copy2` follows it and can create the link target **outside backup**. A Linux temporary-file POSIX reproduction confirmed creation of an outside synthetic file. This is a source-backup staging defect, not proof of a device-exploitable save-file path.

New isolated synthetic tests (no private game content):
- `test_dangling_backup_leaf_cannot_redirect_original_save_source`
- `test_dangling_backup_leaf_cannot_redirect_original_offline_source`

Source [RED 3c3c5cbc](https://github.com/alwansan/raf/commit/3c3c5cbc286d2ed9b8ca6ae3ad7f5e9773b20606):
- [save workflow 41658800717](https://github.com/alwansan/raf/actions/runs/41658800717): FAILED, 1/6 synthetic save tests, `AssertionError: ValueError not raised`.
- [offline workflow 41658800643](https://github.com/alwansan/raf/actions/runs/41658800643): FAILED, 1/10 offline-adapter tests, same assertion. Expected RED; do not misattribute to compiler.

Source fixes:
- [d922f999](https://github.com/alwansan/raf/commit/d922f999c11bbd2e9b02fef5bc4ea945d0eb8f1e) rejects `exists() OR is_symlink()` for each original SaveAndLoad source/meta backup destination.
- [b6a96201](https://github.com/alwansan/raf/commit/b6a962018e06513d5cf408e646751f161f0e00ca) applies equivalent check to each pinned original offline source/meta backup destination.

Same-source CPU green:
- [save CI 41659075182](https://github.com/alwansan/raf/actions/runs/41659075182), head d922f999, COMPLETED SUCCESS: original save 6/6 and A10 selector 4/4; SHA-pinned original SaveAndLoad path adaptor and 14 .NET path behavior checks completed.
- [offline CI 41659111730](https://github.com/alwansan/raf/actions/runs/41659111730), head b6a96201, COMPLETED SUCCESS: offline tests 10/10, save tests 6/6 plus independent integration suites; original private managed compile `exit=0 errorCodes={}`.

The original .meta bytes/GUIDs, game sources, .rgd serialization, touch, audio/shaders, and native request were not modified. Test-only copies were synthetic. No Unity import, APK/OBB/XAPK, release, LFS hydration, Android phone, automation or CL write occurred.

## Scope limits and follow-up

This hardens **pre-existing** linked backup destinations; it is not an atomic filesystem sandbox or complete anti-TOCTOU defense against an actively changing malicious tree. LOCAL-005 original single-player world creation, save/load/resume of authentic .rgd and device acceptance remain OPEN. WATER-001/RENDER-002/FFT-FORMAT-009 remain blocked, overall NOT_READY and full independent reviews 0/3. Future candidate must be evaluated by the separate readiness/build coordinator.

## Coordination incident

During initial batched Git ref updates, three calls returned transient GitHub GraphQL UNKNOWN; a subsequent live read confirmed both old source guards were still present. Switched to file-SHA conditional source writes and verified both new commits and CI. No force push, other session state edit, protected branch or cancellation.
