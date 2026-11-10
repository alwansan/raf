# GFX-LAB — 20261110-GFX-chat-original-register-operands-18
- session_id: 20261110-GFX-chat-original-register-operands-18; origin: chat
- resumed_from: 20261110-GFX-chat-shdr-declaration-census-17
- base_sha: eeda17d6570315b3362eb4d6685b2ce2342af509
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-017-authentic-original-DXBC-operand-register-shape
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: for one exact source VS+FS per 7 Shader48 passes, parse DCL_RESOURCE/DCL_CONSTANT_BUFFER/DCL_SAMPLER OperandToken0 type/index_dimension/representation and privately recover immediate32 register indices and CB declared sizes; safe aggregate only, no ShaderLab APK or game changes.
- previous: GFX-MULTI-016 CI42736745984 SUCCESS 85 tests; source SHDR declarations 66 CB, 29 resources, 27 samplers, original source bytes purged.
- reference: Microsoft DirectX-Headers D3D12TokenizedProgramFormat.hpp OperandToken0 type [19:12], index dimension [21:20], 3-bit index representation per dimension [22+3i].
- negative controls: reject mismatched operand kind, wrong index dimensionality, relative/dynamic representations, operand extension, invalid source instructions; do not publish original slot values/CB sizes.
- evidence_level: ORIGINAL_SOURCE only. CB register→SPIRV descriptor, original Material/TexEnv and Android runtime parity remain FALSE.
- run: workflow triggered on push; pending CI.
- next_step: inspect CI and persist to live RESTORE/backlog/session/STATE/MEMORY; if source slot decoding valid, plan controlled private source-vs-SPIRV descriptor mapping experiment.

## Verified outcome GFX-MULTI-017
- [CI42737442510](https://github.com/alwansan/raf/actions/runs/42737442510) COMPLETED SUCCESS, 89 unit tests; 14 original DXBC stage declaration operand streams from source Shader48 parsed with authoritative D3D10 index dimension/type/representation checks.
- **66** original CB declaration immediate32 register slots, all **66** have positive declared CB-size indices; **29** original Resource register declarations, **27** Sampler declarations. Within each stage, **0 duplicates** in each category. All stage reports and original bytes purged from ephemeral runner.
- Source register indices were recovered privately by the test; *slot values were not written to public Git or CI log*. That is not proof of source register semantic mapping to SPIR-V descriptor set/binding, CB variable offsets or Material TexEnv.
- Original Shader48 not compiled/run on Android, no original game pixels, no full variant coverage. Next GFX-MULTI-018 independent private register-to-SPIRV descriptor matching attempt with strict fail closed and no public register identifiers.
