# T2 scheduled — JSON integer parser boundary
session_id: 20261110T1224Z-T2-scheduled-json-integer-boundary-m7q3
origin: scheduled
baseline_sha: 807117e38b8b029b6c8a0a822c0db2aca70094a7
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf; run 42058825739; world enter/save/reenter proven by owner, water/FFT not proven.
resumed_from: clients/T2/sessions/20261110T1123Z-T2-scheduled-json-duplicate-q6m4.md
work: work/experiments/20261110T1224Z-T2-scheduled-json-integer-boundary-m7q3.md
scope_commit: 57f9ae2a939200542e526945ea0d664bef06779c
source_commit: 82f1ed510527952e2004bf7bd5da39df05b5c0ac
test_commit: a3ce1fb5b6a7fdc4fc8eb959a438ca3993ac11d7
result: Strict aggregate JSON gate now converts Python 3.11+ long-integer ValueError into EvidenceError instead of uncaught traceback; added regression for 5000-digit integer within MAX_BYTES. This is a publication-boundary hardening only, not a water shader recovery.
verification: Commits published with current content blob SHA. Full repository tests NOT RUN: local git ls-remote fails DNS resolution for github.com. No Unity, GPU, device, or shader pixel proof. No new CI launched. No other agent's files changed.
next: Run python -m unittest -v tests.test_t2_foam_evidence_gate_20261110 on immutable SHA; connect gate to evidence producer; prioritize original Mono.Cecil/ZIP2 Spectrum/Foam/Blur source and ShaderLab pass mapping over further synthetic tests.
readiness: WATER-001 OPEN / NOT_READY 0/3.
