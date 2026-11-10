# GFX-LAB — 20261110-GFX-chat-variant-reflection-sweep-23

- session_id: 20261110-GFX-chat-variant-reflection-sweep-23
- origin: chat
- resumed_from: 20261110-GFX-chat-original-shader-text-source-22
- base_sha: df6889f4bd9178d0dd5c7b061b77e730e702d280
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-022-authentic-Shader48-all-variant-RDEF-and-parameter-metadata-sweep
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: inspect every authentic Shader48 linked legacy/player stage-variant row, every unique referenced DX11 DXBC stage container, RDEF presence, and serialized parameter metadata. Source bytes and identities remain private in the ephemeral runner.
- workflow: .github/workflows/gfxlab-multi-variant-reflection-sweep.yml

## Runs and execution evidence

- First attempt [CI42742873015](https://github.com/alwansan/raf/actions/runs/42742873015): source audit completed and emitted the full safe report, but the workflow assertion raised `KeyError: rdef_present_stage_programs` because a zero-valued Counter key was omitted from JSON. The private-source purge step still succeeded. This was a workflow/reporting bug after the audit, not a source parsing failure.
- Corrected zero counters explicitly and reran [CI42743017021](https://github.com/alwansan/raf/actions/runs/42743017021): **COMPLETED SUCCESS**, all 119 tests passed, source audit passed, safe artifact uploaded, and private source purge succeeded.
- Safe artifact: [artifact 13730635053](https://github.com/alwansan/raf/actions/runs/42743017021/artifacts/13730635053), expires 2026-11-17T02:29:04Z UTC.
- Final workflow commit: `32f60ca8cd39f5fd4615bbe4c364ac303a65620b`.

## GFX-MULTI-022 final source result

- Six source-authenticated models, seven original Material slots, one exact Shader48 identity, two SubShaders and seven Passes.
- **1,435/1,435** original stage-variant link rows validated; all blob indices and declared program types matched.
- **524** exact keyword/hardware-tier matched VS/FS pairs.
- **1,275** unique referenced stage programs were inspected as bounded authentic DXBC containers.
- RDEF: **0/1,275 present**, **1,275/1,275 absent**.
- Serialized parameter metadata across all 1,435 linked variant rows: **0** non-null `m_Parameters` blocks; **0** null parameter blocks; **0** `m_TextureParams` arrays/entries; **0** `m_ConstantBufferBindings` arrays/entries; **0** top-level sampler metadata rows; **0** top-level constant-buffer metadata rows.
- Shader48 embedded `m_Script` remains absent, consistent with GFX-MULTI-021.
- Safe conclusion: `SOURCE_PROPERTY_TO_REGISTER_BRIDGE_BLOCKED_IN_ALL_REFERENCED_VARIANTS`. Material property name → original DX11 t/s register mapping remains unverified; no order-based inference is permitted.
- The previous GFX-MULTI-019 result (56/56 original t/s register → vkd3d SPIR-V symbolic-name links) remains valid, but it cannot supply the missing Material-property → source-register edge.

## Evidence level, controls and limits

- Evidence level: **ORIGINAL_SOURCE**, using the pinned ZIP2 revision only.
- All 1,435 serialized link rows and all 1,275 unique referenced stage binaries were checked. This does **not** mean every one of the 1,656 compiled-table entries was referenced; unreferenced table entries were not included in this linked-variant sweep.
- No source shader bytes, property names, keywords, register numbers, GUID/PPtr identities, texture pixels or paths were exported. Runner purge confirmed `GFX_MULTI022_ALL_PRIVATE_SHADER_SOURCE_PURGED=true`.
- No Unity Android ShaderLab runtime, Adreno execution, PC pixel parity, original animation/rig restoration or owner acceptance was established. No APK was built.
- `originalShaderRestored=false`; `actual_android_original_shader_pixels_verified=false`; `phase_closed=false`. RENDER-002 and WATER-001 remain OPEN.

## Next step

- **GFX-MULTI-023**: source-only audit of original Material/Texture2D semantics across the seven Material slots and 21 bound textures: exact role counts, original texture format/color-space/mip/stream metadata, UV scale/offset, material tint/color/float metadata, and role-specific decoded-channel statistics for Normal and Metallic maps. Use the authenticated sparse ZIP2 stream pipeline; publish only safe aggregates. This is independent of the blocked property→register edge and must not claim shader or GPU parity.
- After this source audit, plan a controlled PC reference or a narrowly scoped Android GPU experiment only if its inputs and exact Shader48 identity can be grounded. Do not modify T1–T5 branches or create a new worker.
