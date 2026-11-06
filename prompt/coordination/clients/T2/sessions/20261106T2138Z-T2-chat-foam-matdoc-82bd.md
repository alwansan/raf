# T2 source-only exported Foam .mat completeness guard

- session_id: 20261106T2138Z-T2-chat-foam-matdoc-82bd
- origin: chat
- status: active
- base_sha: afa18e3371c882f2b0842111ef6ea61aa78b71fc
- updated_at: 2026-11-06T21:38:01Z
- resumed_from_sessions: 20261106T2117Z-T2-scheduled-foam-ci-reconcile-k6m2; 20261106T2044Z-T2-chat-field-consumer-trace-d4a6
- issue_id: WATER-001
- work: prompt/coordination/work/WATER-001/20261106T2138Z-T2-chat-foam-matdoc-82bd.json
- observed gap: scripts/t2_foam_export_binding_probe.py accepts a %YAML .mat with no Material (!u!21) document and reports a clean inventory, unlike the inherited broad W1 auditor. This can hide a malformed Material asset while the test falsely reports complete GUID pointers.
- scope: read-only probe + synthetic tests only; no private bytes/Unity/GUID/game modifications; existing path-filter source-only CI.
- active native: https://github.com/alwansan/raf/actions/runs/42296450023 (independent T5/owner build; don't cancel or duplicate).
- plan: add red/green malformed .mat document guard while preserving legitimate no-.mat dynamic Material case; run existing synthetic CI; document verified limits.
- next_step: edit two isolated files, validate by source-only CI, close work and record result.

## Verified completion — 2026-11-06T21:40:33.769Z
- Code commit: https://github.com/alwansan/raf/commit/9951deea2c2c055ceedfc4c0997efb040c5288db; only `scripts/t2_foam_export_binding_probe.py` and `tests/test_t2_foam_export_binding_probe.py` modified. No raw/private data and no Unity asset edits.
- Source-only [CI42298466950](https://github.com/alwansan/raf/actions/runs/42298466950) **SUCCESS** on exact code SHA: 18/18 export Material/GUID tests and 17/17 preexisting private installer tests (job 128169749600); new cases: YAML .mat missing !u!21, .mat with non-Material class or malformed header, and allowed .asset without Material. Existing negative/positive guards still pass.
- The gap was in **validation completeness**, not restoration of Foam pixels. Zero serialized .mat files remains valid when runtime creates materials; malformed .mat is now rejected. W1 broad inventory already rejected `.mat` without Material; this brings T2 strict probe into parity.
- Additional automatic original Foam private source workflow [42298467191](https://github.com/alwansan/raf/actions/runs/42298467191) was `in_progress` at checkpoint, triggered by source path; not manually dispatched. Native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) is separate on older immutable source a1737bd; not cancelled or requested again.
- No original exported YAML audited by this source-only CI; no actual Unity importer, CB0 upload, mobile GPU, XAPK or water pixels proved. T2 vote remains `لا يحتاج`, WATER-001 OPEN, NOT_READY.
- experiment: `prompt/coordination/experiments/T2/20261106T2138Z-T2-chat-foam-matdoc-82bd.json`; event: `prompt/coordination/B_TEAM/events/T2/20261106T2138Z-T2-chat-foam-matdoc-82bd-result.json`.
- status: completed; next_step: coordinate with T5 to run read-only strict Foam export inventory on authentic exported Assets within a native/Unity run that is already authorized; collect only safe aggregate results, then verify original CB0/FFT and pixels on device separately.

## Team-summary integration follow-up — 2026-11-06T21:42:08.442Z
- T2 own event commit `cdd595f0ae1b162250795590c5c6460e60c7850b` triggered deterministic evidence summary workflow [42298698447](https://github.com/alwansan/raf/actions/runs/42298698447), which FAILED pre-render on T3 legacy event lacking `id`/`event_id`, independent of Foam source-only successful CI. Canonical summary remains stale until owner T3 adds stable explicit event identifier; do not relax validator or rewrite historic attribution.
- Sent owner-scoped [T3 discussion](../../../../discussions/COORD-001/20261106T2142Z-T2-chat-summary-event-to-T3-82bd.md); T2 did not touch another worker's event or summary generator. This is a real known blocker, not evidence of water runtime failure.
- Native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) remained in_progress at checkpoint; source-original private Foam workflow [42298467191](https://github.com/alwansan/raf/actions/runs/42298467191) in_progress; no duplicate dispatch.
