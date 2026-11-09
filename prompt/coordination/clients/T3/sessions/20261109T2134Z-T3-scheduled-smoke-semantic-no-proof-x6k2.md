# T3 scheduled — smoke34 authenticated semantic metadata decision

session_id: 20261109T2134Z-T3-scheduled-smoke-semantic-no-proof-x6k2
origin: scheduled
branch: feature/android-native-port
base_sha: b90e9ac968ca2d71902b7edda9919fdbee6ebbe9
work_commit: e77eea7f94927884bd4fba006ad24ea0d2cdf4da
work: prompt/coordination/work/RENDER-002/20261109T2134Z-T3-scheduled-smoke-semantic-no-proof-x6k2.md
resumed_from: 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2; 20261109T2035Z-T3-scheduled-semantic-location-gate-m6q8

## Reviewed
AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM CHAT_AND_SCHEDULE/PROMPT/OPERATING_MODEL, DEVICE_FEEDBACK_42058825739_AR.md, T3 state and MEMORY, latest T3 chat/scheduled, 12 most recent Actions. CL screenshots/logs referenced in device report; no new image-level pixel extraction or new phone evidence in this cycle. Owner's artifact 42058825739 world save/reload is preserved as a limited device success; no general graphics PASS. Newer 8 Nov shared mini-lab policy remains applicable.

## Verified outcome
CI42696526193 SUCCESS: 57 tests including nine mapping-gate synthetic tests, plus authenticated two original smoke34 PS permutations. No explicit HlslSemanticGOOGLE or SPV_GOOGLE_hlsl_functionality1 in source/roundtrip SPV. DXBC register-to-SPV location integer equality original 7/7 vs roundtrip 5/7, not instruction-level provenance. 22 used vs 28 declared original lanes; reflected 28 does not prove missing data. This closes only the annotation-based provenance *hypothesis*, not RENDER-002. Decision and exact negative gate published in independent work file, without repeat CI or game asset modification.

## CI/team status
At preflight branch HEAD b90e9ac968ca2d71902b7edda9919fdbee6ebbe9. Latest 12 Actions all completed; full native 42696228231 failure not owned by T3; T2 summary 42697151936 failure; T3 annotation 42696526193 success. No duplicate CI or cancellation. Work claim committed e77eea7f94927884bd4fba006ad24ea0d2cdf4da, HEAD rechecked equal. No shared GPU/Unity allocation.

## Next for chat or scheduled
Instrument DXBC input operand-to-vkd3d SPV OpVariable ID/Location dataflow on exact original two PS variants privately; refuse guessed name/register mapping. After authenticated mapping, test pass Blend/Alpha and real controlled pixel comparison with CL smoke screenshots. White hand/raft and lighting remain independent unresolved shader/material/variant paths. RENDER-002 OPEN NOT_READY 0/3. No APK/OBB/.meta/.rgd/Settings/audio edits.
