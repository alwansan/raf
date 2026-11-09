# T5 work — shared Mini T1-05 GPU 512 thread build
session_id: 20261109T1946Z-T5-chat-shared-mini512-73bc
origin: chat
issue_id: WATER-001 (synthetic mini GPU evidence only)
base_sha: 81a3cef1309d188f122b5fd83f3c06905a0a990e
resumed_from_sessions: 20261109T1922Z-T5-chat-cl-obb-evidence-f4c2; 20261109T1855Z-T5-chat-obb-contract-b1d7; T1 request 20261109T1915Z-T1-chat-mini-butterfly-a9f3
scope: T5-owned one SHARED mini APK build request + source/pack identity and artifact proof for T1-05. Excludes full Raft XAPK, CL edits, Unity, original shaders, and any other worker source.
intended_files: .github/raft-mini-lab-build-request.json; work/T5/20261109T1946Z-T5-chat-shared-mini512-73bc.md; clients/T5/sessions/20261109T1946Z-T5-chat-shared-mini512-73bc.md; optionally T5's row only in apk-for-testing/SHARED_BUILD_READINESS.md and current delivery note in apk-for-testing/TEST_CENTER.md after verified build.
experiment_key: t1-05-shared-gles31-local512-two-pass:compiled-source-2f627cb:pack-rev2-sha256-9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6:android35:one-apk
resource_key: unified-mini-lab-gradle-build
updated_at: 2026-11-09T19:46:00Z
status: active
evidence: CI42682971944 SUCCESS, CI42683061084 SUCCESS, CI42683658745 SUCCESS; T1 row NEED_BUILD shared-20261108-r4; prior mini r3 CI42519487402 29 cases (old signed debug cert 1b47e47...); no queued/in_progress/pending branch runs at 19:45Z.
next: Check live HEAD and Actions again, commit one request pinned to immediate parent HEAD and actual embedded pack SHA. Wait for CI result; inspect full artifact identity and signer. Supply artifact ZIP URL honestly unless public verified direct APK becomes available.
