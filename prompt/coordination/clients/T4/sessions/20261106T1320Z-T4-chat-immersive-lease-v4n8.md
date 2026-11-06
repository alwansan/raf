# T4 chat — Android immersive Activity owner and generation lease

- session_id: `20261106T1320Z-T4-chat-immersive-lease-v4n8`
- origin: `chat`; status: `active`
- resumed_from_sessions: `20261106T1304Z-T4-chat-null-activity-p7h2`, `20261105T2241Z-T4-chat-immersive-bars-h8q2`
- work: `prompt/coordination/work/INPUT-005/T4-20261106T1320Z-T4-chat-immersive-lease-v4n8-immersive-activity-lease.json`
- experiment_key: `T4-INPUT005-immersive-bars-Activity-owner-lease-epoch-UI-runnable-original-Unity2021-v1`
- resource_key: `T4-immersive-source-only-ABI-workflow`

## Baseline, gap, and scope

The current AndroidImmersiveSystemBars.ScheduleHide obtains `UnityPlayer.currentActivity` to enqueue runOnUiThread, but the callback resolves it again and could hide bars on a newer, unrelated Activity. It has a focused/paused flag check, no request activity-identity or queued-generation guard. Target only this as a distinct lifecycle issue. Explicitly preserve Android OS swipes/Back/Home, 15s sparse refresh, Unity fullscreen settings, mouse/touch/keyboard/world SaveAndLoad and other team's assets. No game build. On owner phone only prior artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) confirmed save/reopen; this scope has no device claim.

## Reserved work, planned tests

Check legacy flags and WindowInsetsController still run only for original focused Activity and valid current generation. Use numeric Java Activity identity, never capture Java wrappers across threads. Invalidate on focus loss/pause/disable/restart, unit test policy with positive/negative cases and original Unity2021 managed API compile via existing T4 immersive CI (dedicated resource). T5 is running independent signed APK/OBB ZIP range CI; T1/T2/T3 and separate T4 cross-process RGD files remain untouched.

## Next

Implement, inspect exact C# + Python regressions, verify source ABI CI and log SHA/status, provide T5 a future-phone acceptance boundary.

## Implemented source checkpoint — awaiting exact CI

- Source and tests pushed on `feature/android-native-port`, final [f4b92e1](https://github.com/alwansan/raf/commit/f4b92e1da30fd78356f57ffe3c28bd72aae4be55); original runtime+policy+managed Program+Python tests modified, no workflow alteration.
- `CanApplyQueuedHide` requires nonzero owner, matching current Activity ID, nonzero matching generation, foreground focused and unpaused; `ScheduleHide` validates before getWindow; lifecycle invalidates old generation; check again immediately before modern or legacy hide. No saved Java wrapper across threads; Android swipe/transient bars policy unchanged.
- CI source only [42225179203](https://github.com/alwansan/raf/actions/runs/42225179203) on exact final SHA was pending at checkpoint. Earlier superseded pending runs 42225172874/42225166933 show cancelled by GitHub concurrency; **do not label them failures or claim T4 manually cancelled**. No native Unity/player build and no Android phone test.
- Next: inspect exact run conclusion and compile/test logs, set work/experiment result precisely. INPUT-005 OPEN; world RGD scope remains separately active; NOT_READY 0/3.
