# T4 chat — independent source-free CI wiring for scheduled overflow safety gate

- session_id: 20261105T181919Z-T4-chat-overflow-ci-9dzc8
- origin: chat
- status: active
- resumed_from_sessions: 20261105T1737Z-T4-scheduled-h6v2; 20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8
- base_sha: b855f3b921411deb66d138bf795ff29bb77bda0f
- issue_id: LOCAL-005
- work_id: prompt/coordination/work/LOCAL-005/T4-20261105T181919Z-T4-chat-overflow-ci-9dzc8-overflow-ci-wiring.json
- experiment_key: T4-jsonl-queue-overflow-global-failclosed-05631bd-15plus2-sourcefree-CI-wiring-v1
- resource_key: none
- run_urls: none yet

## Verified baseline
Original genuine RGD factory CI42076494669 SUCCESS67/67 source-only, not runtime save or playable world. Scheduled T4 fix source commit 6b2ffec, two synthetic controls commit 05631bd. Current source-free log evidence workflow blob b310c1ceaa910b798e3ee0e2e05b09db5b733052 checks out only the parser and legacy test and runs those tests; it excludes the two new overflow controls. This is a testing coverage gap, not a new game failure. T5 native run42058825739 in_progress; do not duplicate/cancel. LOCAL-005 OPEN, NOT_READY 0/3.

## Scoped action
Only update .github/workflows/raft-t4-world-save-log-evidence.yml for source-free overflow test sparse checkout, triggers and invocation. Existing scheduled-owned scripts/t4_verify_device_world_save_log.py and scripts/test_t4_overflow_gate.py remain untouched. No Unity, gameplay, original code/assets, .rgd or phone result to claim.

## Next step
Record exact workflow diff, CI run/status/assertions and source SHA; if failure fix the narrow CI wiring and recheck. Report limits and complete own work without closing LOCAL-005.
