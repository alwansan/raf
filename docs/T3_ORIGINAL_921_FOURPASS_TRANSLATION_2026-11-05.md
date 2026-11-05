# T3 — selected original 921-use Shader48: genuine four-Pass DXBC → SPIR-V → HLSL diagnostic

**Owner:** T3; **origin:** chat; **session:** `20261105T1459Z-T3-chat-921-4pass-translation-c7d2`; **issue:** RENDER-002 OPEN. This is a bounded CPU shader-translator experiment, **not** Unity Android graphics fidelity, an authored shader source restoration, or a device build.

## Already authenticated source baseline

- [CI42042819113](https://github.com/alwansan/raf/actions/runs/42042819113) SHA-pinned original six scenes + four owner source Renderer/Material/Shader48 graph: original highest-use Shader48 referenced by 921 original serialized Renderer material slots.
- [CI42044249541](https://github.com/alwansan/raf/actions/runs/42044249541) authenticated source Shader48 → same-instance AssetRipper shader GUID: this top Shader still carries `DummyShaderTextExporter` after TMP/PostFX/Volumetric vendor-only restorers.
- [CI42046329453](https://github.com/alwansan/raf/actions/runs/42046329453) source name is not an exact match to 198 official Unity2021 built-in shader identities. Exact builtin-name replacement is not a proven recovery path.
- [CI42047611046](https://github.com/alwansan/raf/actions/runs/42047611046) authenticated original top source Shader48 program table: 1 SubShader, 4 original normal Passes, 120 D3D11 compiled entries, 41 original Vertex and 33 Fragment variant records, 33 exact keyword/tier permutation pairs, 8 unpaired Vertex variants. These were source-linkage checks, **not actual code translation**.

## Distinct experiment

The new tool `scripts/t3_original_top_shader_fourpass_translation.py` chooses **one** originally linked Vertex/Fragment program pair from **each of four original normal Passes**, where both the player-table bucket and the source hardware-tier/global/local keyword permutation match exactly. It rejects ambiguous or missing pairs instead of arbitrarily choosing a Fragment stage, building placeholders or dropping the eight unpaired original Vertex permutations.

All scene/provider files are obtained from immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` with original SHA256 and byte-length verification. `UnityPy==1.23.0` reads the true serialized Shader48 program. Each of the eight selected original compiled D3D11 stages is passed privately to the existing `scripts/w1_recover_graphics_programs.py` real `vkd3d-compiler` translation pipeline, followed by `spirv-val`, `spirv-cross --hlsl`, `glslangValidator` and second SPIR-V validation. Where valid, stage reflection is checked through existing `scripts/w1_recover_depth_passes.py` to compare input/output location types, numeric resource binding layouts and original source-SPIR-V V/F interface compatibility.

Only safe **aggregate integer counters** are published: attempts, stages with valid original SPIR-V, HLSL generation, valid HLSL→SPIR-V roundtrip, source/reflected interfaces compared and structurally matching, resource-slot comparison counts. **No** original Shader names/IDs/GUIDs, DXBC, SPIR-V, generated HLSL, source paths, per-code digests or individual translated-program records may be logged or uploaded. All private program files are created inside an automatically deleted GitHub runner temporary directory. The artifact allow-list contains only two previously safe source-number reports and the new aggregate report. Original game assets and `.meta` are not edited.

**Workflow:** [original high-use four-pass source translator](../.github/workflows/raft-t3-original-921-fourpass-translation.yml). **CI:** [#42052605123](https://github.com/alwansan/raf/actions/runs/42052605123). The authentic four-Pass outcome is **pending verification as this document is first written**; do not count green preliminary synthetic checks as a successful translation. At initial inspection, original SHA staging and source tests succeeded; package installation was in progress. T5 simultaneously owns an independent full native [CI42052375742](https://github.com/alwansan/raf/actions/runs/42052375742), which was not modified or cancelled.

## Interpretation safeguards

An SPIR-V validation pass proves that the generated SPIR-V is structurally valid according to the selected validator, **not** ShaderLab render-state fidelity, binding semantic fidelity, correct textures/colors, original HLSL source, numeric image parity or Adreno device pixels. HLSL is a **derived translation**, not recovered original author source. A successful one-pair-per-Pass sample does **not** translate all 33 original matched pairs or restore the eight unpaired Vertex variants. Runtime framebuffer comparison, actual Unity 2021 ARM64/Vulkan shader compilation and device scenes remain separate later acceptance gates.

**Next:** record real translation counts; identify the first failing phase if any, then privately inspect genuine constant buffer/texture/sampler/keyword and original Pass state. Do not install synthesized shaders, bypass Unity graphics gates or declare RENDER-002 READY.
