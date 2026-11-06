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

## Exact final CI and safe conclusion

- [Commit f4b92e1](https://github.com/alwansan/raf/commit/f4b92e1da30fd78356f57ffe3c28bd72aae4be55) final source+tests; intermediate source commit 0533e5e and runtime 3fbd63b are not final acceptance. These edits are only AndroidImmersiveSystemBars.cs, AndroidSystemBarPolicy.cs, its managed test Program and Python source tests. No game source, resources, input, HUD, resolution, SaveAndLoad, .rgd or workflow changed.
- [T4 CI42225179203](https://github.com/alwansan/raf/actions/runs/42225179203) exact source f4b92e1 **COMPLETED SUCCESS**, job 127916846161, step log: **9/9 Python** incl ownership/lifecycle source contracts; **28/28 executable C#** legacy+queued lease positive/negative cases; authenticated ZIP2 original Assembly-CSharp managed ABI source gate; **original Unity2021 Android JNI/Core C# compile success**. Workflow explicitly printed `AndroidPlayerBuilt=false DeviceVerified=false`.
- Distinguish GitHub Actions cancelled intermediate pending 42225166933 and 42225172874 due group concurrency; T4 did not cancel jobs. Initial policy-only CI42225154463 also success but not final source. T1/T2/T3 water and T5 ZIP runs left alone.
- Identity/token: `System.identityHashCode` opaque numeric identity captured for request and compared only to current UI-thread Activity. `hideGeneration` invalidates queued requests on focus, pause, disable and enable, and modern/legacy hide double-check token immediately before mutation. No Java wrapper retained across threads, no OS Back/Home block or gesture exclusion. Numerical identity collision remains theoretically possible; full device window recreation/gesture behavior not proven.
- Work `prompt/coordination/work/INPUT-005/T4-20261106T1320Z-T4-chat-immersive-lease-v4n8-immersive-activity-lease.json` complete for bounded source/ABI fix. Experiment `prompt/coordination/experiments/T4/20261106T1320Z-T4-chat-immersive-lease-v4n8.json`; event and T5 discussion to be linked. **INPUT-005 OPEN** and unrelated LOCAL-005 device candidate work remains OPEN; overall NOT_READY 0/3.
- Next: T5 next signed Raft APK+matching OBB with exact SHA/source provenance. Owner real Activity focus/home/pause/recreate and screen-edge swipe/Back/Home test with mouse+keyboard, menu/game transition and saved world force-stop/reopen, post-marker private logs. Do not consider source-only test Android acceptance.
