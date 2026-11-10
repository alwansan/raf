# 20261110-GFX-chat-sampled-image-register-pairs-20 — GFX-MULTI-046
- session_id: `20261110-GFX-chat-sampled-image-register-pairs-20`; origin: `chat`; resumed_from: `20261110-GFX-chat-managed-cil-argflow-19`
- base_sha: `150a3378597daf7f10dfc11ccb0e9d97b9f5a08e`; branch: `experiment/android-graphics-rootcause` only
- experiment_key: `GFX-MULTI-046`; issue: `RENDER-002`, GPU resource register pairing; scope: original source SHA-pinned, no original IL/Shader48 bytes in Git
- source: ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, seven representative exact VS/FS keyword+tier matched pairs (14 stages), not all 524 variants.
- prior verified: GFX045 [CI42833852638](https://github.com/alwansan/raf/actions/runs/42833852638), one original script-side `Set*` first-argument proof; `G8` original Shader48 Material property→DX11 t/s/b/CB still blocked.
## Test / negative controls
Investigate whether translated Vulkan1.1 SPIR-V sample/gather OpSampledImage chain has exact image/sampler pairs grounded by source DXBC SHDR original resource register declarations and vkd3d generated symbolic names. For each stage: verify source register set matches reflected variable names exactly, validate SPIR-V, disassemble with raw IDs, count only OpLoad/OpCopyObject→OpSampledImage→OpImageSample*/Gather direct use. Reject unknown pointers/OpPhi/OpAccessChain, duplicated names, missing IDs, and count unresolved samples. No register numbers or pair edges exported. Source-free tests cover those negative controls.
## Files
- `gfxlab/tools/multi_shader_spirv_sample_use.py`
- `gfxlab/tests/test_multi_shader_spirv_sample_use.py`
- `.github/workflows/gfxlab-multi046-sample-use.yml`
## Run/Result
- CI pending after push. Do not infer success from code publication; check run, purge, aggregate artifact.
## Strict limits
SPIR-V sample pairing is a **compiler-translation** use-site audit, not independent original DXBC instruction-use equivalence. No Material TexEnv property→DX11 t/s source link; no CB byte offsets, original shader Android GPU runtime or real PC-vs-Adreno pixel equivalence. `originalShaderRestored=false`, `phase_closed=false`.

## Final verified CI result
- GFX-MULTI-046: [run 42835954397](https://github.com/alwansan/raf/actions/runs/42835954397) SUCCESS; 305 source-free tests, original ZIP2 SHA pinned and purged; artifact 13773567029 expires 2026-11-17T14:38:22Z
- Private source anchors source DXBC SHDR t/s register sets to converted SPIR-V resource symbolic names, and raw disassembled SPIR-V variables to actual sampled-image use sites. **37/37 sample/gather operations traced**, 0 unresolved; by Pass [10,4,2,6] + [10,4,1]. 29 is SUM of distinct counts within each Pass, not globally unique.
- Two failed attempts were corrected and their private source purged: CI42835402578 missing sparse contract tests; CI42835521326 missing SPIRV-Cross reflection numeric ID was handled by exact unique OpName rather than guessed numeric binding.
- Evidence_level: ORIGINAL_SOURCE_AND_TRANSLATOR_SPIRV_CPU_ONLY; direct original DXBC opcode pair comparison still NOT DONE. Original Shader48 material-property→DXBC t/s register unknown, CB byte offsets unknown, shader Android GPU runtime false, PC↔Adreno original parity false.
- Outcome: SUCCESS_COMPILER_LOWERED_37_OF_37_SAMPLES_SOURCE_REGISTER_ANCHORED. Next GFX047 independent original DXBC sample/gather opcode operand pairing with private comparison to vkd3d translated graph; no APK/game build.
