# T2 independent scope — 20261110T0816Z-T2-scheduled-foam-cil-preconditions-k8v3
origin: scheduled
baseline_sha: e0d4a26a9afd459672186b16d72ad0a9b21b04b7
issue: WATER-001 / Foam RHS original provenance
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (42058825739, CL 520c4cf)
taken_over_from: clients/T2/sessions/20261110T0425Z-T2-scheduled-literal-newline-fix-q7m2.md
files: work/experiments/20261110T0816Z-T2-scheduled-foam-cil-preconditions-k8v3.md; clients/T2/sessions/20261110T0816Z-T2-scheduled-foam-cil-preconditions-k8v3.md
hypothesis: The current source-free classifier can report FIELD_READ for ldfld even without verified receiver stack and may be misused as a complete CIL proof. Add explicit precondition evidence and a fail-closed diagnostic contract; do not touch original shaders, T3 files or Unity.
experiment_key: T2-FOAM-RHS-RECEIVER-PRECONDITION-20261110
shared_resource: none (no CI, Unity or packaging)
planned_validation: static source review and targeted synthetic regression; real Mono.Cecil receiver proof remains separate.
status: scoped; no original-game proof.
