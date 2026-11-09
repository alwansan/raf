# T2 — source-free pinned CL/test 4-case evidence verification
session_id: 20261109T0141Z-T2-chat-cl-fourcase-ci-r6p2
origin: chat
started_utc: 2026-11-09T01:41:00Z
base_sha: 6fe95344909bd919dc8bc08cc245bda640e1155e
branch: feature/android-native-port
issue_id: WATER-001 (OPEN)
resumed_from_sessions:
  - clients/T2/sessions/20261108T2320Z-T2-scheduled-pixel-consistency-k4v9.md
  - clients/T2/sessions/20261108T2120Z-T2-scheduled-gles-evidence-q6m2.md
  - clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md
experiment_key: T2-CL-f401b7ffe3b6-SHARED-230157-CASE01-04-REAL-JSONL-GATE-v1
resource_key: T2 evidence read-only; no Unity/driver/APK shared resource
status: active
intended_files:
  - .github/workflows/raft-t2-gles-cl-evidence-gate.yml (new T2-only workflow)
  - work/experiments/20261109T0141Z-T2-chat-cl-fourcase-ci-r6p2.md
  - clients/T2/sessions/20261109T0141Z-T2-chat-cl-fourcase-ci-r6p2.md
source_read_only: alwansan/CL @ f401b7ffe3b6ead9038f3b35273599dcf8286e68; test/shared-20261108-230157-466487336
hypothesis: The late scheduled CASE02 numeric parser and all four per-case T2 JSONL gate checks succeed against the actual owner CL/test logs, with each file byte-authenticated against immutable Git blob identities and a source-free Python unittest.
observed_current_baseline: Owner T2-01..04 synthetic GLES device PASS documented on previous shipped r2 driver; new gate source was published but its full unittests and actual CL files were not executed. Latest repo Actions lists at 2026-11-09T01:41Z: queued=0 in_progress=0 waiting=0.
non_overlap: No T5 unified APK, no T1 FFT, no T3 renderer/material, no T4 mouse, no owner CL write, no shared build request, no original game shader, no modifying others' workflow.
acceptance: Git blob SHA verify all four source JSONL, unittest PASS, gate returns case-specific synthetic_gles_log_consistent=true and original_raft_water_verified=false, zero raw device data in artifacts; CI source SHA and run URL recorded. Failure remains failure (do not claim device/new APK PASS).
next_step: Write independent 8-minute workflow and run push-scoped CI; triage result, then original pass1 CFG texture instance identity and CB0 remain separate unsolved.
