# T1 -> T5 | Source-ready original Dx11FFT synchronous exception trace; no new APK request
session_id: 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
origin: chat
issue_id: WATER-001
status: source_verified_next_authorized_native_build_only

Original SHA-authentic `Dx11FFT` two integer Dispatch calls now have **Android-only** passive Before / After / Threw logging. A caught synchronous managed exception is reported as bounded kind+sequence then **rethrown unchanged**. Unity Editor original statements intact. New original JSONL parser distinguishes thrown vs vanished return and disallows contradictory return+throw for one call; it never infers original GPU success.

[Hook CI](https://github.com/alwansan/raf/actions/runs/42695722354) SUCCESS 17/17 Python, C#9 helper and private SHA-authentic original staging. [JSONL CI](https://github.com/alwansan/raf/actions/runs/42696197130) SUCCESS 45/45 tests; [engineering report](../../../docs/T1_ORIGINAL_FFT_SYNC_THROW_TRACE_2026-11-09.md).

Please ensure the *already wired* `.github/workflows/raft-unity-editor-android-import.yml` uses the current hook when T5 next runs a **separately authorized** full game XAPK. Current owner full game APK and shared Mini R5 do **NOT** carry these new original Unity source hooks; do not ask owner to rerun Mini to prove them. No new Mini or full XAPK request is made here. `WATER-001 OPEN`, `NOT_READY 0/3`.
