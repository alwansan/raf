# T5 — APK/OBB pairing verifier
session_id: 20261109T1459Z-T5-scheduled-obb-pair-a7c2
origin: scheduled
baseline_head: bca32f1a88004047e9fa7df473b85a1c1f93e1d9
experiment_key: t5-apk-obb-pairing-static-v1
resource_key: none (CPU-only; no Unity, CI, or native packaging)
files: scripts/t5_verify_apk_obb_pair.py; prompt/coordination/clients/T5/work/20261109T1459Z-T5-scheduled-obb-pair-a7c2.md; prompt/coordination/clients/T5/sessions/20261109T1459Z-T5-scheduled-obb-pair-a7c2.md
hypothesis: packaging can silently mismatch APK versionCode and main.<versionCode>.<package>.obb; a standalone static checker will reject mismatches and report SHA256/size without claiming phone proof.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md: world/save/reentry on 42058825739; delivery failed; source e9c358eda01785b65e4eb14f18723da426635628; OBB provenance unresolved.
coordination: T4 retains physical mouse; T1/T2 water; T3 graphics; T5 only offline delivery identity. Existing PNG work already CI-proven; no repeated CI. Current GitHub run 42058825739 returns four small diagnostics artifacts, not the owner-mentioned signed/delivery IDs. Do not conclude absent delivery; artifact endpoints may have retention/permission differences.
status: scoped before implementation. No claims of installed APK or GPU performance. Only feature/android-native-port, no force.
