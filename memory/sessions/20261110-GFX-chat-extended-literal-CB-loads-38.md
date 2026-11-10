# GFX-LAB — 20261110-GFX-chat-extended-literal-CB-loads-38
- session_id=20261110-GFX-chat-extended-literal-CB-loads-38; origin=chat; resumed_from=20261110-GFX-chat-dynamic-CB-source-shape-37; base_sha=79c11c391c99cf8ffc9d81a0dbab592f9b85ccc4.
- experiment_key=GFX-MULTI-064, issue_id=RENDER-002, resource_key=original-Shaders48-extended-literal-CB-source-range-to-authenticated-SPV-OpLoad.
- Only writable branch experiment/android-graphics-rootcause. Main, feature/android-native-port, ZIP2, CL and T1–T5 untouched.
- ZIP2 original source pinned SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385, private runner only.
## Baseline
- GFX056–062 seven source-private CI runs covered 157/157 Pass joint CLASS representatives via bounded CPU SPV resource checks, not all 524 variant full semantics.
- GFX063 CI42873734355: 1190 source CB previously unresolved operands in nine arithmetic families over 314 original representative source stages: **763 extended modifier but literal source b and vec4 indices**, 350 immediate32+relative and 77 direct relative, 427 truly dynamic. 50 actual SPV dynamic UBO OpLoads in separate 14-stage pilot ≠ source operation parity.
## Current narrow experiment
- Independently read same 157 original representative stage pairs and use strict tokenized source DXBC operand reader to extract private original literal b/vec4 ranges with extended operand modifiers; validate against GFX063 taxonomy and legacy GFX051 static/dynamic counts on each stage. Source operand extension may transform *value* so a literal range match does not prove per-operation or numeric value equivalence.
- Select one original matched VS/FS pair from each of seven Shader48 Passes maximizing literal-index modifier-only source occurrences. Translate **7 pairs / 14 real stage instances** with vkd3d Vulkan1.1 SPV; require spirv-val and independent original source b→real SPV Uniform global name plus strict reflected single vec4-array length/stride. Compare private source modifier-bearing literal vec4 address *range set* against actual translated SPV OpAccessChain/OpLoad vec4 range set; count both matches and misses. Do not assert full 763 reads from a seven-pair pilot, or per-original-instruction semantics from a shared vec4 load.
- Source-free negative tests: DXBC literal vs relative representation, unknown/chained extended operands, declared CB bounds, duplicate source occurrences vs unique range, missing SPV load and component read semantics. Run full Python regressions, publish only anonymous aggregate counters, purge original ZIP2/DXBC/SPV in if:always.
- Material property→authentic DXBC t/s/b register/CB member mapping GFX054 BLOCKED; originalShaderRestored=false, phase_closed=false; no Adreno GPU proof nor T-Team APK/build edits.
## Files
- gfxlab/tools/multi_shader_original_extended_literal_cb_loads.py
- gfxlab/tests/test_multi_shader_original_extended_literal_cb_loads.py
- .github/workflows/gfxlab-multi064-extended-literal-CB-SPV-loads.yml
- experiments/20261110-GFX-chat-extended-literal-CB-loads-38.json.
- CI pending; after final success update memory/STATE/RESTORE_AR/roadmap/safe evidence. Next investigate all 157 source representative modifier-literal CB range checks if pilot viable, then dynamic 427 expression-level traces separately.
