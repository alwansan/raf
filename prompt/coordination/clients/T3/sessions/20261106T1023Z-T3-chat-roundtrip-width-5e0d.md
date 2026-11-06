# T3 chat — authenticated Particle108 HLSL roundtrip vertex output width attribution

- session_id: `20261106T1023Z-T3-chat-roundtrip-width-5e0d`
- origin: `chat`
- status: `completed` — only source-level diagnosis. RENDER-002 OPEN, native Android graphics NOT_READY.
- base_sha: `24aa76f6bb66d6a954448d146a43581b4b1c0407`
- resumed_from_sessions: `20261106T1017Z-T3-chat-roundtrip-interface-c97e`, `20261106T1010Z-T3-chat-fragment-usedmask-5c2f`, and independently scheduled `20261106T0930Z-T3-scheduled-blockcomment-2d7f`.
- work_id: `prompt/coordination/work/RENDER-002/20261106T1023Z-T3-chat-roundtrip-width-5e0d.json`
- experiment_id: `prompt/coordination/experiments/T3/20261106T1023Z-T3-chat-roundtrip-width-5e0d.json`
- experiment_key: `T3-Particle108-original-fourpair-HLSL-roundtrip-same-location-vertex-width-direction-v2`
- resource_key: `T3-original-Particle108-4owners-private-shader-runner`
- workflow: `.github/workflows/raft-t3-particle108-roundtrip-interface.yml`
- run_urls: https://github.com/alwansan/raf/actions/runs/42202565721
- code commit: `097cb1e90b9c26e71505000d76b8b5f1d3750cab`; test commit: `fcbbc28c254d0666926931d5c4903a173e45e93a`; workflow SHA: `0a093842859ef919c8a3210dae9ca9076075a223`.

## Live sources and own independent scope

Read latest T3 historical state, MEMORY and scheduled/chat sessions; T_TEAM live restore, coordination and current owner phone feedback; current work for RENDER-002 and actions. No overlapping T3 scheduled source work or Unity build was active when this scoped SHA-authentic experiment started; T2 Foam and T5 canonical ledger commits were separate and preserved. This is a **distinct question** from previous T3 original DXBC source 46/48 numeric Location; prior 2/2 missing Fragment inputs have original DXBC used_mask zero and source SPIR-V stage pairs 4/4. Previous real HLSL roundtrip [42201795150](https://github.com/alwansan/raf/actions/runs/42201795150) identified 2/4 VSFS type mismatch at same roundtrip Location, not missing location.

Current code adds strict count-only Vertex output type vector-width/class direction and Fragment-consumption classifier to own `scripts/t3_particle108_roundtrip_interface_diagnostic.py`, with 4 new synthetic controls in `tests/test_t3_particle108_roundtrip_interface_diagnostic.py`. The source original immutable ZIP2 ref is `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; the workflow SHA-authenticated four exact original shader/material owner files and six scene files, selected original one-Pass Particle Shader48 four keyword pairs (eight true DXBC stage programs), translated source SPIR-V and recovered-HLSL compiled roundtrip SPIR-V in private job.

## Verified terminal result

[CI42202565721](https://github.com/alwansan/raf/actions/runs/42202565721), job `127841185885`, completed **SUCCESS**. Python py_compile and **15/15 source-free negative/positive tests pass**, exact original four-owner/six-scene SHA evidence retained. Original vkd3d source VSFS pairs **4/4 compatible**, recovered HLSL roundtrip **2/4 compatible**. No missing Fragment input numeric Location in roundtrip stage link; **two type mismatches at existing VS-output/FS-input Location**.

Across all four source-vs-roundtrip same-numeric-Location Vertex output type changes: **4** changed output records; **2 vector-width narrowings** and **2 vector-width widenings**, **0** same-width base type/class change, **0** unsupported type. Exactly **2** changed Vertex output Locations are consumed by roundtrip Fragment; in both the Fragment input type equals the **original source** Vertex output type, **not** roundtrip Vertex output type. The other **2** changed output Locations are not represented in roundtrip Fragment input. Thus observed conflicts arise from **Vertex output width/type drift** at Fragment-consumed locations rather than Fragment type changes.

This is **anonymous structural numeric SPIR-V reflection**. It does *not* establish original DXBC semantic name/index to recovered HLSL declaration correspondence or original authored shader program equivalence. No per-variant location/type/semantic names, game asset bytecode, private PathIDs, GUIDs or shader names published. No original Unity ShaderLab/Material/Texture/mesh/.meta/FX, T1 FFT, T2 Foam, T4 mouse, T5 integration, Unity APK/OBB/XAPK, audio, Settings, touch, .rgd save or on-phone pixels modified.

## Next work handoff

Private next question: cross-tab exactly **which of the two Fragment-consumed VS output type changes are vector-width narrowing versus widening**, and connect original authored DXBC Vertex output component mask/register to source and roundtrip SPIR-V numeric reflection **without assuming numeric Location is semantic identity**. Inspect the relevant generated `private.hlsl` output declaration semantic/type, build an unambiguous source semantic→field map or report BLOCKED. If possible, construct disposable recovered HLSL output-width candidate and verify `glslangValidator`/spirv-val plus **4/4** stage interface compatibility before touching any Unity shader files. Android device visual validation still required; RENDER-002 OPEN / NOT_READY.
