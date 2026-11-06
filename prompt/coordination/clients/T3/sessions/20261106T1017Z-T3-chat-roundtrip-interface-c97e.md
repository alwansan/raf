# T3 chat — authentic Particle108 HLSL roundtrip four-pair VSFS drift diagnostic

- session_id: `20261106T1017Z-T3-chat-roundtrip-interface-c97e`
- origin: `chat`
- status: `waiting_ci` (source/fixture stage complete, original HLSL comparison pending)
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

## Waiting/next

At initial poll run [42201795150](https://github.com/alwansan/raf/actions/runs/42201795150), job `127838602630` was in progress after source-free Python check succeeded; immutable source checkout in progress. Inspect terminal job and safe count log, record pass/fail without leaking private script error data. If 2/4 roundtrip confirmed, attribute mismatch to location or type, classify which stage shifted and whether original compiled active reads are present as *numeric candidates*; avoid automatic shader changes. If failed, root-cause isolate and fix without repeating equivalent expensive job blindly. No Unity APK/OBB/Adreno pixel claim.

No original game ShaderLab, asset, .meta/GUID, .rgd, FX prefabs, world, water FFT, audio, Settings or touch modified; no other client's action canceled.
