# T1 work 20261107T1806Z-T1-scheduled-boundary-a7c9
origin=scheduled
baseline_sha=7a9ff07e1a848f973789e758e2dc9f20eccac7e0
scope=WATER-001 LogRaft bounded-line classifier, scripts/t1_water_logcat_first_roots.py and independent test.
hypothesis=Exactly 32768 bytes without newline is a truncated fragment of an oversized physical line, yet current condition len(raw)>32768 accepts it. A matching prefix may be counted as a real log record.
experiment_key=T1-logcat-exact-boundary-32768
shared_resource=none; no Unity/CI dispatch
ownership=T1 only, no T4 mouse/T5 resolution files.
taken_over_from=T1 prior bounded-line fix 197f891; latest owner device feedback docs/DEVICE_FEEDBACK_42058825739_AR.md.
acceptance=drop full overlong physical line, retain valid 32768-byte newline-terminated record; unit tests for both. No device/kernel attribution claim.
