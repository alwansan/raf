# T5 scheduled — original Resolution delegate evidence hardening
session_id: 20261111T1748Z-T5-scheduled-resolution-graph-m6q8
origin: scheduled
baseline_sha: 9a82050b35b556afaa7c8948810baa3f1e4a9079
resumed_from: 20261111T0146Z-T5-scheduled-v4m8.md
scope: prompt/coordination/T_TEAM/work/20261111T1748Z-T5-scheduled-resolution-graph-m6q8.md
status: source_committed; CI_unverified; NOT_READY

## Evidence
Owner device report docs/DEVICE_FEEDBACK_42058825739_AR.md: run 42058825739 source e9c358eda01785b65e4eb14f18723da426635628 owner confirmed world/save/re-entry; water, cursor, effects and performance issues remain. Prior T5 signed-envelope evidence in 20261111T0146Z session is metadata-only, not cryptographic nested APK/OBB verification.

Live branch HEAD before work 9a82050b35b556afaa7c8948810baa3f1e4a9079 (T4 INPUT-005); existing source-only CI run 43067879408 SUCCESS on earlier SHA c7f042d, not a validation of this patch. No Unity duplicate requested. T4 owns mouse input; T5 only touched source-only Resolution proof gate.

## Change
Added a strict count consistency check to scripts/t5_validate_resolution_delegate_probe.py: option methods with delegate sites cannot exceed two authenticated delegate instruction sites. Added four regression tests in scripts/test_t5_validate_resolution_delegate_probe.py, including runtime success claim rejection. Changes: 4475971c6ab955f9cbe03c1a5cdf45b4c83566f9 and dc5e88697812f8879a0d4f18d8e0a6b4389fd902. Work result: ee24c3ba33d1b7c820fd6520beebd3977c72b9d6.

## Limitations / next
CI/unit tests not executed in this runtime; no claim of verified success. No changes to game Resolution Settings, three right controls, APK/OBB, phone or LogRaft. Next run: run python -m unittest scripts.test_t5_validate_resolution_delegate_probe and investigate actual original Settings callback/persistence evidence before modifying game UI. Signed APK/OBB nested bytes and performance attribution still pending. Stay in Chat; no other clients' sessions or memory overwritten.
