# GFX-LAB — 20261110-GFX-chat-android-interpolation-probe-14
- session_id: `20261110-GFX-chat-android-interpolation-probe-14`; origin=`chat`; resumed_from=`20261110-GFX-chat-shdr-interpolation-13`; base_sha=`72c81d4ef67cf1465723b5cc27f78008b5b2e13a`
- experiment_key: GFX-MULTI-040; issue RENDER-002
- Scope: **synthetic-only**, independently installed Android GLES3 interpolation diagnostics (linear, flat/constant, noperspective), GPU triangle sampling + screenshot and all-logs ZIP via existing GfxSessionRecorder/GfxDownloadsZipExporter to `/storage/emulated/0/Download/Games/cl/test/g/`.
- Reason: GFX039 source-only showed 3,405 linear, 76 constant, 16 noperspective declarations in original DX11 Pixel SHDR. GFX037 found no RDEF/debug in true source programs; actual Material-to-register/CB proof and PC pixel parity still blocked.
- Controls: no original source mesh/Shader48/texture/bytecode shipped in diagnostic APK; distinct package from six-model lab; no real shader restoration claim. A binary build is not actual GPU proof until user runs on Adreno and exports log.
- status: IMPLEMENTING
## Results / CI
Pending.

## GFX-MULTI-040 implementation + active build checkpoint
- Authored three **synthetic** shaders: `gfxlab/unity/Assets/Shaders/GfxLabInterpolationLinear.shader`, `...Flat.shader`, `...NoPerspective.shader`. The latter two deliberately use HLSL `nointerpolation` and `noperspective` qualifiers, `#pragma target 4.0`. All three render the same authored colored triangle with unequal per-vertex clip W.
- New C# GPU app `gfxlab/unity/Assets/Scripts/GfxInterpolationProbe.cs`: CommandBuffer.DrawMesh to 256×256 GPU RT, sync `ReadPixels`, sample 3 interior pixels, compute constant spread and perspective-vs-noperspective difference. Save **three PNGs** to the recorder's session directory. Record all case states+Unity errors with full stacks; `EXPORT ALL LOGS ZIP` reuses existing MediaStore bridge, target `/storage/emulated/0/Download/Games/cl/test/g/`.
- Independent builder `gfxlab/unity/Assets/Editor/GfxInterpolationAndroidBuilder.cs`: separate package `com.alwansan.raft.graphicslab.interpolation`, ARM64 IL2CPP GLES3 landscape, never reads ZIP2, does not alter prior six-model app.
- Source-free contracts `gfxlab/tests/test_multi040_android_interpolation_probe.py`. Initial [CI42818515662](https://github.com/alwansan/raf/actions/runs/42818515662) failed a **synthetic test only** (asserted broad uppercase `ORIGINAL` text instead of exact structured `originalRaftShaderBytecodeUsed=false` guard). Fixed.
- Corrected [CI42818589985](https://github.com/alwansan/raf/actions/runs/42818589985) source-free **249 tests PASS**, Unity 2021.3.45f2 signed Android IL2CPP build in progress at this checkpoint. Do not claim APK built or GPU device pixel proof yet.
