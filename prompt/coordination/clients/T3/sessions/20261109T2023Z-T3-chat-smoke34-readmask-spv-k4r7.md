# T3 chat — genuine original smoke34 PS ReadMask vs SPIR-V scalar lane diagnostic

session_id: 20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7
origin: chat
base_sha: 5016e372792c31a343fde6b25eeb904531181888
resumed_from_sessions: 20261109T2012Z-T3-chat-smoke34-dxbc-semantics-j8m4; 20261109T2003Z-T3-chat-smoke34-name-anchors-n7c2
issue_id: RENDER-002 (OPEN, NOT_READY 0/3)
branch: feature/android-native-port
scope: prompt/coordination/work/RENDER-002/20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7.md
scope reservation commit: 746353c0f54f559154ec4f52dcba4229f49ab174
experiment_key: t3-sha15964-smoke34-2keyword-original-private-dxbc-ps-readmask-vs-spv-original-roundtrip-reflected-input-lanes-v1
resource_key: t3-readonly-zip2-6scene4owner-smoke34-private-isgn-spirv-ps-lane-2pairs

## Restored genuine predecessor evidence
- [CI42691211652](https://github.com/alwansan/raf/actions/runs/42691211652) successful 38 Python tests, SHA-original smoke34 2 DXBC keyword stage pairs, 7 true original VS-output↔PS-input Semantic+Index matched records, zero missing semantic/type/channel mismatch, 28 *declared* output and input lanes. This does NOT prove *used* PS lanes.
- [CI42689814110](https://github.com/alwansan/raf/actions/runs/42689814110) SHA-original private DXBC→SPV 4/4 stages and 4/4 roundtrip validated, 2/2 V/F SPV pairs structurally compatible, compiler reflected name matches 0/13 input, 0/9 output; cannot use generated names as DXBC semantic anchors. Source and phone identity still not proved.
- Read current RESTORE_AR, CHAT_AND_SCHEDULE_AR; older clients/T3/state.json and MEMORY.md are indexes and stale to 2026-11-08. At claim HEAD 5016e37, no overlapping in-progress T3 smoke34 source jobs; T1/T2/T4/T5 distinct scopes, unified Mini owned T5 only.

## New independent evidence question
Compare actual original **fragment ISGN/ISG1 ReadWriteMask read components**, NOT the declared mask width alone, against user input vector scalar widths reflected in original and HLSL-roundtrip SPIR-V from the exact same two SHA-authenticated smoke34 compiled PS permutations. Do not infer per-semantic Location, interpolant, draw-pixel parity, or Unity shader replacement from equal lane counts.

## Implemented / CI checkpoint
- `scripts/t3_original_smoke34_ps_readmask_spirv.py` commit [36a2a23](https://github.com/alwansan/raf/commit/36a2a2376e3931b3c64ab0dc12c84e2783a4985a) exact original smoke34 private SHA object/pass selector and two genuine PS stage translation CPU only, reuses tested DXBC signature + read-mask helpers; private typed raw data discarded; public aggregate fields fixed allowlist, failed source signals INCONCLUSIVE error type only.
- `tests/test_t3_original_smoke34_ps_readmask_spirv.py` commits [ce532b3](https://github.com/alwansan/raf/commit/ce532b3d85186b22cf9ecda6dcb50eb43614f315) and [b195941](https://github.com/alwansan/raf/commit/b195941a1829bc42794959b592f45898309ec88e): 14 source-free tests for used-vs-declared lanes, genuine VS semantic source baseline, differences to SPIR-V original and roundtrip, bad translator, duplicate location, unsupported SPIR-V type, malicious count/report and no private leakage.
- `.github/workflows/raft-t3-original-smoke34-ps-readmask-spv.yml` commit [c2f00ec](https://github.com/alwansan/raf/commit/c2f00ec6137eeb2736a7c6cbf6bb28d196e96e58) SHA pinned ZIP2 15964ea..., 6 original scenes and 4 owners, Ubuntu24.04 apt vkd3d-compiler/spirv-tools/spirv-cross/glslang-tools, bounded private CPU test and 7d safe JSON-only artifact. Per-source 2 PS stage translations, unlike previous four stage source coverage. Does NOT require equality for CI SUCCESS; logs category counts and guard flags.
- Running [CI42692895633](https://github.com/alwansan/raf/actions/runs/42692895633), head c2f00ec, test stage seen completed and private SHA source checkout in progress at last checkpoint. Do not report numerical output until authenticated source log completes.

## Handoff gates
On final Actions conclusion, inspect logs and safe artifact. Source ReadMask totals may differ from SPIR-V reflected vectors; document measured difference without treating it as GPU failure or victory. Update work/experiments/event and this own session. Don't collide with unified Mini, other agents or full game; no phone testing/repair until ShaderLab integration and shader pixels are genuinely proved.

## FINAL authentic SHA-original experiment — 2026-11-09 20:27 UTC

- [CI42692895633](https://github.com/alwansan/raf/actions/runs/42692895633) **COMPLETED SUCCESS**, dedicated source workflow head `c2f00ec6137eeb2736a7c6cbf6bb28d196e96e58`. 14/14 new source-free tests, 21/21 inherited DXBC mask/semantic parser controls, 7/7 smoke stage inventory controls, **42/42** total. SHA-original zip2 15964ea... six scenes/four shader owners reverified.
- Genuine paired smoke34 source original 2 keyword permutations PS ISGN ReadWriteMasks: **7 user PS semantic records with 28 declared components, 22 actually read, 6 declared-but-unread**; 4 partially unread semantic records, 0 completely unread. No original VS missing semantic/read-component, and two original system-value records.
- Both original vkd3d SPIR-V and HLSL roundtrip SPIR-V fragment reflection include **7 user input vectors/28 scalar components**, all compared at 2 original PS stage samples. Comparison of genuine original DXBC actually-read 22 lanes vs original reflected 28: **0/2** stage-permutation equality; versus roundtrip reflected 28: **0/2**. Original-vs-roundtrip reflected lane count agrees **2/2**. Source and derived aggregate absolute reflected-vs-used lane count gap **6**, matching the six declared DXBC channels that were not read.
- Important interpretation: SPIR-V reflection exposes **declared variable widths**, whereas DXBC ISGN ReadWriteMask says source shader **used component lanes**. 22≠28 is expected representational mismatch, *not proof that translator dropped or added live data*, nor an SPIR-V semantic/Location match. There is no private per-semantic/Location mapping evidence, no Unity authored ShaderLab restoration, no device pixels/owner smoke-square identity verified.
- Artifact [13708091567](https://github.com/alwansan/raf/actions/runs/42692895633/artifacts/13708091567), 815 bytes counts-only JSON, expires 2026-11-16 20:26:49 UTC. No private names, paths, shader code, compiled binaries, GUID or PathID released.
- Record under `docs/T3_SMOKE34_PS_READMASK_SPV_2026-11-09_AR.md`, experiment/event same session ID, work completed/released. Only T3 scripts/tests/private CI changed; no game assets, APK/OBB, other agents' files or main edits.
- Next: prove original DXBC semantic-index-register/component ↔ original SPIR-V Location correspondence through explicit per-stage provenance or instruction/dataflow (not generated names or type multiset) and prove pixel parity on a controlled Unity/Android test before claiming smoke fix. Do not ship fake map to Unity.
