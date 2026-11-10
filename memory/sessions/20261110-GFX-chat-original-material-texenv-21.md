# GFX-LAB — 20261110-GFX-chat-original-material-texenv-21
- session_id: 20261110-GFX-chat-original-material-texenv-21; origin: chat
- resumed_from: 20261110-GFX-chat-symbolic-binding-map-20
- base_sha: 3cdf399d4656dc05692fcc7f559069372e8f2977
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-020-original-Unity2021-serialized-program-texture-metadata-to-Material-TexEnv
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: six source-verified original Mesh models/seven Material slots and original Shader48 seven Passes. For one source exact VS+FS variant per Pass inspect private Unity 2021 m_Parameters.m_TextureParams m_NameIndex/m_Index/m_SamplerIndex and pass m_NameIndices, compare to original SHDR t/s and original m_SavedProperties.m_TexEnvs names and bound/nonbound entries. No material property names or private indices exported.
- previous_run: [GFX-MULTI-019 CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) SUCCESS 98 tests: 29/29 original texture registers +27/27 sampler registers matched vkd3d SPIR-V symbolic descriptor names, all 56 renumbered. 66 CB program reflected names unrecognized. Material semantics OPEN.
- external schema: AssetStudio SerializedSubProgram Unity>=2021.1.1 m_Parameters, TextureParameter m_NameIndex/m_Index/m_SamplerIndex; SerializedPass m_NameIndices. Name table references resolved privately. Do not equate shader property name/texture role with an actual GPU sample use site without proof.
- controls: source typed original Shader48 exact identity; map passes by (subshader,pass) and only exact source program index/tier; require Material21 and TexEnv schema; missing name/index/role returns zero proven bridge not fabricated mapping; original shader flags false.
- run: GFX-MULTI-020 auto-triggered by workflow commit CI_PENDING.
- next_step: read actual CI and identify which original m_TextureParams t/s metadata are present and match original Material properties. Then independent CB metadata/byte offsets and shader GPU test.
- required end-of-session: update live RESTORE_AR.md, memory/STATE.json, memory/MEMORY.md, current session, gfxlab/OPEN_WORK_AND_IDEAS_AR.md and verify commit.

## Final actual source result GFX-MULTI-020
- [CI42740776655](https://github.com/alwansan/raf/actions/runs/42740776655) **COMPLETED SUCCESS**, 103 source-free tests and privately inspected original ZIP2 Unity 2021.3 Shader48 + seven original Material21 slots.
- Six selected Mesh models, **7 original materials**, **63 material TexEnv entries total**, **21 original Texture2D bound entries**, 42 originally null TextureEnv slots (as typed original material pointers), source original Shader48 `m_ParsedForm.m_PropInfo.m_Props` contains **27** serialized shader properties.
- 7 genuine original Shader48 Passes and 14 exact VS/FS representative source program metadata rows inspected. Each selected `m_PlayerSubPrograms` row **lacks `m_Parameters`**; `0/14` usable SerializedProgramParameters; `0` metadata `m_TextureParams` rows; hence `0` proven name-index→t/s→material bridges.
- Each pass does retain `m_NameIndices` entries: 29,17,6,10,23,15,9, but name-index tables alone **cannot establish original t#/s# binding**. Older GFX-MULTI-006 already reported 0 parameter_metadata_variants across the original program inventory; GFX-MULTI-020 confirms the missing field in the actual selected Shader48 variants and that original Material TexEnvs are present.
- This is a **source metadata absence / evidence limitation**, not absence of textures: authentic DX11 SHDR t/s program registers survived (GFX016/017) and 56/56 symbolic register→SPV descriptors matched (GFX019). Need a separate authoritative property-name→register binding source or a carefully grounded semantic reconstruction; NEVER infer from material property order or declare GPU shader restored.
- Original source assets purged from CI. No private names/indices or shader codes exported. No Android original Shader48/CB layout/normal-map/PC pixel comparison yet.
