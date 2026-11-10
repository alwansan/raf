# T2 scheduled — strict Foam CIL preconditions
session_id: 20261110T0816Z-T2-scheduled-foam-cil-preconditions-k8v3
origin: scheduled
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739; CL 520c4cf
baseline_sha: e0d4a26a9afd459672186b16d72ad0a9b21b04b7
scope_commit: 905a66c91c6a2d6f38b63d7ab488ce3f6a2beee1
source_commit: 4fc93a3cb066639284064168754f1e5bcc6686bd
test_commit: aa658ea0ef4e319342542d9e27d02f3f8d83edf8
work: work/experiments/20261110T0816Z-T2-scheduled-foam-cil-preconditions-k8v3.md
resumed_from: clients/T2/sessions/20261110T0425Z-T2-scheduled-literal-newline-fix-q7m2.md
result: Added classify_verified_rhs wrapper. The original synthetic classify_rhs stays backward compatible. Original-IL consumers now have an explicit fail-closed API requiring complete_slice; instance ldfld additionally requires receiver_verified; calls require original nonvoid signature. Six unittest cases added covering positive and negative conditions.
verification: Source and test committed using blob SHA conditional writes. Python test execution NOT VERIFIED (local git fetch DNS unavailable). No original Mono.Cecil proof, Unity build, device test or visual proof. GitHub Actions run 42776921454 T4 completed success; no equivalent T2 CI launched. No concurrent jobs cancelled.
constraints: T3 effects and T4 mouse and T5 resolution files untouched. New owner 8 Nov unified mini APK policy in AGENTS takes precedence over old separate mini APK guidance.
next: Execute python -m unittest -v tests.test_t2_foam_rhs_verified_preconditions tests.test_t2_foam_rhs_classifier_synthetic on immutable SHA. Then add original Mono.Cecil stack receiver and complete CFG slice evidence before invoking strict wrapper; only integrate ShaderLab with authenticated resources and pixel/device proof.
readiness: WATER-001 OPEN / NOT_READY 0/3; no original render pass restored in this cycle.
