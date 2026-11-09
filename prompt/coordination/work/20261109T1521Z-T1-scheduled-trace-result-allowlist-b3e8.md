# T1 WATER-001 scoped work
session_id: 20261109T1521Z-T1-scheduled-trace-result-allowlist-b3e8
origin: scheduled
issue_id: WATER-001
base_sha: a79704658c2c8fdd061da9014d2711bd14ca83c3
status: active
updated_at: 2026-11-09T15:21:00Z
intended_files: scripts/t1_fft_dispatch_pair_audit.py; tests/test_t1_fft_dispatch_pair_audit.py (if present); prompt/coordination/clients/T1/sessions/20261109T1521Z-T1-scheduled-trace-result-allowlist-b3e8.md; this work file
experiment_key: t1-fft-dispatch-return-result-strict-presence-v1-source-only
resource_key: none (no CI or Unity)
hypothesis: AfterDispatch missing result must not be counted as a confirmed success if another return has explicit result; inspect actual trace schema before modifying legacy compatibility.
Owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; 5-Nov sessions 23884/3850 and 39132/6026; 8-Nov session 74359/11165 separate. No runtime kernel identity proven.
No mouse/Resolution modifications: T4/T5 ownership; no duplicate build.

## Result (2026-11-09T15:25Z)
status: completed_source_unverified
Source commit: e21d1801d53e8cab55da8a15f37390366cbc1ed0
Test commit: 9d75a3c215daf803a0b0e941588886bca11b6762
Actual issue after inspection: simultaneous kernel identity mismatch + result=exception previously hid dispatch_result_failure due to elif. Now both are reported independently. Two regression cases added. Not an FFT kernel or GPU fix. Tests not run (local GitHub DNS unavailable); no CI dispatched, no build. Next: run python -m unittest tests.test_t1_fft_dispatch_pair_audit and inspect real Android trace fields.
