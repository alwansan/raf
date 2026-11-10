# 20261110-GFX-chat-source-ISHL-SPV-ancestry-44 — GFX-MULTI-070

- identity: GFX-LAB; origin=chat; resumed_from: GFX-MULTI-069 CI42884845500
- base SHA: 5d08f083ce6830b39f6348ba9358f7b3a6ee129a
- source SHA: original ZIP2 15964ea8f246b6e076ce26b60931ee2e1a9a2385
- only writable branch: experiment/android-graphics-rootcause
- scope: 157 original Shader48 Pass-JOINT class VS/FS representatives (314 SPV stage instances); independent translated SPV real dynamic Uniform CB OpLoad index shift ancestry, NOT source→SSA instruction matching
- run: https://github.com/alwansan/raf/actions/runs/42886852291
- state at creation: CI_RUNNING; no claim before run logs and source purge verified
- new tools: gfxlab/tools/multi_shader_spv_shifted_cb_index070.py; gfxlab/tools/multi_shader_original_cb_ishl_spv_probe070.py
- tests: gfxlab/tests/test_multi_shader_spv_shifted_cb_index070.py

SPV test requires original source b-register→actual Uniform global OpName/binding and strict reflected single vec4 UBO layout, follows actual OpAccessChain into OpLoad, and recursively checks its own dynamic vec index SSA for OpShiftLeftLogical direct/via supported arithmetic. Phi/Select source ambiguity and unsupported SSA remain UNPROVEN. In parallel independently recount original 427 source relative CB uses, 68 local ISHL writer candidates, 359 unresolved. Even stage-level overlap of original local ISHL and translated SPV shifted UBO reads does NOT prove same original expression, CFG dominance, value equivalence or runtime bounds. Do not export source private registers, SPV IDs, DXBC, original shader bytes or GUID/PPtr. No APK, no Unity build or T1–T5 branch modifications. originalShaderRestored=false, phase_closed=false.
