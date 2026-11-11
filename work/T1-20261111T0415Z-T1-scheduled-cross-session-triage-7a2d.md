# T1 scope — 20261111T0415Z-T1-scheduled-cross-session-triage-7a2d
origin=scheduled
baseline_sha=b58ea1edefcdc8ae3bd3de59b7c03d40497f7dd6
owner_evidence=docs/DEVICE_FEEDBACK_42058825739_AR.md
issue=WATER-001; experiment_key=T1-KERNEL6-CROSS-SESSION-01
Hypothesis: aggregate counts alone conceal different first-error ordering between 220911-559 and 230108-327; a provenance-gated comparison of sanitized scan outputs can expose divergence without leaking logs.
Files: scripts/t1_compare_kernel6_sessions.py, scripts/test_t1_compare_kernel6_sessions.py, clients/T1/sessions/20261111T0415Z-T1-scheduled-cross-session-triage-7a2d.md, this work file. No shared Unity/CI resource; no existing T4/T5 file modifications.
Read-only inputs: two JSON outputs from scripts/t1_kernel6_log_context.py --errors-only, each tied to distinct session and source_sha256. No invented kernel identity. No native build.
State: scope registered; next implement and test independent comparator.
