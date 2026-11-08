# T4 → T3/T5 support: authentic owner CL/test PNG colour audit (2026-11-08)

**Independent helper owner T4, affected track RENDER-002/T3 and shared integration T5.** No original game or T3-owned driver code modified by T4.

## Immutable inputs / proof
Owner CL test upload [original first six PNGs](https://github.com/alwansan/CL/tree/f401b7ffe3b6ead9038f3b35273599dcf8286e68/test/shared-20261108-214145-461675491) at immutable CL commit `f401b7ffe3b6ead9038f3b35273599dcf8286e68`. Six images `T3-01` through `T3-06`, all 1600×900. Their immutable Git blob SHAs, in case order:

| Case | Git blob SHA | Bytes |
|---|---|---:|
| T3-01 | `33572d9228164650713a6387dc762ffa9836d1c5` | 118859 |
| T3-02 | `fc2793cfed8a7597c6f70cb8cddf6257fa72dd65` | 120553 |
| T3-03 | `b62832a39a3e6ff169bf475b6f96513c610149f2` | 126170 |
| T3-04 | `f6eaecd9263c41767f036569587df57c634ca34e` | 126514 |
| T3-05 | `8e81eb539f5fea2212b3bc928c05bbc9cecaf384` | 127821 |
| T3-06 | `614b6a28eb12a1e5ce2d4d4fb581c9b5957d204e` | 127801 |

**User re-upload** [second shared folder](https://github.com/alwansan/CL/tree/f401b7ffe3b6ead9038f3b35273599dcf8286e68/test/shared-20261108-214548-461919098) repeated each case with changed filename timestamps but **all six Git blobs byte-identical**. This is duplicate upload, not independent new rendered frames.

## Audited original image output: 0 visible RGB stripes
Source scanner `scripts/t4_support_t3_visual_png_audit.py` uses bounded Python stdlib PNG RGB/RGBA/indexed decoder, verifies header/chunk CRC/IEND/decompression, no raw pixel output, checks exact original Git blob SHA. Independent tests `tests/test_t4_support_t3_visual_png_audit.py` use synthetic RGB-strip and truly-black screenshots, PNG filter and CRC/size/symlink/hash negative controls. Isolated read-only workflow `.github/workflows/raft-t4-support-t3-cl-png-audit.yml`.

**Actual CI [42519251690](https://github.com/alwansan/raf/actions/runs/42519251690) COMPLETED SUCCESS**, 8/8 synthetic controls plus the six owner real PNGs SHA verified and later six exact duplicate SHA verified. Numeric-only statistics (all six images have the same measured percentages):

| Measurement | Full PNG 1600×900 | Central region (x=20–80%, y=25–75%) |
|---|---:|---:|
| Saturated red coverage (R≥140 and >1.6×G/B) | **0.000%** | **0.000%** |
| Saturated green coverage | **0.000%** | **0.000%** |
| Saturated blue coverage | **0.000%** | **0.000%** |
| Nearly black RGB (<28 per channel) | **39.572%** | **79.111%** |
| Neutral RGB (max–min<24) | **100.000%** | **100.000%** |
| Alpha ≥64 | **62.391%** | **20.667%** |

**Conclusion:** All six archived screenshots are achromatic and show **none of the RGB test colours**. The case T3-01 was designed to show three saturated red/green/blue stripes, so the PNG image is **not faithful evidence of its expected synthetic visual output**. A syntactically valid PNG, positive `EVIDENCE_READY`, a nonzero SHA/size, or even successful `glReadPixels` alone cannot certify visual capture fidelity. These are **real uploaded screenshots**, not a hypothetical rendering inference. The test only assesses screenshot contents, not the original Raft game renderer or GPU.

## Root-cause path and now-existing T5↔T3 source correction
The old `T3LabActivity.java` at unified v0.2.9/v0.2.10 Mini source copied from `PixelCopy.request(getWindow(), bmp,...)` whereas the synthetic GLES framebuffer was drawn in a separate `GLSurfaceView`. Android `PixelCopy.request(SurfaceView, Bitmap,...)` copies that SurfaceView's most recent queued buffer; the Window variant operates on the Window surface. Source divergence is consistent with a window screenshot missing an independently composed SurfaceView layer. Android reference: https://developer.android.com/reference/android/view/PixelCopy.

**A team fix was already committed after the existing APK** by T5↔T3 (commit `f60355a49a9f236f9757cdac65cf3d12ebbfafc3`) and independently source verified in [42519126545](https://github.com/alwansan/raf/actions/runs/42519126545) **SUCCESS**. Latest T3 source uses `PixelCopy.request(surface,gpu,...)`, compares two direct pixel samples with the same-frame `glReadPixels` results, retries/rejects mismatched frames, and uses optional window overlay composition only *after* proving real surface pixels. This addresses the root-cause candidate, but is **not phone-verified**.

## Actionable T3/T5 handoff
1. Treat original CL/test `T3-01..06` `EVIDENCE_READY` as **UNVERIFIED_VISUAL_CONTENT**, not PASS; retain raw images and prior test provenance.
2. Preserve T5↔T3 correction `f60355a49` and avoid reverting to Window-only `PixelCopy`. Source gate success is not Android15 or same-signed-APK verification.
3. When T5 next has a genuinely justified **single unified Mini build**, ensure source parent contains `f60355a49` and include the T3 surface-pixel policy. T5 owns build/signing and one Mini APK; don't ask for five separate APKs. Existing Arabic Portrait v0.2.10 build [42517104924](https://github.com/alwansan/raf/actions/runs/42517104924) was pinned earlier to `93e32950` and **cannot contain** this later change.
4. On owner Android15 phone, after running T3-01 and a *deliberate* manual capture, require `screenshot_pixel_match` for red/blue test reference positions, an actual readable `T3-01*.png`, and visible RGB content in the real rendered central region before any visual success. If `screenshot_pixel_mismatch`, defer `EVIDENCE_READY`, inspect EGL onDraw buffer age, GLSurfaceView dimensions/presentation and lastRendered sequence; do not falsely call original Raft colours restored.
5. If the same screenshot problem occurs in the full game, distinguish Unity Renderer materials/shaders from synthetic GLES Mini output; this test validates a **lab capture pathway**, not RENDER-002 solution.

This T4 assist is **read-only on CL**, **source-only in raf**, **no shared Mini build**, **no Unity game XAPK build**, **no T3-owned Java source edits**. RENDER-002 and full game readiness `NOT_READY 0/3` remain open.
