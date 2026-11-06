# T5 scoped work
session_id: 20261106T0751Z-T5-scheduled-apk-archive-coverage-c81
origin: scheduled
issue_id: INTEGRATION-001
baseline_sha: df106c4e5caa21925cb6c420fd227d9fe2249a86
status: waiting_ci
intended_files: tests/test_t5_verify_apk_obb_pair.py; prompt/coordination/clients/T5/sessions/20261106T0751Z-T5-scheduled-apk-archive-coverage-c81.md; this work file
experiment_key: apk-zip-symlink-encryption-regression-on-synthetic-archive@df106c4
resource_key: none (no Unity)
hypothesis: ZIP entry-type/encryption protection is tested for OBB but not for APK; symmetric tests prevent regressions on signed delivery archives.
resumed_from: 20261106T0654Z-T5-scheduled-pair-ci-a7k2; 20261106T0248Z-T5-chat-native-delivery-retention-e8a3
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md
limitations: no signed binary or device evidence; no gameplay modifications; T4 owns physical mouse.

code_commit: a14d9f1ef5f2b8c347c6c830c159e29b84f78b6f
new_tests: APK symlink; APK encrypted ZIP member
next: verify CI and signed real pair provenance
