# GFX-LAB — 20261110-GFX-chat-joint-class-batch-24-48-31
- session_id: `20261110-GFX-chat-joint-class-batch-24-48-31`; origin=`chat`; resumed_from=`20261110-GFX-chat-pass-scoped-declaration-sampling-30`.
- base_sha: `2fc415bef734a31d3b11f7aa127fcb71f0c3feca`. Only writable branch `experiment/android-graphics-rootcause`. All other project/T-team branches read-only.
- experiment_key: `GFX-MULTI-057`; issue: `RENDER-002`; resource_key: `shader48-original-joint-class-deterministic-private-batch-24-48`.
- Source original ZIP2 pinned commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
## Baseline and goal
- [GFX056 CI42857815446](https://github.com/alwansan/raf/actions/runs/42857815446) SUCCESS: full 524 exact source VS/FS pairs, 157 Pass-scoped JOINT declaration b/t/s+CB size and source DXBC t/s sampled-use classes. **First 24/157** source-private representative pair CPU source-to-SPV checks all passed; **133** class representatives remained untested.
- GFX057 rebuilds deterministic source-private *entire* class order and checks drift (524, 936 compiled stage programs, 110 global/132 Pass-scoped source declaration classes, 58 global sampled-use classes, **157 joint Pass classes**). It then **skips private positions [0,24)** and inspects exclusively **[24,48)**, 24 new original genuine VS/FS exact source pairs. Uses original source SHA and identical selector ordering/inspector as GFX056, with a source-free nonoverlap test, and does NOT rerun prior GFX056 workflow.
## CPU audit and negative controls
- For selected second batch: real DXBC→vkd3d→Vulkan1.1 SPIR-V + spirv-val; original DXBC sampled texture/sampler instruction pair-use multiset versus real translated SPV graph. Original CB b-register SPV global OpName, UBO single vec4 array identity/stride/size and nine bounded ALU opcode original b#/vec access-to-actual-SPV-load range comparisons; unsupported dynamic CB accesses remain unresolved. Categorical failures do not become successes.
- Source-free tests include batch offset negative/overflow, ordering reproducibility, class identity nonoverlap between [0,24),[24,48),[48,70) synthetic classes, and non-leaking aggregate.
- Runner private source, generated DXBC/SPV and temporary files purged unconditionally. Only safe counts/artifact published. No ShaderLab Material→original t/s/b register/CB member semantic proof (GFX054 BLOCKED), no Android GPU or phone APK, no changes T1–T5. `originalShaderRestored=false`.
## Files
- `gfxlab/tools/multi_shader_pass_joint_batch057.py`, `gfxlab/tests/test_multi_shader_pass_joint_batch057.py`, `.github/workflows/gfxlab-multi057-pass-joint-batch24-48.yml`.
- CI not yet verified. After terminal run update session/RESTORE/STATE/MEMORY/OPEN_WORK and safe evidence; next batch planned [48,72).
