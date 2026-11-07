# T1 work scope — 20261107T1211Z-T1-scheduled-cl-timing-f8c2
origin: scheduled
baseline_sha: 8a0236b31a502bb8d28e7519b38679b165d065ec
issue: WATER-001
scope: pinned CL session-summary timing correlation only; files: docs/T1_WATER_FFT_CL_TIMING_2026-11-07.md and this work record plus T1 session. No shader, Android input, T4 or T5 files changed.
hypothesis: invalid FFT kernel and invalid water pass categories start in same startup window, supporting one shared binding/initialization investigation rather than assuming unrelated errors.
experiment_key: T1-CL-ONSET-42058825739-f8c2
shared_resource: none; CL read-only
result: 2ms onset separation in both sessions, but no causal or numeric proof; see evidence report.
status: completed_source_evidence_only
