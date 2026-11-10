# 20261110-GFX-chat-normalized-spv-address-stores-49 — GFX-MULTI-076

- role=GFX-LAB; origin=chat; branch=experiment/android-graphics-rootcause only.
- resumed_from: GFX075 [CI42898149143](https://github.com/alwansan/raf/actions/runs/42898149143) SUCCESS 561 tests, 427/427 source-b authenticated real SPV `OpLoad` index pointers = single-literal `OpInBoundsAccessChain` to `Function`, 0 exact same-pointer-SSA-ID prior Store proven. Session `20261110-GFX-chat-spv-pointer-origin-48`.
- baseline SHA at beginning of GFX076 changes: `afd0cbbbff5557b6500b7adb84751c0fc0f54a12`.
- experiment_key=GFX-MULTI-076; source ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- question: when different original source-private SPV `OpInBoundsAccessChain` SSA pointers refer to same Function root and exact literal index path, is a preceding source-translated SPV `OpStore` syntax observed in the same basic block, outside trusted same-block window, or not seen before?
- code: `gfxlab/tools/multi_shader_spv_index_address_path_store076.py`, synthetic tests `gfxlab/tests/test_multi_shader_spv_index_address_path_store076.py`, runner `gfxlab/tools/multi_shader_original_cb_index_private_multiset076.py`, workflow `.github/workflows/gfxlab-multi076-SPV-normalized-Function-literal-path-Store.yml`.
- runs: [CI42899280014](https://github.com/alwansan/raf/actions/runs/42899280014) IN_PROGRESS on submission. Check actual outcome and artifact before claiming pass.
- controls: same root and literal path but different pointer ID, different literal, different Function variable, branch to second block, FunctionCall or unknown pointer Store, OpCopyObject, dynamic path, Volatile, duplicate UBO loads, invalid source-b Uniform CB layout. Source IDs/indices/values and original DXBC remain private in Runner only.
- evidence gate: source-only CPU SPIRV structural syntax. No proof of same effective runtime memory value, alias freedom, CFG dominance, DXBC temp component→SPV SSA, Unity Material CB semantics, original shader GPU pixels. `originalShaderRestored=false`, `phase_closed=false`.
- expected invariant: original 157 pairs/314 stages, 311 CB stages, 427 loaded dynamic UBO index pointers, and exactly 427 anonymous path-categories; do not assert positive candidate count. Runner private SHA source purge mandatory.
- next: if positive same-block path evidence emerges investigate OpStore stored value operand SSA ancestry (GFX077); if none, expand to proven cross-block CFG dominator with safe negative controls instead, never guess that missing local Store means broken shader.
