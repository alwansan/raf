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
