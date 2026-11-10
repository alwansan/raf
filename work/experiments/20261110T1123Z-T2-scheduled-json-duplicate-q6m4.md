# T2 independent scope — 20261110T1123Z-T2-scheduled-json-duplicate-q6m4
origin: scheduled
baseline_sha: 022f694e7ef6e065d103356604dc0cd3c4a29881
issue: WATER-001 / public aggregate evidence integrity
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf; run 42058825739
resumed_from: clients/T2/sessions/20261110T0816Z-T2-scheduled-foam-cil-preconditions-k8v3.md
files: scripts/t2_foam_evidence_gate_20261110.py; tests/test_t2_foam_evidence_gate_20261110.py; work/experiments/20261110T1123Z-T2-scheduled-json-duplicate-q6m4.md; clients/T2/sessions/20261110T1123Z-T2-scheduled-json-duplicate-q6m4.md
hypothesis: JSON parser accepts duplicate keys and nonfinite numeric constants by default; aggregate evidence gate must reject ambiguous or nonstandard JSON before sanitization.
experiment_key: T2-FOAM-EVIDENCE-JSON-STRICT-20261110
shared_resource: none; no Unity, CI, packaging or shader files
validation: unit regression for duplicate top-level/nested keys and NaN/Infinity; existing aggregate acceptance unchanged.
status: scoped before code change; original Spectrum/Foam/Blur ShaderLab and device validation remain open.
