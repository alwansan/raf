# T4 chat — preserve concurrent runtime source edits after install

- session_id: `20261106T2250Z-T4-chat-runtime-postinstall-rollback-p9v3`; origin: chat; status: active; issue_id: LOCAL-005.
- base_sha: `44938b3eab546ec9744bd721f27bf2e91684b9c0`; work lease commit `f04855d4de43e7174f52cc38e8f022a473da958a`.
- resumed_from_sessions: `20261106T2226Z-T4-chat-runtime-staging-drift-c6p2` (pre-write drift fixed, original managed .NET compile CI42305089873 green); scheduled `20261106T2237Z-T4-scheduled-native-sha-boundary-k8v3` (native read-only watcher, no overlap).
- owned files: `scripts/instrument_android_runtime_operations.py` and `tests/test_runtime_operation_traces.py` only. Work: `prompt/coordination/work/LOCAL-005/T4-20261106T2250Z-T4-chat-runtime-postinstall-rollback-p9v3-postinstall-foreign-rollback.json`.
- hypothesis: successful Path.write_bytes of staged instrumented original C# is followed by another writer editing source or GUID meta; adapter notices mismatch but always writes original raw source during rollback, destroying changes from another writer.
- approach: synthetic RED post-install interleavings for source C# and `.cs.meta` independently; fail closed on foreign epoch and retain all original backups without overwriting new data; keep interrupted-partial-write recovery for truly attempted writes; original source SHA gates unchanged.
- T5 owner Unity native run [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) pinned `a1737bd7`, still running at initial check; no cancel, duplicate dispatch or shared request edits.
- limits: source staging only, not `.rgd` save schema or phone acceptance. Protect working audio and Settings; touch/layout deferred. LOCAL-005 OPEN, NOT_READY 0/3, trial vote unchanged.

## RED/GREEN and checkpoint
Pending.
