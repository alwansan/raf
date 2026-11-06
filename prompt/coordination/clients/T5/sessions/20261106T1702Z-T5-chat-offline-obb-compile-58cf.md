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
