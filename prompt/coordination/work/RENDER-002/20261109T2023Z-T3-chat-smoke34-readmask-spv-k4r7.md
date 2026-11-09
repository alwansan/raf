# T3 — original smoke34 fragment DXBC read-mask vs original/roundtrip SPIR-V lane count

session_id: 20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7
origin: chat
base_sha: 5016e372792c31a343fde6b25eeb904531181888
resumed_from_sessions: 20261109T2012Z-T3-chat-smoke34-dxbc-semantics-j8m4; 20261109T2003Z-T3-chat-smoke34-name-anchors-n7c2
issue_id: RENDER-002
status: active
updated_at: 2026-11-09T20:23:00Z
experiment_key: t3-sha15964-smoke34-2keyword-original-private-dxbc-ps-readmask-vs-spv-original-roundtrip-reflected-input-lanes-v1
resource_key: t3-readonly-zip2-6scene4owner-smoke34-private-isgn-spirv-ps-lane-2pairs
intended_files:
  - scripts/t3_original_smoke34_ps_readmask_spirv.py (NEW)
  - tests/test_t3_original_smoke34_ps_readmask_spirv.py (NEW)
  - .github/workflows/raft-t3-original-smoke34-ps-readmask-spv.yml (NEW)
  - docs/T3_SMOKE34_PS_READMASK_SPV_2026-11-09_AR.md (NEW)
  - prompt/coordination/clients/T3/sessions/20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7.md (NEW)
  - prompt/coordination/experiments/T3/20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7.json (NEW)
  - prompt/coordination/B_TEAM/events/T3/20261109T2023Z-T3-chat-smoke34-readmask-spv-k4r7.json (NEW)

At 20:21 UTC HEAD 5016e372; no queued/in_progress same smoke34 T3 original source job in last GitHub Actions. T1 WATER-001, T2 foam, T4 input, T5 unified mini occupy separate source files and resource. Recent CI42691211652 SUCCESS verified 2 exact authentic source DXBC pairs with 7 matched original VS/FS user semantic-index records and 28 declared fragment input/vertex output channels, 0 mismatches. CI42689814110 SUCCESS 4/4 genuine DXBC→SPIR-V CPU and roundtrip, 2/2 VS/FS SPV compatible, but 0/13 source→roundtrip compiler input name matches and 0/9 output name matches. Need not replay the previous experiment without new hypothesis.

This cycle computes **used** channels from original DXBC PS ISGN/ISG1 ReadWriteMask, checks used subset of declaration, matches genuine original VS output mask privately, translates ONLY two exact SHA-original compiled PS stages and privately reflects source and roundtrip SPIR-V input scalar lane cardinalities. Classifies equality/differences as aggregate counters; count equality is NOT DXBC semantic-to-Location proof. Fail closed on unsupported types, source mismatch, malformed program stages or untrusted translator, refuse private name/code/GUID/PathID artifacts. No game asset/APK/OBB/main/other-agent modifications, no redundant heavy Unity CI or competing zip2 checkout, isolated workflow cancel:false. Release scope after CI and journal.
