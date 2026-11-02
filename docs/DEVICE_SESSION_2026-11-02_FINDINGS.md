# LogRaft device session and reliability findings — 2026-11-02

Owner-provided local ZIP: LogRaft-1793636471014.zip. Only aggregate observations are recorded here, not the original raw personal logs.

## Confirmed baseline
- Recorder build: LogRaft 0.5.34, signed, Xiaomi 23013PC75G, Android 15 API 35.
- Capture began 19:19:22 (Asia/Baghdad). This ZIP contains 3 raw log segments, 1 metrics segment and session metadata.
- Raw log lines: 1,008,422 (97,645,501 uncompressed line bytes); 33 valid JSON telemetry samples over approximately 104 seconds.
- Invalid Graphics.Blit shader-pass messages: 38,744, including 7,149 for PostFX - Bloom pass 2 and 7,149 for pass 3.
- Invalid UltimateWater compute-kernel index messages: 1,430. DirectoryNotFoundException entries for packaged haptics WAV assets: 35.
- Game PID 21258 was reported dead at 19:20:58.982, with foreground state in ActivityManager. No matching SIGSEGV, Fatal signal, FATAL EXCEPTION or ANR appeared in the supplied segments. **Death mechanism remains unverified.**
- Game process RSS reached 1,632,596 KiB; device MemAvailable reached a low of 603,816 KiB; Raft CPU usage peaked at 265.21% of one core equivalent. Neither CPU nor memory figures alone establish process death cause.
- Game Logcat line rate rose above 25,000 lines/s in some samples. The raw logs were not filtered or deleted.
- GPU busy utilization 31/33 samples, range 1.18–54.36% (device-wide KGSL counter). GPU frequency 0/33 samples; unavailable, not zero.
- Presented-frame FPS estimate 14/33 samples, range 3.92–120.69 FPS. SurfaceFlinger presentation is an external estimate, not Unity Update FPS or GPU frame time; surface changes can invalidate it.
- One Raft game process transition start and one exit; no Logcat reconnects reported.

## Recorder-side changes made after inspecting this ZIP
1. Preserve raw logs; independently count shader pass, compute kernel, missing asset path, Java/native fatal markers, and process death messages. All counters are included in metrics JSONL and live on-screen status.
2. Write a lightweight session-summary.json on Stop. It contains last telemetry and file totals, and is included with ZIP export. No expensive raw-log scan runs while stopping.
3. Correct UI rendering of telemetry newline separators.
4. On game exit, query Android's package-scoped process exit history via Shizuku shell (dumpsys activity exit-info com.alwansan.raft.androidtest); retain evidence in metrics JSONL and final summary. This may be inaccessible on the vendor ROM and must be matched by PID/timestamp. It is not a verified crash reason until inspected.

## Game-side findings (read-only; no changes made to game branch)
- UltimateWater shader passes and compute kernels remain incompatible/missing in the current game runtime, producing severe log floods.
- Android jar:file asset path used with ordinary filesystem APIs for Haptics/SharkBiteRaftHaptics.wav causes path errors.
- For authoritative FPS, Unity frame timings, FMOD state and precise process-exit reason, inspect the game-side persistent JSONL log and Android exit history from a new post-fix recording.

## Hardware verification still required
- The new exit-history snapshot may be delayed or restricted by Xiaomi firmware. Do not infer low-memory kill without Android reason code or corroborating LMKD evidence.
- Confirm session-summary.json is produced, ZIP includes it, live counters tally correctly and upgrade remains possible with the existing public signing key.
