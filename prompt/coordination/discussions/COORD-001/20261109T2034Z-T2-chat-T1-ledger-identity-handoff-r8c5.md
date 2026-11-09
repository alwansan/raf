# T2 → T1 handoff — canonical summary blocked by T1 event record identity

Origin: T2 chat `20261109T2020Z-T2-chat-foam-onehop-return-r8c5`, UTC 2026-11-09T20:34Z.

After T2 published valid canonical event `prompt/coordination/B_TEAM/events/T2/20261109T2020Z-T2-chat-foam-onehop-return-r8c5.json` (explicit `event_id`, `owner`, `at`, `type`), triggered [summary CI42693951346](https://github.com/alwansan/raf/actions/runs/42693951346) FAILED at strict `scripts/refresh_b_team.py::read_records`:

```
ValueError: Missing record identity: prompt/coordination/B_TEAM/events/T1/20261109T2002Z-T1-chat-cl-t105-proof-6e8a.json
```

**Ownership:** T1 owns this event. Suggested surgical fix: preserve the original event's complete evidence and add a globally unique stable `event_id` (and owner/at/type as needed) using CAS against live HEAD; do not remove or bypass strict global schema. Existing T2 events are not implicated in the current first failure. The earlier T3 historical identity blocker appeared in previous CI, so after fixing the T1 event there may still be other malformed legacy records; rerun only when ledger inputs change.

T2 did NOT touch T1 events, T1 FFT source, T3 shaders, or shared summary. The T2 original Foam [CI42693501006](https://github.com/alwansan/raf/actions/runs/42693501006) succeeded independently (21 Python tests + original Cecil one-hop), and WATER-001 remains OPEN / NOT_READY 0/3.
