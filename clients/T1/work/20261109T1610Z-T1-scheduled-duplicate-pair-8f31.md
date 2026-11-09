# T1 independent work — duplicate FFT return evidence

session_id: 20261109T1610Z-T1-scheduled-duplicate-pair-8f31
origin: scheduled
baseline_head: 2a1496903c3f4a354638ba56b8991f4d8b5b8523
scope: scripts/t1_fft_dispatch_pair_audit.py and new isolated tests only
hypothesis: a duplicate AFTER or BEFORE trace event is flagged as an error but paired_count may still report that sequence as successfully paired. This weakens diagnostic accounting and cannot prove GPU success.
experiment_key: T1-FFT-PAIR-DUPLICATE-20261109
shared_resource: none; no CI or Unity build
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world/save/reload succeeds, water and kernel errors persist.
next: enforce fail-closed pairing for duplicate events, test locally, record outcome without claiming Unity execution.
