# T3 chat — authentic Particle108 missing source SPIR-V Location is Fragment input only

- session_id: `20261106T1002Z-T3-chat-stage-role-misses-7e13`
- origin: `chat`
- issue: RENDER-002 OPEN, NOT_READY; status: completed diagnostic, no game repair claim
- base_sha: `841d3ae2ffc3bb9400f3c4cafcce020a0d48d202`
- resumed_from_sessions: `20261106T0950Z-T3-chat-dxbc-spv-location-27af`; `20261106T014652Z-T3-chat-particle108-authoredsem-1f83`; most recent `20261106T0930Z-T3-scheduled-blockcomment-2d7f` is independent Shader48 gate
- work_id: `prompt/coordination/work/RENDER-002/20261106T1002Z-T3-chat-stage-role-misses-7e13.json`
- experiment_key: `T3-Particle108-original-4pair-48reg-46located-sha15964ea8-stage-role-counts-v2`
- resource_key: `T3-original-Particle108-4owners-private-20min-runner`
- files changed: `scripts/t3_particle108_register_location_probe.py`; `tests/test_t3_particle108_register_location_probe.py`; `.github/workflows/raft-t3-particle108-register-location.yml`; own work/experiment/event/session only
- code commit: `fa3955a3518f5b43fe68da92add4e9176206b2aa`; test commit: `9e0a09f399a90cef35bc9346d9df244f1911b8c0`; workflow commit: `9991791b0952f2d079c1a57bd5f732cfcf9b7869`
- run_urls: https://github.com/alwansan/raf/actions/runs/42199952229

## Confirmed live original results

Actual pinned original ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, 4 source Shader/Material owners and 6 scenes independently SHA verified in job `127832481829`. Four exact Particle108 original DXBC VS/FS keyword pairs, eight original DXBC programs translated to source SPIR-V, type/width/read-only reflection. Source-free Python tests **12 of 12 passed**; run `42199952229` terminal **success**.

Original register→source SPIR-V numeric Location scoped total is unchanged at **46 of 48** exact numeric/type candidates, zero type mismatches, zero lane-count shortfalls, zero extra SPIR-V Locations, **two missing numerical matches**. Stage-role aggregation across all four variants is now proven:

| Stage role | Original user registers | Numerically matching source SPIR-V | Missing |
| --- | ---: | ---: | ---: |
| Vertex input | 12 | 12 | 0 |
| Vertex output | 16 | 16 | 0 |
| Fragment input | 16 | 14 | **2** |
| Fragment output | 4 | 4 | 0 |

Thus the **two missing numerical location cases are exclusively original fragment-stage inputs**, not absent vertex outputs. This is *not* proof of source semantic renaming or compiled HLSL variable identity. Source SPIR-V has no extra location not present in original registers, so this points to omissions rather than demonstrated relocations; the **reason** remains unproven (compiler input elimination vs active data loss). Do not auto patch.

## Boundaries and next exact step

Private shader names, PathIDs, GUIDs, bytecode, register numbers and per-pair records were neither published nor added to public artifacts. Only class-level aggregate counts stored. No Unity .shader, assets, .meta/GUID, T1/T2 shader/water, T4 mouse, T5 release, Android build, touch/Settings/audio, world .rgd or on-device pixels touched. Owner's previous 5 November world/save/reentry test is limited to artifact 42058825739; NO GPU phone acceptance.

Next independent original experiment: for exactly the two absent fragment input numeric register locations, inspect original DXBC input `used_mask` privately and classify zero versus nonzero; compare semantic/mask with original VS output and translated source SPIR-V fragment interface without disclosing names/locations. If the original actually reads a missing register, treat as potential live-varying loss; if unused, consider benign removal but still require native shader fidelity checks. Coordinate with active T3 scheduled jobs before running. RENDER-002 OPEN / NOT_READY.
