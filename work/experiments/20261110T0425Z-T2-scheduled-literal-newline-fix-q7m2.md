# T2 WATER-001 — Python source syntax repair
session_id: 20261110T0425Z-T2-scheduled-literal-newline-fix-q7m2
origin: scheduled
baseline_sha: 77138848e62a4b297f945106305f6e43209d0212
experiment_key: T2-FOAM-RHS-LITERAL-ESCAPED-NEWLINE-20261110
files: scripts/t2_foam_rhs_origin_guard.py; tests/test_t2_foam_rhs_classifier_synthetic.py; this work file; clients/T2/sessions/20261110T0425Z-T2-scheduled-literal-newline-fix-q7m2.md
hypothesis: prior commit inserted literal backslash-n sequences in Python code, causing SyntaxError before tests can run. Replace only literal escaped line breaks with real newlines and verify compile/unittest.
shared_resources: none; no CI/Unity; no T3/T4/T5 edits.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, world save/reentry confirmed, water remains unresolved.
limits: synthetic CIL only, not original Mono.Cecil/ShaderLab or device proof.
