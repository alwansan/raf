# T1 independent scope
session_id: 20261111T0514Z-T1-scheduled-comparison-invariants-c7d2
origin: scheduled
issue_id: WATER-001
status: completed_source_only; tests_pending
intended_files: scripts/t1_compare_kernel6_sessions.py; scripts/test_t1_compare_kernel6_sessions.py (if free); this work file; independent session file
experiment_key: kernel6-sanitized-compare-invariants-v1|20261105-220911-559|230108-327|source-e9c358e
resource_key: none (CPU-only)
Hypothesis: malformed sanitized summaries with zero kernel6 errors but sampled error events, or with samples exceeding error count, currently pass validation and can yield misleading comparisons.
Owner report: docs/DEVICE_FEEDBACK_42058825739_AR.md (read first). Success: world entry/save/re-entry from artifact, NOT FFT restoration.
Boundaries: no native build; no touch/mouse/Resolution overlap with T4/T5; no proprietary logs. Check HEAD and overlap again before modifying source.

Outcome: 966f7ab167fbe19e369f39462d0d742aceb74bd3 source guard, f9a242dfb61a34943455138c026225794f7a7696 regression tests, session 20261111T0514Z-T1-scheduled-comparison-invariants-c7d2. No native/Unity CI dispatched; next run test suite and CL scans.
