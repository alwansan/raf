# LogRaft: deterministic primary process selection — 2026-11-03

## Evidence and risk
At the start of this cycle, `lograf` was at `06e092d0b934` and the Raft Android branch at `de5dec1e7aed`. The latest Raft Actions for isolated binary16/FFT precision and CI runner compatibility passed, but do not establish Adreno rendering correctness. The prior LogRaft APK workflow run 41578941276 completed successfully and published `lograf-57`.

Code inspection found that `RemoteLogService.currentPid()` iterated a synchronized **HashSet** of PIDs returned by `pidof` and selected its first element. HashSet iteration order is unspecified. If the app ever has multiple processes, telemetry could jump between processes; the CPU/RSS/FPS and process-transition records would then be misattributed. This is a preventive fix based on a real source-level defect, **not a claim that a device recording has exhibited multiple Raft processes**.

## Implementation
The shell-side watcher retains every discovered PID for system-context correlation, but reads the first NUL-terminated field of `/proc/<pid>/cmdline` to select the process whose command line equals the exact Raft package. It publishes only this verified PID to the performance sampler. Unreadable cmdlines, no matching PID, or transient `pidof` failure yield an unavailable main PID, never a guessed worker PID. This is a low-frequency read (0.8s watcher) of at most 256 bytes per candidate. The sampler and Logcat UID stream remain independent. Startup resets the selected PID and tracked set; Stop clears it.

## Validation
Structural checks were extended in `scripts/test_lograf_v06.py`. GitHub Actions must still compile and sign the app before any APK is claimed ready. On a real Poco F5 Pro, verify that the metrics PID is the exact main Raft process, especially during restarts or if a secondary process exists. If `/proc/<pid>/cmdline` is inaccessible to the Shizuku shell, `pid` and process-specific metrics will be null; that is deliberate, and the raw UID Logcat remains available.

No game source or other branch was modified.
