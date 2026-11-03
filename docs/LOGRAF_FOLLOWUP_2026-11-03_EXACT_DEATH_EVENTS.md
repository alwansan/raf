# LogRaft follow-up — 2026-11-03 (06:33 Asia/Baghdad)

## Evidence checked
- `lograf` before change: `28f384a9aedd3181a945502fb62bb0eff28b46f3`; release `lograf-55` and Actions run `41567189953` completed successfully.
- Game branch `feature/android-native-port`: `cd12c90cd9fb03996556705e64eacfe6115fbf97`. Recent visible game CI runs `41566206211` (synthetic FFT contracts), `41566206022` (three-LFS-owner compute audit) and `41566206253` (runner guard) succeeded; these are **not** device GPU/Unity gameplay proof.
- The prior stop-time process-exit evidence fix selected only an exact process name for `lastDeathPid`, but its `processDeathEvents` counter and death timestamp were incremented **before** the exact-name test. A system event for a similarly named `:worker` process could inflate the game death count and attach a misleading timestamp to the last actual game PID.

## Source fix
Commit `016573bb8421bda6729df6b9811f67e105355805` moves death-count, PID and timestamp updates into the exact-target-name and positive-PID branch; tolerates whitespace around Android event buffer fields. The original raw system lines remain unchanged. Updated structural safety assertions check that counting occurs only after exact-package validation.

## Verification limitations
Static test assertions are not a substitute for on-device test of event formatting or Android exit-info. A new signed APK must not be advertised as ready until the Actions build, signing and release asset are confirmed. In a follow-up session, record an actual Raft exit and compare `system_death_event_count`, `last_system_death_pid`, `matched_pid`, and the raw `am_proc_died` line; worker-process exits must not increment the main-game counter.

## Next diagnostic priorities
Keep collecting raw Unity/Adreno/FFT shader error messages and frame telemetry gaps; prioritize an explicit capture-health warning when the game logs at extremely high rate and a device-testable exact-PID event fixture. Do not attribute SIGKILL to memory pressure without corroborating system evidence.
