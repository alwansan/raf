# T5 scheduled session — 2026-11-09T03:53Z
session_id: 20261109T0353Z-T5-scheduled-png-bytes-n7q4
origin: scheduled
status: SOURCE_INTEGRATED_UNTESTED
branch: feature/android-native-port
scope: work/experiments/T5_20261109_PNG_BYTES_PARITY_PLAN.md

## Evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first: world entry/save/reentry only verified for game artifact 42058825739; device estimated 22.29 FPS/57 samples, water pass/FFT errors remain. Read AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md and T_TEAM CHAT_AND_SCHEDULE/PROMPT/OPERATING_MODEL; shared Mini build readiness r4 says NO_BUILD. Inspected scripts/t5_verify_shared_device_summary.py: validates png_bytes/png_sha256 strings but does not open PNG bytes. Existing T4 mouse input work remains independent.

## Changes
- Scope plan commit d62fb4318638ac8fe7124199eb4bd91f06fbe03e.
- New independent offline scripts/t5_verify_png_bytes.py commit bdd814226b7503145b88e3844f7a781fb3d4f5ec: verify six T3 PNG files by SHA256, byte size, PNG signature/chunk bounds/CRC, IHDR dimensions, IDAT and IEND. No image pixel decoding or visual acceptance claim.
- No Unity build, no Actions cancellation or duplication, no CL mutation.

## Limitations and continuation
Git remote inaccessible from local shell (DNS failure), so script not executed locally and no phone/PNG data downloaded; connector source publish succeeded. Need run Python syntax and unit tests on actual script, then collect six exact PNG files from CL pinned session and run against corresponding summary. PNG structural validation cannot establish nonblack pixels, SurfaceView parity, game APK/OBB provenance or game FPS. Confirm live HEAD and overlapping scopes before any future edits. Existing game READY 0/3.
