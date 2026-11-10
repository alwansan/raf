# GFX-LAB 20261110-GFX-chat-524-original-resource-profile-coverage-29
- session_id: `20261110-GFX-chat-524-original-resource-profile-coverage-29`; origin=`chat`; resumed_from=`20261110-GFX-chat-original-property-register-evidence-gate-28`.
- base_sha `7f20ad1e6ec84de2db986bd4a51f2684077f4014`; only writable branch `experiment/android-graphics-rootcause`; source ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- experiment_key `GFX-MULTI-055`, issue_id `RENDER-002`; resource_key `original-source-all-524-shader48-declaration-structural-coverage`.
## Motivation
- GFX054 [CI42852112971](https://github.com/alwansan/raf/actions/runs/42852112971) 377 tests, source property-to-GPU b/t/s identity BLOCKED: Shader48 RDEF/debug and `m_Parameters` absent from checked original ZIP2; no new source mapping witness. Do not re-audit the absent metadata, invent Material binding or call compiler SPIR-V property identity proof.
- GFX049 covered 58 original t/s sampling profiles (not all 524) and GFX052–053 proved 66/66 original CB source register→SPV global+vec4 layout, 208/208 source CB vec4 range loads, **only 14 source stages chosen as first pair in each of 7 passes**. The exact original b/t/s declaration **structural coverage across all 524 exact matched VS/FS pairs** has not been independently classified; untested CB/texture/sampler layouts could exist.
## Method and limitations
- Parse SHA-authenticated original DXBC source real stage `code_from_ref` and SHDR declaration using `private_source_slots`, cache by genuine original `BlobIndex`/program type/stage (max 1656), canonicalize private original b-register slot+vec4 sizes and t/s sets.
- Count anonymous distinct private joint VS/FS structural declaration profile classes across **all 524 exact keyword+tier paired variants**, and by original public Pass; count which variants share/differ from the first representative pair that earlier GFX053 used. No private register IDs, CB sizes, shader bytecode, names, variant IDs, keywords, actual signature hashes or linkage records exported.
- The presence of a source CB/t/s declaration has no ShaderLab/Material property mapping and same b/t/s profile does **not** imply equal shader ALU instructions, textures, sampler state or GPU pixels. Do not expand the 14-stage SPIR-V proof to all 524. No new APK, Unity project rebuild, or T-team changes.
- Synthetic negative tests: one slot same count different identity, CB vec4 count changed, source CB register changed, wrong/missing CB size, empty CB, unbounded/invalid row, false semantic elevation. Original source-private CI plus unconditional purge.
## Files / CI
- `gfxlab/tools/multi_shader_original_decl_profile_coverage.py`
- `gfxlab/tests/test_multi_shader_original_decl_profile_coverage.py`
- `.github/workflows/gfxlab-multi055-all-524-declaration-coverage.yml`
- CI pending. `originalShaderRestored=false`, `phase_closed=false`.

## Verified final CI / corrected scope conclusion
- [CI42854556445](https://github.com/alwansan/raf/actions/runs/42854556445) **SUCCESS**, 385 source-free tests; authentic private pinned ZIP2 analyzed all 524 exact matched pairs /1048 stage reference uses and **936 unique source programs** in those matched pairs; purge verified, original private labels/registers/CB lengths and binaries never published.
- **110 global** distinct b/t/s+CB size full paired declaration classes, **132 Pass-scoped** joint VS/FS classes (32,28,10,16,16,28,2). Only **30** pairs match first chosen pair in their Pass; **494** do not. This is not an error in source: earlier CPU proofs on first exact pair per Pass cannot be extrapolated to all original variants.
- Source pass positions / original exact pairs / structural classes / first-pair mismatches: 0:0=80/32/78, 0:1=156/28/153, 0:2=32/10/28, 0:3=80/16/76, 1:0=40/16/38, 1:1=120/28/117, 1:2=16/2/4.
- **466** vertex and **418** fragment references differ vs own Pass's first-pair **CB register+vec4-length** profile; stage-level counts, not unique variants. 12 reference uses have zero CB declarations; 536 source reference uses each contain no declared t resource and s sampler. No original ShaderLab/material-property semantic map obtained; GFX054 blocker remains.
- Safe [artifact 13782690861](https://github.com/alwansan/raf/actions/runs/42854556445/artifacts/13782690861), expires 2026-11-17T16:27:19Z UTC. Outcome `SUCCESS_ALL_524_ORIGINAL_B_T_S_CB_DECLARATION_PROFILE_SCOPE_UNDERCOVERED_BY_7_FIRST_PAIRS`; originalShaderRestored=false, phase_closed=false.
- Next GFX056 private source select pass-scoped classes (+ sampling-profile class diversity) then bounded compiler-SPV sample validation; not all 524 SPV translated and no Android GPU verified.
