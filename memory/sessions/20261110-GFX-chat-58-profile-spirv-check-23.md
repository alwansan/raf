# GFX-LAB 20261110-GFX-chat-58-profile-spirv-check-23
- session_id `20261110-GFX-chat-58-profile-spirv-check-23`; origin `chat`; resumed_from `20261110-GFX-chat-all-524-dxbc-sampling-22`.
- baseline `974505be51e8ac944f0943e4f0589e8f155e4d4b`, branch `experiment/android-graphics-rootcause` only. Team T1–T5, main, zip2 readonly.
- experiment_key `GFX-MULTI-049`; issue `RENDER-002`; resource_key `gfxlab-original-private-58-source-sampling-profile-spv`
- original pinned ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
## Source baseline and goal
- GFX048 [CI42839415657](https://github.com/alwansan/raf/actions/runs/42839415657) 320 tests SUCCESS: 524 original exact Shader48 VS/FS variant pairs; 58 globally distinct t/s source sample-use multiset profiles; these are not full shader semantics.
- Select one genuine keyword/tier exact pair per each private global t/s source sampling profile from all 524, without logging selected variant identities. For each selected pair convert both stages to Vulkan1.1 SPIR-V using vkd3d and compare direct original SHDR source sampling opcode t/s tuple multiset to the translated actual `OpSampledImage` use graph with SPIR-V verified `OpName` identity. Report safe totals/failure category counters only.
- Negative source-free controls: profile dedup independent of source order, multiplicity, duplicate program reuse, malformed pair/count, bounds and total 524 drift; source-private parser rejects unresolved/dynamic/or absent reflection. No source register/sample pairs or shaders in public.
- Workflow `.github/workflows/gfxlab-multi049-58-profile-spv.yml`; tool `gfxlab/tools/multi_shader_representative_spirv_profiles.py`; pure tests `gfxlab/tests/test_multi_shader_representative_spirv_profiles.py`.
## Current state
- CI pending after code publication. Do not assert parity success until real ZIP2 runner completes, including source purge.
## Interpretation limits
- Selection of 58 sampled-resource usage patterns does not cover all other opcodes, CB, texture semantics, interpolation, Material property→DX11 binding, real original ShaderLab on Android or PC-to-Adreno pixels.
- originalShaderRestored=false, phase_closed=false, original full source→GPU register property bridge remains BLOCKED.

## Final verified CI and fixes
- Final [CI42841830832](https://github.com/alwansan/raf/actions/runs/42841830832) SUCCESS, 330 synthetic Python tests; authentic original SHA-pinned ZIP2 private, runner source purge PASS.
- All 524 original keyword/tier pair records scanned for 58 private global sampling-pattern classes. **58/58** original exact pair representatives converted and validated with Vulkan1.1 SPIR-V and original DXBC t/s sample opcode pair multiset equivalence. 116 selected stage instances, **350/350** sampled operations, no mismatch, 0 failures; 57 sampled stages, 59 zero-sample stages.
- First CI42840578811 yielded 49/58 accepted; CI42841011288 diagnosed nine `GFX046_AMBIGUOUS_SPIRV_OPNAME` caused by non-resource duplicate debug labels. Corrected debug-only filtering to genuine UniformConstant resource globals; duplicate true globals still fail-closed. CI42841494737 Python syntax error and CI42841736438 synthetic fixture error were resolved before final success.
- Safe aggregate artifact [13776926311](https://github.com/alwansan/raf/actions/runs/42841830832/artifacts/13776926311) expires 2026-11-17T15:12:45Z. No original source files, shader bytes, DXBC slot IDs, SPIR-V IDs, or private t/s pairs released.
- Evidence level: ORIGINAL_SOURCE plus CPU translated program SAMPLE-USE parity for representative 58 classes only. Not all 524 variant conversions, and sample profiles NOT complete shader equivalence. Material property→GPU slot/CB member offsets, PC↔Adreno pixels, true original Shader48 Android runtime remain unproved. originalShaderRestored=false, phase_closed=false.
- Next GFX050: source-private Shader48 D3D11 CB declaration vector count ↔ vkd3d Vulkan SPIR-V reflected UBO byte-size census; reject missing/mismatched metadata, no invented property offsets. Then genuine PC reference/HLSL for semantic bridge.
