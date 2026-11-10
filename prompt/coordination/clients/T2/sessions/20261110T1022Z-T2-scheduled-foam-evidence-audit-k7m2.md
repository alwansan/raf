# T2 scheduled session — 2026-11-10T10:22Z
session_id: 20261110T1022Z-T2-scheduled-foam-evidence-audit-k7m2
origin: scheduled
issue_id: WATER-001
status: source_change_unverified
resumed_from: prior T2 Foam CIL RHS verifier sessions (last reported commit 0ba8582d8e38ae4f2d3db1190aeda41b2bc1818d); live branch is authoritative.

## Owner evidence first
Read docs/DEVICE_FEEDBACK_42058825739_AR.md blob 756d6b3f9d0846255994fd0fe619d52f17594825. Run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628: owner entered world, saved, exited, re-entered from Artifact; package publishing failed. CL fixed snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57. 220911-559 reports 23,884 water pass errors, 3,850 FFT kernel errors, 1 OBB GUID warning and 1,333 cursor warnings. Those are log summary aggregates, not GPU timing or proof of water restoration.

## Current owner policy
8 November shared mini APK supersedes five individual mini APKs. T5 owns shared build; T4 mouse, T5 resolution; T3 visual FX. No overlapping changes made. WATER-001 remains OPEN/NOT_READY 0/3.

## Changes
- Scope: prompt/coordination/work/T2/20261110T1022Z-T2-scheduled-foam-evidence-audit.md at e61b7219fa4c7a5bbb1c265b61970a3eea2b8524.
- scripts/t2_foam_evidence_gate_20261110.py at 95619aa2f39abe3bdcc63a045f1028fcc664e5b1, hardened at ec118919ca2e0502e56015ccc5be66029ce5f1f0.
- tests/test_t2_foam_evidence_gate_20261110.py at bae6e64e50a43d166bdd3ea4586b1758a5dcc2cb.

Fail-closed schema only accepts fixed aggregate counters, source SHA, run ID, sanitized label, and status. Unknown keys and nonnumeric counts rejected; no raw paths or game shader data can enter a conforming report. CLI deliberately emits generic error class instead of source payload. Test suite added with eight cases; NOT executed on repository checkout or CI this session. No Unity/phone test, no native shader integration, no new Action.

## Next
1. Run `python -m unittest discover -s tests -p 'test_t2_foam_evidence_gate_20261110.py'` at immutable source SHA, fix any failures.
2. Use aggregate-only reports to compare actual Spectrum/Foam/Blur pass errors against stable build fingerprints; never infer GPU correctness from aggregate counts.
3. Continue original Mono.Cecil receiver/return-type binding, then authentic ShaderLab and device confirmation with T1/T3; no readiness upgrade.
