# GFX-LAB 20261110-GFX-chat-pass-scoped-declaration-sampling-30
session_id: 20261110-GFX-chat-pass-scoped-declaration-sampling-30; origin: chat; resumed_from: 20261110-GFX-chat-524-original-resource-profile-coverage-29.
base_sha: 318e54b320e0bb2b09fc521cf735dba395f8d729; writable only experiment/android-graphics-rootcause; original source ZIP2 SHA 15964ea8f246b6e076ce26b60931ee2e1a9a2385.
experiment_key: GFX-MULTI-056; issue_id: RENDER-002; resource_key: shader48-original-pass-scoped-declaration-sample-joint-class-first24-cpu
## Question and hypothesis
GFX055 CI42854556445 (385 tests) proved 132 original source Pass-scoped full b/t/s and CB vector-size declaration classes among 524 exact VS/FS pairs; GFX048/049 found 58 global t/s sample opcode-use classes. They are independent structural dimensions. Re-run exact source-private b/t/s+CB size and actual DXBC sampling use on all 524 pair rows; select one original exact source pair per combined Pass-scoped joint class, not simply first per Pass, without exporting private signatures.
## Scope and controls
- Full original 524 source pairs with same SHA; strict drift cross-check against 110 global/132 Pass declaration classes, 58 global sample signatures, 936 compiled source stages.
- First 24 joint class representatives chosen round-robin over seven Passes; convert only these 24 VS/FS pairs with vkd3d to Vulkan1.1 SPIRV and compare exact source t/s opcode pair use, real original b CB global OpName and reflected UBO vec4 layout plus limited known source CB vec4 literal-load coverage. Report failure/unresolved counts without treating them as validated.
- Negative synthetic tests: same declaration different sampling, different declaration same sampling, repeated rows, different Pass classes, budget and inspector validation, no source identifiers in output. CI original private files purged unconditionally.
- No ShaderLab Material property to original register mapping from GFX054, no full pixel parity, no actual original Android shader runtime; originalShaderRestored=false, phase_closed=false. No APK or T team edits.
- File paths: gfxlab/tools/multi_shader_pass_joint_class_selection.py; gfxlab/tests/test_multi_shader_pass_joint_class_selection.py; .github/workflows/gfxlab-multi056-pass-joint-bts-sample-reps.yml.
CI PENDING.
