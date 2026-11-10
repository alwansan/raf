# T2 scheduled — strict aggregate JSON gate
session_id: 20261110T1123Z-T2-scheduled-json-duplicate-q6m4
origin: scheduled
baseline_sha: 022f694e7ef6e065d103356604dc0cd3c4a29881
current_head_at_handoff: 1598fb933f68b06638f20fd2f36bec82f7ba85a8
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf; phone run 42058825739
resumed_from: clients/T2/sessions/20261110T0816Z-T2-scheduled-foam-cil-preconditions-k8v3.md
work: work/experiments/20261110T1123Z-T2-scheduled-json-duplicate-q6m4.md
scope_commit: cd37a20138321c28a3430fdd30a84fbe642dff6c
source_commit: 75e3e863b986b33fe4d690e56c5fe6ce17a26d41
test_commit: 1598fb933f68b06638f20fd2f36bec82f7ba85a8
result: Strict JSON evidence parser now rejects duplicate object keys at any depth and nonstandard NaN/Infinity tokens before sanitization. Existing allowlisted owner aggregates remain accepted by design. Five additional unit cases committed.
verification: Source and tests committed via current blob SHA conditional writes. Full tests NOT EXECUTED: container git ls-remote failed DNS resolution for github.com; no original Mono.Cecil, shader pixels, Unity, device, or release proof. No CI launched or cancelled. No T3/T4/T5 files touched.
next: Execute python -m unittest -v tests.test_t2_foam_evidence_gate_20261110 on immutable SHA, then connect strict gate to producer pipeline (currently standalone CLI) and verify sanitized artifact, while continuing original Spectrum/Foam/Blur resource and ShaderLab proof.
readiness: WATER-001 OPEN / NOT_READY 0/3.
