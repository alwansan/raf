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
