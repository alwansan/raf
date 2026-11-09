# T5 — Owner-direct latest full Raft native build
session_id: 20261109T2045Z-T5-chat-native-owner-rerun-5f28
origin: chat
base_sha: 20efd8020d68bca166a2a23a24e8d4f03163bc6d
resumed_from_sessions: 20261109T2002Z-T5-chat-owner-local-logs-6d27; 20261109T1946Z-T5-chat-shared-mini512-73bc; 20261109T1922Z-T5-chat-cl-obb-evidence-f4c2
issue_id: NATIVE-BUILD / full Raft Android experimental
status: waiting_ci
updated_at: 2026-11-09T20:45:00Z
scope: Owner explicitly requested a new full APK+OBB+XAPK from latest merged feature branch including T1–T4 fixes, repair proven blocker(s), and launch one nonduplicate full native workflow; preserve owner/agent votes and water/authenticity safeguards; fix source-gate failures before heavy Unity.
intended_files: .github/raft-native-build-request.json (one T5-owned native request), isolated work/T5/20261109T2045Z-T5-chat-native-owner-rerun-5f28.md, clients/T5/sessions/20261109T2045Z-T5-chat-native-owner-rerun-5f28.md, optional isolated preflight workflow, report to T1 without writing T1 source; preserve GitHub-owned existing workflow unless proven defect.
experiment_key: native-full-owner-direct-new-head-after-a1737bd7:source-gates-original-fft-hook+mouse-abicheck:unity2021.3.45f2:arm64-il2cpp:zip2-pinned:water-limits-exact
resource_key: raft-native-engine-feature/android-native-port; full native workflow mutex, cancel-in-progress=false
observed:
- Last built signed artifact #42296450023 @ a1737bd736e276d53df808442cfae3b1eea0d488: reconstruct=SUCCESS; signed output artifact 13550196498 and delivery artifact 13549514149; publish-early-test FAILED HTTP403 Resource not accessible by integration, delivery-result FAILED. Artifact expiry 2026-11-09 ~23:48–23:49Z. Android owner-tested game #42058825739 remains older, graphics still problematic. #42281310905 was earlier CS0234 AndroidPhysicalMouseCapture source failure, fixed by T4 f554e8b6 and early native ABI gates.
- Full trial vote trial-20261106-r1 remains 1/5 and stale, 3/3 full readiness NOT_READY. Owner explicit direct instruction in chat is distinct from 5/5 and is accepted ONLY for this one experiment; no votes rewritten/no READY claim.
- HEAD advanced 2393 commits from a1737bd7, including T1 original FFT metadata hook, T4 mouse callback/reader and source tests, T2 Foam audits, T3 smoke DXBC source diagnostics, T5 package/OBB checks. Many are source-only and do not yield original water/shader recovery. Compare endpoint lists 300-file sample only.
- T1 source guard #42695525795 FAILED (two source test assertions); T1 corrective guard #42695722354 in_progress at 20:44Z. Existing native workflow executes test_t1_stage_original_fft_dispatch_trace before heavy downloads; must wait for a passing source gate before native launch.
- Release workflow publish step already requests contents:write and optional RAFT_RELEASE_TOKEN, but latest authenticated token returned HTTP403. Cannot fake publish SUCCESS; retain downloadable GitHub Actions artifact even if permission blocks Release.
- At 20:42Z no full native delivery or experiment active/queued; unrelated source-only T1/T4 jobs are active and preserved.
next_step: Verify T1 corrective CI, run source/preflight checks on stable candidate SHA, CAS-publish one request with [raft-native-build] [raft-device-test], owner_direct_request true, explicit full-game water limitations; monitor until bounded checkpoint and save exact run+step status. No Force, do not change main/zip/zip2/CL.

## Verified native request checkpoint — 2026-11-09 20:48 UTC
- Source-only T1 corrected hook CI42695722354 SUCCESS; offline adapter CI42695722198 SUCCESS; T4 mouse CI42695755986 SUCCESS. T1 CI42695525795 had two source assertions; fixed in later run.
- User explicitly requested new FULL Raft game build, not shared Mini; old 5/5 vote round unchanged and stale. This is a distinct owner-direct exception only.
- CAS-pinned full build request commit 6316f457dd7587db47469ebd29ec0cbc849584dd changed ONLY .github/raft-native-build-request.json, parent candidate SHA f66277c0572065e6fde495a52468542851124281, owner_direct_request=true; exact five documented unmet water conditions, markers [raft-native-build] [raft-device-test].
- Full native run https://github.com/alwansan/raf/actions/runs/42696228231 launched; request-gate SUCCESS job129428677749, Unity-license-preflight SUCCESS job129428868161, reconstruct IN_PROGRESS job129428944191 at original graphics payload restoration. NO new APK/OBB/XAPK or device PASS yet.
- Previous completed full #42296450023 reconstruct SUCCESS and publish Release HTTP403 (Resource not accessible by integration); release-result FAILED, artifacts signed13550196498 and delivery13549514149 (5.95 GB), expire 2026-11-09 23:48–23:49 UTC. Old source a1737bd7 not current.
- Publish job already has contents:write and GH_TOKEN optional RAFT_RELEASE_TOKEN || github.token. If 403 persists this is effective GitHub app/token authorization, cannot be fixed by falsely treating artifacts as a successful Release.
- No active full native workflow or native experiment detected immediately before request, no other work cancelled, no branch other than feature/android-native-port written.
- Work state: waiting_ci; next: inspect first failed CI step after actual run concludes; if reconstruct SUCCESS audit signed APK/OBB/XAPK hashes, package/version/signature and artifact ZIP, distinguish Release permission failure and preserve exact download details. No duplicate heavy native run. Full game NOT_READY 0/3.
