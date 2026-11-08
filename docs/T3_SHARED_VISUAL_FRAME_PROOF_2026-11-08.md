# T3: shared Android lab GLES frame and readback evidence (2026-11-08)

**Issue:** RENDER-002. **Scope:** only the shared synthetic mini APK (`com.alwansan.raft.lab.shared`), not Unity/Raft actual graphics.

## Source defect
Earlier T3 activity selected T3-01..06, slept a fixed 1000 ms, then called PixelCopy without confirming a completed `GLSurfaceView.Renderer.onDrawFrame` for the same case, a usable GLES program, or correct GPU pixel readback. Thus a screenshot marked `EVIDENCE_READY` could be stale, despite passing PixelCopy.

## Production change
- Case selection increments synchronized `renderSequence`; GL captures case+generation atomically and acknowledges only after drawing, `glReadPixels` and `glGetError`.
- The shared runner waits for the same frame/case, bounded at 8 seconds. Failed shader, unexpected pixel data, GLES error and no-frame timeout return FAIL, not fake PASS.
- Six genuine synthetic readback assertions: T3-01 red/blue panels; T3-02 non-white vertex interpolation; T3-03 alpha blend RGB; T3-04 straight/premultiplied comparison; T3-05 UNORM brighter than sRGB; T3-06 invalid GLSL rejected with valid fallback.
- PixelCopy starts only after actual frame acknowledgement, with a short EGL compositor delay; both before request and asynchronous callback ensure case identity has not changed. Context recreation invalidates shader and negative-control state.
- Even a captured real PNG yields only `EVIDENCE_READY` requiring owner visual review. Failed capture yields `NEEDS_SCREENSHOT`.

## Checks / boundaries
- On current source, **26/26 JS source invariants** passed, verifying routing, synchronization, real GLS readback, gl-error and negative control, no original fixed timer and no automatic PASS. `tests/test_t3_shared_visual_frame.py` adds five regression methods; **the Python suite was not remotely run or verified yet**.
- The older [unified compile CI42504045625](https://github.com/alwansan/raf/actions/runs/42504045625) is **pre-patch**. New Java/Gradle compilation, signed APK, PixelCopy on Android and Adreno pixels **not yet confirmed**.
- These are simplified synthetic color/render contracts, not actual ShaderLab/Unity shaders, material/texture parity, water FFT, fire or Raft game visual acceptance; RENDER-002 and WATER-001 remain OPEN, whole game NOT_READY 0/3.
- Compiled T3 driver changed, so a JSON-only update is insufficient. T3 should vote NEED_BUILD for the **one shared mini APK**, subject to T5 independent integration/CI/signature/Actions review. The 5/5 XAPK vote and full Unity request must not be touched.

## Commits
- [204dabb9](https://github.com/alwansan/raf/commit/204dabb9c18b7122550c7aa30a51fdc385de6f45) frame matching and GPU readback
- [6bb0b165](https://github.com/alwansan/raf/commit/6bb0b165f5849c84b1210eed0c7d8eba00468b2f) PixelCopy async guard and GLES context reset
- [c0a2213b](https://github.com/alwansan/raf/commit/c0a2213bc97d594a3c04c42d956cb51b3c3a291e) source-only tests

## Follow-up: reject an empty but equal alpha comparison

[99e3ee5c](https://github.com/alwansan/raf/commit/99e3ee5c7d3d107d7f5ab197a8ea4e19383562a7) adds independent red/blue positive-channel thresholds to T3-04, so two matching blank black outputs cannot pass merely because their channel differences are small. [2e3ce81b](https://github.com/alwansan/raf/commit/2e3ce81b3a092e7823eedb8aafe1d0bc6e3f2c3c) locks that invariant in the source-only tests. Final live source audit also checked 14 invariants and all 29 unified testpack cases on current HEAD, including six T3 visual cases, but **new Android Java compile/device remains unverified**.

## T5 shared APK handoff — exact included source
T5 [CI42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) compiled a **real single shared mini APK** at source parent `cbe7a038bad2c7ca5ad587b242e8baf7128ecb8`. Git ancestry confirms it includes the T3 frame handshake, GPU readback and asynchronous PixelCopy guards (204dabb9/6bb0b165) but **not** the later T3-04 nonblank enhancement 99e3ee5c and corresponding regression 2e3ce81b. Artifact ZIP ID13628828717 contains APK SHA256 `cee2df1b3bb2a1a3c8e9ab757f520040d36c5bf16d711587f7e2bc537f917472`; it is not a direct APK download. Android GPU/PixelCopy and Raft original shader accuracy remain unverified. Having recognized that existing usable baseline, T3 closed its separate Mini request with NO_BUILD rather than duplicate CI; one follow-up source improvement awaits next justified integration.
