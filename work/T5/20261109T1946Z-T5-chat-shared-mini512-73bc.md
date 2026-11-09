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
status: completed
evidence: CI42682971944 SUCCESS, CI42683061084 SUCCESS, CI42683658745 SUCCESS; T1 row NEED_BUILD shared-20261108-r4; prior mini r3 CI42519487402 29 cases (old signed debug cert 1b47e47...); no queued/in_progress/pending branch runs at 19:45Z.
next: Check live HEAD and Actions again, commit one request pinned to immediate parent HEAD and actual embedded pack SHA. Wait for CI result; inspect full artifact identity and signer. Supply artifact ZIP URL honestly unless public verified direct APK becomes available.

## Finished result — 2026-11-09 19:51 UTC
- One requested Mini commit: [3185e449](https://github.com/alwansan/raf/commit/3185e449dcefd27ab77b527f9d3b85d71104f497), exact parent 2d7c268248b505e4dd9ad1daa9491787df07665c, source unchanged. `pack_sha256=9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6` (7454 bytes, 30 cases).
- [GitHub Actions 42686652150](https://github.com/alwansan/raf/actions/runs/42686652150) completed SUCCESS; run number 14; artifact ZIP ID13705307079 expires 2026-11-23T19:48:24Z. ZIP size 98869 bytes; SHA256 067c150204468dea9daf49f7a06b908a0c2833f272435dae6a12cc182a637626. Contains 1 APK, 1 pack, 1 SHA256SUMS.
- Actual APK extracted and checked: 99622 bytes, SHA256 e145a50b8b2be0a9f3a37493fe5f0f243b65644b844706cf82192c91d4ea6c52; `com.alwansan.raft.lab.shared`, versionCode14, versionName0.2.14-shared. Binary manifest parsed, v2 signed Android Debug DER SHA256 a60c8608f3c79a40a074e191f1696700dd6bbe160cb9343b971091b114709927; differs previous v13 cert 1b47e47c4e4a170a8b6a7f31c9718c8bd9be4a20a77b72a08edf65b3e754e3e6. Verified DEX class T1FftButterflyProbe, local512 literal, byte-identical embedded pack.
- Updated T5 only readiness row and decision in apk-for-testing/SHARED_BUILD_READINESS.md and current user delivery in TEST_CENTER.md. Sent verified handoff to T1 and event under B_TEAM/events/T5. Owner received standalone extracted APK via this chat (not a public GitHub Release APK).
- No app installed on actual phone by T5; GPU device result pending. Legacy T1-01..04 prior results and actual Raft original shader unproven for this new APK. Full game XAPK 5/5 and 0/3 unchanged. No overlap with scheduled T5 OBB files.
updated_at: 2026-11-09T19:51:00Z
status: completed
next_step: Wait for owner upload of `events*.jsonl` and `summary*.json` to CL/test, then T1 runs numeric evaluation; T5 maintains delivery consistency. Do not rebuild same driver without new code or evidence.