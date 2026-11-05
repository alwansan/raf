# T5 chat session — 20261105T2153Z-T5-chat-signed-pair-4e91
- origin: chat
- session_id: 20261105T2153Z-T5-chat-signed-pair-4e91
- base_sha: 0c17397f349789e94aaf8bfa8ec6cc1f75971529
- resumed_from_sessions: 20261105T2110Z-T5-chat-retain-delivery-a6f8; 20261105T2055Z-T5-chat-obb-pair-9f2d; scheduled 20261105T2045Z-T5-scheduled-ui-right-a71
- status: active
- work: prompt/coordination/work/INTEGRATION-001/20261105T2153Z-T5-chat-signed-pair-4e91.json
- intent: independently inspect **actual signed APK/OBB pair** from retained ZIP and Android Build Tools without Unity rerun.
- immutable original native run: 42058825739, source e9c358eda01785b65e4eb14f18723da426635628, versionCode 89, original source archive 5948243524 B SHA256 29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6.
- retained GitHub Actions artifact ID 13454900880, outer ZIP 5948243834 B SHA256 41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef, expires 2026-11-08T21:12:40Z.
- CI prior run42110297871 passed full exact ZIP / 7 transport and 3 logical SHA checks; no APK aapt, apksigner or OBB ZIP inspection then.
- live work conflict: T5 scheduled/source handling Android Settings Resolution at HEAD; avoid UI/Resolution files; T1/T2 shaders and W1 native Depth Copy CI running; no shared Unity dispatch or native build.
- experiment_key: t5-signed-apk-obb-rehydrate-verified-42058825739-13454900880-aapt-apksigner-v1
- resource_key: read-only-original-artifact-13454900880-GHA-6GB
- intended implementation files: scripts/t5_extract_actual_signed_pair.py, tests/test_t5_extract_actual_signed_pair.py, .github/workflows/raft-t5-real-apk-obb-identity.yml, docs/T5_REAL_SIGNED_APK_OBB_IDENTITY_2026-11-05.md.
- next: implement/validate no-clobber extraction from exact original transport ZIP, pin all sources and signature/tool versions. Avoid proprietary artifacts/uploading complete game; keep only aggregate logs and SHA match flags. Preserve audio/Settings/touch. NOT_READY 0/3.

## Verified engineering checkpoint — 2026-11-05 22:03 UTC

- origin=chat, session_id=20261105T2153Z-T5-chat-signed-pair-4e91; session scope registered before writes in prompt/coordination/work/INTEGRATION-001/20261105T2153Z-T5-chat-signed-pair-4e91.json; no overlap with T5 scheduled Android Resolution edits or T1–T4 code.
- Created `scripts/t5_extract_actual_signed_pair.py` (exclusive, no-clobber, SHA-pinned transport part + complete file checking and safe cleanup), `tests/test_t5_extract_actual_signed_pair.py` (17 synthetic controls), `.github/workflows/raft-t5-real-apk-obb-identity.yml` (one-shot source pinned, no Unity and no release), `docs/T5_REAL_SIGNED_APK_OBB_IDENTITY_2026-11-05.md`.
- Real [CI42117471172](https://github.com/alwansan/raf/actions/runs/42117471172) job127560839415 on **cbe80c452ec8973f6cb5f55f26df6c113cd2ac4d COMPLETED SUCCESS**. Both 17/17 source-free new test controls (0.023s) and 17/17 existing paired-checker tests (0.022s) passed.
- Actually downloaded previously retained artifact13454900880, checked outer **5,948,243,834B SHA41bf01f9991521fac876c591b75adc19b493ad47882687846e5aae1c2af6a3ef**, unwrapped nested original **5,948,243,524B SHA29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6**. Actual signed APK+OBB **2,974,110,182B** streamed, original logical whole SHA and byte lengths matched, no missing part.
- Actual APK `aapt dump badging` package=com.alwansan.raft.androidtest versionCode **89** matches OBB filename `main.89.com.alwansan.raft.androidtest.obb` and `delivery.json`. APK ZIP members **31**; OBB ZIP members **39**; original Unity ZIP cores present. Android Build Tools aapt reported v0.2-15087165; apksigner 0.9 successfully verified the real APK cryptographic signature (exit0 and `Verifies`).
- Genuine APK/OBB corruption, transport part mix-up, invalid APK signing, wrong original versionCode/OBB filename are now **not supported by this exact pinned CI artifact**, but installed phone's OBB physical bytes/path and actual internal Unity GUID are **UNKNOWN**. Exact CL 2026-11-05 obb_guid_load_failed target not yet mapped. Owner's gameplay/save/relaunch remains separate limited positive phone evidence.
- No game payload upload, no renewed game artifact, Unity, native build, Release, LFS, .meta/GUID/Steam changes, audio/Settings/touch or teammate files touched. STATUS/experiment/event documented, shared issue INTEGRATION-001 OPEN and NOT_READY0/3; Release HTTP403 remains unresolved.
- Next engineering step: isolate the exact CL OBB GUID warning and installed file identity, then compare to same-source valid original resource GUID; preserve current T5 Resolution work and T1–T4 specialized areas.
- status: completed
