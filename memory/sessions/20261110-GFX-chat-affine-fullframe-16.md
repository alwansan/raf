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
