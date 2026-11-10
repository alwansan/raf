# T2 checkpoint 20261110T2315Z-T2-scheduled-producer-contract-k7m2
origin: scheduled
base_sha: ba0be646bf3d6557e1d3a34c220e80f3d6f10469
resumed_from_session: 20261108T1956Z-T2-chat-pass1-source-kind-4d6a; 20261110 prior scheduled sanitizer CI checkpoints
issue_id: WATER-001
experiment_key: t2-foam-public-product-allowlist-regression-python311-20261110

## Owner evidence
2026-11-05 device test 42058825739: world enter/save/reopen succeeds from artifact, publish packaging failed; 23,884 water-pass errors and 3,850 FFT errors in 220911 session. This takes precedence over APK86. Screenshots and CL pinned in docs/DEVICE_FEEDBACK_42058825739_AR.md. No GPU or phone test executed here.

## Observed gap and bounded change
Existing strict aggregate sanitizer workflow ran only tests/test_t2_foam_evidence*.py. An independent existing test tests/test_t2_foam_json_product_guard.py verifies public JSON produced by compare_private_names cannot leak private original symbols/numeric pairs and does not claim ShaderLab binding. That test was not in this workflow's path triggers or command. Add producer file/test triggers and a separate source-only job step running the existing product-schema regression; no original game assets required.

## Limits and follow-up
CI outcome: pending after commit; do not assert PASS before run. Publisher invocation remains UNKNOWN: this does not connect sanitizer to any real publication step. Foam RenderTexture cross-pass instance equality, CB0, sampler, ShaderLab and device pixels remain unverified. WATER-001 OPEN / NOT_READY 0/3. Next: check CI and trace real producer/publisher call site, then resume original Foam pass1 return/receiver identity with pinned source.

## Coordination
No shared Unity/Android build, no touch layout changes, no cancellation, no source assets published. T3 owns visual fire/smoke/white material root cause; T4 mouse, T5 resolution and packaging.
