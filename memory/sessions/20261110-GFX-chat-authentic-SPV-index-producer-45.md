# 20261110-GFX-chat-authentic-SPV-index-producer-45 — GFX-MULTI-071

- Origin: chat; role: GFX-LAB; write branch: experiment/android-graphics-rootcause
- Resumed from: GFX070 [CI42886852291](https://github.com/alwansan/raf/actions/runs/42886852291) SUCCESS, 509 tests, 427 real SPV dynamic UBO loads, zero direct shift ancestry, original DXBC→SPV SSA parity not proven.
- Original ZIP2 source SHA: 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- Base SHA: 5d08f083ce6830b39f6348ba9358f7b3a6ee129a
- GFX071 run: https://github.com/alwansan/raf/actions/runs/42887526330
- State when created: CI_RUNNING; never treat code push as test success.

Source-private 157 original Pass-JOINT representative pairs (314 stages); 311 with authenticated b→real SPV Uniform global + reflected vec4 UBO, 3 without source CB. For every dynamic vector index whose OpAccessChain pointer actually receives OpLoad, classify the SPV defining opcode and bounded unary wrapper chain; for indexes with SPV OpLoad producer also classify the pointer producer opcode. All original shader bytes, dxbc/SPV IDs, actual source registers and program identities stay CI-private; JSON only anonymous histogram/counts and negative capability flags. A value's defining OpLoad opcode does NOT imply which OpStore produced it, original DXBC temp writer or CFG dominance. No Unity game APK, Android or GPU parity. originalShaderRestored=false; phase_closed=false.
