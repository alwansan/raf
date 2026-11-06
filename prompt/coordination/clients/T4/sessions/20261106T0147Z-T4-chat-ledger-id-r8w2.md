# T4 chat — repair missing event ledger identity

- session_id: 20261106T0147Z-T4-chat-ledger-id-r8w2
- origin: chat
- status: active
- base_sha: 608d8506e5af5efa89fe7113cf7415169cf6fb04
- resumed_from_sessions: 20261106T0137Z-T4-scheduled-n7p2; 20261106T0130Z-T4-chat-touchpad-device-source-q4m7
- work: prompt/coordination/work/INPUT-005/T4-20261106T0147Z-T4-chat-ledger-id-r8w2-event-identity.json
- issue_id: INPUT-005
- experiment_key: T4-20261106-0130-event-identity-surgical-same-original-summary-latest-T3-ledger-failure-42145627443
- resource_key: cheap-T4-ledger-identity-python-no-Unity
- intended_files: prompt/coordination/work/INPUT-005/T4-20261106T0147Z-T4-chat-ledger-id-r8w2-event-identity.json; prompt/coordination/clients/T4/sessions/20261106T0147Z-T4-chat-ledger-id-r8w2.md; prompt/coordination/B_TEAM/events/T4/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.json; tests/test_t4_event_ledger_identity.py; .github/workflows/raft-t4-event-ledger-identity.yml; prompt/coordination/experiments/T4/20261106T0147Z-T4-chat-ledger-id-r8w2.json; prompt/coordination/B_TEAM/events/T4/20261106T0147Z-T4-chat-ledger-id-r8w2.json

## Reproduced blocker

T3 ledger run [42145627443](https://github.com/alwansan/raf/actions/runs/42145627443) failed with `ValueError: Missing record identity: prompt/coordination/B_TEAM/events/T4/20261106T0130Z-T4-chat-touchpad-device-source-q4m7.json`. T3 communicated precise ownership boundary in chat session 20261106T013239Z; no shader issue in that traceback. The event was written by T4 after successful isolated mouse CI42144434260 and accidentally omitted `id` despite retaining `session_id`. Previous T4 events have `id`. This scope edits **only stable identity for the offending T4 event**, adds source-free T4 regression test/CI. T3 shaders and common refresh workflow remain untouched.

## Validation and handoff

Pending.
