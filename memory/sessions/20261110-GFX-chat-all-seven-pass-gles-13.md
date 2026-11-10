# 20261110-GFX-chat-all-seven-pass-gles-13
- session_id: 20261110-GFX-chat-all-seven-pass-gles-13; origin: chat
- resumed_from: 20261110-GFX-chat-shader-gles-stage-io-12
- base_sha: d95c20d78d036ccfc48972206fb5b1df7949a6d8
- experiment_key: GFX-MULTI-013-original-seven-passes-one-variant-each-offline-gles
- scope: 7 original Shader48 passes, each with an exactly keyed genuine DXBC VS+FS variant pair, source-only Vulkan1.1 SPIRV validation + SPIRV-Cross GLSL ES310 + glslangValidator + safe interface/resource counts; no APK/OBB or T-Team changes.
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- proven run: GFX-MULTI-012 CI42732370025 SUCCESS 69 tests. First pass VS/FS both translate and offline GLSL ES310 syntax PASS, SPIRV stage IO 7/7 locations AND types equal, no absent FS inputs or mismatched types, 5 vertex UBO, 7 fragment UBO, 7 separate images, 6 separate samplers. No actual Adreno verification or binding equivalence.
- new run: GFX-MULTI-013 auto-trigger pending; 7 pass representative pairs CPU-only; exact source keywords and hardware tier.
- acceptance: no original shader claim even if all seven pass syntax works: missing full 524 variants, resource bindings, semantic interpolation, original material behavior, Unity/phone GPU, PC parity, rig and animation.
