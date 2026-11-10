# GFX-LAB — 20261110-GFX-chat-shdr-declaration-census-17
- session_id: 20261110-GFX-chat-shdr-declaration-census-17; origin: chat
- resumed_from: 20261110-GFX-chat-rdef-seven-pass-source-16
- base_sha: af00b6e067b07347e7937c0b90a27f51d4ba019d
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-016-original-DXBC-SHDR-declaration-inventory
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: 14 genuine DX11 SHDR stage chunks from one exact VS+FS pair per 7 Shader48 passes; count opcode declarations 88 resource, 89 constant buffer, 90 sampler, 161 raw, 162 structured. Never export program source, register indexes, keywords, GUID/PPtr or assets.
- previous: [GFX-MULTI-015 CI42736017218](https://github.com/alwansan/raf/actions/runs/42736017218) COMPLETED SUCCESS, 80 tests, 14/14 source stages RDEF absent, all 14 have SHDR and original IO signatures; original register count unknown without independent declaration parsing.
- reference_format: Microsoft DirectX-Headers D3D12TokenizedProgramFormat.hpp D3D10_SB_OPCODE_TYPE enum and instruction length bits [30:24], special CUSTOMDATA length next DWORD.
- negative_controls: fail if DXBC bad offsets, instruction length zero/overrun, wrong claimed token count, invalid custom length. Report aggregate counts only.
- evidence_level: ORIGINAL_SOURCE only, not semantic register-to-Material or SPIRV/Android.
- run: GFX-MULTI-016 workflow triggered by push, status CI_PENDING.
- next_step: inspect CI; if counts recover correctly, decode private original register indexes and compare to independent shader reflection, then Android GPU test only after mapping proves.
- backlog: gfxlab/OPEN_WORK_AND_IDEAS_AR.md

## CI final evidence GFX-MULTI-016
- [CI42736745984](https://github.com/alwansan/raf/actions/runs/42736745984) COMPLETED SUCCESS; **85** source-free tests. Original fixed ZIP2 Shader48 one representative exact VS/FS pair per 7 Passes (14 stage DXBC SHDR chunks) parsed with bounded Microsoft token instruction lengths, without RDEF.
- Declarations across 14 original stages: **66 DCL_CONSTANT_BUFFER**, **29 DCL_RESOURCE (texture/resource)**, **27 DCL_SAMPLER**, **0 raw/structured**. Source register numbers not extracted.
- Source Pass0: VS 5 constant buffers, FS 7 buffers/7 resources/6 samplers, which agrees with SPIR-V *counts* in earlier GFX-MULTI-012. All pass resource counts align with GFX-MULTI-013 safely reported per-pass reflection.
- All 14 stage tokenized streams parsed, 0 custom blocks in representative choices. No original register slot ids/CB offsets, material binding mapping, GLES3 actual shader compile, GPU pixel validation, full 524 pair coverage. Original source purged by CI.
- Next GFX-MULTI-017: decode original private DXBC operand index types/register slots for declarations, compare privately with SPIR-V binding sets, avoid asserting semantic equivalence from equal counts.
