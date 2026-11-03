# LogRaft system-context package boundary fix — 2026-11-03

Source commit: `c6d1be464938e95a65a20f4b057f25f4153f82b6`. Branch: `lograf` only.

## Finding

The recorder intentionally captures the game's own UID stream without filtering, plus a narrow subset of system/crash/event logcat lines. The system subset previously admitted any line containing the target package as a substring. This could include an unrelated `com.alwansan.raft.androidtest` or a separate `com.alwansan.raft:worker`, polluting the raw system context and making diagnostics harder. The exact-PID death-event counter was already fixed separately, but other system-context messages were still subject to substring matches.

## Change

System-context package detection now requires boundaries on both sides: package-name characters (ASCII letters, digits, underscore, period and colon) disqualify a match. Punctuation such as brackets, spaces, commas and slashes remains accepted. Lines from known live game PIDs are still accepted. This changes **only** which system-context lines are included; the target UID raw Logcat capture is unchanged, as are the writer's queue limits and loss indicators.

Examples: exact target `com.alwansan.raft` accepted; `com.alwansan.raft.androidtest` and `com.alwansan.raft:worker` rejected unless the emitting PID itself is known to be a game PID. Structural regression checks added to `scripts/test_lograf_v06.py`.

## Verification and next steps

GitHub Actions workflow `lograf-apk.yml` is triggered by the Java and test changes. Its final result and APK release must be checked before claiming build success. Device verification: run both Raft and a similarly named process if possible, compare raw `[SYSTEM]` segments with `[RAFT]` and verify no unrelated process-prefix noise is included. Confirm that process exit info is still matched to the exact game PID. This is not a change to the Raft game or its Unity diagnostics.

The Raft branch `feature/android-native-port` currently emphasizes original-water 20-program SPIR-V image operand and FFT format checks. Its latest independent CPU-only tests passed; these are not on-device GPU/Adreno or Unity runtime validation. LogRaft's existing shader/compute error counters remain relevant, but additional private GPU instrumentation cannot be inferred from these tests.
