# 20261110-GFX-chat-affine-rootcause-15 — GFX-MULTI-041
- session_id: `20261110-GFX-chat-affine-rootcause-15`, origin=`chat`, resumed_from `20261110-GFX-chat-android-interpolation-probe-14`
- base SHA `a839a1d0b80c29bc0965ea60f069fc9c9e0ade8c`; ONLY writable branch `experiment/android-graphics-rootcause`
- owner device ZIP SHA256 `5de5522120ad41b51c07d1ffbaa59567a9240d0351687a980db792e9476b7aee` (user-private; **do not publish original ZIP/photo**)
## Real owner GFX040 evidence (2026-11-10)
- ZIP integrity passed. One session, 22 snapshots, 44 events, zero errors/warnings/dropped events. Device runtime explicitly GLES3, all 3 shaders supported, GPU readbacks completed.
- All three diagnostic PNGs present; **Linear and NoPerspective PNG byte-for-byte equal** (identical SHA256), although Flat image is solid blue and 0 spread. Four automatic/repeated GPU cycles all reported mismatch, linear/NoPerspective 0 difference.
- Independent CPU barycentric calculation at three owner readback points: linear GPU RGB vs expected perspective (w=[0.55,1.0,2.7]) average absolute error **0.0010914**, versus expected affine **0.1629662**. Perspective-vs-affine mathematical delta **0.1630194**. The triangle stimulus is valid. This demonstrates HLSL `noperspective` native route was **not preserved in this Unity GLES3 render path**; it does **not** establish which layer dropped it or that Adreno lacks an extension.
- Khronos GLSL ES 3.20 core section 4.5 defines `smooth`/`flat`, not `noperspective`; `noperspective` needs a vendor extension such as `GL_NV_shader_noperspective_interpolation` where available. Source refs: https://registry.khronos.org/OpenGL/specs/es/3.2/GLSL_ES_Specification_3.20.html and https://registry.khronos.org/webgl/extensions/NV_shader_noperspective_interpolation/.
## New engineering scope
- Build independent **GFX-MULTI-041** APK package, fourth synthetic shader AffineEmulated, four GPU screenshots and report including CPU perspective/affine reference errors. Formula: interpolate `color * clipW` and `clipW` both via standard perspective-correct varyings; `(Σλ color_i)/Σλ` is recovered by their ratio.
- Keep all original GFX040 source and user APK unchanged; no original Raft source files or Shader48 code in 041.
- Source-only synthetic tests + CI APK signature/package/ABI + ZIP auditor private. Update RESTORE/STATE/MEMORY and docs.
## CI
Pending.
