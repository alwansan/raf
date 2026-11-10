# T4 scheduled checkpoint — 20261110T0235Z-T4-scheduled-evidence-gap-n7q4

origin: scheduled
session_id: 20261110T0235Z-T4-scheduled-evidence-gap-n7q4
initial_HEAD: dfbaffb9fe2cac0177c5a73225f26f56820e477e
HEAD_after_work_scope: f62b7a6ebb0ef8daf0ad01f5d3eaf57e5941234e
work: [independent evidence scope](../work/20261110T0235Z-T4-scheduled-evidence-gap-n7q4.md)

## Restored evidence
- Owner feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: Artifact 42058825739 phone world entry, save, exit, reopen confirmed, scoped only to that artifact; packaging publication failed. Original .rgd remains untouched.
- T4 prior session 20261110T0140Z-T4-scheduled-cl-missing-input-v8q2.md: CL/test/shared-20261109-233132-554663211 has T4-01..09 NEEDS_INPUT, not a signed Raft captured button proof.
- T4 MEMORY: source-only integration of 20 original Unity Legacy mouse button/wheel call sites in 12 authenticated original files; source CI42518143297 passed, but phone proof remains absent. No reason to repeat source-only gate.

## Live inspection
- Branch HEAD at start dfbaffb9fe2cac0177c5a73225f26f56820e477e (2026-11-10 02:31Z); latest GitHub Actions runs inspected, e.g. shader CI42743017021 SUCCESS; no equivalent new signed Raft mouse test in inspected latest runs.
- CL/test listing latest shared export shared-20261109-233132-554663211, no newer shared mouse capture data. No new input can resolve Unity-to-game boundary yet.
- Scope-only write committed at f62b7a6ebb0ef8daf0ad01f5d3eaf57e5941234e; no other files modified, no CI canceled or repeated.

## Result and limits
No source change or phone execution. This cycle documented an evidence-dependent blocker with exact provenance instead of fabricating a fix. INPUT-005 OPEN, LOCAL-005 still OPEN for other scenarios, game NOT_READY. Camera capture success is not click/wheel acceptance. T5 retains Resolution and three HUD buttons; keyboard, touch, .rgd, audio, Settings unchanged.

## Next concrete action
When CL includes a captured physical mouse run from a signed game candidate, correlate same-session capture_request ON, captured true LEFT/RIGHT/MIDDLE, vertical/horizontal wheel, Unity getter and gameplay response, then patch only the proven failed boundary. If no new CL input, inspect existing Android-to-Unity bridge for a deterministic source-level defect independent of device evidence; avoid redundant synthetic gates.
