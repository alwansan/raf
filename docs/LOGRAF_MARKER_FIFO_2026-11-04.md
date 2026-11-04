# LogRaft device marker ordering and persistence — 2026-11-04

**Write branch:** `lograf` only. The game branch `feature/android-native-port` was checked read-only at `6b60c35e845a3bc8e559a7df7e408363032697cb` with no newer commit in this review. Latest confirmed native experimental delivery remains the split APK/OBB/XAPK release `android-early-test-41812889049-1`; its CI success does not prove game-side water, sound, input, offline startup or frame rendering.

## Reproduced design flaw and relevant evidence

The owner-supplied Android 15 LogRaft 0.6.82 export `LogRaft-1793816124441.zip` contains a `[USER MARKER]` written directly into a raw log segment, without a monotonic timestamp. The session's writer accepted and wrote 10,514 batches; it had up to 230,040 bytes pending with maximum recorded queue delay of 145ms. Previously, `CaptureService.appendMarker()` bypassed the queued binder/SAF writer by taking `writeLock` and writing to `output` immediately. If earlier Logcat batches were waiting in the queue, the marker could be persisted **before** those earlier accepted batches. It also performed potentially slow Storage Access Framework writes on the Android service command thread and reported success before unambiguous writer-side accounting.

This is an ordering/diagnostic correctness defect. It does NOT by itself prove that the game crashed or that every older event timestamp is sorted at capture: upstream remote Logcat can still buffer and deliver events later.

## Fix in the logger

- Route user markers through the **same bounded FIFO** as game and system Logcat; never write a marker directly to SAF. A marker is a single small, non-blocking queue offer, so the service main thread cannot wait 1200ms for queue capacity. A failed offer triggers the existing explicit recorder-overflow failure rather than silently losing a requested marker.
- Persist only `[USER MARKER] timestamp_unix_ms=... elapsed_realtime_ms=... event=owner_reported_issue` with no user-entered contents, credentials, or file paths; retain the recognisable historical prefix.
- Flush user marker immediately when the writer processes it; report `Issue marker written to session log` only **after** `OutputStream.write()` and `flush()` returned. Output-stream success does not guarantee physical-media durability.
- Export `user_markers_enqueued` and `user_markers_written` in session summary. These complement, but do not replace, the global received/written/failed-batches and queue-delay counters.
- JVM test checks formatting, two clocks and invalid timestamp handling; Python structural checks enforce that raw SAF marker writes do not return and that marker accounting and non-blocking queue routing remain present. All game log content, segments, limits, privacy and Shizuku permissions are unchanged.

## Verification / remaining limits

Run `python3 scripts/test_lograf_v06.py` and `bash scripts/test_lograf_diagnostics.sh` in Actions, followed by Gradle signed release build. A signed APK build cannot prove phone-level marker latency, Shizuku disconnect tolerance, SAF filesystem full behavior or game replay quality. Validate the next 0.6.x release on Poco F5 Pro: start under high log flood, issue markers while game is active, stop and verify the ZIP includes raw segments and summary with equal marker enqueued/written counts and both clocks.

No new game build is requested, and no game branch, other repo, task, source asset, or signing key is changed.
