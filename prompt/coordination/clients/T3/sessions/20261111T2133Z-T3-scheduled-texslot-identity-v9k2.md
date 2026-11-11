# T3 scheduled session 20261111T2133Z-T3-scheduled-texslot-identity-v9k2
origin=scheduled
issue=RENDER-002
baseline_sha=c670467b7516d875ca3270fdd38846f85550e602
last_observed_head=c15a71a5496344bcba222e5c7842ea31da6ed579
owner_feedback=docs/DEVICE_FEEDBACK_42058825739_AR.md (world/save/reload confirmed only for artifact 42058825739; white materials and square smoke unresolved)
prior_work=prompt/coordination/T_TEAM/work/20261110T1431Z-T3-scheduled-pair-ci-coverage-k8r2.md; prompt/coordination/T_TEAM/work/20261110T1532Z-T3-scheduled-guid-link-a7q2.md
scope=prompt/coordination/T_TEAM/work/20261111T2133Z-T3-scheduled-texslot-identity-v9k2.md
experiment_key=t3-pair-texenv-slot-identity-negative-control-v1

## Finding and changes
Existing scripts/t3_material_dependency_pair_audit.py compared Counter(GUID), not slot-key identity. A swap of _MainTex and _BumpMap GUIDs could be counted as unchanged. Implemented Counter((slot,GUID)) for YAML m_TexEnvs with same-indent dash slot support. Added tests/test_t3_material_dependency_pair_audit.py synthetic swapped-slot and unchanged controls.
commits=d6524b1040b7bcbf835e3a756c16223a1f40dcf0; fb1366a3945a5fe80fbb5c61c90ec4794af30f72; c15a71a5496344bcba222e5c7842ea31da6ed579

## Validation and limits
Static code review completed; tests not executed (working container cannot resolve github.com, and no duplicate Actions dispatched). No source/exported ZIP2 pair executed. This detects one possible false negative, NOT the phone white texture root cause. Same-relative-path material matching and serialized references only; no Unity import, Android pixels, alpha/lighting or raw asset provenance proven. No .meta/GUID/game assets/save files touched.

## Next
Run python -m unittest tests.test_t3_material_dependency_pair_audit on checkout, then compare pinned ZIP2 and authenticated exported material trees. If swaps found, trace prefab/renderer/material/texture slot and shader variants; if none, prioritize smoke Shader48 render-state and lighting/keyword provenance. Coordinate T4 physical mouse and T5 resolution; no full APK build without readiness protocol.
status=source_change_pending_ci
