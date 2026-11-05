# T5 chat — original LocalProfileStore cross-process writer-window boundary

- session_id: `20261105T1407Z-T5-chat-profile-reader-window-c8a1`
- origin: `chat`
- status: `active`
- resumed_from_sessions: `20261105T1302Z-T5-chat-delivery-e2e-f72c`; `20261105T1348Z-T5-scheduled-7c91` (newer scheduled work in a different area)
- base_sha: `0b92538ad46403bc2cdd7c3bf06b403eba88b7a4`
- issue_id: `INTEGRATION-001` (independent LOCAL-005 platform failure discriminator)
- experiment_key: `localprofile-actual-netstandard-lib-multiprocess-exclusive-writer-open-80ms-vs-2500ms-vs-corrupt-99retry-v1`
- resource_key: `t5-isolated-dotnet8-profile-race-probe`
- work_ids: `prompt/coordination/work/INTEGRATION-001/T5-20261105T1407Z-T5-chat-profile-reader-window-c8a1-original-profile-crossprocess-window.json`
- intended_files: new standalone `android-port/Experiments/T5/LocalProfileWindowProbe` files, new isolated `.github/workflows/raft-t5-local-profile-window.yml` and this T5 session, experiment and event records.
- run_urls: none yet.

## Restored verified evidence
T5 scheduled [20261105T1348Z] isolated real platform smoke failure CI42020924863 job127223188005: 16/17 smoke passed, cross-process profile initialization failed `System.IO.InvalidDataException` in `LocalProfileStore.ReadExistingId` via `ReadWhenWriterCloses`. T4 had already observed new source/platform smoke CI42028108335 17/17, but passing suite does not explain the old race. Original `LocalProfileStore.cs` source blob at baseline `d0c3105973461e14c740c0052734d4239d6d567d`: the exclusive `FileMode.CreateNew` writer publishes its pathname before flush; reader performs 99x10ms retries for IOException/InvalidDataException. Neither T4 nor T5 proved whether the old failure was caused by exceeding that window, so do not claim it was. Current most recent in-progress action at first check: platform smoke CI42041826134 on original branch SHA; do not cancel or duplicate full smoke.

Other team data: T1 Unity OpenGLCore input copies exact, FFT mismatches persist; T3 authentic bounded post-restorer 495/511 custom Material docs still Dummy-linked; T4 source-only Save/Load markers validated, no durable Android .rgd proof. Game APK86 remains last actual tested release; NOT_READY 0/3.

## Scope and controls
No production game/source edit or shared T4 runtime/smoke/workflow touched. New independent .NET8 harness will link actual `android-port/Runtime/Platform/RaftAndroid.Platform.csproj`, run a separate writer process with an exclusively held *visible but empty* `profile.id` for a short and a long interval. Child signals READY only once the file is created, before writer populates the valid GUID. Parent calls the actual `GetOrCreateProfileId`, validates aggregate outcome and eventual persisted identity match, does not print GUID. Persistent corrupt file control must fail-closed and retain bytes. Only synthetic disposable local data, no raw original game/credentials. Workflow uses ubuntu-24.04, dotnet8, timeout and isolated concurrency.

## Pending
Implement and run real source harness in standalone CI; record exact run, positive/negative outcomes, distinguishing limits, and hand off narrowed result to T4. Actual phone/game/platform-failure root cause will remain unconfirmed until proven.
