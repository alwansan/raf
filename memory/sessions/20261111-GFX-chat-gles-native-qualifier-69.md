# 20261111-GFX-chat-gles-native-qualifier-69 | GFX101 GLES qualifier and CPU/GPU independent witness
- **role:** GFX-LAB
- **origin:** chat
- **resumed_from:** `20261111-GFX-chat-owner-gfx098-archive-68`
- **base_sha:** `9ae855ee9d1dd238c32feafa7a2c171bf308e99b`
- **write branch only:** `experiment/android-graphics-rootcause`
- **experiment key:** `GFX-MULTI-101`, resource `gfxlab-101-gles-native-qualifier`
- **level:** source-free implementation and test contracts committed. **Do NOT declare Android device proof until CI signed APK and owner ZIP.**

## Reason for new experiment
Owner actual GFX098 ZIP SHA256 `60b6cb3e13ea1da7808128311696e9a906655340ea6a2537ad9c9db8d50faa69` passed local audit: 3 sessions, 227 events,147 snapshots,48/48 hashed matrix PNGs, 8 interpolation GPU readbacks and two collapsed native-vs-smooth results. No GL extension list was recorded. GLSL ES 3.20 core has smooth and flat, **not core noperspective**; optional vendor extension must be enumerated and compiled explicitly. The Unity diagnostic cannot establish native GPU support.

## Actual engineering committed
- Original-free Android Activity `gfxlab/android-gles-qualifier-probe/src/com/alwansan/gfx101/MainActivity.java`, package `com.alwansan.gfx101`, direct EGL3 context via `GLSurfaceView`.
- On the GL render thread, reads GL_RENDERER/GL_VERSION/GLSL version and enumerates exact GLES30.GL_EXTENSIONS entries with `glGetStringi`; optional `GL_NV_shader_noperspective_interpolation` compiled **only when advertised**, with explicit `#extension ... : require`.
- Uses hardcoded synthetic triangle NDC [(-.86,-.77),(.86,-.77),(0,.86)] with clip W [.55,1,2.7]; four cases Smooth, Flat, AffineEmulated (smooth perspective of color*w divided by interpolated w), and optional NativeNoPerspective. `glDrawArrays` into RGBA8 256x256 FBO, `glReadPixels`, 3 known interior samples per case and independent CPU barycentric witnesses. Verifies Smooth/affine controls with mean absolute channel threshold .035 and refuses native success unless both controls pass, optional extension exists and native output matches CPU affine reference.
- Every GPU result carries numerical reference errors and SHA256 of raw pixels plus PNG file SHA; auto scoped `MediaStore.Downloads` export to `/storage/emulated/0/Download/Games/cl/test/g/` (Android 10+/29 min), with private ZIP and verified size/path. Manual EXPORT ALL retry available.
- `gfxlab/tests/test_gfx101_gles_capability.py`: nine independent source/analytic contracts and numerical witness. `gfxlab/tools/gfx101_owner_zip_audit.py` plus `gfxlab/tests/test_gfx101_owner_zip_audit.py`: six synthetic owner ZIP positive/negative tests; false original-restored flags, malformed PNG hash, missing capture and forged native success explicitly rejected.
- Source-free APK workflow `.github/workflows/gfxlab-multi101-gles-native-interpolation-apk.yml`: checks source-only tests, uses runner Android SDK Java17/javac+d8/aapt2+zipalign+apksigner, publishes signed APK and safe metadata only; no Unity asset, Raft_Data or ZIP2 fetched. `cancel-in-progress: false`, separate from T workflows.
- Workflow latest explicitly updated at commit `6ed66887253b511bb464ac639a30a7642fbf26ec`, and push should trigger it, **but live terminal success/artifact/signature unconfirmed** because installed GitHub connector has no general workflow-runs listing; do not guess IDs/times.

## Guardrail decision
Expected result on user Adreno if vendor extension absent is `NATIVE_EXTENSION_NOT_ADVERTISED` (not driver-failure). If present and compiled, require GPU affine-vs-smooth actual evidence. A negative/unsupported outcome should move full source parity to a Vulkan SPIR-V NoPerspective probe or explicitly labeled GLES emulation, not claim repaired shader. Separate Shader48 original program and material/CB/skin/normal/PC pixel gates remain OPEN.

**Flags:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `sourceMaterialCbGpuVerified=false`, `pcAdrenoPixelParityVerified=false`, `phase_closed=false`.
