# T5 — Owner local Download/logs SAF bridge
session_id: 20261109T2002Z-T5-chat-owner-local-logs-6d27
origin: chat
base_sha: be69f74c1f4d902e7c731e4a17cc4bd3c7609ff0
resumed_from_sessions: 20261109T1946Z-T5-chat-shared-mini512-73bc; 20261109T1922Z-T5-chat-cl-obb-evidence-f4c2
issue_id: T5-02 / SHARED_MINI_LAB_OWNER_INPUT
status: active
updated_at: 2026-11-09T20:02:06Z
scope: T5-only unified Mini Android UI integration for user-supplied local Download/logs/Raft-Android-Test tree. Read-only document tree enumeration, visible APK/OBB/manifest/pack/log roles, explicit user action for 2GiB+ SHA, independent signatures/versions; preserve T1-05, T2/T3/T4 engines.
intended_files: apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java; apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/LocalOwnerBundleScanner.java; apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/LocalOwnerBundlePolicy.java; tests/java/com/alwansan/raftlab/LocalOwnerBundlePolicyTest.java; .github/workflows/raft-t5-local-owner-bundle-source.yml; apk-for-testing/unified/T5_OWNER_TEST_GUIDE_AR.md; own work/session files. Build request only after new source CI and separate current-run check.
experiment_key: t5-owner-android15-saf-tree-download-logs-apk-obb-91-recon-v1:api35:30cases-no-external-code
resource_key: t5-shared-mini-ui-bridge-source (no Unity; single shared Gradle build only when source reviewed)
owner_evidence: /storage/emulated/0/Download/logs contains Raft-Android-Test/Android/obb/com.alwansan.raft.androidtest/main.91.com.alwansan.raft.androidtest.obb, com.alwansan.raft.androidtest.apk, manifest.json; team-testpack.json,T3.json,t2-water-render-testpack.json,t4-mouse-testpack.json,top.niunaijun.blackbox_logcat.txt. Physical local path cannot be accessed remotely; SAF explicit picker required.
existing_evidence: shared mini v0.2.14 CI42686652150 SUCCESS, versionCode14, SHA256 e145a50b8b2be0a9f3a37493fe5f0f243b65644b844706cf82192c91d4ea6c52, debug signer a60c8608f3c79a40a074e191f1696700dd6bbe160cb9343b971091b114709927.
safety: no automatic import or execution of legacy JSON, no automatic loading raw game data/shaders, no deceptive PASS based on file presence, no storage permission broad or Android/obb bypass; no direct CL write. Preserve all session data and other workers code.
next_step: implement sources with bounded scans, source CI, one CAS-pinned mini build, inspect actual APK/pack/signature and deliver user instructions.
