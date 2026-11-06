# T3 chat — authentic Particle108 HLSL VS-output narrowing on Fragment-consumed Locations

- session_id: `20261106T1034Z-T3-chat-consumed-width-0c6e`
- origin: `chat`
- status: `completed` (only source-level diagnostic, RENDER-002 OPEN / NOT_READY; no original game fix or verified Android pixels).
- base_sha: `87ccb82b8e82517f3314583963804aae3fdd56de`
- resumed_from_sessions: `20261106T1023Z-T3-chat-roundtrip-width-5e0d` (chat), `20261106T1026Z-T3-scheduled-91ac` (distinct scheduled scope).
- issue_id: `RENDER-002`
- work: [this session work](../../../work/RENDER-002/20261106T1034Z-T3-chat-consumed-width-0c6e.json)
- experiment: [private aggregate](../../../experiments/T3/20261106T1034Z-T3-chat-consumed-width-0c6e.json)
- run: https://github.com/alwansan/raf/actions/runs/42203844803, job `127845429843` **completed SUCCESS**.
- branch: `feature/android-native-port` only.
- experiment_key: `T3-Particle108-SHA-authentic-fourpair-roundtrip-vertex-width-by-fragment-consumption-v3`
- resource_key: `T3-original-Particle108-4owners-private-shader-runner`

## Team/source overlap and purpose

Read the live RESTORE_AR, CHAT_AND_SCHEDULE_AR and PROMPT_AR, current HEAD, workflow runs, previously verified authentic HLSL width experiment, scheduled session `20261106T1026Z-T3-scheduled-91ac` and owned code/tests. T3 scheduled was working on independent `scripts/t3_shader_identity_gate.py` and its tests. T1 handles FFT, T2 Foam shaders, T4 world, T5 integration; no game shader or shared repair files touched. Prior [42202565721](https://github.com/alwansan/raf/actions/runs/42202565721) proved 4 source VS type changes: 2 narrow, 2 widen, exactly 2 Fragment-consumed. This session resolves which direction is actually consumed.

## Scoped implementation

New isolated work file was registered active on current HEAD before edits. Edited only:
- `scripts/t3_particle108_roundtrip_interface_diagnostic.py` — strict allow-listed count-only Vertex output width/used 2×4 cross-tab, no private HLSL texts, semantic IDs or original programs in aggregate. Code commit `e3f3d12b8a331cd39349ca604b426d3e848522a1`.
- `tests/test_t3_particle108_roundtrip_interface_diagnostic.py` — consumed widening and unconsumed narrowing distinct cases; mixed independent count-conservation fixture and coverage for non-width type/unsupported. Test commit `7fc6df9b93aef285cb4a262fd6147ba14cedb9d9`.
- `.github/workflows/raft-t3-particle108-roundtrip-interface.yml` — trigger scoped SHA-authentic private runner; assert 2 consumed + 2 unconsumed and direction-conservation. CI commit `3a30a95838cc92dbc63f3d170ee6b31688f953d7`.

No original ShaderLab/.shader/.meta, Material, mesh, water, textures, inputs, controls, world/save, APK/OBB/XAPK or Android executable changes. ZIP2 original source pinned to `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; SHA validates 4 original source owners and 6 scenes privately.

## Verified CI outcome and limits

[42203844803](https://github.com/alwansan/raf/actions/runs/42203844803), job `127845429843` **SUCCESS** (2026-11-06 UTC). Python compile/test: **18/18 synthetic source-free tests PASS**. Genuine private original programs: 4 exact original VS/FS variants (8 DXBC stages), source SPIR-V 4/4 vertex/fragment compatible, generated HLSL→roundtrip SPIR-V only 2/4 compatible, two Fragment type mismatches at existing numeric output Location and zero missing Fragment Location. **Both** of the 2 Vertex output changes consumed by Fragment are **vector-width narrowings**; **both** of the 2 unconsumed changes are **vector-width widenings**. The 2 consumed Fragment inputs still expect original source Vertex output type and do not match narrowed roundtrip Vertex type. Counts conserve all four changes (2 + 2), with zero unsupported/base-kind changes. This is a sharper root-cause class, **not proof of original authored DXBC semantic identity, correct generated HLSL field, Unity shader repair, or device appearance**.

The true source shader identity and authored DXBC semantic name/index → generated HLSL Vertex output field → roundtrip SPIR-V output Location correspondence remain UNPROVEN; do not blindly patch output declarations or apply numeric Location as semantic index. Original active Fragment signature records 14; two missing numeric source inputs have zero original compiled used_mask (existing verified prior run). No private per-variant identifiers/Locations/program hashes/compiled bytes leaked.

## Next independently useful action

In a **new isolated work session** inspect HLSL private output struct declarations and real source SPIR-V reflected output *identity* inside ephemeral SHA-pinned CI to determine whether the 2 narrowed consumed outputs arise during SPIRV-Cross HLSL emission or glslangValidator HLSL recompile; require one-to-one source output semantic/field mapping to patch a disposable HLSL candidate. If no unambiguous map, BLOCKED, no Unity gameplay asset edits. Preserve stage/phone acceptance distinction and RENDER-002 OPEN. Scheduled T3 gate work remains separate.
