# GFX-LAB — 20261110-GFX-chat-source-vs-spirv-binding-19
- session_id: 20261110-GFX-chat-source-vs-spirv-binding-19; origin: chat
- resumed_from: 20261110-GFX-chat-original-register-operands-18
- base_sha: 36fbf0fece5abb5f3e84792f09416cbb4e551e8f
- experiment_key: GFX-MULTI-018-source-DX11-register-versus-SPIRV-descriptor-numeric-comparison
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- issue_id: RENDER-002
- scope: private source original DX11 b/t/s register index sets from one exact original Shader48 VS+FS pair per 7 Passes (14 stages), compare numerically against SPIRV-Cross reflection descriptor sets/bindings after same-stage vkd3d translation. Report aggregate numeric match/mismatch only. Original source and converted code stay inside runner; no Android APK/game changes.
- prior: [GFX-MULTI-017 CI42737442510](https://github.com/alwansan/raf/actions/runs/42737442510) SUCCESS 89 unit tests; 66 CB slots with nonzero CB declared sizes, 29 resources, 27 samplers, 0 duplicate register slots within stage.
- hypothesis: despite equal resource counts, vkd3d may remap descriptor binding numbers, so equality must be measured and must not be treated as semantic parity.
- negative_controls: equal counts but disjoint register numbers fail numeric identity; duplicate SPIRV descriptor sets and missing binding are counted; original register numeric sets never exported; explicit original material semantics=false.
- evidence_level: SOURCE_TO_CPU_SPIRV_REFL_DIAGNOSTIC only. No Android real shader or PC pixels.
- run: GFX-MULTI-018 auto-triggered by workflow push, status CI_PENDING.
- next_step: inspect CI; if numeric binding sets mismatch, create explicit source register-to-SPIRV remap and matched material/CB/sampler layout experiment (not a fake ShaderLab).

## Verified GFX-MULTI-018 outcome
- [Run 42738042943](https://github.com/alwansan/raf/actions/runs/42738042943) COMPLETED SUCCESS with **93** source-free tests. Same ZIP2 authentic Shader48 exact original VS+FS one pair per each 7 Passes (14 stages) translated privately to SPIRV and reflected; original b/t/s register sets compared numerically.
- Source register declarations = SPIRV resource counts in **42/42** stage×family groups; total original declarations **122**, reflected resources **122**; no missing reflected bindings and no duplicate SPIRV descriptor set/binding pair.
- Numerically equal source register set for **all 14/14 constant-buffer groups**. Vertex non-CB empty group sets also trivially equal. **0/7 Fragment texture/resource register sets** and **0/7 Fragment sampler register sets** equal SPIRV binding-number sets. Total 28/42 numeric exact groups includes 14 empty vertex group cases.
- Conclusion: converter remaps or renumbers texture/sampler bindings relative to original DX11 register numbers; **cannot use original t#/s# directly as SPIRV binding values**. Equal CB numbers and resource counts do NOT prove CB layout or semantic Material mapping.
- No original bytecode, register IDs, shader text, material identifiers or generated programs published. Source/converted code purged in runner; originalShaderRestored=false, real Adreno and PC pixel parity remain untested.
- Next experiment GFX-MULTI-019: prove exact original t#/s# -> SPIRV descriptor set/binding map privately and connect to verified Material TexEnv/texture coordinates and GPU sampler semantics. Validate mapping with independent reflection and negative controls; no accidental placeholder ShaderLab.
