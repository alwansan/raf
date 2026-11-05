# T5 chat session — 20261105T2055Z-T5-chat-obb-pair-9f2d
- session_id: `20261105T2055Z-T5-chat-obb-pair-9f2d`
- origin: chat
- status: active
- base_sha: ace661139f33ee801af500a1dbe212f86d98cfac
- resumed_from_sessions: 20261105T1738Z-T5-chat-release-manifest-6e91, 20261105T1953Z-T5-scheduled-release-permission-a72e, 20261105T2045Z-T5-scheduled-ui-right-a71
- work: prompt/coordination/work/INTEGRATION-001/20261105T2055Z-T5-chat-obb-pair-9f2d.json
- scope: source-only APK+OBB completed-file pair and aapt identity integrity verifier, distinct from scheduled AndroidTouchUiPanel.cs.
- experiment_key: t5-android-apk-obb-pair-validate-local-complete-bytes-deliveryjson-aapt-zip-integrity-v1
- resource_key: source-only-CPU-no-game-artifact
- latest owner phone evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, original source e9c358eda01785b65e4eb14f18723da426635628, world/save/reopen owner confirmed; OBB GUID warning remains separate.
- latest native delivery: CI42058825739 reconstruct succeeded, Release POST 403, delivery artifact 13441227298 expires 2026-11-06T18:19:05Z. No release published, no new dispatch.
- latest scheduled T5 UI commit: 96f41443d8545776b17b1d828fa52be60046c2dd, CI42106538730+42106538822 success. Avoid UI overlap.
- initial HEAD: ace661139f33ee801af500a1dbe212f86d98cfac; no in_progress native Actions from latest filtered query.
- planned files: scripts/t5_verify_apk_obb_pair.py, tests/test_t5_verify_apk_obb_pair.py, .github/workflows/raft-t5-apk-obb-pair.yml, docs/T5_APK_OBB_PAIR_VERIFIER_2026-11-05.md.
- next: implement adversarial bounded test + path-scoped CI, document exact covered bytes and limits. No Unity/REA necessity for file-level packaging hypothesis; no private binary disclosure.

## Completed engineering checkpoint
- origin=chat, session_id=20261105T2055Z-T5-chat-obb-pair-9f2d; independent scoped work was recorded before implementation.
- New source scripts/t5_verify_apk_obb_pair.py validates complete APK and OBB SHA256/byte sizes vs local delivery.json, checks filename/versionCode against actual aapt output, plus bounded APK/OBB ZIP core entries; never extracts original bytes.
- Added adversarial tests/test_t5_verify_apk_obb_pair.py (17 cases) and path-only .github/workflows/raft-t5-apk-obb-pair.yml; rationale/limitations docs/T5_APK_OBB_PAIR_VERIFIER_2026-11-05.md.
- Verified immutable CI https://github.com/alwansan/raf/actions/runs/42108354510, job127529069130, source 8bca9e2bff682e3eee0686571b8536ae3a7037a1: COMPLETED SUCCESS, 17/17 tests, 0.023s, py_compile success. This does **NOT** check real downloaded game bytes or installed APK/OBB.
- Commits source 79c2cd2fcdb4e1225d1e7a0eec8155de523a1e3b, tests 600ac5990dcb5748e0d886933bbe7094ef543c94, workflow 8bca9e2bff682e3eee0686571b8536ae3a7037a1, docs 3000c2040cbb2bc5f02d1fdf08c93f0d80fae725.
- Origin/phone boundary: CL 220911-559 reported 1, 230108-327 reported 2 OBB GUID warnings; phone world/save/reopen owner confirmed for artifact 42058825739. OBB internal Unity GUID cause remains unknown; release publish POST403 still blocked despite job contents:write.
- No native build rerun, no other T1-T4 source, T5 scheduled UI, audio or Settings changed; no LFS/proprietary artifacts copied. Game NOT_READY 0/3.
- Experiment: prompt/coordination/experiments/T5/20261105T2055Z-T5-chat-obb-pair-9f2d.json; event: prompt/coordination/B_TEAM/events/T5/20261105T2055Z-T5-chat-obb-pair-9f2d.json.
- next_step: preserve/check retained delivery artifact 13441227298 before 2026-11-06 18:19:05 UTC, authenticate delivery manifest to immutable native source, run verifier on *actual* reassembled APK/OBB with aapt, then extract exact OBB GUID log line to distinguish internal GUID issue. If unavailable, report verified blocker. Work status completed_source_only; this chat cycle concluded.
- status: completed_source_only
