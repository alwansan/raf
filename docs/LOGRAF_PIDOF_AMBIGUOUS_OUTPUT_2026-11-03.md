# 2026-11-03 — Ambiguous pidof output is not proof of game absence

## Evidence and defect

Reviewed the live `lograf` remote PID watcher and its structural tests. The watcher previously silently discarded any non-numeric tokens printed by `pidof` and treated exit code 0 with no numeric PIDs as a valid empty observation. An unexpected diagnostic or anomalous empty-success output could therefore turn a command/protocol failure into `pidof_empty` and a false `game_exited` transition.

## Change

- Reject non-numeric tokens with `pidof_invalid_output` and report an unverified probe.
- Treat exit 0 with an empty PID set as `pidof_empty_success` (unknown state), not confirmed absence.
- Keep Android toybox exit 1 with truly empty output as the documented normal no-match case.
- Preserve raw UID-filtered Logcat, the bounded 2-second probe timeout, exact main-process cmdline checks and the existing stable signing identity.
- Added structural regression assertions, and corrected the pre-existing stale structural assertion expecting an unbounded `p.waitFor()` rather than `p.exitValue()` after the timed wait.

Commits: `2b256dc5`, `092254e4`, `a3c3c422`.

## Validation boundary

These checks are source-level; no Android device validation is claimed. A CI build must complete before a signed APK containing this change is considered available. On Poco F5 Pro / Android 15, capture while game is absent, running, and after a genuine exit. Confirm `pid_probe_status=pidof_empty` for exit 1/empty, `pidof_probe_failed` and `game_process_state_unknown` for malformed/ambiguous probes, and no false process-death attribution. Compare to exact `am_proc_died` and Android exit-info where accessible. Do not infer crash from pidof alone.
