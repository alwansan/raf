# GFX-LAB — 20261110-GFX-chat-symbolic-binding-map-20
- session_id: 20261110-GFX-chat-symbolic-binding-map-20; origin: chat
- resumed_from: 20261110-GFX-chat-source-vs-spirv-binding-19
- base_sha: 3686ec91b4b940ba36393e15d54545ee7ec546b9
- issue_id: RENDER-002
- experiment_key: GFX-MULTI-019-strict-vkd3d-symbolic-original-source-to-SPIRV-descriptor-map
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- scope: one source-authentic keyword/tier matched VS+FS pair from each of Shader48's seven passes. Decode private original DCL b/t/s slots and compare SPIRV-Cross reflected descriptor names and set/binding metadata; accept only exact anchored vkd3d register grammar tN/sN/cbN_size and safe aggregate coverage.
- baseline: GFX-MULTI-018 [CI42738042943](https://github.com/alwansan/raf/actions/runs/42738042943) SUCCESS 93 tests; 122/122 resources count-equal across 42/42 family-stage groups, but all 7 fragment texture and all 7 sampler register numeric sets differ from SPIR-V bindings; CB numeric sets equal 14/14.
- grounded external independent format: vkd3d-shader spirv_compiler_get_register_name in Wine/ReactOS names source registers t%u, s%u and cb%u_%u, but names are not an independent proof of source material/CB/texture sampler semantics.
- negative_controls: reject arbitrary names, out-of-source name, duplicate SPIRV bindings and missing descriptor; synthetic complete name mapping does not turn AndroidShader/Material flags true.
- commands: GitHub Actions workflow gfxlab-multi-vkd3d-symbolic-binding.yml (CI pending).
- evidence_level: SOURCE_TO_CPU_SPIRV_GENERATED_SYMBOL_MAPPING; Android original shader, PC visual comparison, CB layout and Material TexEnv still OPEN.
- next_step: analyze symbolic mapping coverage. If names preserved for each resource, use private mapping for a separate source Material texture/register/properties proof. If stripped, test alternative SPIRV OpName or independent vkd3d config; do not guess.


## First CI attempt failed in a pure test fixture
- [CI42739322749](https://github.com/alwansan/raf/actions/runs/42739322749) FAILED before reading ZIP2: test_empty_groups_complete_but_not_semantically_proven supplied [] instead of set() to strict source slot guard. A genuine parser type guard correctly rejected list input. Fixed test only; re-triggered workflow. No original shader resource conclusion from this failed run. `originalShaderRestored=false`.

## Verified GFX-MULTI-019 outcome
- First CI [42739322749](https://github.com/alwansan/raf/actions/runs/42739322749) FAILED **only synthetic test** because empty slot group was a list, not strict set. Fixed fixture, no Raft source inspected in failed run.
- [GFX-MULTI-019 CI42739427552](https://github.com/alwansan/raf/actions/runs/42739427552) COMPLETED SUCCESS: **98 tests**; original Shader48 7 Passes with one exact VS/FS source pair per Pass translated privately by vkd3d to Vulkan1.1 SPIRV and reflected by SPIRV-Cross.
- All **29/29 source DX11 resource register slots t#** and **27/27 source DX11 sampler slots s#** matched strictly anchored vkd3d generated names and had a distinct SPIRV descriptor set/binding. All **56 of 56** t#/s# mappings numerically renumbered by compiler; **0 unmatched/unknown source t/s names**.
- **66/66 source Constant Buffer names UNRECOGNIZED** under tested vkd3d output regex grammar, so broad all-resource symbolic map remains **FALSE**: 28/42 source resource groups complete (14 true empty vertex resource/sampler groups plus 14 nonempty fragment resource/sampler groups); 56/122 named resources mapped, 66 CB unmapped by names. Numeric CB binding-set parity across 14 stages separately established in GFX-MULTI-018.
- Source and converted bytecode purged from runner. No original private OpName or register slot value published.
- Source shader per-pass metadata `m_TextureParams/m_Samplers/m_ConstantBufferBindings` may provide independent property-index↔register-slot connection; next experiment investigate it to bridge original Material m_TexEnvs and t#/s# without assuming property order. Original Shader48 Android shader/restored FALSE.
