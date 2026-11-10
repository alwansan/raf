# T2 scheduled session — 20261110T1724Z-T2-scheduled-cli-boundary-p6k8
session_id: 20261110T1724Z-T2-scheduled-cli-boundary-p6k8
origin: scheduled
baseline_sha: 7d90f989b6d8e1b7432c9497a9146b0f5a7cb68a
latest_observed_head: 3e5b7388fd1fbe771c8e6f9924d14b3ed450968c
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; run 42058825739; CL 520c4cf; owner world enter/save/reenter succeeded; water/FFT unresolved.
resumed_from: clients/T2/sessions/20261110T1518Z-T2-scheduled-flag-integrity-n5q2.md
work_scope: work/experiments/20261110T1724Z-T2-scheduled-cli-boundary-p6k8.md
scope_commit: 33ab2e386ebe098f6228ad8f655b3f784c2a7efc
test_commit: 3e5b7388fd1fbe771c8e6f9924d14b3ed450968c
result: Added executable subprocess integration regression for the real t2_foam_evidence_gate_20261110.py CLI: valid aggregate roundtrip, raw-path injection, nested duplicate keys, invalid UTF-8, NaN, >64KiB input, and 4000-deep nesting. Rejection must exit 2, write zero stdout, and avoid raw details/traceback. No source shader or game asset modified.
verification: NOT RUN. GitHub connector source reviewed; container git ls-remote failed DNS (Could not resolve host github.com). No claim of tests passing. No CI dispatched; no Unity or device testing.
limitations: This proves only CLI boundary when executed, not actual producer-to-publisher wiring. Original Foam pass/resource/CB0/name binding and ShaderLab remain unverified. Follow up: run python -m unittest tests/test_t2_foam_evidence_cli_integration.py on fixed SHA; inspect actual publishing workflow and enforce this gate before artifact upload. Continue original Spectrum/Foam/Blur resource proof with T3.
readiness: WATER-001 OPEN; NOT_READY 0/3. Preserve owner-confirmed world/save and audio/Settings.
