# T5 chat — shared Mini GPU T1-05
session_id: 20261109T1946Z-T5-chat-shared-mini512-73bc
origin: chat
resumed_from_sessions: 20261109T1922Z-T5-chat-cl-obb-evidence-f4c2; 20261109T1855Z-T5-chat-obb-contract-b1d7; T1 20261109T1915Z-T1-chat-mini-butterfly-a9f3 request
base_sha: 81a3cef1309d188f122b5fd83f3c06905a0a990e
work: work/T5/20261109T1946Z-T5-chat-shared-mini512-73bc.md
scope: One new compiled SHARED mini GLES T1-05, version identity, provenance and one artifact link; source and pack read-only, no XAPK.
intended_files: .github/raft-mini-lab-build-request.json, this session, T5 own work, and delivery proof updates once confirmed.
experiment_key: t1-05-shared-gles31-local512-two-pass:compiled-source-2f627cb:pack-rev2-sha256-9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6:android35:one-apk
resource_key: unified-mini-lab-gradle-build
status: completed
starting_evidence:
- T1 request prompt/coordination/T_TEAM/T1_TO_T5_20261109T1931Z_SHARED_MINI_LOCAL512_AR.md.
- T1 row NEED_BUILD shared-20261108-r4, compiled source CI42682971944 SUCCESS, CI42683061084 SUCCESS.
- T5 Arabic portrait T1-05 30/30 source gate CI42683658745 SUCCESS.
- Current shared pack exact SHA256 9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6, 7454 UTF-8 bytes, revision2 30 cases.
- Prior R3 APK CI42519487402 versionCode13 (29 cases) debug certificate not stable; old certificate SHA256 1b47e47c4e4a170a8b6a7f31c9718c8bd9be4a20a77b72a08edf65b3e754e3e6.
- GitHub Actions queued/in_progress/pending for feature branch were zero at 19:45 UTC; HEAD shifted during investigation due T3 independent work, no shared mini run pending.
next_step: Verify active runs and latest HEAD, commit one exact-parent CAS pinned request with [raft-mini-lab] marker, collect new run/artifact, inspect actual APK not just source SUCCESS.

## Execution completed — 2026-11-09 19:52 UTC
- One T1-05 compiled driver build request committed [3185e449](https://github.com/alwansan/raf/commit/3185e449dcefd27ab77b527f9d3b85d71104f497). Source parent pinned at 2d7c268248b505e4dd9ad1daa9491787df07665c; original T1 driver commit 2f627cb; pack exact SHA256 9dd272a183548443813b5046f8a1f44115626ad8eca316df30692f35b12ec9f6.
- [CI42686652150](https://github.com/alwansan/raf/actions/runs/42686652150) completed SUCCESS on request commit; 30-case shared Gradle APK, run #14, Android35. Artifact ZIP ID13705307079, expires 2026-11-23T19:48:24Z, 98869 bytes SHA256 067c150204468dea9daf49f7a06b908a0c2833f272435dae6a12cc182a637626. Contains exactly Raft-Team-Lab-debug.apk, team-testpack.json and SHA256SUMS.txt.
- APK verified from downloaded real artifact, not guessed from source: 99622 bytes SHA256 e145a50b8b2be0a9f3a37493fe5f0f243b65644b844706cf82192c91d4ea6c52; binary manifest `com.alwansan.raft.lab.shared` versionCode 14/versionName 0.2.14-shared, targetSdk35 minSdk26, Portrait; v2 DER signer SHA256 a60c8608f3c79a40a074e191f1696700dd6bbe160cb9343b971091b114709927. Different from v13 debug cert SHA256 1b47e47c4e4a170a8b6a7f31c9718c8bd9be4a20a77b72a08edf65b3e754e3e6; old Mini export then uninstall required before installing new. T1FftButterflyProbe and local_size_x=512 present in DEX, 30-case pack asset byte-identical.
- Direct standalone APK supplied to owner as ChatGPT sandbox attachment `Raft-Team-Lab-T1-05-v0.2.14.apk`; optional 30-case testpack `Raft-Team-Lab-testpack-30cases.json`; neither sandbox pathname is a permanent GitHub Release URL. GitHub run contains ZIP artifact, not a direct APK.
- Updated T5 row and overall delivered decision in apk-for-testing/SHARED_BUILD_READINESS.md commit 00f90cde, TEST_CENTER.md delivery commit 52cde28d; T1 handoff [T5_TO_T1_20261109T1950Z_SHARED_MINI_T1_05_APK_DELIVERED_AR.md](../../../prompt/coordination/T_TEAM/T5_TO_T1_20261109T1950Z_SHARED_MINI_T1_05_APK_DELIVERED_AR.md), independent event B_TEAM/events/T5/20261109T1946Z-T5-chat-shared-mini512-73bc.md.
- No Raft full XAPK built, no original Raft shader/Unity GPU proof. One source-level CI success plus build success cannot imply phone GPU PASS. No T2/T3/T4 source modified, no scheduled T5 OBB work touched, and no other workers' readiness rows changed.
- Device owner next: Open Arabic Portrait Shared Mini and press «تشغيل T1 تلقائيًا», then export events*.jsonl and summary*.json to CL/test. T1-05 numerical expected checked_floats=1024, first_mismatch=-1, gl_error=0x0, max_abs_error<=0.00003. FAIL/BLOCKED not rewritten as PASS, no screenshot needed. Remains WAITING_PHONE_DATA / WATER-001 OPEN.
run_urls: https://github.com/alwansan/raf/actions/runs/42686652150; https://github.com/alwansan/raf/actions/runs/42683658745; https://github.com/alwansan/raf/actions/runs/42682971944
updated_at: 2026-11-09T19:52:00Z
status: completed
next_step: T1 inspect real CL/test Android15/Adreno730 T1-05 outcomes and compare logs, T5 available for any OBB/package evidence reconciliation; do not trigger duplicate Mini/XAPK build.
