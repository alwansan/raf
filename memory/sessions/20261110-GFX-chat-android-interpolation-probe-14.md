# GFX-LAB — 20261110-GFX-chat-android-interpolation-probe-14
- session_id: `20261110-GFX-chat-android-interpolation-probe-14`; origin=`chat`; resumed_from=`20261110-GFX-chat-shdr-interpolation-13`; base_sha=`72c81d4ef67cf1465723b5cc27f78008b5b2e13a`
- experiment_key: GFX-MULTI-040; issue RENDER-002
- Scope: **synthetic-only**, independently installed Android GLES3 interpolation diagnostics (linear, flat/constant, noperspective), GPU triangle sampling + screenshot and all-logs ZIP via existing GfxSessionRecorder/GfxDownloadsZipExporter to `/storage/emulated/0/Download/Games/cl/test/g/`.
- Reason: GFX039 source-only showed 3,405 linear, 76 constant, 16 noperspective declarations in original DX11 Pixel SHDR. GFX037 found no RDEF/debug in true source programs; actual Material-to-register/CB proof and PC pixel parity still blocked.
- Controls: no original source mesh/Shader48/texture/bytecode shipped in diagnostic APK; distinct package from six-model lab; no real shader restoration claim. A binary build is not actual GPU proof until user runs on Adreno and exports log.
- status: IMPLEMENTING
## Results / CI
Pending.
