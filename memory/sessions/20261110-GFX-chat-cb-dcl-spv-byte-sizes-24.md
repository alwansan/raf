# GFX-LAB 20261110-GFX-chat-cb-dcl-spv-byte-sizes-24
- session_id `20261110-GFX-chat-cb-dcl-spv-byte-sizes-24`, origin `chat`, resumed_from `20261110-GFX-chat-58-profile-spirv-check-23`
- base_sha `b63f83d2634fa425aad2711944bd3f1b88b0f780`; branch `experiment/android-graphics-rootcause` only, ZIP2 pinned SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- experiment_key `GFX-MULTI-050`, issue_id `RENDER-002`, scope `original DXBC CB vec4 declarations vs vkd3d SPIRV UBO reflected block_size byte counts`.
- Prior GFX049 [CI42841830832](https://github.com/alwansan/raf/actions/runs/42841830832) 330 tests; 58/58 source sampling-profile pair comparisons passed, 350/350 samples, no original Shader48 Android GPU parity.
## Hypothesis
Original Microsoft tokenized source `dcl_constant_buffer` registers include vector counts. Their 16-byte Vec4 total should be comparable to SPIRV-Cross reflected UBO `block_size` from the same SHA-pinned genuine DXBC stage converted by vkd3d. Distinguish source register identity, generated name length suffix and reflected `block_size` separately; publish count-only stats. Equal total length is not proof of member byte offsets or original Unity property semantics.
## Controls / CI
- Seven exact keyword/tier representative original Shader48 VS/FS pairs (14 stages), not all 524.
- Synthetic source-free negative controls: mismatched size, missing size, unknown reflected symbol, duplicate descriptor, wrong generated name suffix, empty CB stage and bounded vector limits. Private original source purge guaranteed.
- Tool: `gfxlab/tools/multi_shader_original_cb_spv_blocksize.py`, tests `gfxlab/tests/test_multi_shader_original_cb_spv_blocksize.py`, workflow `.github/workflows/gfxlab-multi050-original-cb-spv-blocksize.yml`.
- CI pending: no claim until terminal success.
- OriginalShaderRestored=false; no device APK, Shader48 Android GPU compilation, individual CB byte-offset map, property-to-b# or pixel parity.

## Final evidence / updated interpretation
- [CI42842984932](https://github.com/alwansan/raf/actions/runs/42842984932) 338 tests success, source private purge verified; 66 DXBC source CB declarations and 66 SPV reflected UBO entries in 14 representative original stages; **0/66 name-authenticated CB-register pairs** due unrecognized UBO name grammar. Matches GFX019 CB name unresolved.
- [CI42843665847](https://github.com/alwansan/raf/actions/runs/42843665847) SUCCESS, **341 tests**. Explicitly provisional set0 same numeric source b#→SPIRV binding candidate matches **66/66**, `original DCL vec4_count ×16 == SPV UBO block_size` for all **66/66**, no mismatches/missing sizes; 14/14 stages with full numeric candidate alignment. Name-based original CB identity remains 0/66, CB member offsets remain UNKNOWN.
- Safe count [artifact13775824322](https://github.com/alwansan/raf/actions/runs/42843665847/artifacts/13775824322), expires 2026-11-17T15:23:27Z. All private original shaders, source and SPV staging removed; private values not logged.
- Outcome: SUCCESS_PROVISIONAL_NUMERIC_CB_BLOCK_SIZE_66_OF_66; evidence_level ORIGINAL_SOURCE_AND_CPU_TRANSLATOR_NUMERIC_DESCRIPTOR_CANDIDATE, not named CB semantic identity. OriginalShaderRestored=false; phase_closed=false.
- Next GFX051: source-private original DXBC b# CB access operand->SPIRV access chain/member offset evidence only if independently authenticated; no fabricated CB member layout.
