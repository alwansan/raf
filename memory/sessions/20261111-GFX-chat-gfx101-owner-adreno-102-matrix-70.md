# 20261111-GFX-chat-gfx101-owner-adreno-102-matrix-70 — GFX101 Adreno proof and GFX102 version-matrix engineering

- **role:** GFX-LAB
- **origin:** chat
- **branch (only writable):** `experiment/android-graphics-rootcause`
- **resumed_from:** `20261111-GFX-chat-gles-native-qualifier-69`
- **base_sha:** `6d3c7a0b73cd6e65d47fd52e88906a964e9bfb22`
- **experiment:** `GFX-MULTI-102` / `GFX101_ADRENO_NATIVE_NP_RESERVED_GLSL_VERSION`
- **owner device evidence:** two uploaded original ZIP files (private, not committed).
- **evidence level:** `GPU_EXPERIMENT` synthetic GLES3 on Adreno 730 from GFX101; GFX102 implementation/CI is source-only pending phone proof.

## GFX101 actual device outcome
Two private owner ZIPs SHA256:
1. `8b788636517fc672416ccd76d5a32baea9da627fa8c7b2a261c04ba81556af6c`
2. `350a42d8494918c16e07e3c73dde1ef9622f8bc2cec813c930b9290115d512c4`

Both outer ZIP CRC pass; 3 PNG per ZIP (256×256 ARGB8888) metadata SHA256 and image parse/CRC pass. 17 events each. `summary.json` and `events.jsonl` have identical content across the two tests. On POCO F5 Pro / Adreno 730 / GLES 3.2, GLSL ES 3.20, **104 driver GLES extensions**, the exact `GL_NV_shader_noperspective_interpolation` extension is **advertised true**. GLSL 300 es `Smooth`, `Flat`, `AffineEmulated` VS/FS compile/link and real GPU `glReadPixels` succeed (3/3 controls). Mean CPU-vs-GPU error: Smooth/perspective 0.001091419; AffineEmulated/affine 0.001141990, Flat identical blue at all samples. `GL_NO_ERROR=0` for compilations. **Both NativeNoPerspective VS and PS fail compilation** on each run with `'noperspective' : Reserved word.`, not because vendor extension is missing. Status `NATIVE_EXTENSION_ADVERTISED_BUT_SHADER_COMPILE_OR_LINK_FAILED` applies to GLSL **#version 300 es only**; it does not establish lack of GLSL 320 support. This corrects prior hypothesis that native extension may be absent on owner device.

Safe aggregate: `gfxlab/evidence/20261111_gfx101_owner_adreno_safe_counts.json` (private raw ZIP/PNG/event lines excluded). No full-game files or proprietary source uploaded.

## External exact specification/workaround evidence
Khronos OpenGL ES extension `NV_shader_noperspective_interpolation`, complete revision 2 (2014), permits `noperspective` on ES shader inputs/outputs when `#extension ... : require`. It requires OpenGL ES 3.0, but implementation details can differ. Official https://registry.khronos.org/OpenGL/extensions/NV/NV_shader_noperspective_interpolation.txt .
Skia contains documented Qualcomm workaround refusing native `noperspective` under GLSL ES 3.00/3.10, retaining ES 3.20: https://skia.googlesource.com/skia.git/+/d782fd600e2c44d09e751588189a54f1d3612484/src/gpu/ganesh/gl/GrGLCaps.cpp . **This is a promising hypothesis, not proven on owner Adreno until the new APK runs.**

## GFX102 code and provenance
- Separate `com.alwansan.gfx102` Android test `gfxlab/android-gles-qualifier-probe-v102/` on *only* the GFX-LAB branch; old 101 remains unchanged and installable.
- Synthetic `Smooth`, `Flat`, `AffineEmulated` GL controls, plus three explicit required-extension VS/PS variants `NativeNoPerspectiveES300`, `NativeNoPerspectiveES310`, `NativeNoPerspectiveES320`. Uses direct GLES3 context on GL thread, real RGBA8 `glDrawArrays`+`glReadPixels`, three CPU reference sample points, per-case PNG/SHA.
- Retains all compile/link failure logs by version; `native_glsl_version_trials` array tracks 300/310/320 separately and `native_best_glsl_es_version` identifies an actual GPU readback winner. A candidate that compiles but matches smooth rather than affine is explicitly a mismatch, not success.
- Source-free 8 analytic/source tests `gfxlab/tests/test_gfx102_glsl_version_matrix.py`; 10 synthetic positive/negative owner ZIP audit tests `gfxlab/tests/test_gfx102_owner_zip_audit.py` and independent PNG CRC/structure+hash validator `gfxlab/tools/gfx102_owner_zip_audit.py`. Source-free Actions file `.github/workflows/gfxlab-multi102-qualifier-version-matrix-apk.yml` signs with Android SDK javac/d8/aapt2/apksigner, uploads only GFX102 APK/safe JSON. `cancel-in-progress: false`.
- Arabic owner test details `gfxlab/GFX102_OWNER_TEST_AR.md`. Auto ZIP to `/storage/emulated/0/Download/Games/cl/test/g/`.
- **GitHub Actions success/signature/artifact NOT YET VERIFIED** in this chat. The available GitHub connector cannot list push-triggered workflow runs; do NOT invent run ID/URI/APK SHA. No claim GFX102 has executed yet.

## Next
1. Confirm GFX102 Actions green terminal, real signed APK/package SHA, and artifact. If real build fails, inspect exact failing job then patch GFX-LAB branch only.
2. Owner installs GFX102 on POCO F5 Pro, sends `GFX102-ALL-TEST-LOGS-*.zip`. Check whether GLSL 3.20 compiles with NV required and produces screen-linear GPU output; if not, capture exact driver failure and move to Vulkan/verified GLES emulation.
3. Then restore original indexed weighted skinned geometry/hierarchy and original Shader48 material, binding, dynamic pass states and PC↔Adreno pixel comparison. Original official Standard PC SHDR recompilation GFX099 already shown at representative stage CPU level, **not Android shader/pixel completion**.

**Truth flags:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `pcAdrenoPixelParityVerified=false`, `phase_closed=false`. T1–T5 and `main`, `feature/android-native-port`, `zip2` untouched.
