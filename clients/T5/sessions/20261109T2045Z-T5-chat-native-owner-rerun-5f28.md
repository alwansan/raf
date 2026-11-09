# T5 chat — Owner-directed full Raft Android latest rebuild
session_id: 20261109T2045Z-T5-chat-native-owner-rerun-5f28
origin: chat
resumed_from_sessions: 20261109T2002Z-T5-chat-owner-local-logs-6d27; 20261109T1946Z-T5-chat-shared-mini512-73bc; previous full #42296450023
base_sha: 20efd8020d68bca166a2a23a24e8d4f03163bc6d
work: work/T5/20261109T2045Z-T5-chat-native-owner-rerun-5f28.md
scope: Inspect last full build failure and newly integrated team source, repair/preflight proven failures, start one owner-direct current full Unity2021.3.45f2 Android ARM64 APK+OBB+XAPK run, record evidence.
intended_files: .github/raft-native-build-request.json (one separate commit after preflight); work/T5/20261109T2045Z-T5-chat-native-owner-rerun-5f28.md; clients/T5/sessions/20261109T2045Z-T5-chat-native-owner-rerun-5f28.md; new isolated experiment report when necessary.
experiment_key: owner-direct-full-native-zip2-latest-fft-hook-mouse-source-gates-v1
resource_key: raft-native-engine-feature/android-native-port
initial_evidence: #42281310905 Unity CS0234 failure fixed f554e8b6; #42296450023 Unity reconstruct SUCCESS, publish HTTP403 despite contents:write (possible missing optional secret RAFT_RELEASE_TOKEN), no release success; saved artifacts at #42296450023. Unrelated last Mini v0.2.17 built #42691609924 and does not incorporate Raft game runtime fixes.
initial_blocker: T1 source guard #42695525795 has two failures; #42695722354 is running corrective source check. Existing native source-gate will fail if not fixed. Wait for confirmed corrected result before heavy build.
governance: trial-20261106-r1 vote is 1/5 and stale; explicit owner directive 2026-11-09 is per-request owner-direct exception, NOT team consensus or READY. No artificial water/kernel flags or loss of data.
status: active
next_step: verify source gate, reserve immutable source SHA, issue one native request on exact parent SHA without overwriting others; document full Actions run and artifact/Release limits.
