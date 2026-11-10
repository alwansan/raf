# T2 scheduled — Foam RHS stack-order guard
session_id: 20261110T0220Z-T2-scheduled-rhs-stack-order-n6q4
origin: scheduled
baseline_sha: 70986ce1f17935d4cd4540ae9d9a2150c21d76ba
scope_commit: 69950b7dcc86af09425b12502a646021bfdee944
source_commit: 6091da552707c5adec3e315ef5386fba60d70428
test_commit: d3b09191c9f8a52da9867465e62b0680e7409434
work: work/experiments/20261110T0220Z-T2-scheduled-rhs-stack-order-n6q4.md
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf; original phone world enter/save/reentry, water errors unresolved.
resumed_from: clients/T2/sessions/20261109T2220Z-T2-scheduled-alias-nonidentity-m4q8.md; scripts/t2_foam_rhs_origin_guard.py.
result: Fixed synthetic CIL RHS origin classifier to fail closed for dup (stack simulation not implemented) and castclass preceding the sole producer (invalid stack ordering). Added negative controls for both and positive control for cast after producer.
verification: source and tests committed; execution NOT YET VERIFIED. Local container cannot resolve raw.githubusercontent.com (DNS), so did not claim Python unittest/CI or Unity/device success. No CI launched, no concurrent runs canceled.
limits: This is synthetic pre-normalized straight-line CIL; not original Foam IL, shader integration, or runtime RenderTexture identity. WATER-001 OPEN / NOT_READY 0/3.
next: run python -m unittest -v tests.test_t2_foam_rhs_classifier_synthetic on immutable SHA; then integrate stack-aware Mono.Cecil receiver/RHS analysis on verified original without leaking raw IL; coordinate with T1/T3.
