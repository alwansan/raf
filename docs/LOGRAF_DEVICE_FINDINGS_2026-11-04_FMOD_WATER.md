# LogRaft 0.6.80 — device evidence (2026-11-04)

Source: three owner-provided private ZIP exports from Poco F5 Pro / Android 15. **No raw user logs are committed.** Compare against v0.6.51 only after obtaining matched scenarios and actual earlier exports; these are not a controlled A/B comparison.

- 17:35 session: 64,038 raw lines, 23 telemetry samples; repeated `[FMOD] Initialization failed` / `SystemNotInitializedException` messages. The game ran with verified PID 17652; FPS was unavailable, not proven frozen. The local writer reported 376/376 batches and no local failed writes.
- 17:38 session: one user marker and one sample with game absent; insufficient evidence for recorder failure or game crash.
- 17:54 session: 88,480 raw lines; 3,262 invalid Graphics.Blit pass messages and 466 invalid compute kernel messages. The error's following stack traces identify UltimateWater.Internal.Dx11FFT; a single-line classifier cannot reliably infer that association. Keep the original raw traces. Writer reported 301/301 batches, no local failed writes.
- The 17:54 PSS candidate (1,597,901 KiB) exceeded contemporaneous RSS (957,772 KiB) and was rejected. Do not present it as a verified process PSS. Validate the dumpsys meminfo format and sampling timestamps before altering this check.
- SurfaceFlinger presented FPS was never readable in these sessions. Neither zero FPS nor a Unity hang is established. Game-side FrameTimingManager data would require separate instrumentation in the read-only game branch.
- GPU busy is system-wide KGSL, not the game's utilization. No GPU clock was available.
- `game_log_lines_per_second` is an interval measurement, not the average across a session; a low last-sample rate can coexist with a high total log count.

## Change made on lograf

Add fixed, privacy-preserving categories for observed FMOD initialization failures and missing events. This is a classification improvement, not a repair to FMOD or the game. No automatic upload or private-file access is added.

## Next engineering work

1. Add deterministic parser fixtures for water FFT stack traces, and count the parent exception once without falsely attributing unrelated compute failures.
2. Investigate Android 15 SurfaceFlinger latency availability without inventing FPS.
3. Correlate OBB expansion-bank failures and shader load failures from actual emitted messages; do not treat any OBB path mention as an error.
4. Compare the earlier 0.6.51 session under matched conditions and preserve all raw segments and uncertainty indicators.
5. Test Shizuku/Binder interruption and writer durability on device; CI compilation is not hardware validation.

Game branch remains read-only. Current owner instructions prefer verified zip2 resources for Raft shader/water restoration; LogRaft must only observe their emitted diagnostics.
