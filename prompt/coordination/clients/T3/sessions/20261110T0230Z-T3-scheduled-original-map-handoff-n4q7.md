# T3 scheduled — smoke original instruction provenance checkpoint
session_id: 20261110T0230Z-T3-scheduled-original-map-handoff-n4q7
origin: scheduled
resumed_from_sessions: 20261110T0130Z-T3-scheduled-provenance-ci-pass-r8v5; 20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7
base_sha: 144a7b9ccba569035af60112f92d7d7b9f8c895d
scope_commit: 86bf99bdf44acd14748efaf4cec00d9eeccc4834
scope: prompt/coordination/work/RENDER-002/20261110T0230Z-T3-scheduled-original-map-handoff-n4q7.md
issue: RENDER-002 OPEN; NOT_READY 0/3

## Verified
Read current owner feedback, AGENTS, owner requirements, status, T_TEAM live operating model and chat/schedule protocol, T3 memory/state and recent chat/scheduled sessions. Owner confirms world/save/reentry on 42058825739, while visual defects remain. On read branch HEAD 144a7b9ccba569035af60112f92d7d7b9f8c895d. Latest relevant Actions 42728727179 SUCCESS 14 synthetic provenance tests, 42728726420 SUCCESS compatibility. Original private-source 42692895633 SUCCESS, 22 PS read lanes versus 28 declared SPIR-V input lanes; these counts are different measurement domains and do not establish missing live data. CL/test contains 20261109 owner uploads; no newer proven shader correction established here. No Actions duplicated.

## Engineering determination
The current scripts/t3_smoke34_location_provenance_gate.py takes an externally supplied opaque semantic-to-location mapping and intentionally returns STRUCTURAL_INJECTION_ONLY, never an authenticated mapping. Therefore passing its 14 tests cannot close the semantic provenance gate. To establish provenance, a private original-source runner must follow each PS input load in DXBC through the actual VKD3D conversion and SPIR-V access chains, accounting for vector component extraction and compiler optimizations, and reject ambiguous aliases. A direct 7/7 or 5/7 numeric register-location comparison is not sufficient. This is a specific missing experiment, not an observed Android rendering fix.

## Result and limitation
Published isolated scope contract; no new shader code, raw assets, Unity/phone experiment or CI execution this cycle. No assertion of fixing white raft/hand, smoke square, lighting or fire. Other agents' mouse, resolution and Mini APK scopes untouched.

## Next exact step
Read current HEAD and any newer T3 chat session. Use the pinned ZIP2 provider 15964ea8f246b6e076ce26b60931ee2e1a9a2385 and existing original smoke34 private workflow; implement an instruction-derived mapping with fail-closed ambiguous cases and counts-only artifact. Verify 2 keyword permutations and compare actual particle renderer material, Blend/Alpha and ShaderLab before requesting device pixel test. No raw source output. If the converter does not preserve enough provenance, classify INCONCLUSIVE instead of inventing semantics.
