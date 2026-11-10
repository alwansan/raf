# T3 RENDER-002 — provenance regression result
session_id: 20261110T0130Z-T3-scheduled-provenance-ci-pass-r8v5
origin: scheduled
issue_id: RENDER-002
status: completed_source_only
base_sha: 7b9d290d69a65c41bdc1c5f7b738157a4a476a79
intended_files: prompt/coordination/work/RENDER-002/20261110T0130Z-T3-scheduled-provenance-ci-pass-r8v5.md; prompt/coordination/clients/T3/sessions/20261110T0130Z-T3-scheduled-provenance-ci-pass-r8v5.md
experiment_key: t3-smoke34-provenance-synthetic-unittest-14cases-uint32-boundary-v1
resource_key: none (read-only existing CI)
updated_at: 2026-11-10T01:30:00Z

## Scope and evidence
Continuation of 20261110T0029Z-T3-scheduled-provenance-ci-h6q2; verified the existing CI run https://github.com/alwansan/raf/actions/runs/42728727179: completed/success, source commit 80f4c4d27f6dee329d4a548df592b73beabfcd2b. No duplicate dispatch. Latest observed branch HEAD 7b9d290d69a65c41bdc1c5f7b738157a4a476a79. Latest 15 Actions all completed; T4 mouse and T5 build scopes left untouched. CL owner report is read-only.

## Conclusion
The 14 synthetic unit cases for the structural provenance validator are green in CI. This closes the specific waiting_ci test verification, not original DXBC→SPIR-V instruction-derived mapping, renderer linkage, alpha blending, or phone smoke. The validator returns STRUCTURAL_INJECTION_ONLY by design; no READY claim. 22 used original components versus 28 declared SPIR-V components remain unauthenticated at the semantic-lane level.

## Next falsifiable step
Use SHA-verified private ZIP2 source and pinned DXBC conversion to derive instruction-based component mapping; publish aggregate counts and mismatches only, then compare original/export particle pass Blend/ZWrite/ColorMask and texture alpha to CL images. Coordinate before any heavy run. Do not publish raw shaders/assets. NOT_READY 0/3.
