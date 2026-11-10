# GFX-LAB — 20261110-GFX-chat-joint-class-batch-96-120-34
- session_id=20261110-GFX-chat-joint-class-batch-96-120-34; origin=chat; resumed_from=20261110-GFX-chat-joint-class-batch-72-96-33; base_sha=c124e7194172cd7da2cb7d68e9234afce19371a2.
- Sole writable branch experiment/android-graphics-rootcause; no writing main, feature/android-native-port, zip2 or T-Team work. Pinned ZIP2 source SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385 in ephemeral GitHub Actions only.
- experiment_key=GFX-MULTI-060; issue_id=RENDER-002; resource_key=shader48-original-pass-scoped-joint-source-class-fifth-batch-96-120.
## Verified source baseline
- GFX056 [CI42857815446](https://github.com/alwansan/raf/actions/runs/42857815446) [0,24), GFX057 [CI42859754233](https://github.com/alwansan/raf/actions/runs/42859754233) [24,48), GFX058 [CI42861618032](https://github.com/alwansan/raf/actions/runs/42861618032) [48,72) and GFX059 [CI42863853554](https://github.com/alwansan/raf/actions/runs/42863853554) [72,96), all 24/24 source CPU structural checks. Total **96/157** Pass-scoped original b/t/s CB declaration and real t/s sample-use joint-class representatives CPU verified, **61 pending**.
## New bounded experiment
- Reconstruct all 524 SHA-pinned original exact Shader48 VS/FS keyword+tier pairs, 936 distinct compiled stages, 110 global /132 Pass declaration classes, 58 global /80 Pass t/s sample-use classes and exactly 157 Pass-scoped JOINT classes.
- Select **only [96,120)** (24 authentic original exact VS/FS pairs) from deterministic source-private Pass-round-robin representative order; do not retest [0,96). Source-free unit tests prove all five class slices [0,24), [24,48), [48,72), [72,96), [96,120) disjoint, reject start95 and source corruption.
- Audit original DXBC→vkd3d Vulkan1.1 SPV validator, original t/s opcode sample-use multisets vs actual SPV use, original CB b# real Uniform global OpName plus strict reflected one vec4 array/stride/size and nine supported source arithmetic opcode b/vec4 ranges with actual SPV OpLoad. Dynamic or extended original CB operands and unhandled opcode families remain unknown; no inferred member offsets or pixel parity.
- Count-only public artifact; delete original ZIP2/DXBC and generated SPIR-V unconditionally. GFX054 original Shader48 Material property→original DXBC t/s/b register/CB semantic link BLOCKED, originalShaderRestored=false, phase_closed=false; no Android APK, no T1–T5 edits.
## Files / CI
- gfxlab/tools/multi_shader_pass_joint_batch060.py
- gfxlab/tests/test_multi_shader_pass_joint_batch060.py
- .github/workflows/gfxlab-multi060-pass-joint-batch96-120.yml
- experiments/20261110-GFX-chat-joint-class-batch-96-120-34.json
- CI pending; after terminal run only, update session/RESTORE/MEMORY/STATE/OPEN_WORK and count-only batch ledger. Next expected [120,144).
