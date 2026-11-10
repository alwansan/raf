# 20261110-GFX-chat-obj-duplicate-attribute-parity-08
- session_id: 20261110-GFX-chat-obj-duplicate-attribute-parity-08; origin: chat
- resumed_from: 20261110-GFX-chat-original-obj-index-parity-07
- base_sha: 010089bba8cb2af2a0d6697674bd07f1b7cfe8f1
- experiment_key: GFX-MULTI-008-source-float32-attribute-dedup
- scope: source-only, measure duplicate original OBJ position/UV/normal tuples in float32 as possible cause for Unity-import 374 duplicate-merging vertex delta. No game build or shader source export.
- source_ref: ZIP2@15964ea8f246b6e076ce26b60931ee2e1a9a2385
- runs: GFX-MULTI-006 revised CI42726999353 SUCCESS; GFX-MULTI-007 CI42727286357 SUCCESS; new CI pending.
- GFX-MULTI-006 result: 7 Passes contain source variants within Unity2021 m_PlayerSubPrograms: P0 192VS/152FS, P1 156/169, P2 32/32, P3 96/152; Subshader1 P0 96/76, P1 120/130, P2 16/16. Keyword metadata and BlobIndex present, no original Android execution. 52 tests passed, private source purged.
- GFX-MULTI-007 result: all source OBJ v/vt/vn referenced, zero unused vertices in all 6; M01 374, M04 374, M02 4 unexplained by unused vertices, needs attribute dedup investigation. 54 tests passed, private source purged.
- unknowns: original shaders not compiled/semantically mapped on Adreno, original rig/animation absent, PC comparison absent. Pass/variant counts are source only.
- controls: duplicate key exact float32 position/UV/normal, no private attributes or model OBJ published.

## GFX-MULTI-008 outcome — proven from CI
- [CI42727777657](https://github.com/alwansan/raf/actions/runs/42727777657): SUCCESS (57 tests), run on commit ed6f8ba200d7673e2e23799ebcf58a742fefe67a.
- ZIP2 original OBJ positions/UV/normals were privately decoded as float32 composite attributes; exact unique counts equal Unity imported vertex count in **all 6/6**.
- M01 source 5095v -> 4721 unique complete attributes -> Unity4721, exactly 374 duplicates; M04 2445 ->2071 ->Unity2071, exactly 374; M02 1666 ->1662 ->Unity1662, exactly 4; M00 375, M03 2163, M05 4452 unchanged.
- All original index positions used (CI007). The discrepancy is fully compatible with vertex attribute dedup, not evidence of lost mesh faces. Still need index-remap/normal-map tangent fidelity and whole-object assembly; no original shader restored.
- All original assets deleted after runner; safe aggregate-only Artifact. 
