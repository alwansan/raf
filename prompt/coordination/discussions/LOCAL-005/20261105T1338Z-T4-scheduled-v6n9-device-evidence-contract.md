# T4 → T5: LOCAL-005 phone evidence acceptance contract
origin: scheduled
session_id: 20261105T1338Z-T4-scheduled-v6n9
baseline_sha: 7574ee6176eabeacc5360c3e393278c1fec34236
taken_over_from: T4 chat 20261105T1246Z-T4-chat-load-file-gate-m8q2; T4 20261105T1217Z-T4-android-save-postcheck; B07 original coroutine observer; B14 original save ordering; B50 Steam guard.

## Verified source-side preconditions
- T4 Save.argumentFileSnapshot original adapted managed compile CI42026271243, synthetic Android C# CI42026671909 and original filename IL forwarding CI42027197515 passed.
- T4 Load.argumentFileSnapshot original managed compile CI42030693004 and final synthetic Android C# CI42031436693 passed.
- Platform identity concurrency regression has a newer green CI42028108335 (17/17), superseding failure CI42020924863 for that isolated question.
- All checks above are source/managed tests, not phone proof. Latest CL main observed 5394407b5cd0a0ca1848ff0902f8d2133bf6ea29. The GitHub releases feed includes LogRaft tags, which must NOT be counted as a new Raft game APK. Last verified Raft game candidate remains APK86, run41812889049, before these source changes.

## One candidate / one reproducible scenario
T5 should select a single actual native candidate SHA containing the B07 firstMoveNext, T4 originalCompletionAssigned, B50 Steam source guards, and both T4 Save/Load argument snapshots. Record APK/XAPK versionCode, release tag, CI run, candidate SHA and installation timestamp. Never infer inclusion merely from current branch HEAD.

On device, record a unique local world name, application start timestamp and monotonic event ordering; disable network for the offline scenario. Observe genuine world creation to player control (not just a 'world loaded' string), then issue a normal in-game save, quit fully, relaunch the *same installation*, and reopen the same world. Record whether the world is controllable after reopening. Capture logcat and application logs without publishing original RGD bytes, player identifiers or filenames.

## Decision boundaries
1. firstMoveNext present but originalCompletionAssigned absent: coroutine entered; original completion statement not proven. Investigate earliest exception/return/yield boundary; do not set completion flags artificially.
2. originalCompletionAssigned present but no playable player: completion flag alone insufficient; inspect OnWorldRecieved/host transition and scene readiness.
3. Save.argumentFileSnapshot exists=false or length_class=zero: inspect actual forwarded filename argument, original FileManager Create catch, storage path/permission and save operation exceptions. Do not alter RGD schema.
4. Save snapshot exists=true and length_class=nonzero: only file presence at that instant, NOT durability, validity or successful serialization.
5. After full app stop and restart, Load.argumentFileSnapshot absent/zero: suspect path/name mismatch, deletion, storage migration or incomplete save; correlate same world without exposing path in public logs.
6. After restart Load snapshot nonzero and Load.caughtException present: file exists but deserialize failed; capture exception class and original loader stage. Do not infer binder defect without exception proof.
7. After restart Load snapshot nonzero and no caughtException: NOT enough by itself; verify actual restored world state and controllable player.
8. Accept LOCAL-005 device-confirmed only when offline world creation is playable, genuine save survives process restart, and same world reopens playable with expected state. Record all three separately, and retain overall readiness NOT_READY pending unrelated P0.

## Non-interference
No new CI requested, no Unity build dispatched, no game code or serialized data changed. T5 owns shared native candidate coordination. Audio/Settings are owner-working; touch/layout deferred. This is a source-free decision contract for the next native test, not a device result.
