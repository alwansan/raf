# 20261110-GFX-chat-spv-pointer-origin-48 — GFX-MULTI-075

- origin=chat; role=GFX-LAB; writable branch=experiment/android-graphics-rootcause only.
- resumed_from=`20261110-GFX-chat-spv-index-memory-writer-47` / GFX074 [CI42896574210](https://github.com/alwansan/raf/actions/runs/42896574210) SUCCESS; 545 unit tests, 157 original pair/314 stages, 427 actual loaded SPV index memory roots all pointer provenance UNKNOWN under narrow direct Function-variable guard.
- base_sha before this GFX075 code: `d58a4196d2cd9269baf2e195e14c1641eafcf2b6`.
- experiment_key=GFX-MULTI-075; source_ref=ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.
- question: what is the actual SPV `OpLoad` memory-pointer shape/root storage and anonymous same-block exact pointer `OpStore` pattern feeding these 427 original-b-authenticated UBO index reads?
- code: `gfxlab/tools/multi_shader_spv_index_pointer_origin075.py`, `gfxlab/tests/test_multi_shader_spv_index_pointer_origin075.py`, `gfxlab/tools/multi_shader_original_cb_index_private_multiset075.py`.
- workflow: `.github/workflows/gfxlab-multi075-SPV-dynamic-CB-index-pointer-origin.yml`.
- run: [CI42897768619](https://github.com/alwansan/raf/actions/runs/42897768619) `queued` when first checked (not yet verified SUCCESS).
- scope: authenticated original private b-register/SPIR-V `OpLoad` of a dynamic CB vector index, stage-private 157 original VS+FS joint representatives. Count anonymous pointer def opcode, `Function/Private/Input/Output/other/unresolved` storage, static/dynamic AccessChain indices, same-block prior exact pointer SSA ID `OpStore` syntactic candidate.
- negative controls: wrong CB root, duplicate SSA ID, volatile store/load, branch/function call barrier, different pointer ID even same Function source, dynamic AccessChain pointer indexing, OpCopyObject and Phi, duplicate CB real loads, byte-layout mismatch.
- gate: no original source temp→SPV index SSA mapping, no CFG dominance or pointer alias freedom; exact same pointer result ID is syntax only. `originalShaderRestored=false`, `phase_closed=false`. Shader/material GFX054 source register CB member mapping blocked.
- evidence_level=PENDING_ORIGINAL_SOURCE_AND_TRANSLATED_SPV_CPU; CI must validate Python tests, all 427 and source identity, safe artifact and private runner purge. If failure, correct first and preserve negative evidence.
- next: inspect actual shape buckets, refine real memory stores (GFX076), then source DXBC SSA/CFG separately only if credible pointer evidence emerges.
