# T4 chat — Android runtime logger startup retry after transient storage fault

- session_id: `20261106T1704Z-T4-chat-android-logger-startup-retry-x7m2`; origin: `chat`; status: `active`
- base_sha: `e45f57f1f236b1ca4096408c1f2cf5375bd3eb5a`
- scope work: `prompt/coordination/work/LOCAL-005/T4-20261106T1704Z-T4-chat-android-logger-startup-retry-x7m2-startup-retry.json` at commit `98c90104f3481d2bcfd04dffe90e3a068315688b`.
- resumed_from_sessions: `20261106T164053Z-T4-chat-logger-recovery-status-k7m4` (completed logger LastError source red/green CI42254862695 / CI42255132103), `20261106T1637Z-T4-scheduled-v8m2` (scheduled physical mouse source provenance), and earlier original owner save cross-process results.
- Last owner-signed phone proof [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) at source `e9c358eda01785b65e4eb14f18723da426635628` is playable world/save/exit/reopen; it is not evidence of later code on device.
- T1/T2 shader work, T3 colors, T5 OBB and native delivery are independent; latest T5 first-byte installed OBB source probe [42257103707](https://github.com/alwansan/raf/actions/runs/42257103707) SUCCESS, no phone Unity/OBB mount proof. At initial check branch Actions no in_progress/queued; no native request or cancellations.

## Bounded independent hypothesis
`AndroidRuntimeLog.Initialize` currently returns immediately when either `sink != null` **or** `StorageError != null`. A single failed `PersistentDiagnosticLog` directory open can therefore permanently suppress all later explicit initialization, even after the backing app sandbox becomes writable. This is evident in current source; no proof such fault occurred on owner's device.

Target ONLY `android-port/Runtime/Platform/AndroidRuntimeLog.cs`, existing source-only `android-port/Tests/Diagnostics/{Diagnostics.csproj,Program.cs}` and test-only `UnityEngineStubs.cs`. Test the exact conditional Android logger C# source compiled under `UNITY_ANDROID` with synthetic Unity API members. First create a deterministic failing fixture: app persistentDataPath refers to a regular file, initial Initialize records StorageError, replace file with directory, second Initialize must create logger.ready and clear StorageError, preserve no duplicate creation and valid private JSONL. Red CI first. Patch source minimally: keep sink non-null guard, enable later explicit retry when sink was never created, only clear StorageError after success; do not change original game/serialization, Unity scenes, input, shader/audio, OBB, native/REAs or schedule.

Work status active until real source-only gate and source SHA verified. LOCAL-005 remains OPEN; Android/IL2CPP/phone startup status UNKNOWN. Next: red/green isolated CI and independent event/T5 handoff.
