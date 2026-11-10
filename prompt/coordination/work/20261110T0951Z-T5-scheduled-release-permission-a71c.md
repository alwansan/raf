# T5 scope — 20261110T0951Z-T5-scheduled-release-permission-a71c
origin: scheduled
issue_id: DELIVERY-001 / INTEGRATION-001
status: active
baseline: source workflow inspected 2026-11-10 UTC
intended_files: prompt/coordination/work/20261110T0951Z-T5-scheduled-release-permission-a71c.md; prompt/coordination/clients/T5/sessions/20261110T0951Z-T5-scheduled-release-permission-a71c.md
experiment_key: release-403-token-permissions-static-audit-42058825739-current-workflow
resource_key: none (read-only audit; no Unity/CI)
hypothesis: 2026-11-05 HTTP403 release creation is an effective token permission denial, not an APK/OBB integrity failure; determine whether current workflow already mitigates it before modifying shared release workflow.
conflicts: T4 owns mouse input; no edits to T4 or Unity workflow; no CI dispatch.
evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; .github/workflows/raft-unity-editor-android-import.yml; apk-for-testing/SHARED_BUILD_READINESS.md.
next: inspect repo Actions policy/token and delivery manifest of exact signed artifact before any permission patch; preserve 5/5 gate.
