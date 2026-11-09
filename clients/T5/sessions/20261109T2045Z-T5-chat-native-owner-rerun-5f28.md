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
status: waiting_ci
next_step: verify source gate, reserve immutable source SHA, issue one native request on exact parent SHA without overwriting others; document full Actions run and artifact/Release limits.

## Verified native request checkpoint — 2026-11-09 20:48 UTC
- Source-only T1 corrected hook CI42695722354 SUCCESS; offline adapter CI42695722198 SUCCESS; T4 mouse CI42695755986 SUCCESS. T1 CI42695525795 had two source assertions; fixed in later run.
- User explicitly requested new FULL Raft game build, not shared Mini; old 5/5 vote round unchanged and stale. This is a distinct owner-direct exception only.
- CAS-pinned full build request commit 6316f457dd7587db47469ebd29ec0cbc849584dd changed ONLY .github/raft-native-build-request.json, parent candidate SHA f66277c0572065e6fde495a52468542851124281, owner_direct_request=true; exact five documented unmet water conditions, markers [raft-native-build] [raft-device-test].
- Full native run https://github.com/alwansan/raf/actions/runs/42696228231 launched; request-gate SUCCESS job129428677749, Unity-license-preflight SUCCESS job129428868161, reconstruct IN_PROGRESS job129428944191 at original graphics payload restoration. NO new APK/OBB/XAPK or device PASS yet.
- Previous completed full #42296450023 reconstruct SUCCESS and publish Release HTTP403 (Resource not accessible by integration); release-result FAILED, artifacts signed13550196498 and delivery13549514149 (5.95 GB), expire 2026-11-09 23:48–23:49 UTC. Old source a1737bd7 not current.
- Publish job already has contents:write and GH_TOKEN optional RAFT_RELEASE_TOKEN || github.token. If 403 persists this is effective GitHub app/token authorization, cannot be fixed by falsely treating artifacts as a successful Release.
- No active full native workflow or native experiment detected immediately before request, no other work cancelled, no branch other than feature/android-native-port written.
- Work state: waiting_ci; next: inspect first failed CI step after actual run concludes; if reconstruct SUCCESS audit signed APK/OBB/XAPK hashes, package/version/signature and artifact ZIP, distinguish Release permission failure and preserve exact download details. No duplicate heavy native run. Full game NOT_READY 0/3.
