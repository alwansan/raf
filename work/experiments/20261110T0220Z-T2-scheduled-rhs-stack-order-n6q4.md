# T2 WATER-001 — RHS stack-order safety
session_id: 20261110T0220Z-T2-scheduled-rhs-stack-order-n6q4
origin: scheduled
baseline_sha: 70986ce1f17935d4cd4540ae9d9a2150c21d76ba
experiment_key: T2-FOAM-RHS-STACK-ORDER-20261110
files: scripts/t2_foam_rhs_origin_guard.py; tests/test_t2_foam_rhs_classifier_synthetic.py; this work file; clients/T2/sessions/20261110T0220Z-T2-scheduled-rhs-stack-order-n6q4.md
hypothesis: accepting dup and pre-producer castclass as inert allows malformed stack slices to be misclassified as evidence. Conservative classifier should reject dup (needs stack simulation), and require castclass after sole producer.
shared_resources: none; no CI/Unity; T3/T4/T5 files untouched.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; owner confirms world save/reentry but water FFT failure.
prior: scripts/t2_foam_rhs_origin_guard.py synthetic only; no actual IL or runtime identity proof.
verification_plan: synthetic unittest including invalid stack-order cases; classify only pre-normalized single-producer slices.
