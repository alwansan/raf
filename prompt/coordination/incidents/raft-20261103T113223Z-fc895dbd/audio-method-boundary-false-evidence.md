# AUDIO-004 — Source method-body false evidence (A8)

Detected 2026-11-03T11:38:48.676Z. Client raft-20261103T113223Z-fc895dbd. **Status: diagnostic probe fixed; real phone audio acceptance unknown**.

## Repro and impact

The previous `scripts/probe_original_scene_audio.py::method_body` counted braces in comments and literals, causing synthetic method extraction to end at a quoted URL `}` before a valid later FMOD call. A misleading method body can alter SHA/call counters and downstream world/ground-control reasoning without a real runtime bug. This bug is a structural source-audit issue, not a proven historic device FMOD crash.

## Repair

[c4fae959](https://github.com/alwansan/raf/commit/c4fae959ca9417e8ba7e37c1cd5520e34f923d83) uses non-executable C# token masking for both declaration selection and brace matching and returns original source substrings. [CPU-only CI41628714708](https://github.com/alwansan/raf/actions/runs/41628714708) completed SUCCESS with 10 scene-audio unit cases, original SHA-authenticated checks and managed compile exit0.

## Limits

No Unity runtime/audio, game FMOD events or OBB release tested; cannot claim AUDIO-004 closed. Candidate NOT_READY 0/3, water/shaders remain open. No source/proprietary asset/CL modification.
