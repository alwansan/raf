# A6 — LOCAL-005 original source Assets root symlink guard

Identity `raft-20261103T132000Z-a6e7f219`; resumed from completed prior A6 `raft-20261103T121333Z-a6c7f4e2`. Branch `feature/android-native-port` only. No Unity, APK/OBB/XAPK, native request, protected branch, LFS or CL writes.

Read live prompt/README, CONTINUE_RAFT_AR, STATUS, CURRENT_OWNER_REQUIREMENTS, AGENTS, coordination README, handoff/readiness; Actions/recent commits and LOCAL-005 work. Other A10 original managed staging transaction, A9 profile, A8 world probe scopes completed. Initial HEAD `33c30f81dddf608413e1a28697b0b161725e2b46` before registration.

## Hypothesis

Both `scripts/adapt_original_save_paths.py` and `scripts/adapt_android_offline_startup.py` scope original source to `project/Assets` via `rglob`, but reject only the terminal file symlink, not `Assets` itself. Python on Linux traverses a directory-symlink used as the **root** of `rglob`; a temporary POSIX experiment showed `project/Assets -> outside` returns `project/Assets/Assembly-CSharp/SaveAndLoad.cs`. This permits the generated-project stage to read and write source bytes from outside the intended project without the original file itself being a link. Independently, the previous native built-in shader restore path already rejects a linked Assets root.

Plan: bounded fail-closed check for Assets-root symlink/non-directory before discovery in both original source adapters. Two synthetic negative tests assert no external source/meta mutation and no backup creation; existing normal fixtures and private original compile paths remain. Record red/green CIs; never claim real .rgd world runtime or phone proof. Owner requires NOT_READY/0-of-3 until all genuine blockers and independent reviews close.

## Verified A6 RED/GREEN checkpoint 2026-11-03T13:29:48.985Z

- Source-stage bug: root `project/Assets` symlink traversed by `Path.rglob`; child `SaveAndLoad.cs`/`Settings.cs` not a link, and previous helper guards were bypassed. Local POSIX filesystem reproduction confirmed root traversal; no original game files used in synthetic fixture.
- [Test-only red d2db847](https://github.com/alwansan/raf/commit/d2db847142f0a1bb316434aa4c5f86fe5f9a4a8d) added one synthetic rejection fixture per source adapter. [RED 41644077257](https://github.com/alwansan/raf/actions/runs/41644077257): 1/5 save tests failed at ValueError not raised; [RED 41644077268](https://github.com/alwansan/raf/actions/runs/41644077268): 1/9 offline startup tests failed same way.
- [Save guard 33afc2](https://github.com/alwansan/raf/commit/33afc2ac8f7868f4ed74bff00208d2711a9c43f9) and [offline guard da4b98a63cf008c05249046595fee10fb2976d09](https://github.com/alwansan/raf/commit/da4b98a63cf008c05249046595fee10fb2976d09) require actual non-symlinked Assets directory before original-source search. They do not modify the original `.rgd` format, game code assets or .meta/GUID.
- [GREEN save-path CI 41644415213](https://github.com/alwansan/raf/actions/runs/41644415213) COMPLETED SUCCESS: 5/5 save tests +4/4 original selector; private SHA-pinned SaveAndLoad source verified 16 expressions/14 .NET path checks.
- [GREEN offline integration CI 41644473219](https://github.com/alwansan/raf/actions/runs/41644473219) COMPLETED SUCCESS at exact source da4b98a63cf008c05249046595fee10fb2976d09: 9/9 Android offline adapter, 5/5 original save, original private managed compile exit0 errors{} and other upstream contracts; [reconstruction preflight 41644472847](https://github.com/alwansan/raf/actions/runs/41644472847) SUCCESS same source.
- Evidence report `docs/A6_LOCAL005_ASSETS_ROOT_SYMLINK_2026-11-03.md`; issue overall LOCAL-005 OPEN for original world RGD/full game/device. Shader WATER-001/RENDER-002/FFT-FORMAT-009 OPEN; NOT_READY, 0/3. No Unity/native/APK/OBB/XAPK/release/LFS/task changes.
- Scoped A6 fix complete; paused so future explicit Continue chooses a new deconflicted source experiment after refreshing live state.
