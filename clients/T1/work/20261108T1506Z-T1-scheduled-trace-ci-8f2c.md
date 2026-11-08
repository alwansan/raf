# T1 WATER-001 scoped work
session_id: 20261108T1506Z-T1-scheduled-trace-ci-8f2c
origin: scheduled
baseline_head: d5bfdc4519ebfdfb3c44a64a079e2fc5fd0d50b7
scope: .github/workflows/raft-t1-fft-paired-diagnostic-checks.yml; clients/T1/sessions/20261108T1506Z-T1-scheduled-trace-ci-8f2c.md
hypothesis: Existing paired diagnostic CI omits new trace-consistency, duplicate-key, short-read and mutation regression suites; a green CI run does not cover these guards.
experiment_key: T1-FFT-TRACE-CI-COVERAGE-20261108
shared_resource: existing lightweight source-free CI only; no Unity/GPU/build request.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md and apk-for-testing/OWNER_FEEDBACK_2026-11-08_AR.md. Latest phone log 74359 invalid passes and 11165 invalid kernels; counts are not proof of kernel identity.
constraints: preserve game assets/meta/GUID; no device proof; avoid duplicate workflows.
plan: add four existing test modules and their paths to existing paired diagnostic workflow, run/inspect CI; no equivalent workflow cancellation.
status: scoped
