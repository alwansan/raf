# T5 chat — original-managed offline compile dependency restoration

- session_id: `20261106T1702Z-T5-chat-offline-obb-compile-58cf`
- origin: `chat`
- issue_id: `INTEGRATION-001` (LOCAL-005 offline compatibility compile, not game acceptance)
- resumed_from_sessions: `20261106T1649Z-T5-scheduled-runtime-attribution-c82f` (separate PERF-007), `20261106T1541Z-T5-chat-obb-routes-b8a1`, active `20261106T1645Z-T5-chat-installed-obb-read-e7c4` (different file owner)
- base_sha: `d8b014363bcfcf82cbcb496a81e512acad60b7d8`
- work: `prompt/coordination/work/INTEGRATION-001/20261106T1702Z-T5-chat-offline-obb-compile-58cf.json` created at commit `30ba282d9b17e2e3419218c57ec0c62d4099f47f`.
- experiment_key: `T5-42256234615-offline-compile-CS0103-AndroidExpansionArchiveProbe-missing-copy-dependency-v1`
- intended_files: `scripts/verify_android_offline_candidate.py`, `tests/test_t5_offline_runtime_support_deps.py`, `.github/workflows/raft-android-offline-integration-tests.yml`, this session, own work/experiment/event.
- resource_key: source-only managed compatibility build; no shared Unity native/OBB or runner lock.
- status: active

## Confirmed failure before repair
[Original managed integration CI 42256234615](https://github.com/alwansan/raf/actions/runs/42256234615), job 128024049155, completed failure. The compile-private log summary is `errorCodes={'CS0103': 2} affectedFiles=[('RaftAndroid-AndroidTestDiagnostics.cs', 'CS0103')]`. Live `AndroidTestDiagnostics.cs` references `RaftAndroid.Platform.AndroidExpansionArchiveProbe.Inspect`; `scripts/verify_android_offline_candidate.py` copies an explicit subset of native runtime files into the private original gameplay project, excluding `AndroidExpansionArchiveProbe.cs`. This is a test build coverage regression, not evidence of Unity IL2CPP or phone failure.

## Conflict check
T5 concurrent chat owns `AndroidTestDiagnostics.cs` and its installed OBB probe workflow; T5 scheduled owns LogRaft performance process-epoch guard; T1–T4 own the graphics/world/mouse fixes. Do not touch those files, repeat previous signed OBB scans, or dispatch a full Unity build.

## Planned test
Preflight and copy complete runtime compilation dependencies, add a negative test for missing file, include test+probe in workflow trigger, then use the existing cheap full original-managed CI as the deciding runtime compilation evidence.

- run_urls: [42256234615](https://github.com/alwansan/raf/actions/runs/42256234615) (failure, old SHA)
- next_step: publish scoped source change + new test, examine exact source CI result, save verified evidence and unresolved device limitations.

## Final checkpoint — 2026-11-06T17:06:50.603Z

- **status: completed (scoped source CI repair)**.
- **Source commits:** allowlist + preflight `261c1434b9ac47274da604912096785a4878853a`; four regression tests `3fd471eb1df5b6831ac4b800f1e241e1a38fb1bc`; workflow trigger/test hook `591e6e7da79b69916f8fe9a63f6242a17c226934`.
- **CI:** [42258190836](https://github.com/alwansan/raf/actions/runs/42258190836), job **128030880997**, exact code `591e6e7da79b69916f8fe9a63f6242a17c226934`, **completed SUCCESS 2026-11-06T17:05:01Z**. New adversarial test **4/4 PASS**, selected private original-managed source units 14, authentic adapted original local RPC/identity test PASS, and **`RAFT_OFFLINE_COMPILE exit=0 errorCodes={} affectedFiles=[]`**. Prior original source CI [42256234615](https://github.com/alwansan/raf/actions/runs/42256234615) had two CS0103 on copied AndroidTestDiagnostics. Result establishes that the missing compiler unit regression was addressed for the original managed diagnostics build.
- **Current head retention check:** branch still contains same blobs for script `916f1da991392e10fa9ca7d4496697ee3e80d7b0`, workflow `9331e6deb5bfa02a3961fc28e5dd2b515d69f6fd`, tests `74951a591bf7613290c10072249734900ab9ca6d`.
- **Wrote scope:** `prompt/coordination/work/INTEGRATION-001/20261106T1702Z-T5-chat-offline-obb-compile-58cf.json` (completed), `prompt/coordination/experiments/T5/20261106T1702Z-T5-chat-offline-obb-compile-58cf.json` (result), and own canonical event `prompt/coordination/B_TEAM/events/T5/20261106T1702Z-T5-chat-offline-obb-compile-58cf.json`.
- **No unauthorized overlap:** other T5 chat retains owner of runtime OBB probe `AndroidTestDiagnostics.cs` and native pipeline; scheduled T5 retains PERF-007 epoch work; no T1/T2/T3/T4 files overwritten; no original game bytes/secrets, heavy Unity or APK build or release triggered.
- **Limits:** managed .NET compatible original-source compile is not Unity Editor import/ARM64 IL2CPP, installed `main.89` OBB phone mount, rendered pixels or water/shader repair. The actual phone-tested package remains owner old run42058825739, not new branch output. Readiness remains `NOT_READY 0/3`.
- **next_step:** preserve copy-set when adding new diagnostic dependencies; integrate the OBB installed-archive read reports from a future signed phone build (exact APK/OBB versionCode and hashes). Let T1/T2/T3 resolve P0 water/shaders/rendering. Watch unrelated T2 canonical summary CI42257148394 failure due a T3 event missing record `id`; do not edit someone else's event or claim summary regeneration succeeded. This completed scoped work does not reserve a Unity resource.
