# T4 chat — owner-only historical event identity repair

session_id: 20261109T1922Z-T4-chat-own-eventid-repair-z6q4
origin: chat
issue_id: COORD-001
status: completed_source_record_only
resumed_from_sessions:
- 20261109T1919Z-T4-chat-ledger-preflight-v4k8
scope_commit: 022871eb14c1fcd6b5baa655ce357cbfe6ae2435
experiment_key: T4-COORD001-3-historical-event-id-additive-CAS-source-audit-v1
resource_key: none
baseline: Source CI42682466747 read all 595 events, 22 missing IDs = T3 14/T4 3/T5 5.

## Safe ownership proof and exact action

Before modification read each original JSON and Git blob SHA, verified `owner=T4`, preexisting `session_id` and no `id/event_id`. Added only one owner-chosen stable unique `event_id` per record with sequential GitHub contents CAS (never other workers):
1. `prompt/coordination/B_TEAM/events/T4/20261106T2222Z-T4-owner-jsonl-single-read-n7b4.json`: explicit `T4-20261106T2222Z-T4-owner-jsonl-single-read-n7b4`; commit `2b41ea0da3976cb3f9815677d45acdd3390492dd`.
2. `prompt/coordination/B_TEAM/events/T4/20261106T2231Z-T4-original-runtime-operation-stage-drift-c6p2.json`: explicit `T4-20261106T2231Z-T4-original-runtime-operation-stage-drift-c6p2`; commit `891027dbbd040c87df29d0d9264f779e6e362068`.
3. `prompt/coordination/B_TEAM/events/T4/20261106T2254Z-T4-runtime-postinstall-safe-rollback-p9v3.json`: explicit `T4-20261106T2254Z-T4-runtime-postinstall-safe-rollback-p9v3`; commit `a41c46ef9e5369129dc6e65eae17be274dbfd871`.

Original evidence, author, issue ID, CI links, experiment, source snapshots and status preserved. No synthetic PASS, source or game modification.

## Verified independent re-audit

[GitHub Actions 42682900051](https://github.com/alwansan/raf/actions/runs/42682900051) **COMPLETED SUCCESS**, job `129381898864`, 10/10 Python tests, complete real-branch event census: 596 files, **20 MISSING_RECORD_ID** after fixes. Remaining T4 **0**; T3 **15** (+1 new original-scope event) and T5 **5**. The first audit was 595 files/22 cases, so 3 T4 records were actually corrected; T3 added one file in parallel. No duplicate/conflict findings. Safe artifact 13702214952 and T4→T2/T3/T5 owner-specific discussion `prompt/coordination/discussions/COORD-001/20261109T1923Z-T4-chat-all-event-identities-v4k8.md`.

## Limits and next action

The T4 owner-local correction is done. Canonical T2 `refresh_t_team.py` still fails on T3/T5 owner records until those workers repair them; don't bypass requirement or claim summary PASS. T2 owns global index. No other worker files or `snapshot.json` touched. No Unity, APK, OBB, touch, camera, audio, save data or device test; full game NOT_READY 0/3. Next T4 sessions can resume INPUT-005 device-acceptance when a fresh signed same-source Raft XAPK is available, or choose another independent source blocker.

## Final post-check after T4 event checkpoints — 2026-11-09T19:27Z

[CI42683474160](https://github.com/alwansan/raf/actions/runs/42683474160) **COMPLETED SUCCESS** on `84513a7f794e164695248c43ad16389f8a14724d`; job `129384033757`: 10/10 source tests, actual full event audit **598 files, 20 missing identity (T3=15/T5=5/T4=0)**. Artifact [13703303275](https://github.com/alwansan/raf/actions/runs/42683474160/artifacts/13703303275). Two newly recorded T4 event checkpoints included their own valid `event_id` and did not introduce a regression. Canonical T2 summary still NOT_VERIFIED; only T2/T3/T5 owner-fixes should remove remaining blockers. No game or phone claim.
