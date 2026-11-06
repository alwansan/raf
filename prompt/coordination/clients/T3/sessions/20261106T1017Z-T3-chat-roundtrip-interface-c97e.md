# T3 chat — authentic Particle108 HLSL roundtrip four-pair VSFS drift diagnostic

- session_id: `20261106T1017Z-T3-chat-roundtrip-interface-c97e`
- origin: `chat`
- status: `completed` (source-only diagnostic; real game RENDER-002 OPEN / NOT_READY)
- resumed_from_sessions: `20261106T1010Z-T3-chat-fragment-usedmask-5c2f`; `20261106T014652Z-T3-chat-particle108-authoredsem-1f83`; independent T3 scheduled `20261106T0930Z-T3-scheduled-blockcomment-2d7f`
- base_sha: `a04368f3b4b5197bfb2b9a34969f8921e42c5dc5`
- issue_id: `RENDER-002` (OPEN; Android graphics NOT_READY)
- work_id: `prompt/coordination/work/RENDER-002/20261106T1017Z-T3-chat-roundtrip-interface-c97e.json`
- experiment_key: `T3-Particle108-ZIP2-15964ea8-fourpair-vkd3d-HLSL-SPV-source-vsfs-roundtrip-mismatch-shape-v1`
- resource_key: `T3-original-Particle108-4owners-private-shader-runner`
- run_urls: https://github.com/alwansan/raf/actions/runs/42201795150
- files: `scripts/t3_particle108_roundtrip_interface_diagnostic.py`, `tests/test_t3_particle108_roundtrip_interface_diagnostic.py`, `.github/workflows/raft-t3-particle108-roundtrip-interface.yml` and own work/session/experiment/event only.
- code commit: `c79b22a201db40df84f502ff8eca827773569175`; test commits: `78b175e2d030cd9a2751154a7d00dc64698d443d`, `13dfd0289a0646026d15b684ccbefd992227f177`; workflow SHA: `430b20ef65dc9f9083b7e2525574bb31f9b94712`

## Verified baseline / precise new question

Prior authentic original source [42146385054](https://github.com/alwansan/raf/actions/runs/42146385054) proved all four authored DXBC VS/FS semantic-mask links. Source SPIR-V original pairs 4/4 compatible, HLSL SPIR-V roundtrip pairs 2/4 compatible in [42141506120](https://github.com/alwansan/raf/actions/runs/42141506120). Real original four-pair current private source tests [42199149873](https://github.com/alwansan/raf/actions/runs/42199149873), [42199952229](https://github.com/alwansan/raf/actions/runs/42199952229), and [42200663399](https://github.com/alwansan/raf/actions/runs/42200663399) established 46/48 original user register/type/width numeric source-SPV candidates, two missing exclusively Fragment INPUT, both original DXBC input used_mask 0 and original VS semantic linked. No active original input known lost at *source* stage. Source-to-roundtrip HLSL name semantic identities remain unknown.

New `classify_pair` uses strictly validated source/roundtrip SPIR-V numeric Location+type interfaces for four original SHA-authentic pairs. Separately compares original DXBC fragment compiled used_mask against source and roundtrip *numeric only*, never asserts semantic identity. Reports **only aggregated** missing VS output Locations, same-Location type mismatches, fragment vs vertex stage drift, and original used masks; no per-stage/private names/IDs/locations/bytes. Source-free tests and real original four-source-owner/six-scene SHA path run in independent 26-minute CI.

## Completed authentic source CI and next

At initial poll run [42201795150](https://github.com/alwansan/raf/actions/runs/42201795150), job `127838602630` was in progress after source-free Python check succeeded; immutable source checkout in progress. Inspect terminal job and safe count log, record pass/fail without leaking private script error data. If 2/4 roundtrip confirmed, attribute mismatch to location or type, classify which stage shifted and whether original compiled active reads are present as *numeric candidates*; avoid automatic shader changes. If failed, root-cause isolate and fix without repeating equivalent expensive job blindly. No Unity APK/OBB/Adreno pixel claim.

No original game ShaderLab, asset, .meta/GUID, .rgd, FX prefabs, world, water FFT, audio, Settings or touch modified; no other client's action canceled.

## Terminal proven result — CI42201795150

Completed original SHA-authentic source run [42201795150](https://github.com/alwansan/raf/actions/runs/42201795150) job `127838602630` **SUCCESS**, `11/11` source-free tests and Python syntax PASS. Six original scene providers and four shader/material owners SHA authenticated at immutable ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Four real original DXBC keyword stage pairs/eight programs, original vkd3d-source SPIR-V and independently validated HLSL→SPIR-V roundtrip were reflected privately.

**Source VS/FS stage interface: 4/4 compatible. HLSL roundtrip: 2/4 compatible.** There are **two** fragment-to-vertex type mismatches at an *existing* roundtrip Location, and **zero missing roundtrip Fragment input Locations**. Across all four pairs the total source Vertex outputs are 16 and source Fragment inputs 14, and HLSL roundtrip outputs/inputs retain 16/14 respectively; both Vertex output and Fragment input interfaces change in some numeric Location/type for **all 4 pairs**. Source→roundtrip Vertex outputs have 4 same-Location reflected type changes; Fragment inputs have zero same-Location reflected type changes. Each side also has 4 source→roundtrip numeric Location removals and 4 additions (counts, not copied identities). Two pairs end incompatible specifically due VS output and FS input reflected types disagreeing at matching roundtrip Location.

Original compiled DXBC Fragment user inputs: 16 across exact variants; 14 original `used_mask!=0`, 2 original `used_mask=0`. All 14 active source DXBC inputs are numeric Location candidates in original translated source SPIR-V; 10 remain same numeric Location in HLSL roundtrip Fragment input (numeric coincidence only; not proven original semantic identity). This does **not** prove original compiled semantic-to-generated HLSL location or that a roundtrip type patch is safe. No original shader assets, materials, textures, water, .meta/GUID, save files, Unity build or Android pixels altered.

Evidence: `prompt/coordination/experiments/T3/20261106T1017Z-T3-chat-roundtrip-interface-c97e.json` and own event `prompt/coordination/B_TEAM/events/T3/20261106T1017Z-T3-chat-roundtrip-interface-c97e.json`.

**Next engineering step:** privately identify which original compiled Vertex output semantic registers / component masks map to the 4 observed original-vs-roundtrip Vertex type changes; inspect generated HLSL output `SV_*` / `TEXCOORD*` declaration type and SPIR-V vector widths. Require exact unambiguous mapping and Vulkan validator before any disposable HLSL candidate; no automatic ShaderLab repair. Keep game and issue NOT_READY.
