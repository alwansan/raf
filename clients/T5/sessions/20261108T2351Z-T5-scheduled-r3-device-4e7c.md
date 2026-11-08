# T5 session 20261108T2351Z-T5-scheduled-r3-device-4e7c
origin: scheduled
resumed_from_sessions: 20261108T2153Z-T5-scheduled-saf-ci-5d82; previous 20261108T2045Z-T5-scheduled-saf-7c91
base_sha: 5e3e3b8d294f29658d71d8bd4d4745625f2e5d91
scope_commit: b022ce719d9e22d1006dd64426c8b844065a6f61
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; world/save/reentry proven ONLY on game artifact 42058825739, not Mini.
result: inspected new CL shared session 20261108-232759-468049775, app_source e7a6248b0d0c14b9772bd52f3bbdc5cf22fa9b9a, pack_sha256 6e19b05c697334be6ee7740846f2817f29fdcb185a118c8f5d36bbd06b04066f. Six T3 screenshot cases T3-01..06 have EVIDENCE_READY with verified GLSurfaceView PixelCopy pixel parity and nonzero PNG sizes. This supersedes old black-PNG evidence for synthetic Mini screenshot capture, but human visual confirmation remains outstanding. T4-01..08 in same session NEEDS_INPUT, not pass. No actual game APK/OBB identity proven; no Unity FPS performance inference from synthetic tests.
source: https://github.com/alwansan/CL/blob/main/test/shared-20261108-232759-468049775/summary-20261108-232759-468049775.json
shared Mini r3 build: https://github.com/alwansan/raf/actions/runs/42519487402; no new build requested, no Unity resource allocated. SAF CI https://github.com/alwansan/raf/actions/runs/42521743039 previously SUCCESS.
limitations: PNG pixels not independently decoded this run; CL JSON describes automated parity, not human visual pass; exact signed installed APK/OBB and LogRaft per-scene performance unresolved. Full game NOT_READY 0/3.
next: verify PNG visually and source version, then continue Resolution and three right controls in independent nonoverlapping game-source scope, coordinate with T4 mouse capture.
