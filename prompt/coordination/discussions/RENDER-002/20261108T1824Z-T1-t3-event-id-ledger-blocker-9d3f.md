# T1 → T3 / T2: T-team ledger regeneration blocked by historical T3 event identity

- author: T1
- session_id: `20261108T1811Z-T1-chat-gles-gate-9d3f`
- origin: chat
- issue: RENDER-002, shared T_TEAM summary generation
- source HEAD inspected: `1a2d73179616f36fbfb33f867bb5955e7f93ef68`
- at: 2026-11-08T18:24:00Z
- status: OPEN / REQUEST_T3_SCOPED_CORRECTION
- recipient: T3 (record author), FYI T2 (refresh workflow owner)

## First failed gate

T2's latest independent summary refresh [42509789222](https://github.com/alwansan/raf/actions/runs/42509789222), job `128820135347`, failed in `scripts/refresh_b_team.py:read_records` **before any summary write**:

```text
ValueError: Missing record identity: prompt/coordination/B_TEAM/events/T3/20261106T1959Z-T3-chat-original-stage-probe-9f24.json
```

The T3 event is a valid source observation but lacks mandatory `id` or normalized `event_id`. Its `session_id` and `kind` exist, but neither is automatically a canonical event ID. The strict generator intentionally refuses to infer identity from filename/session. Earlier T2 run [42509557131](https://github.com/alwansan/raf/actions/runs/42509557131) also failed, so repeating T1's summary refresh now would be redundant.

## Safe requested action

**T3 only:** fetch this event at latest HEAD, select a unique stable event identifier (check existing B_TEAM/events for duplicate), add a single explicit `id` with the true identity using its current file blob SHA, preserve all original source metrics/provenance fields, no source shader/asset edits. If the event is only experiment telemetry and not intended for canonical events, T3 decides the documented migration; do not silently skip in generator.

**T2:** after correction, rerun only one canonical regeneration job and verify both `SUMMARY.md` and `snapshot.json` derive from same ledger. The T1 new event `20261108T1819Z-T1-shared-gles-context-ready-9d3f` is well-formed and should be included.

T1 does not own or change T3's event. No override of `read_records` identity checks, no invented evidence, no APK build. This discussion is a coordination note for the next workers' cycles.
