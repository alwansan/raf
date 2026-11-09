# T3 scheduled — SPIR-V Location bounds hardening
session_id: 20261109T2332Z-T3-scheduled-spv-location-bound-f4k9
origin: scheduled
issue_id: RENDER-002 OPEN / NOT_READY 0/3
resumed_from_sessions: 20261109T2226Z-T3-scheduled-used-lane-superset-q8m3; 20261109T2042Z-T3-chat-smoke34-usersemantic-decorations-v8p2
base_sha: 8cf4fdc75a89987b62eabe396ee1f11fd197a1b0
work: prompt/coordination/work/RENDER-002/20261109T2332Z-T3-scheduled-spv-location-bound-f4k9.md
work_commit: 305a5fc8bf46914091e33476b172a2041469e42f
source_commit: ebd90bc07dff7ff380596d10564dd6361a92f6b2
test_commit: 75e904946a23208854e99d2398f8465a49364b00
experiment_key: t3-source-free-spv-location-uint32-overflow-negative-v1
status: source_published_tests_unverified

## Actual engineering
Read owner phone feedback, T_TEAM protocols, requirements, status, latest T3 chat/scheduled sessions, current source/tests, HEAD and eight latest Actions. Original phone artifact 42058825739 demonstrated world/save/reentry, not graphics restoration. CL square smoke/white hand/raft remain RENDER-002. T4 physical mouse, T5 resolution/UI and mini-build remain separate. Recent T5 Actions 42715257606 and 42715257589 completed failure; no equivalent T3 CI running in the checked eight runs.

The synthetic explicit mapping validator previously accepted arbitrary positive Python integers as SPIR-V Location even though Location decoration operands are uint32. Hardened reflected and mapping Location checks to reject >0xffffffff, preserving acceptance at the maximum valid boundary. Added three source-free tests for overflow reflected, overflow mapping and maximum boundary. This prevents a fabricated out-of-range location from receiving STRUCTURAL_INJECTION_ONLY. This is not semantic provenance, not an original shader fix and not phone pixel evidence.

## Validation limits and next
No local GitHub DNS, so newly added tests were not executed. Existing CI42696526193 57/57 applies to older commit only; it does not validate this change. Next run source-only tests/test_t3_smoke34_location_provenance_gate.py in an isolated CI or available local checkout, then obtain instruction-derived DXBC→SPIR-V input provenance and authentic Blend/Alpha pass evidence before modifying game shaders. Preserve source/ZIP2, .meta/GUID/.rgd, audio and Settings. No Unity, full APK, shared mini APK or CI dispatch. RENDER-002 OPEN, NOT_READY 0/3.
