# 20261110-GFX-chat-stage-relative-to-SPV-index-shape-46 — GFX-MULTI-072

- origin=chat; role=GFX-LAB; writable branch=experiment/android-graphics-rootcause
- resumed_from: GFX071 CI42887830590 SUCCESS (427 loaded actual SPV dynamic CB vector indices: 350 OpIAdd, 77 OpBitcast), GFX070 CI42886852291, GFX069 CI42884845500
- source SHA: ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- run: https://github.com/alwansan/raf/actions/runs/42888662350
- status=CI_RUNNING on session creation (not yet an approved result)

GFX072 verifies all 157 exact original source representative VS+FS pairs, 314 stages. The source GFX067 relative taxonomy has 77 direct-relative and 350 immediate32-plus-relative index uses. Independently, GFX071 real source-b authenticated Vulkan SPV Uniform CB OpLoad index roots yielded 77 OpBitcast and 350 OpIAdd across the same 157 pairs, though not yet grouped per individual source stage. This pass uses stage-local 2-bin source vs SPV histogram equality, plus SPV OpIAdd literal/bitcast-of-OpLoad shape with strict errors and separate mismatch counts. Equal histograms per stage, even if all 311 CB stages pass, are NOT specific source operand→SPV instruction bijection, matching numeric index, source temp→SPV SSA root proof, or GPU parity; they cannot close GFX054 Material CB semantics.

Only count-only categories and success/mismatch aggregates may be public. Original shader bytecode, temp/register IDs, original offsets, SPV IDs, GUID/PPtr stay runner private; purge always. originalShaderRestored=false, phase_closed=false.
