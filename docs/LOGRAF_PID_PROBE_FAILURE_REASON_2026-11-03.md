# LogRaft PID probe failure reason — 2026-11-03

Baseline: `a7accef8` (previous PID overflow safety check); source changes: `ce0a27d`, structural regression checks: `aa231a0`.

## Change
The remote Shizuku PID watcher already distinguishes a successful empty `pidof` result from a failed probe. Previously all failures were reported only as `pidof_probe_failed`, making a timeout, oversized output, invalid diagnostic text, and process-execution failure indistinguishable during field diagnosis.

New metric `pid_probe_failure_reason` emits bounded codes: `none`, `pidof_timeout`, `pidof_output_overflow`, `pidof_invalid_output`, `pidof_empty_success`, `pidof_exit_<code>`, or `pidof_execution_error`. It resets on successful probes and at session start. Exception messages and raw subprocess output are never emitted. Existing `pid_probe_status`, success/failure counters, PID fail-closed behavior, and UID-filtered raw Logcat remain unchanged.

## Validation and limits
`scripts/test_lograf_v06.py` adds structural checks for the exported field, bounded reason codes, and absence of raw exception export. GitHub Actions result and release verification must be checked separately after this commit. This is not a device test; on Poco F5 Pro / Android 15, inspect the metric when Shizuku or `pidof` fails and confirm that missing PID does not imply a game exit. Do not infer a crash from process tracking loss.
