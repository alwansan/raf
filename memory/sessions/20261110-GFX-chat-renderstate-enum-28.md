# GFX-LAB — 20261110-GFX-chat-renderstate-enum-28
- session_id: 20261110-GFX-chat-renderstate-enum-28
- origin: chat
- resumed_from: 20261110-GFX-chat-sevenpass-channel-apk-27
- base_sha: dfe32cd9ce38e7dad44560065aab67c8b771d8bc
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- experiment_key: GFX-MULTI-028S-original-Shader48-render-state-fixed-vs-dynamic-enum-categories
- issue_id: RENDER-002
- scope: independent source-only seven-Pass Shader48 Cull/ZWrite/ZTest/AlphaToMask and rtSeparateBlend shape, source 7 Material alternative valid/invalid keyword fields. Do not touch Android channel APK CI42748792585 or T-Team. No raw state values, names, shaders or IDs exported.
- baseline: GFX-MULTI-026S [CI42749148702](https://github.com/alwansan/raf/actions/runs/42749148702) SUCCESS 154 tests. Seven m_State records, direct rtBlend/colorMask keys absent, five default queue/materials two explicit, instancing 7/7, m_ShaderKeywords direct field absent. Prior failed CI42749035585 was sparse checkout unit fixture only, rerun passed.
- enum_source: UnityCsReference 2021.3 GraphicsEnums.cs CullMode (Off0/Front1/Back2) and CompareFunction (Disabled0/Never1/Less2/Equal3/LessEqual4/Greater5/NotEqual6/GreaterEqual7/Always8).
- negative_controls: named overrides never interpreted as constant even if val is numeric; missing fields, nonintegral/nonfinite values, out-of-range explicit; no implied blend/color mask effective GPU state. Source values only reported as allowlisted aggregate categories.
- planned_run: GFX-MULTI-028S workflow triggered by push. CI initially pending.
- stage: ORIGINAL_SOURCE only; original Shader48 on Android, source property->register semantic map, PC GPU pixel parity, rig/animation, WATER-001 remain OPEN.
- next_step: inspect CI safe results and update live RESTORE_AR.md, persistent backlog, STATE.json and MEMORY.md. Keep the channel APK workflow independent.

## GFX-MULTI-028S VERIFIED CI42749968983 — source-only negative GPU gate
- [CI42749968983](https://github.com/alwansan/raf/actions/runs/42749968983) COMPLETED SUCCESS, **159** unit tests; authenticated ZIP2 Shader48 (source SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385) 7 Pass state records and seven source Material21 slots.
- **7/7** Passes for each `culling`, `zWrite`, `zTest`, `alphaToMask` have `name` dynamic parameter override; `val` is not safe to interpret as fixed effective GPU enum without resolving material/source property. No static Cull/Depth/AlphaToMask state was proven. **7/7** have `rtSeparateBlend=false`; direct `rtBlend` field absent 7/7, which is not evidence that Blend is disabled.
- `m_ValidKeywords` nonempty in **7/7** source material slots, `m_InvalidKeywords` empty in **7/7**, direct legacy `m_ShaderKeywords` absent in **7/7**. Therefore old metadata absence must not be interpreted as source keyword absence.
- Ground enum names: official [Unity 2021.3 GraphicsEnums.cs](https://github.com/Unity-Technologies/UnityCsReference/blob/2021.3/Runtime/Export/Graphics/GraphicsEnums.cs). Fail-closed unit tests cover numeric enum fallback, invalid/unrecognized value and named dynamic override. Original numeric state values, private property names and source Shader48 bytes never exported; runner purge verified.
- OriginalShader48Restored=false; actual Android diagnostic channel APK (GFX026 [CI42748792585](https://github.com/alwansan/raf/actions/runs/42748792585)) is a separate shader `Hidden/GfxLab/ChannelProbe`, not original Shader48; owner GPU channel images/COPY LOG remain pending. Signed APK checksum documented by parallel delivery owner in RESTORE and `gfxlab/DEVICE_TEST_GFX_MULTI026_AR.md`.
- Next **GFX-MULTI-029S**: verify each dynamic `m_State.{culling,zWrite,zTest,alphaToMask}.name` is a true Shader48 `m_PropInfo` property and occurs in original seven Material `m_SavedProperties.m_Floats`/typed property tables. Reject mismatched alias and unknown parameter; do not guess enum from numeric fallback or source property array order.
