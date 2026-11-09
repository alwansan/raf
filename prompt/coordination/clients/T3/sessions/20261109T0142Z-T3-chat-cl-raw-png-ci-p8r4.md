# T3 — pinned CL R3 PNG image evidence CI
- **session_id:** `20261109T0142Z-T3-chat-cl-raw-png-ci-p8r4`
- **origin:** `chat`
- **issue:** RENDER-002 / NOT_READY
- **base_sha (before reservation):** `6fe95344909bd919dc8bc08cc245bda640e1155e`
- **scope reservation commit:** `96fe36f1f50601015420ee35ccba466a291c6f5b`
- **work:** `prompt/coordination/work/RENDER-002/T3-20261109T0142Z-T3-chat-cl-raw-png-ci-p8r4-raw-png-ci.json`
- **resumed_from_sessions:** `20261109T0134Z-T3-scheduled-cl-png-pixel-audit-k7m2`, `20261108T2326Z-T3-scheduled-cl-r3-proof-j7k4`, `20261108T2013Z-T3-chat-cl-pixelcopy-surface-f2n8`
- **planned owned files:** `.github/workflows/raft-t3-cl-r3-png-evidence.yml` plus this session, independent T3 work/event; no edits to scheduled T3 Python scripts/tests.
- **reason:** scheduled T3 generated a synthetic PNG decoder and tests but could not access raw CL binary PNG in current environment. New chat scope is a pinned lightweight hosted CI audit, separate from scheduled source work.
- **CL input:** `alwansan/CL@24a677fc8fa4749c0bcf8a3cac01fa80b1641c86`, `test/shared-20261108-232759-468049775` six PNG blob SHAs from GitHub API, R3 shared APK `0.2.13-shared`.
- **baseline evidence:** 6/6 real T3 GLES events report `verified_surface_pixels=true`, GL error 0, but still `EVIDENCE_READY` not human visual PASS. Earlier `0.2.10` Window PixelCopy saved black GLES content; `0.2.13` uses SurfaceView PixelCopy matching.
- **CI status:** ✅ [42547145230](https://github.com/alwansan/raf/actions/runs/42547145230) COMPLETED SUCCESS (01:45:11 UTC), source `e839d4e3e54b761a95a421f48e1ce70593751725`.
- **limits:** Synthetic GPU lab screenshot is not Raft Unity scene/white hand/smoke/material restoration. CL read-only. No proprietary files in artifacts.
- **next:** track authentic Raft particle shader/material and screenshot-specific appearance separate from mini; this CI scope is complete.

## Verified results and delivery — 2026-11-09 01:45 UTC
- Added [independent evidence workflow](https://github.com/alwansan/raf/blob/feature/android-native-port/.github/workflows/raft-t3-cl-r3-png-evidence.yml), commit `e839d4e3e54b761a95a421f48e1ce70593751725`, isolated `ubuntu-24.04` with short bounded timeout, no heavy Unity build or APK build, `cancel-in-progress:false`.
- Hosted [CI run 42547145230](https://github.com/alwansan/raf/actions/runs/42547145230): `completed/success`. Synthetic test suite PASS; six source SHA-pinned CL PNG downloads and Git blob SHA-1+length checks PASS; real PNG CRC/scanline/pixel distribution audit PASS; only aggregate JSON uploaded ([artifact 13644076425](https://github.com/alwansan/raf/actions/runs/42547145230/artifacts/13644076425)).
- All six R3 saved images are 1080×2400, audited **from real CL PNG bytes**, not simulated data. For T3-01 through T3-06, center `unique_rgb` = **3, 81448, 332, 332, 331, 330** respectively; `black_fraction` = **0, 0.000043, 0.000043, 0.000043, 0.000043, 0.000043**. Full-frame black fractions 0.000162 for T3-01 and 0.000062 for each other case.
- Interpretation: R3 corrected PNGs **do not exhibit the previous all-black GLES capture region**; the T3-01 three-color center supports the synthetic bars test and T3-02 has abundant gradient colors. **This is not an exact frame-to-owner-screenshot pixel match, not user visual PASS, not any original Unity Raft scene test, not alpha/sRGB correctness proof**.
- Preserved immutable file pins, summary metrics, and limits at [docs/T3_CL_R3_PIXEL_EVIDENCE_2026-11-09.md](../../../../docs/T3_CL_R3_PIXEL_EVIDENCE_2026-11-09.md) and `prompt/coordination/experiments/T3/20261109T0142Z-T3-chat-cl-raw-png-ci-p8r4-r3-png-proof.json`; independent event under `prompt/coordination/B_TEAM/events/T3/20261109T0142Z-T3-chat-cl-r3-png-ci-p8r4.json`.
- Scheduled T3 worker files `scripts/t3_cl_png_pixel_audit.py` and `tests/test_t3_cl_png_pixel_audit.py` were **not modified** by this chat; work scope released in `work/RENDER-002`.
- **Next engineering problem:** on authenticated ZIP2 original game graph, investigate the specific square smoke particle prefab→material→shader→texture and original blend/alpha state, then compare owner real in-game photos. RENDER-002 OPEN / full game **NOT_READY 0/3**. No new mini or XAPK built.
