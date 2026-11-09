# T5 scheduled session 20261109T2049Z-T5-scheduled-native-watch-b72e
origin: scheduled
work: work/T5/20261109T2049Z-T5-scheduled-native-watch-b72e.md
baseline_sha: 70f4c256af7479efb1788b444051e757660ba38e
scope: latest owner-directed Unity run provenance, distinct from chat's request dispatch.
verified: https://github.com/alwansan/raf/actions/runs/42696228231 native-request-gate SUCCESS, unity-license-preflight SUCCESS, reconstruct IN_PROGRESS (original graphics restore) at 2026-11-09 20:49 UTC.
other_checks: https://github.com/alwansan/raf/actions/runs/42695722354 T1 FFT source gate SUCCESS; https://github.com/alwansan/raf/actions/runs/42696430679 T3 semantic source test FAILED (separate scope); https://github.com/alwansan/raf/actions/runs/42691609924 R5 Mini SUCCESS, not full game.
phone_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md confirms world/save/reload for older artifact only. Current v91 APK/OBB owner bytes not available to this session, so SHA/installation and performance comparison unverified.
collision: Unity already running; no duplicate build/cancellation or native request edit. T4 mouse and T3 renderer untouched.
result: waiting_ci, no new source fix justified until reconstruct or publish result. No READY inference.
next_step: after #42696228231 terminal status, inspect signed delivery artifacts and manifest, then use scripts/t5_verify_apk_obb_pair.py on actual APK/OBB; if publishing fails recover signed checkpoint without rerunning Unity if possible. Follow CL/test v17 device output separately.
