# T4 chat checkpoint — genuine PersistentDiagnosticLog logger provenance

session_id: 20261109T1912Z-T4-chat-logger-session-guard-n5r7
origin: chat
worker: T4
issue_id: INPUT-005
status: completed_source_only_device_pending
resumed_from_sessions:
- 20261109T1858Z-T4-chat-epoch-evidence-p6m4
- 20261109T1836Z-T4-scheduled-capture-provenance-k7d2
base_sha: e36012258e1cb2fd0e35d1b93fa05210200fe755
scope_reservation_commit: ed7e8cdb0ad9de9622c3a078ff1749315cf31978
experiment_key: T4-INPUT005-Unity2021-PersistentDiagnosticLog-session-sequence-provenance-gate-jsonl-v2
resource_key: none
scope: own T4 mouse evidence parser JSONL provenance, source-only, no Unity build.
intended_files:
- scripts/t4_correlate_mouse_runtime_epochs.py
- scripts/tests/test_t4_correlate_mouse_runtime_epochs.py
- docs/T4_MOUSE_PERSISTENT_LOG_PROVENANCE_2026-11-09.md
- own session/work/experiment/event

## Recovered reality and team coordination

Recovered previous 16/16 source gate successful CI42679768824 and T4 scheduled captured-callback CI42657857161. New real full Raft game mouse acceptance still absent. Checked current CL/test (latest shared 20261108-232759 source, no T4 captured=true), T5/T2/T3 active scopes and runs. T5 owner SAF v89 snapshot initial CI42680558991 failed due `shared-` session normalization; T5 itself fixed and CI42680745095 is green, no cross-agent modification by T4. T2 canonical summary CI42680680366 fails at T3 20261106T2007Z event with no id/event_id; T2 already explicitly requested a T3-owned additive fix under `prompt/coordination/discussions/COORD-001/20261109T1911Z-T2-chat-T3-event-identity-n6q8.md`. No changes to T3 or T2 files. No queued/in_progress T4 competing scope was observed at reservation.

## New engineering question

Actual C# `PersistentDiagnosticLog` in `android-port/Runtime/Platform/PersistentDiagnosticLog.cs` emits `utc,session,sequence,thread,area,operation,detail`, where `session` changes on logger recreation and `sequence` increments within session. Prior T4 epoch-only parser could combine a captured callback from session A with a Unity getter in session B bearing the same `epoch` (e.g. after logger recreation), or accept duplicate startup JSONL after raft log rows.

## Source implementation and proof

1. Source commit `a8e475613ccc2e438fb4c71e7c76aab04aac4149`: `scripts/t4_correlate_mouse_runtime_epochs.py` reads actual log's `session+sequence`, requires actual `area=input` for JSONL, closes open capture on logger scope transition, refuses mixed attribution, marks repeated/decreasing sequence as poisoned for entire session (including previously observed matches), retains legacy plain-text analysis but distinctly classifies unattributed logs. Aggregate-only counters, no raw logger session ID or original assets logged.
2. Test commit `abf1ede6bbea3b9073c9ab20b826be46dd486c93`: eight additional negative/positive controls built from actual JSONL envelope fields; total now 24 source-only tests. No Android code modified.
3. Existing lightweight T4 path-filtered workflow triggered. Initial [CI42681390984](https://github.com/alwansan/raf/actions/runs/42681390984) SUCCESS at source commit. **Final [CI42681491521](https://github.com/alwansan/raf/actions/runs/42681491521) COMPLETED SUCCESS**, `job 129376929867`; fetched job log states **Ran 24 tests in 0.006s; OK**.
4. Report `docs/T4_MOUSE_PERSISTENT_LOG_PROVENANCE_2026-11-09.md`; experiment `prompt/coordination/experiments/T4/20261109T1912Z-T4-chat-logger-session-guard-n5r7.json`; event `prompt/coordination/B_TEAM/events/T4/20261109T1912Z-T4-chat-logger-session-guard-n5r7.json`.

## Limits

The analyzer is source-only and has no real new captured=true game log. Its scopes are logger sessions not cryptographic process identity; do not concatenate app processes and trust output as game evidence. `device_pass=false` and `unity_gameplay_verified=false` remain hardcoded. Same-session+epoch source counters cannot prove exact one-to-one physical gesture nor authored game response. World/save on old game Artifact 42058825739 was observed earlier but not extrapolated to current mouse fallback source. No writes to `.rgd`, game original ZIP2 assets, unity scripts, camera, touch, audio, Settings, T5 Arabic Mini/pack, APK/OBB/XAPK, team summary or other worker sources.

## Handoff

Next T4 scheduled/chat session should first read this checkpoint and final CI 42681491521. On a signed full Raft build including T4 source, pin package signature/source, collect original game JSONL for a **single** app process, test physical LEFT/RIGHT/MIDDLE and V/H wheel plus focus/camera/keyboard/touch, run `python3 scripts/t4_correlate_mouse_runtime_epochs.py /path/to/one-raft-log.jsonl`, correlate Android callbacks and original Unity readers, and independently verify actual gameplay and prior owner world/.rgd save/reopen. Do not dispatch a new APK from this source gate. T4 INPUT-005 OPEN / game NOT_READY 0/3.

Session completed; no waiting CI.
