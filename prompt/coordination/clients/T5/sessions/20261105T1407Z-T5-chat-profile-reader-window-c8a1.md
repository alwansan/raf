# T5 chat — original LocalProfileStore cross-process writer-window boundary

- session_id: `20261105T1407Z-T5-chat-profile-reader-window-c8a1`
- origin: `chat`
- status: `completed`
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


## Verified CI checkpoint — 2026-11-05 14:18 UTC

**status: completed for this bounded source-level diagnostic.** `origin=chat` remains unique from T5 scheduled sessions.

**Unchanged real runtime source:** `android-port/Runtime/Platform/LocalProfileStore.cs` Git blob `d0c3105973461e14c740c0052734d4239d6d567d`. New standalone probe at `android-port/Experiments/T5/LocalProfileWindowProbe/{Program.cs,LocalProfileWindowProbe.csproj}`, code commit [69fe4aed](https://github.com/alwansan/raf/commit/69fe4aedcdd85f4dc75149f6472a09000b12bf2b). Isolated no-Unity workflow `.github/workflows/raft-t5-local-profile-window.yml`, final [1e369deb](https://github.com/alwansan/raf/commit/1e369deb03909f20c75eda30706b5d034d716ee2).

- First [CI42042891917](https://github.com/alwansan/raf/actions/runs/42042891917) built actual C# successfully but exited early with `ArgumentException` from unsupported app arguments forwarded by workflow `dotnet run --nologo`. Corrected *only workflow invocation* to call the compiled DLL directly. No runtime patch.
- Final [**CI42043111968**](https://github.com/alwansan/raf/actions/runs/42043111968) **COMPLETED SUCCESS**, job `127298820854`. Exact safe aggregate lines:
  - `case=short writer_held_ms=300 finished_before_release=false outcome=success persisted_stable=true`
  - `case=long writer_held_ms=3500 finished_before_release=true outcome=io_failure persisted_stable=true`
  - `T5_PROFILE_PERMANENT_CORRUPTION outcome=invalid_data original_unchanged=true`
  - `T5_PROFILE_SOURCE_PROBE_PASSED actual_platform_library=true cross_process=true synthetic_data_only=true android_device=false`
- New fixture invokes exact production `new LocalProfileStore(root).GetOrCreateProfileId()` and a real **independent .NET writer process** on disposable Linux-local profile file. Child creates final `profile.id` using exclusive `FileMode.CreateNew`, leaves it empty until explicit release signal, then writes a synthetically generated valid GUID. No IDs, private data, credentials or raw game assets are logged. No game source, save schema, Steam, .meta/GUID, sound/Settings or touch modified.
- This proves an **actual bounded retry failure mode**, NOT the specific mechanism behind older [smoke CI42020924863](https://github.com/alwansan/raf/actions/runs/42020924863): that original failed with `InvalidDataException`, whereas controlled long writer produced `IOException`. Short release succeeds, permanently invalid input still fails closed. No Unity IL2CPP, Android app-private filesystem, device .rgd or gameplay proof.
- Experiment: `prompt/coordination/experiments/T5/T5-20261105T1407Z-T5-chat-profile-reader-window-c8a1-actual-crossprocess-profile-window.json`. Canonical event: `prompt/coordination/B_TEAM/events/T5/20261105T1418Z-crossprocess-profile-window.json`. Work `prompt/coordination/work/INTEGRATION-001/T5-20261105T1407Z-T5-chat-profile-reader-window-c8a1-original-profile-crossprocess-window.json` completed.
- **T4 coordination handoff:** `prompt/coordination/discussions/LOCAL-005/20261105T1417Z-T5-original-profile-writer-window-to-T4.md`. Do not change T4-owned production `LocalProfileStore.cs` without coordinating; any extended retry must remain bounded and preserve permanent corruption fail-closed/no-clobber. No original T4 work or in-progress workflow canceled.
- At close-time check: full native [run42042902522](https://github.com/alwansan/raf/actions/runs/42042902522) source `753802d75196210d721cca0f4fdec6ce7800bf0d` was **in_progress**; T1 Unity Vulkan [run42042650298](https://github.com/alwansan/raf/actions/runs/42042650298) was completed FAILURE, owned by T1. Neither implies game/device result; avoid duplicate/cancel.
- Last confirmed phone-targeted Raft release APK86 is older than T4/B50/new diagnostics; **LOCAL-005 OPEN and project NOT_READY 0/3**.

**next_step:** Let T4 review original-profile prolonged-writer repro and design a tested bounded retry/atomic publish solution if needed, preserving corrupt identity refusal and the 12-process smoke. T5 next coordinates integrated *single current immutable* native candidate/CI evidence after run42042902522 reaches terminal; if failed inspect its actual earliest failing job and avoid wasting shared Unity mutex. Distinguish ongoing T1 water/FFT and T3 ShaderLab work from this source-only profile probe. 
