# T2 independent scope — runtime RT capture gate CI
session_id: 20261111T1723Z-T2-scheduled-runtime-rt-ci-b8n4
origin: scheduled
baseline_sha: 8981fe2fb6ba7800f2f033f9cacae44b58c48269
issue: WATER-001
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL@520c4cf; run 42058825739
files: scripts/test_t2_foam_runtime_rt_pair_gate.py; .github/workflows/raft-t2-foam-runtime-rt-contract.yml; clients/T2/sessions/20261111T1723Z-T2-scheduled-runtime-rt-ci-b8n4.md
hypothesis: runtime RT token parser introduced at ea389f66 has no independent CI coverage; malformed capture fixtures must fail closed before Unity instrumentation is attempted.
experiment_key: T2-FOAM-RT-CONTRACT-CI-20261111
shared_resource: none (Python source-only; no Unity or APK)
coordination: T1 FFT, T3 materials, T4 input, T5 shared lab remain untouched.
expected_result: Python unittest regression in isolated CI; no claim of original runtime identity, water pixels or READY.
