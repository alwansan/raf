# T2 scheduled — 2026-11-10 16:17 UTC
session_id: 20261110T1617Z-T2-scheduled-producer-boundary-v8n3
origin: scheduled
resumed_from_session: 20261110T1419Z-T2-scheduled-json-depth-r4k8
baseline_sha: 2b1bf7eaa0e8f472c594797d450d8bf2a7514ff4
scope_commit: 216d2f3e6f4db6f57799a96dcaf36e2fa7e651fc
issue: WATER-001 OPEN / NOT_READY 0/3

## Owner-first evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md at live feature branch. Owner entered/saved/reentered world from 42058825739 artifact, while packaging publication failed. CL immutable 520c4cf409aa20a4db54ff80ed87d8807d9cba57: 220911-559 has 23884 water-pass errors, 3850 FFT errors. These are phone observations, not CI shader validation. Newer 8-Nov unified mini lab applies.

## Verified this cycle
Read live AGENTS.md and T_TEAM operating model, requirements and instructions. Read previous T2 session and MEMORY; inspected latest T2 evidence parser and 16 unittest methods. GitHub branch head at initial read 2b1bf7eaa0e8f472c594797d450d8bf2a7514ff4. GitHub Actions latest list included 42849324096 skipped on 116fc83b1e47746aa27b9c0e797700ff9f3a6020. Local git ls-remote failed DNS github.com; do not claim repo test run.

Concrete audit: standalone scripts/t2_foam_evidence_gate_20261110.py CLI calls parse_aggregate_json and tests invoke sanitize/parser; neither file establishes producer/upload-step enforcement. The real missing integration is a producer-side gate immediately before publishing safe evidence, not another isolated parser exception patch. Recorded scoped hypothesis and producer test contract in prompt/coordination/work/T2/20261110T1617Z-T2-scheduled-producer-boundary-v8n3.md. No CI rerun, no source/asset edits, no Unity or phone claims.

## Next executable checkpoint
Find actual evidence producer and upload workflow via code/tree read, then add a fail-closed call to parse_aggregate_json at output boundary, with fixture-based integration test and workflow assertion; preserve no raw game data in public artifacts. Separately continue original ZIP2-authenticated pass1 Texture return CFG and CB0/sampler identity. Coordinate T3 effects and T4 mouse/T5 Resolution without modifying their files.
