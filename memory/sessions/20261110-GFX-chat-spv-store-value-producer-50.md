# 20261110-GFX-chat-spv-store-value-producer-50 — GFX-MULTI-077

- role=GFX-LAB; origin=chat; writable branch=experiment/android-graphics-rootcause; no changes to T1–T5/main/zip2.
- resumed_from: GFX076 [CI42899280014](https://github.com/alwansan/raf/actions/runs/42899280014) SUCCESS, 586 tests; original-b-authenticated 427 actual SPV dynamic index OpLoads, of which 128 same-block equivalent Function+literal-address-path Store syntax candidates /47 earlier outside trusted window /252 no matching write seen. Previous GFX075 found 427 original Function-rooted `OpInBoundsAccessChain` index Load pointers and zero same-pointer-SSA-ID matches.
- base_sha before this GFX077 code: `695bddcd52ee3c78ec1ec53d25b59f5d752d3699`.
- experiment_key=GFX-MULTI-077; source=SHA-pinned ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- question: within only 128 syntactic matching Store/Load address-path candidates, what standard SPV result opcode immediately defines Store value? Is there a bounded, transparent SPV SSA `OpShiftLeftLogical` ancestor (direct/via) or no/unknown proof?
- code: `gfxlab/tools/multi_shader_spv_index_local_store_value077.py`, source-free tests `gfxlab/tests/test_multi_shader_spv_index_local_store_value077.py`, 157-pair source runner `gfxlab/tools/multi_shader_original_cb_index_private_multiset077.py` and workflow `.github/workflows/gfxlab-multi077-SPV-sameblock-Function-path-Store-value.yml`.
- CI: [42900376410](https://github.com/alwansan/raf/actions/runs/42900376410) IN_PROGRESS on first check. Final success/failure and deletion to verify.
- synthetic negative controls: direct shift vs IAdd with shift, constant no-shift, memory-loaded unknown, OpSelect unknown, cross-block noncandidate, unknown pointer alias Store barrier, no false original shader correctness.
- expected source-private invariant: 157 original pair, 314 stages/311 CB stages, 427 real UBO index loads, 128 same-block candidates, exactly 128 immediate producer and bounded shift-ancestor aggregate counts. Never leak register numbers, SPV IDs, literal source values or DXBC.
- limitations: same Function literal address path and nearest syntactic Store does NOT prove runtime memory value, alias-free dataflow, CFG dominance or original source DXBC temp/ISHL→SPV SSA identity. Original Shader48 Android shader and GPU parity unproven; GFX054 Material property→CB byte semantics still BLOCKED; `originalShaderRestored=false`, `phase_closed=false`.
- next on completion: persist outcome and all restore documents; only later attempt GFX078 independent CFG/SSA value proof and PC reference.
