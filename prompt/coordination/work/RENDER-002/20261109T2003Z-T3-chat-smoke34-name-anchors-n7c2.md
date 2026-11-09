# T3 chat claim — smoke34 source SPIR-V vs roundtrip compiler-name anchor uniqueness

session_id: 20261109T2003Z-T3-chat-smoke34-name-anchors-n7c2
origin: chat
base_sha: be69f74c1f4d902e7c731e4a17cc4bd3c7609ff0
resumed_from_sessions: 20261109T1943Z-T3-chat-smoke34-dxbc-translation-c4m8; 20261109T1935Z-T3-scheduled-dxbc-handoff-k7m4
issue_id: RENDER-002
status: active
updated_at: 2026-11-09T20:03:00Z
experiment_key: t3-sha15964-original-smoke34-two-keyword-vsfs-spirv-source-roundtrip-name-type-anchor-evidence-gate-v1
resource_key: original-zip2-6scene4owner-private-CPU-spirv-names-T3
intended_files:
  - scripts/t3_original_smoke34_spirv_translation.py (T3-owned previous)
  - tests/test_t3_original_smoke34_spirv_translation.py (T3-owned previous)
  - .github/workflows/raft-t3-original-smoke34-spirv-translation.yml (only if required)
  - docs/T3_SMOKE34_SPIRV_NAME_ANCHORS_2026-11-09_AR.md (NEW)
  - prompt/coordination/clients/T3/sessions/20261109T2003Z-T3-chat-smoke34-name-anchors-n7c2.md (NEW)
  - prompt/coordination/experiments/T3/20261109T2003Z-T3-chat-smoke34-name-anchors-n7c2.json (NEW)
  - prompt/coordination/B_TEAM/events/T3/20261109T2003Z-T3-chat-smoke34-name-anchors-n7c2.json (NEW)
Scope checked at 20:01 UTC: latest 30 GitHub Actions no in-progress T3 stage or any same resource. Head be69f74, prior CI42687117806 and CI42687834153 success. First proved genuine original D3D11 two keyword pairs, 4 original +4 roundtrip SPIR-V stage compilations valid. Follow-up drift classifier found two inputs and two outputs location-only remap CANDIDATE, all type multisets equal; no original DXBC semantic mapping verified.

New independent hypothesis: can exact *compiler reflected name + type* across same original and derived SPIR-V identify unique candidate anchors for the moved locations, or does missing/renamed compiler metadata prevent even a compiler-name map? Reuse existing strict t3_spirv_interface_name_drift.py classifier with private spirv-cross --reflect from the *same* guarded exact-original translation; allow-list only aggregate counts and flags. Reject duplicate/missing/untrusted raw names, disagreement with safe I/O baselines, wrong classifier schema, bool-as-int, or private identity leakage. Preserve user source and any other T agents' work. Compiler-generated names are NOT original DXBC semantic proof. Existing CI success does not settle this new question.
No APK/OBB/Unity or game source changes, and no repeated source-only census. New code can run on the same dedicated isolated workflow, cancel-in-progress:false.
