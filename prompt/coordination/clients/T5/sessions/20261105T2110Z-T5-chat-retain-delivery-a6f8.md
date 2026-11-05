# T5 chat — 20261105T2110Z-T5-chat-retain-delivery-a6f8
- session_id: 20261105T2110Z-T5-chat-retain-delivery-a6f8
- origin: chat
- status: active
- resumed_from_sessions: 20261105T2055Z-T5-chat-obb-pair-9f2d; 20261105T1953Z-T5-scheduled-release-permission-a72e
- base_sha: 2f065e1524f2723d62e9d4bf142d55767f55258f
- intent: recover expiring fully packaged native release-delivery artifact WITHOUT rerunning Unity or testing T1–T4 shaders/mouse.
- work: prompt/coordination/work/INTEGRATION-001/20261105T2110Z-T5-chat-retain-delivery-a6f8.json
- experiment_key: t5-42058825739-native-delivery-archive-single-source-stream-sha256-fullpart-v1
- resource_key: actions-artifact-13441227298-6GB-retention-exclusive
- owner: T5
- pinned immutable native run: https://github.com/alwansan/raf/actions/runs/42058825739 (source e9c358eda01785b65e4eb14f18723da426635628; native reconstruct SUCCESS, publish POST403).
- expiring artifact: delivery id13441227298, 5,948,243,524 bytes, digest sha256:29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6, expires 2026-11-06 18:19:05Z; signed checkpoint id13441766832 expires 2026-11-07 18:18:17Z.
- Actions check: no in-progress as of initial poll; T1/T2/T3/T4 hold rendering/input work independently.
- planned files: scripts/t5_verify_retained_delivery_archive.py, tests/test_t5_verify_retained_delivery_archive.py, .github/workflows/raft-t5-retain-native-delivery.yml, docs/T5_NATIVE_DELIVERY_RETENTION_2026-11-05.md.
- limitations: source-free tests do not prove actual ZIP or signed binary; destination artifact reupload is possible only after actual runner result. Retain 2 days to avoid long storage charges; do not cancel native CI.
- next: register checker + tests and narrowly scoped one-shot workflow, check actual result and SHA, record full evidence; if 403/quota/disk, document without retries.

## Verified end-of-cycle checkpoint — 2026-11-05 21:14 UTC

- origin=chat, session_id=20261105T2110Z-T5-chat-retain-delivery-a6f8, resumed from T5 20261105T2055Z chat APK/OBB pair and 20261105T1953Z scheduled release-permission forensics.
- Scope reserved before work in prompt/coordination/work/INTEGRATION-001/20261105T2110Z-T5-chat-retain-delivery-a6f8.json; no overlap with scheduled T5 AndroidTouchUiPanel/right-side UI or T1/T2/T3/T4.
- Added scripts/t5_verify_retained_delivery_archive.py, tests/test_t5_verify_retained_delivery_archive.py and one-shot .github/workflows/raft-t5-retain-native-delivery.yml; docs/T5_NATIVE_DELIVERY_RETENTION_2026-11-05.md.
- Immutable [CI42110297871](https://github.com/alwansan/raf/actions/runs/42110297871), job127535758223, source df6144411a130cc1ac23f1df4ae7f653d61e9704: **COMPLETED SUCCESS**. 18/18 source-free negative/positive tests in 0.030s and full real archive retrieval/digest+part streaming+new retention all completed.
- Original native pinned 42058825739/source e9c358eda01785b65e4eb14f18723da426635628, run number/versionCode 89. Actual original archive 13441227298, 5948243524B, SHA256 29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6 **verified by reading actual bytes**.
- Real payloads: all **7 actual transport parts** hashed individually and all **3 whole APK, OBB, XAPK** logical joined streams hashed/size-checked against authenticated downloaded delivery.json/SHA256SUMS. Total logical bytes actually scanned 5948221616. No underlying original game raw bytes dumped or published to new Release.
- New retained Actions artifact: id **13454900880**, name t5-retained-native-delivery-42058825739, outer container size 5948243834B, outer sha256 41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef, expiry **2026-11-08T21:12:40Z** (2026-11-09 00:12:40 Asia/Baghdad). Its **inner single ZIP** is the exact original archive; new outer digest differs by envelope design. This is recoverable Actions artifact, NOT public Github Release.
- The earlier native Release POST403 remains unresolved; existing YAML contents:write was present, actual org/repo installation policy unknown. This experiment used actions:read + contents:read only; no release permission assumed. APK crypto signature independent recheck, Unity OBB GUID, Android mount, water/FFT, graphics and device retest remain open. Owner world/save/reopen on original artifacts remains supported but this CI does not test the device.
- Commits: 4a9cfc3323eaa39a7e8fe07acf4ccc4a00844fe0 verifier; 2db482cfb80f2a26f8de7e715d842a1819191990 tests; df6144411a130cc1ac23f1df4ae7f653d61e9704 one-shot workflow; d58aabb470da40ffd56934743a33e3b2639d256f docs verification update.
- experiment: prompt/coordination/experiments/T5/20261105T2110Z-T5-chat-retain-delivery-a6f8.json; event: prompt/coordination/B_TEAM/events/T5/20261105T2110Z-T5-chat-retain-delivery-a6f8.json; STATUS entry pending/updated per branch.
- Latest release android-early-test-42058825739-1 still 404 at check; do not claim public delivery.
- No Unity/native rebuild, no cancellations or changed native-request JSON, no LFS, no game/.meta/GUID/serializer/audio/Settings/touch changes, no T1–T4 files changed. INTEGRATION-001 stays OPEN, game **NOT_READY 0/3**.
- **next_step:** Authenticated future T5 cycle downloads new artifact id13454900880 before expiry, unpacks outer ZIP and checks inner original ZIP SHA, streams/extracts only needed actual APK/OBB; run scripts/t5_verify_apk_obb_pair.py with aapt to bind actual APK package/version to OBB, then investigate exact OBB GUID warning. Authorized maintainer investigates effective workflow token policy and Release 403; do not duplicate native Unity.
- status: completed
