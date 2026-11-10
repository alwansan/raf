# GFX-LAB — 20261110-GFX-chat-affine-fullframe-16
- session_id `20261110-GFX-chat-affine-fullframe-16`; origin `chat`; resumed_from `20261110-GFX-chat-affine-rootcause-15`
- branch of writes `experiment/android-graphics-rootcause`; baseline SHA `70b16e328cf27a69e6587ca88d0fceb1bcc414ff`
- GFX-MULTI-042 (RENDER-002) — full-frame GPU→CPU affine reference confirmation
## Input and privacy
- Uploaded 2026-11-10 GFX041 owner ZIP SHA256 `0f79ffd0420e379c270aaf266b083458146c9de0dc20df36824b3ab625bae173`; private ZIP and screenshot remain in conversation, **never Git**.
- One valid auto-log session (28 events /14 snapshots/4 original-free PNGs), Unity errors/warnings/drop 0, runtime GLES3 Adreno. All 4 GPU readbacks supported and completed.
- Snapshot status `DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH`. Linear/NoPerspective 256x256 PNGs byte-identical, Flat solid blue, AffineEmulated visibly and quantitatively different.
## Whole-frame independent evidence
- Decode entire RGB pixels, convert PNG top-down row order into OpenGL bottom-up pixel centers. Triangle NDC A(-.86,-.77), B(.86,-.77), C(0,.86), clipW=(.55,1,2.7).
- For **20,212 interior pixels** where all 3 screen-space barycentric weights are >0.02: GPU Linear vs analytic perspective mean abs RGB=0.000981208; AffineEmulated vs analytic affine mean abs RGB=0.000983381; AffineEmulated vs *wrong* perspective=0.143924693.
- In-image 8-bit quantization explains ~0.001. This confirms the source-owned smooth-only affine workaround works across the triangle, beyond original three-point sample. **Does NOT prove original Raft Shader48 rendering**.
## Engineering next
- Author a standalone testable full-frame count-only PNG+ZIP auditor using Python standard library (IDAT zlib/PNG filters) with strict bounds/CRC; run source-free tests then apply locally to owner private ZIP; persist safe counters.
- Continue Stage1 Shader48 G8 original Material→register/CB link independently; no source register map from DXBC (RDEF absent). Avoid synthetic test mistaken for full Shader48 APK.
## CI
Pending.

## Terminal GFX-MULTI-042 verified (2026-11-10)
- GFX-MULTI-042 owner Adreno GLES3 actual GFX-MULTI-041 ZIP `SHA256=0f79ffd0420e379c270aaf266b083458146c9de0dc20df36824b3ab625bae173` was verified privately: 1 session, **28 events /14 snapshots**, 4 256×256 RGBA GPU PNGs, **Unity errors/warnings/drops=0**, all four shaders supported/readback. `Linear` PNG and native HLSL `NoPerspective` PNG **byte-identical**; `Flat` blue constant for all **20,212** strict internal triangle pixels. An independent full-image CPU math check (PNG top-down → OpenGL bottom-up centers; barycentric min >0.02, synthetic clipW=[0.55,1,2.7]) found **Linear GPU vs perspective** mean abs RGB `0.000981208`, **AffineEmulated GPU vs affine** `0.000983381`, **AffineEmulated GPU vs WRONG perspective** `0.143924693`. This conclusively validates **our synthetic GLES3 smooth-based affine workaround for this test triangle**, not actual Raft Shader48. Safe counts `gfxlab/evidence/20261110_gfx042_owner_affine_fullframe_safe_counts.json`; no owner photos/ZIP/private event text published.
- Source-free strict whole-PNG decoder `gfxlab/tools/affine_fullframe_owner_zip_audit.py` and synthetic filters/corruption/misclassification tests `gfxlab/tests/test_affine_fullframe_owner_zip_audit.py`; final [GFX-MULTI-042 CI42826480472](https://github.com/alwansan/raf/actions/runs/42826480472) **SUCCESS 272 Python tests**, source-free runner accessed no private owner files or ZIP2; earlier [CI42825803381](https://github.com/alwansan/raf/actions/runs/42825803381) also succeeded, final code adds strict no-unbounded-zlib-flush decompression. Source-only standard-library PNG reader supports 256×256 RGBA8 as produced by lab.
- Documented portable implementation gates and genuine future route `gfxlab/SHADER48_INTERPOLATION_GLES_VULKAN_PORTABILITY_AR.md`: Khronos GLSL ES 3.20 core only `smooth/flat`, SPIR-V `NoPerspective` Decoration 13 is native for Input/Output, Microsoft DXC maps HLSL noperspective→SPIR-V; DXC only consumes authentic **HLSL source**, not original DXBC game blob directly. Neither device GL extension availability nor genuine Vulkan pipeline tested.
- **G7–G12 original Shader48 phase still BLOCKED:** exact original Material property→DX11 t/s/CB registers/CB offsets, pass states, rig/animation, source PC pixels and Android Shader48 runtime. No new APK required to repeat already-verified triangle result; do not promote synthetic test to original shader restoration.
- Success exits: independent real-device full-frame proof; repeatable source-free auditor 272 tests; private input not leaked. Follow-up actual original shader resource-binding evidence remains mandatory. No modifications to T1–T5/feature/main/ZIP2.
