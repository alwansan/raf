# T5 scheduled checkpoint — 20261111T1154Z-T5-scheduled-resolution-boundary-6b29
session_id: 20261111T1154Z-T5-scheduled-resolution-boundary-6b29
origin: scheduled
branch: feature/android-native-port
baseline_head: 237855531cca5025e91ca7f323773dfdc5107a5b
scope_commit: c3e21a100fdaccdcd020ab92cb354f09f29ec172
scope: work/T5-20261111T1154Z-T5-scheduled-resolution-boundary-6b29.md
status: BLOCKED_ON_AUTHENTIC_SERIALIZED_CALLBACK_EVIDENCE

## Verified observations
Read owner phone feedback (5 Nov), AGENTS, owner requirements, STATUS, T_TEAM prompt and coordination/operating model, and latest T5 scheduled checkpoints. World entry/save/reentry is owner-confirmed for artifact 42058825739 only. Prior source-only right-button regression 42998052750 succeeded; no new device result. Latest head at start is T4 237855531cca5025e91ca7f323773dfdc5107a5b, so T4 physical mouse files are out of scope.

Reviewed existing original-resolution evidence: docs/T5_RESOLUTION_ANDROID_POLICY_REVIEW_2026-11-05.md and docs/T5_ORIGINAL_RESOLUTION_APPLY_CALLERS_2026-11-06.md. Authenticated original Assembly-CSharp.dll (3,211,776 bytes, SHA256 0a6f0527856a9ce538d8d4217358b467c58fdcfad95e0ebebf9588c48f24f72e) shows 3 distinct same-class Apply callers, 1 Screen.SetResolution call in Apply, 0 ResizeBuffers there and 0 direct external Apply callers. One Apply caller uses dropdown APIs but its original serialized event binding and preference persistence are unproven. Existing Android early-return prevents desktop mode change; it does NOT implement lower rendering resolution. DynamicResolution separately owns ResizeBuffers. Source experiment CI 42210936332 passed, but no phone/Unity proof.

## Discriminating conclusion
A new Android resolution option cannot safely be connected to the original dropdown by assuming the dropdown-heavy Apply caller is its event target. The missing serialized Unity callback/persistence edge is a specific source-evidence blocker. Do not add a second menu or change physical Screen.SetResolution to lower GPU cost. Next evidence should inspect pinned original serialized level0/level1/prefab binding privately, classify callback and stored setting, and only then connect equal X/Y render scale with landscape/aspect persistence and source regressions. This run deliberately did not modify game runtime or launch a duplicate Unity workflow.

## Remaining open
Signed APK/OBB full-byte SHA256/versionCode matching and controlled LogRaft comparison on the same phone/scene/settings are not demonstrated. Original report: 57 displayed-frame estimates mean 22.29 FPS and HUD 18.27 FPS / p95 82.82ms; neither equals GPU time. T4 owns physical mouse. Current readiness NOT_READY 0/3.

## Handoff
Check HEAD and active Actions before writing; read work/T5-20261111T1154Z-T5-scheduled-resolution-boundary-6b29.md; obtain original serialized callback evidence and update only existing Settings Android adapter once authenticated. No source or Unity validation executed in this run; no false claim of an implemented Resolution feature.
