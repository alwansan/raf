# 2026-11-03 — PID discovery quality and false exit transitions

Live baseline: `lograf` at `1d27128b` before this change; game branch `feature/android-native-port` at `45498067`. The recent game workflow `41591309793` passed CPU-only FFT coordinate tests; this does **not** prove rendering on Adreno or successful Android gameplay. LogRaft run `41590922443` succeeded and published `lograf-59` before this change.

## Verified source defect

The Shizuku PID watcher previously parsed `pidof` stdout but ignored its process exit status. On a nonzero exit (e.g. command error) with empty output, the sampler could classify a known process as `game_exited`. A failed PID lookup is not proof that Raft exited. Also, a nonempty PID list whose /proc cmdline cannot be verified is not proof of absence.

## Change

The watcher now checks `pidof` exit status, and records `pid_probe_status` as `main_pid_verified`, `pidof_empty`, `main_cmdline_unverified`, or `pidof_probe_failed`; it reports cumulative successful and failed probes, and `main_process_pid_verified`. When PID discovery fails or main cmdline is unverified, the emitted state is `game_process_state_unknown` rather than `game_not_running`; an apparent `game_exited` transition is labeled `pid_tracking_lost_unverified`. No stale PID is reused for CPU/RSS/FPS. A successful empty `pidof` still permits the regular game-exited observation, but its cause must be independently verified with system exit evidence.

The changes are diagnostic only: no changes to Raft, no extra high-frequency shell commands, no changes to raw Logcat filtering or signing identity. Added structural checks for exit status and the new counters. The tests are not a substitute for device validation.

## Device acceptance

On Android 15/Poco F5 Pro, record a session with Raft running and one with Raft closed. Check `metrics-*.jsonl` for `pid_probe_status` and that a transient pidof error yields `game_process_state_unknown` instead of a confirmed exit. Validate `session-summary.json` separately against exact PID-matched Android exit evidence. Do not infer a crash from process tracking loss.
