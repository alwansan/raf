# T3 chat — genuine SHA-original smoke34 binary UserSemantic decoration evidence

session_id: `20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2`
origin: `chat`
issue_id: `RENDER-002` OPEN / NOT_READY 0/3
base_sha: `d8da9a55fab4722aca0ff02cb4ea77c9a860265c`
branch: `feature/android-native-port` (only writable branch)
resumed_from_sessions: `20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8`, `20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7`
work_claim: `prompt/coordination/work/RENDER-002/20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2.md`, published at [a4c05fb](https://github.com/alwansan/raf/commit/a4c05fbdd9c796252d7933c86b0cac495d5a7078).
experiment_key: `t3-sha15964-smoke34-two-keyword-private-fragment-dxbc-to-original-and-roundtrip-spv-explicit-UserSemanticGOOGLE-availability-v1`
resource_key: `sha15964-smoke34-original-private-fragment-spv-UserSemantic-2paired-T3`

## Restored context
Latest [CI42692895633](https://github.com/alwansan/raf/actions/runs/42692895633) authenticated original smoke34 DXBC PS: 7 true user inputs across exact 2 matched permutations, 28 input lanes declared but only 22 read by PS; original/roundtrip SPV reflection shows 28 declared lanes. [CI42691211652](https://github.com/alwansan/raf/actions/runs/42691211652) 7/7 source original VS↔PS Semantic+Index matches. [CI42689814110](https://github.com/alwansan/raf/actions/runs/42689814110) source and derived `spirv-cross` generated names do not match (0/13 input, 0/9 output), so no original mapping from names.
Latest scheduled session `20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8` already produced a **synthetic** fail-closed explicit mapping validator `scripts/t3_smoke34_location_provenance_gate.py`. This chat did not edit or duplicate scheduled code. T1/T2/T4/T5 own separate scopes; full original game XAPK CI42696228231 belongs to other workflow, not T3. No game asset/APK/OBB changes or CI cancellations here.

## Actual work
- Created `scripts/t3_smoke34_spirv_usersemantic_annotations.py`: bounded direct SPIR-V word opcode parser for Input OpVariable / Location / Component / `OpDecorateStringGOOGLE` `HlslSemanticGOOGLE` and extension declaration. `OpName` and matching numeric Location/REGISTER never treated as semantic evidence. Rejects unsupported member semantic decorations, bad ID/location/width/string, missing extension, duplicate metadata or raw-vs-sanitized reflection mismatch. Private names never enter public output.
- Created `scripts/t3_original_smoke34_usersemantic_probe.py` bound to original six scenes/four owners from immutable ZIP2 `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, uniquely smoke-linked Shader48 17 renderers/34 material slots and original RGB alpha blend pass; exact two keyword-bucket source VS/PS pairs, two genuine PS→SPIR-V Vulkan1.1→HLSL→SPIR-V CPU transfers, all code ephemeral. Only predefined aggregate counts and explicit false gates published.
- Created `tests/test_t3_smoke34_spirv_usersemantic_annotations.py` (12 synthetic) and `tests/test_t3_original_smoke34_usersemantic_probe.py` (8 synthetic, with source-free malicious/dup/missing/spoof controls). Added dedicated isolated SHA-original `.github/workflows/raft-t3-original-smoke34-usersemantic.yml` including nine inherited scheduled mapping gate regressions and 21+7 other inherited tests, not touching source-free gate.
- First [CI42696430679](https://github.com/alwansan/raf/actions/runs/42696430679) failed synthetic wrapper due fixture invoking the same private temp stage twice (a unit test error, no original evidence). Corrected only test reuse of already-computed result [0ab78d](https://github.com/alwansan/raf/commit/0ab78d56f9d8bc50fb5e6adf5601a7b2e7a5df63).

## Final verified authentic source — 2026-11-09 20:50 UTC
- [CI42696526193](https://github.com/alwansan/raf/actions/runs/42696526193) **COMPLETED SUCCESS**: 12+8+9+21+7 = **57 tests passed**. Reverified six scene owners/private original 4 Shader owners, exact two compiled original smoke34 PS permutations, Vulkan1.1 CPU SPV + derived roundtrip private translation.
- **No `SPV_GOOGLE_hlsl_functionality1` extension, no explicit `HlslSemanticGOOGLE` decorations in original or roundtrip SPV**: 0/7 original semantics mapped via explicit metadata, 0/7 roundtrip, all 7 source semantic IDs missing explicit SPV labels in each set.
- **Original DXBC input register number==SPV original Input Location in 7/7 user records**, after HLSL roundtrip only **5/7**, and each numeric match has same declared vector scalar family and width; matching *numbers* are **not a compiler dataflow guarantee** or a source SemanticName+Index match; should not be fed to scheduled provenance validator as authenticated mapping.
- Source/roundtrip 7 SPV input variables and 28 declared SPV lanes each (two pairs total). These measurements confirm consistent earlier 2 changed input locations but no component-dataflow or pixel parity.
- Safe aggregate [artifact 13710355183](https://github.com/alwansan/raf/actions/runs/42696526193/artifacts/13710355183) 885 bytes, expires 2026-11-16 20:49:42 UTC. Zero game code/private shader names/bytecode/GUID/PathID or per-stage location values published. RENDER-002 remains OPEN NOT_READY 0/3.

## Next
Provenance must be **instruction-derived or compiler-interface authored**: trace original DXBC DCL input operand registers through vkd3d to SPV `OpVariable` + `Location` IDs with an independent inspectable mapping, then ensure per-lane semantic/index and interpolation before synthesizing ShaderLab; controlled Unity GPU/Adreno pixels and owner smoke-square correlation separately required. No fabricated semantic name mapping, no new phone test necessary. Scope completed and resource released.
