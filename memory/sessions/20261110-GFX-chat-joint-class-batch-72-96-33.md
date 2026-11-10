# GFX-LAB 20261110-GFX-chat-joint-class-batch-72-96-33
- session_id=20261110-GFX-chat-joint-class-batch-72-96-33; origin=chat; resumed_from=20261110-GFX-chat-joint-class-batch-48-72-32; base_sha=d4df64554d8dc829bbfb505794f69681c96eb098. Writable branch: experiment/android-graphics-rootcause only.
- experiment_key=GFX-MULTI-059, issue=RENDER-002, resource_key=source-private-Shader48-joint-class-fourth-CPU-batch-[72,96).
- Pinned private original ZIP2 source 15964ea8f246b6e076ce26b60931ee2e1a9a2385; no other branch edit and no original shader code, DXBC or SPIRV published.
## Baseline
GFX056 [CI42857815446](https://github.com/alwansan/raf/actions/runs/42857815446) [0,24), GFX057 [CI42859754233](https://github.com/alwansan/raf/actions/runs/42859754233) [24,48), GFX058 [CI42861618032](https://github.com/alwansan/raf/actions/runs/42861618032) [48,72) each 24/24 strict original CPU source/SPV checks. **72/157** Pass-scoped joint b/t/s CB declaration+sample-use class representatives validated, **85 untested**.
## GFX059 scope and limits
Reconstruct all 524 exact original Shader48 VS/FS keyword/hardware-tier pairs, 936 source stages, 110 global/132 Pass declaration profiles, 58 global/80 Pass t/s source sample-use classes and 157 Pass JOINT classes; deterministic private source order, choose positions [72,96) only; synthetic non-overlap and boundary index71 rejection.
Use source-private vkd3d Vulkan1.1 SPIRV, spirv-val, original DXBC→SPV t/s sample multiset, source b register real SPV Uniform global OpName+reflected CB single vec4 length/stride, and bounded source arithmetic CB vec4-range actual SPV loads. Dynamic CB/other instruction families unresolved. Count only publication and unconditional runner source purge.
No Unity Material property→original GPU t/s/b/CB offsets (GFX054 blocker), no full instruction parity, Android Adreno GPU pixels, no APK or T1–T5 changes; originalShaderRestored=false, phase_closed=false.
## Files
gfxlab/tools/multi_shader_pass_joint_batch059.py
gfxlab/tests/test_multi_shader_pass_joint_batch059.py
.github/workflows/gfxlab-multi059-pass-joint-batch72-96.yml
experiments/20261110-GFX-chat-joint-class-batch-72-96-33.json
CI not yet verified. Update memory/STATE/RESTORE/session/evidence/ledger only after terminal success; next [96,120).
