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

**Workflow:** [original high-use four-pass source translator](../.github/workflows/raft-t3-original-921-fourpass-translation.yml). **CI:** [#42052605123](https://github.com/alwansan/raf/actions/runs/42052605123). **Verified real outcome:** [CI42052605123](https://github.com/alwansan/raf/actions/runs/42052605123) completed **SUCCESS**, committed original source test at `86065408846ef4268ce9a26112c09547bd613bfc`; 15 new four-pass synthetic tests + 12 prior high-use source tests + 12 original Renderer source tests + 22 inherited B03 tests = **61 tests passed**, and the real original six-scene/four-owner SHA source translation completed. SHA-verified input and original source used, translated derivative files never uploaded. T5 simultaneously owns an independent full native [CI42052375742](https://github.com/alwansan/raf/actions/runs/42052375742), which was not modified or cancelled.


## Verified real source translation and reflection counts

All counts below come from the **real** source-bound pipeline in [CI42052605123](https://github.com/alwansan/raf/actions/runs/42052605123), not synthetic test fixtures. Artifact `t3-authentic-original-921-fourpass-SPIRV-HLSL-42052605123` (id **13427388772**) contains numeric aggregate JSON only.

| Stage-level check (one real matched V/F pair × four original Passes) | Verified count |
| --- | ---: |
| Original normal Passes sampled | **4/4** |
| Original compiled D3D11 stages attempted | **8/8** |
| D3D11 stages translated to SPIR-V accepted by Vulkan 1.1 validator | **8/8** |
| Source stages translated to derivative HLSL | **8/8** |
| Derivative HLSL recompiled to Vulkan 1.1-valid SPIR-V | **8/8** |
| Source SPIR-V stage reflections parsed | **8/8** |
| HLSL roundtrip SPIR-V stage reflections parsed | **8/8** |
| Original source-SPIR-V V/F linked Pass interfaces accepted structurally | **4/4** |
| Roundtrip V/F linked Pass interfaces accepted structurally | **4/4** |
| Original ↔ roundtrip **numeric resource-slot binding dictionaries** equal | **8/8** |
| Original ↔ roundtrip **input/output location and type lists** equal | **0/8** |

The last entry is a **proven structural reflection discrepancy** in all eight sampled stages, despite source- and roundtrip-**within-pass** V/F interfaces being mutually compatible and numeric resource-slot layouts appearing unchanged. The exact cause (builtin semantic remapping, explicit input/output relocation, change in register decorations/types, or other) has **not been determined**. This must NOT be erased by a permissive compare or used to claim pixel parity. Next isolate the drift privately by input vs output, location vs scalar type vs builtin semantic shape and test Unity-specific bindings; do not disclose original source shader identifiers or stage bytecode.

Only 8 selected stage programs out of 58 distinct linked original DXBC programs and 4 selected pairs out of 33 original matched permutations were translated. Eight unpaired original Vertex variants remain **untranslated**. Source SubShader/Pass render states, per-stage uniform/resource names, sampler/matrix conventions, material keywords in Unity, actual Unity ShaderLab compilation and Adreno framebuffer output remain **unverified**.

## Interpretation safeguards

An SPIR-V validation pass proves that the generated SPIR-V is structurally valid according to the selected validator, **not** ShaderLab render-state fidelity, binding semantic fidelity, correct textures/colors, original HLSL source, numeric image parity or Adreno device pixels. HLSL is a **derived translation**, not recovered original author source. A successful one-pair-per-Pass sample does **not** translate all 33 original matched pairs or restore the eight unpaired Vertex variants. Runtime framebuffer comparison, actual Unity 2021 ARM64/Vulkan shader compilation and device scenes remain separate later acceptance gates.

**Next:** investigate the real 0/8 stage input/output reflection parity before considering Unity ShaderLab installation. Compare generated original versus HLSL-roundtrip SPIR-V stage interface decorations and binding semantics privately; then inspect genuine constant buffer/texture/sampler/keyword and original Pass state. Do not install synthesized shaders, bypass Unity graphics gates or declare RENDER-002 READY.
