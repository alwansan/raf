# T3 — durable screenshot evidence in the one shared Android lab (2026-11-08)

**Owner scope:** T3, `RENDER-002`, compiled `apk-for-testing/unified/app/src/main/java/com/alwansan/raft/t3lab/T3LabActivity.java`, tests `T3-01..06`. This is **not a game graphics fix**, ShaderLab acceptance, Android PixelCopy success, or a new APK build.

## Confirmed source problem
The previous version selected the exact GLES case and checked real `glReadPixels` before invoking PixelCopy, but inserted a publicly visible MediaStore Downloads item, wrote PNG bytes directly, never verified its contents could be reopened, and did not clean up an incomplete item if compression/write failed. It returned `EVIDENCE_READY` merely when the bitmap compression call succeeded. The shared host also received only an image URI and a generic statement, not the actual GPU pixel/GL-error samples underlying that judgment. This weakened the evidence trail even though the shared host correctly requires human visual acceptance.

## Integrated source repair
1. A real in-memory PNG is created using `Bitmap.compress(PNG)`; bound to 8 MiB, validated for PNG magic and terminal IEND, then SHA-256 is calculated from exact encoded bytes. These are transport sanity checks, **not** independent decoder or visual-parity proof.
2. The owned MediaStore Downloads entry starts with `IS_PENDING=1` in the existing `Download/Games/cl/test/shared-<session>/` path. Output stream writes PNG bytes and closes.
3. Before publication the same MediaStore URI is reopened and its entire contents are read; byte count and SHA-256 must exactly equal the encoded PNG, with overlength and repeated zero-read stalls treated as errors. Then `IS_PENDING=0` is updated and the URI is **reopened and verified again**. Only after both checks can T3 return `EVIDENCE_READY`.
4. Any exception during encoding, insertion, writing, verification, final publication, or missing bounded GPU evidence deletes the partial owned URI and returns `NEEDS_SCREENSHOT`, leaving a real request inside the team lab; cleanup failure is logged separately. T3 never requests root or other-app screenshots.
5. Successful shared child result includes actual T3 renderer `lastRenderedNote` (case generation, two `glReadPixels` RGBA samples, positive contract, GL error, viewport), PNG encoded byte length, URI and SHA-256. The host's normal `case_result`/summary pathway records the observations; visual judgment is **still pending** and no automatic `PASS` is sent.
6. The worker's existing synthetic GLES tests remain unchanged; source-only regressions in `tests/test_t3_shared_visual_frame.py` expanded from five to **seven** test methods covering order, pending state, digest/readback, repeated zero reads, cleanup, GPU evidence, and no fabricated PASS.

## Evidence / source commits
- [03151ea4](https://github.com/alwansan/raf/commit/03151ea4b60f87576f8e5abf9235edbc53e12fdd): pending PNG, exact bytes and digest readback, cleanup.
- [a9ad5f77](https://github.com/alwansan/raf/commit/a9ad5f77df2548a1adee109e1cacb51ad4a190aa): bounded zero-byte reads.
- [a7c9c060](https://github.com/alwansan/raf/commit/a7c9c06059aacf3454d3e8370b5855b74ac0d8a0), [cd5d1057](https://github.com/alwansan/raf/commit/cd5d10576acbb74bc631d34ec336a1c6711ab27e): strict source regression assertions and correction.
- [0a449ab7](https://github.com/alwansan/raf/commit/0a449ab7ce3b3551c42fb6d9a11b1da0c32da519), [e65427ed](https://github.com/alwansan/raf/commit/e65427eda01c9e7970c20551c627c65228aad50f): hand actual GPU readback samples to the shared host and guard their presence.
- [503398ac](https://github.com/alwansan/raf/commit/503398ac767001df4dfec11d2d99bf882d3cb55d): isolated `.github/workflows/raft-t3-shared-png-source-gate.yml`. It runs 7 T3 Python source-only regressions, the existing 29-case pack validator, and Gradle `:app:compileDebugJavaWithJavac` **without assembleDebug, native game, Unity, APK/OBB/XAPK/release**. A particular Actions run URL/conclusion is **not verified** as part of this report.
- Independent live GitHub source-read scan after these commits checked **14/14 focused invariants** (pending/write/verify/publication order, GLES samples, failure cleanup and no fake PASS). It is not execution of Python/Java/Android or GPU.

## APK and device limits
T5's existing [single shared Mini APK CI42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) at source parent `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8` contains the **earlier matching-GLES-frame fix** but **predates this PNG integrity/source-output improvement** and the small blank-alpha threshold. Its Artifact ZIP is not a direct APK Release. Do not attribute these later changes to it or start another Mini build solely to relabel existing evidence. The T3 Mini decision remains `NO_BUILD` pending first actual owner Adreno/device evidence and T5's independent shared-build review.

**Unverified:** Android MediaStore pending-stream behavior, actual screenshot contents/color agreement, screenshot persistence across app process restart, on-device GL/PixelCopy reliability, original Raft fire/particle/white-material ShaderLab bindings, water/FFT, real game FPS. **RENDER-002 / WATER-001 OPEN; full Raft NOT_READY 0/3.**
