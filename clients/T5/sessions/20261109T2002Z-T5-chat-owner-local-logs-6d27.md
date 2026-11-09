# T5 chat — local owner bundle inspection and guided tests
session_id: 20261109T2002Z-T5-chat-owner-local-logs-6d27
origin: chat
base_sha: be69f74c1f4d902e7c731e4a17cc4bd3c7609ff0
resumed_from: 20261109T1946Z-T5-chat-shared-mini512-73bc; 20261109T1922Z-T5-chat-cl-obb-evidence-f4c2
work: work/T5/20261109T2002Z-T5-chat-owner-local-logs-6d27.md
status: active
scope: Implement guarded Android15 SAF tree selection for owner Download/logs, identify APK / OBB v91 / manifest / pack / BlackBox logs and improve guided T1–T5 UI without modifying their drivers or asserting false Android game PASS.
intended_files: unified T5 Java UI and T5-only scanner/policy; JVM tests, source CI and owner guide; isolated T5 work/session; build request after evidence.
experiment_key: t5-owner-android15-saf-tree-download-logs-apk-obb-91-recon-v1:api35:30cases-no-external-code
resource_key: t5-shared-mini-ui-bridge-source
user-provided-file-shape: Download/logs/Raft-Android-Test/{Android/obb/com.alwansan.raft.androidtest/main.91.com.alwansan.raft.androidtest.obb, com.alwansan.raft.androidtest.apk, manifest.json}, plus team-testpack.json, T3.json, t2-water-render-testpack.json, t4-mouse-testpack.json and top.niunaijun.blackbox_logcat.txt. Not accessible in this remote environment.
baseline: new T1-05 packed 30-case mini APK v0.2.14 CI42686652150 SUCCESS artifact 13705307079; debug cert temporary; user must export evidence before uninstall.
next: create a user-triggered, scoped SAF tree scan, no auto file hashes or auto PASS, evidence-aligned guided controls, compile source CI, request one build after gates.
