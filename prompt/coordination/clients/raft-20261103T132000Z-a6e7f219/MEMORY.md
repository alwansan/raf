# A6 — LOCAL-005 original source Assets root symlink guard

Identity `raft-20261103T132000Z-a6e7f219`; resumed from completed prior A6 `raft-20261103T121333Z-a6c7f4e2`. Branch `feature/android-native-port` only. No Unity, APK/OBB/XAPK, native request, protected branch, LFS or CL writes.

Read live prompt/README, CONTINUE_RAFT_AR, STATUS, CURRENT_OWNER_REQUIREMENTS, AGENTS, coordination README, handoff/readiness; Actions/recent commits and LOCAL-005 work. Other A10 original managed staging transaction, A9 profile, A8 world probe scopes completed. Initial HEAD `33c30f81dddf608413e1a28697b0b161725e2b46` before registration.

## Hypothesis

Both `scripts/adapt_original_save_paths.py` and `scripts/adapt_android_offline_startup.py` scope original source to `project/Assets` via `rglob`, but reject only the terminal file symlink, not `Assets` itself. Python on Linux traverses a directory-symlink used as the **root** of `rglob`; a temporary POSIX experiment showed `project/Assets -> outside` returns `project/Assets/Assembly-CSharp/SaveAndLoad.cs`. This permits the generated-project stage to read and write source bytes from outside the intended project without the original file itself being a link. Independently, the previous native built-in shader restore path already rejects a linked Assets root.

Plan: bounded fail-closed check for Assets-root symlink/non-directory before discovery in both original source adapters. Two synthetic negative tests assert no external source/meta mutation and no backup creation; existing normal fixtures and private original compile paths remain. Record red/green CIs; never claim real .rgd world runtime or phone proof. Owner requires NOT_READY/0-of-3 until all genuine blockers and independent reviews close.
