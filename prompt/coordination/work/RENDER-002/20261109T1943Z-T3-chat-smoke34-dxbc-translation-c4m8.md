# T3 chat scope — authentic smoke34 D3D11 VS/FS private translation
session_id: 20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8
origin: chat
resumed_from_sessions: 20261109T1935Z-T3-scheduled-dxbc-handoff-k7m4; 20261109T1924Z-T3-chat-smoke34-dxbc-source-p9n2; 20261109T1913Z-T3-chat-smoke34-sameexport-v5m8
issue_id: RENDER-002
base_sha: 65e7b9c353c07927a63e405aaa8b49cd2a424460
status: completed
updated_at: 2026-11-09T19:56:00Z
experiment_key: t3-authentic-smoke34-two-keyword-paired-dxbc-vs-fs-private-vulkan11-spirv-roundtrip-sha15964-v1
resource_key: original-zip2-6scene4owner-small-readonly-T3-two-pair-translation
intended_files:
  - scripts/t3_original_smoke34_spirv_translation.py (NEW)
  - tests/test_t3_original_smoke34_spirv_translation.py (NEW)
  - .github/workflows/raft-t3-original-smoke34-spirv-translation.yml (NEW)
  - docs/T3_SMOKE34_AUTHENTIC_SPIRV_TRANSLATION_2026-11-09_AR.md (NEW)
  - prompt/coordination/clients/T3/sessions/20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8.md (NEW)
  - prompt/coordination/experiments/T3/20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8.json (NEW)
  - prompt/coordination/B_TEAM/events/T3/20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8.json (NEW)
Evidence at scope reservation: original Pass CI42679312674 SUCCESS (RGB ColorMask / alpha-dependent blend / ZWrite OFF); same-instance source/export CI42681908313 SUCCESS shows actual dummy; genuine D3D11 source pairs CI42683328646 SUCCESS (8 table entries, 2 VS +2 FS, exact two keyword matched). T3 scheduled 19:35 has completed documentation-only handoff, did not start source translation. GitHub Actions most recent CI42685509815 T4 success and no active competing T3 translation in latest 30 runs. This task does not touch T1/T2/T4/T5/Unity game, APK, OBB, .meta, save, or original proprietary data.
Plan: exact immutable ZIP2 source SHA-pin; refuse more/fewer than 2 matched stage pairs, run original DXBC→SPIR-V→HLSL→SPIR-V privately with existing pinned translator and strict fail-closed reflection; record only aggregate counts/boolean evidence. No original code, per-stage hashes, private shader IDs, source file paths in artifact or logs. CI compile/source-only tests then real guarded original translation on a separate job; no false pixel equivalence, RENDER-002 OPEN NOT_READY 0/3.

## Completed authentic original CPU check
- Source implementation commits afba7caa, dc1b855, workflow 40ed30bd and guarded IO drift 7bc1b54.
- Original CI42687117806 SUCCESS: original four stage Vulkan SPIR-V + HLSL roundtrip, but original-to-roundtrip IO 0/4 exact.
- Differential CI42687834153 SUCCESS: 12+7 tests, SHA original 6 scene/4 owner, four valid program stages, two VS/FS compatible pairs, output IO remap candidates without changes in type multiset. Artifact 13705233370 safe aggregate only.
- Scope DONE. Release resource_key and no other team file reserved. ShaderLab and installed Android pixels still unproven. RENDER-002 OPEN / NOT_READY 0/3.
