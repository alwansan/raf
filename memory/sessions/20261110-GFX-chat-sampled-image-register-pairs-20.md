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
