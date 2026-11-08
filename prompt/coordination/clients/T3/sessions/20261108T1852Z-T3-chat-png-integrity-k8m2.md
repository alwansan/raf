# T3 chat checkpoint — verified synthetic screenshot transport / same-case GPU evidence

- **session_id:** `20261108T1852Z-T3-chat-png-integrity-k8m2`
- **origin:** `chat`; **worker:** T3; **issue_id:** `RENDER-002` (T3 shared GLES material/alpha/sRGB evidence).
- **resumed_from:** T3 `20261108T1813Z-T3-chat-shared-frame-proof-p6r9` and live `state.json`, `MEMORY.md`, T5 shared mini handoff and source.
- **base_sha:** `d03d8053088dd5b715705d31675cbad4bae41ae9` before work reservation.
- **scope:** `T3SharedVisualActivity` screenshot integrity only; no shared host/manifest/testpack/workflow request edit, no T1/T2/T4/T5 source or original Raft assets touched.
- **experiment_key:** `T3-shared-png-pending-digest-readback-v1`; **resource_key:** `T3SharedVisualActivity`.
- **intended_files:** compiled T3 visual activity; T3 source regression, independent lightweight T3 source-only compile CI, this session, own memory/state, report and own work/event.

## Actual work
- Fixed previous source defect: MediaStore item became visible before its PNG bytes were durably validated, and failures could leave partial/empty files. Now T3 encodes PNG first; verifies PNG envelope, byte length/SHA256; publishes via `IS_PENDING=1 → full readback/hash → IS_PENDING=0 → second full readback/hash`, with cleanup deletion on failure and `NEEDS_SCREENSHOT` rather than false `EVIDENCE_READY`.
- Added bounded retry for read returning 0 (three tolerated, fourth fatal) to avoid blocking automatic suite indefinitely.
- Propagates real GLES `lastRenderedNote` pixel vectors, GL error, viewport + PNG bytes and sha to the **shared host's** observed result. Image itself still must be reviewed; no automatic visual PASS.
- Expanded `tests/test_t3_shared_visual_frame.py` to 7 test methods and created `.github/workflows/raft-t3-shared-png-source-gate.yml` for source-only Python and Gradle Java compilation, **not** assembleDebug, Unity/XAPK or APK request.
- Fetched updated source/test from live branch; **14/14 JS source contract/order checks** PASS. New workflow creation and source pushes occurred; specific Actions run ID/conclusion **NOT VERIFIED**, so do not claim CI PASS or Android success.

## Evidence commits
- [03151ea4](https://github.com/alwansan/raf/commit/03151ea4b60f87576f8e5abf9235edbc53e12fdd), [a9ad5f77](https://github.com/alwansan/raf/commit/a9ad5f77df2548a1adee109e1cacb51ad4a190aa) — pending verified PNG/readback.
- [0a449ab7](https://github.com/alwansan/raf/commit/0a449ab7ce3b3551c42fb6d9a11b1da0c32da519) — actual GL pixel evidence returned to shared parent.
- [a7c9c060](https://github.com/alwansan/raf/commit/a7c9c06059aacf3454d3e8370b5855b74ac0d8a0), [cd5d1057](https://github.com/alwansan/raf/commit/cd5d10576acbb74bc631d34ec336a1c6711ab27e), [e65427ed](https://github.com/alwansan/raf/commit/e65427eda01c9e7970c20551c627c65228aad50f) — source-only regressions.
- [503398ac](https://github.com/alwansan/raf/commit/503398ac767001df4dfec11d2d99bf882d3cb55d) — source-only no-APK CI workflow.
- [Technical evidence report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/T3_SHARED_PNG_EVIDENCE_INTEGRITY_2026-11-08.md).

## Separation of versions and acceptance
T5 [CI42509945996](https://github.com/alwansan/raf/actions/runs/42509945996) previously **SUCCESS** at `cbe7a038` and artifact ZIP `13628828717`. It includes earlier T3 exact-frame GPU guard, **not** this later PNG transport and real-pixel report. Actual Android T3 PNG save/MediaStore/GL pixels and the original game's colors/fire/water **remain untested**. Do not request a duplicate Mini solely because this source was improved; own Mini vote stays **NO_BUILD** pending first phone results and T5's build review. XAPK 5/5 and NOT_READY 0/3 unchanged.

## Next step
Run/inspect source-only workflow against post-patch SHA (no success claim until real run observed); after T5's next warranted shared Mini use owner Adreno T3-01..06 results and actual exported PNG + URI/SHA/real GLES samples. Continue separate genuine original Particle ShaderLab/Material parity investigations; synthetic test success does not close `RENDER-002` or `WATER-001`.
