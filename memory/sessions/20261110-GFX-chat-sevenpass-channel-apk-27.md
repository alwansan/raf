# GFX-LAB — 20261110-GFX-chat-sevenpass-channel-apk-27

- session_id: `20261110-GFX-chat-sevenpass-channel-apk-27`
- origin: chat
- resumed_from: `20261110-GFX-chat-secondary-color-alias-26`
- base_sha: `ed85119c78897f2631f6cf8dc1e9c6384292261f`
- experiment_key: GFX-MULTI-026-original-sevenpass-states-and-six-model-android-gpu-channel-apk
- scope: original Shader48 seven-pass render states and six-model Android GLES3 diagnostic with channel-viewer, never full game
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- old baseline Unity SHEARS005: https://github.com/alwansan/raf/actions/runs/42707671345 SUCCESS
- six model build baseline: https://github.com/alwansan/raf/actions/runs/42720920391 SUCCESS; owner six-model test not accepted as original Shader48
- last source stage: GFX-MULTI-025 CI42746455458 SUCCESS /146 tests
- status: PREPARING

## Boundaries
No private original source files in Git history, no source GUID/PPtr, no claim that translated DXBC is authentic ShaderLab on Android. Added channel probe is new diagnostic GPU shader (not Shader48) and the source meshes/textures remain exact SHA-linked; Unity Standard PBR remains approximation. User requested APK now and authorised a standalone test APK, not full Raft package or T-TEAM changes.

## Runs, results, owner feedback
Pending. After each CI inspect build/log/artifact SHA/signature/package before saying APK available. User to return screenshots+COPY LOG on Xiaomi; Shader48 original and PC parity remain false.

## GFX-MULTI-026S original seven-pass state census — CI42749148702 SUCCESS (2026-11-10)
Source-only, pinned ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, **154 unit tests** passed after an initial CI42749035585 sparse-checkout test setup failure (4 Unity contract tests looked for omitted Unity assets; source-free-only tests now skip Unity-only contracts when files are intentionally absent). Verified all **7/7** Shader48 source Pass rows have an `m_State` dictionary and tags, with metadata for Cull, ZWrite, ZTest, zClip, Blend separate, alphaToMask, stencil and fog; direct `rtBlend` and generic `colorMask` keys absent. Presence does NOT prove a correct runtime render state or effective Blend/ColorMask behavior. Seven original Material slot rows: instancing enabled 7, shader-default queue -1 in 5, explicit nonnegative queue in 2; `m_ShaderKeywords` direct field absent in 7/7 (not proof there are no keywords in alternate metadata). All source values and IDs private; runner purge successful. Safe artifact [13732363372](https://github.com/alwansan/raf/actions/runs/42749148702/artifacts/13732363372) expires 2026-11-17T03:24:33Z.
- **GFX-MULTI-026 APK build currently NOT completed:** [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585) started at commit 818298ce8fcb71d7906f977c5d03cc8d619db57e, Unity 2021.3.45f2 real import/build IL2CPP ARM64 GLES3 is in progress. Six original SHA-authenticated models, 21 texture role links, original color-space vs forced linear diagnostic channel probe added. Package `com.alwansan.raft.graphicslab.channels`, Android minimal standalone APK only. Verify BuildPipeline, signature, package name, SHA256/CRC, artifact, purge before declaring APK issued.
- **Negative evidence:** `originalShaderRestored=false`, `originalAnimationRestored=false`, `devicePixelsVerified=false`, `PCPixelParityVerified=false`. The new channel probe shader `Hidden/GfxLab/ChannelProbe` is independent diagnostic-only GLES3, **not Shader48**. WATER-001, RENDER-002 remain OPEN.
