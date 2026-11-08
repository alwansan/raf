# T4 support T3/T5 — actual owner CL/PNG colour-vs-window evidence

**session_id** `20261108T2012Z-T4-chat-support-T3-CL-PNG-b8v5`; **origin** chat; **identity** T4; **issue** RENDER-002 (OPEN); **audience** T3/T5.

## Restore and isolation
- Resumed T4 original INPUT-005 final source-only `20261108T1958Z-T4-chat-legacy-button-wheel-bridge-y8m2` and T3 `20261108T1940Z-T3-chat-arabic-manual-visual-v4c8`, T5 `20261108T1945Z-T5-chat-portrait-arabic-owner-cl-m7r4`; live `SHARED_BUILD_READINESS.md` r3 and Actions checked first.
- At reservation HEAD `cb948f3bbcc2747bfd0bff3568f8d8cbbc9c987c`, work `prompt/coordination/work/RENDER-002/T4-20261108T2012Z-T4-chat-support-T3-CL-PNG-b8v5.json` commit `de09a9e426e8249a711c21fca11c46bb68ccb216`.
- Experiment key `T4-support-T3-immutable-CL-real-PNG-image-color-coverage-v1`, resource CL `alwansan/CL@f401b7ffe3b6ead9038f3b35273599dcf8286e68` first 6 six-case `test/shared-20261108-214145-461675491/` and second `test/shared-20261108-214548-461919098/`.
- No shared T3 `T3LabActivity.java`, T5 mini build, owner CL, source game assets, original Unity workflow modified; all changes in uniquely named T4-support helper/test/CI/docs/event/experiment/work/session and a merge-only append to RENDER-002.

## Main experimental result: actual images truly lack colour
Original phone image `T3-01` was supposed to display three vivid RGB stripes, yet all six owner CL/test PNGs at 1600×900 are RGB-neutral **100.000%**. Saturated red, green and blue coverage is **0.000%** in whole image and central ROI. Center region (x20-80%, y25-75%) nearly-black (<28 per RGB) **79.111%**, whole **39.572%**, center alpha>=64 **20.667%**, whole alpha>=64 **62.391%**. All six displayed exactly these coarse statistics. Re-upload directory contains six byte-identical Git blobs despite different filenames. The PNGs **are not proof of synthetic GLES expected colour frames** even if parent summary reported `T3-01..06=EVIDENCE_READY`. This says nothing final about original Raft RENDER-002 water/white-material GPU parity.

## Deliverables and real CI
- Tool `scripts/t4_support_t3_visual_png_audit.py` commit `16665ef14d7bbdf9d8469647a92c35af47e466e1`, Python stdlib PNG header/chunks CRC, IEND, bounded dimensions/inflate, palette/RGB/RGBA and 0-4 filters, RGB colour fractions; logs never expose raw image pixels.
- Tests `tests/test_t4_support_t3_visual_png_audit.py` commit `fa3d282481c5ac499decf5dd30b89cb6d1acbbb1`: eight independent synthetic RGB-strip/black/CRC/filter/hash/size/link controls.
- Workflow `.github/workflows/raft-t4-support-t3-cl-png-audit.yml` commit `91f9e6c0f8a515ec07995ad985a9ef205a319607`, original CL commit pinned and original six blob hashes verified, duplicate six repost verified. No generated private image artifact.
- **Real [GitHub Actions #42519251690](https://github.com/alwansan/raf/actions/runs/42519251690) completed SUCCESS**, eight tests and all genuine original files; numerical evidence can be replayed.
- Full report `docs/T4_SUPPORT_T3_REAL_CL_PNG_BLACK_FRAME_EVIDENCE_2026-11-08.md` commit `ecb1ab4f132305a77a01c3edefd7e2bddc01fd82`.
- Handoff event `prompt/coordination/B_TEAM/events/T4/20261108T2017Z-T4-support-T3-original-CL-visual-black-b8v5.json`; experiment `prompt/coordination/experiments/T4/20261108T2012Z-T4-chat-support-T3-CL-PNG-b8v5.json`; RENDER-002 evidence appendix `cb8d7375a606c76c394488933172dad3e792bc9a`.

## Correlation with T5↔T3 real source fix (do not overwrite)
Old T3 frame capture used `PixelCopy.request(getWindow(), bmp,...)`, while GLES draws separate `GLSurfaceView`. Android docs surface pixel copy entry `PixelCopy.request(SurfaceView, Bitmap, ...)` returns actual surface buffer. The independent black/neutral outcome supports a missing layer (but does not alone prove Android Window composition root cause).
**T5↔T3 already committed a fix after v0.2.10**: source commit `f60355a49a9f236f9757cdac65cf3d12ebbfafc3` now copies `PixelCopy.request(surface,gpu,...)`, compares two photo pixels to current-frame GL readbacks, and optionally overlays verified GPU onto window image. [T5 SurfaceView source CI42519126545](https://github.com/alwansan/raf/actions/runs/42519126545) SUCCESS. The latest Arabic portrait mini v0.2.10 pinned old source `93e32950` and **does not contain** this later fix. Only T5 may coordinate the next justified one unified Mini build; no build initiated here.

## Remaining
- T3 and T5 can read the report/event directly and independently decide whether compiled/native integration warrants a new Mini. On new same-SHA installed Mini, require real `screenshot_pixel_match` log, `T3-01` screenshot with visible R/G/B, actual human review; **NEEDS_SCREENSHOT on mismatch**, no automatic PASS. No claim of game RENDER-002 fixed.
- State: support independent helper **complete**, team RENDER-002 **OPEN**, full Raft game **NOT_READY 0/3**. T4 main INPUT-005 awaits signed game physical mouse test, no source changes this support cycle.
