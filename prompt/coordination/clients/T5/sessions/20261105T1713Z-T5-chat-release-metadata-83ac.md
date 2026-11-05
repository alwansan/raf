# T5 chat — published Raft release public-metadata consistency

- session_id: `20261105T1713Z-T5-chat-release-metadata-83ac`
- origin: `chat`
- status: `active`
- base_sha: `528e21018c912f187ed6e0310804b72db9a66288`
- resumed_from_sessions: chat `20261105T1647Z-T5-chat-native-milestone-7b4e`, scheduled `20261105T1646Z-T5-scheduled-c71e`
- work: `prompt/coordination/work/INTEGRATION-001/T5-20261105T1713Z-T5-chat-release-metadata-83ac-published-release-metadata.json`
- issue_id: INTEGRATION-001
- experiment_key: `t5-apk86-published-release-41812889049-1-actual-release-target-run-sha-split-asset-byte-digest-identity-v1`
- resource: public GitHub release/run metadata and lightweight CPU source-only CI, **no Unity native job dispatch**.

## Boundary
Latest observed native [CI42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) on immutable e9c358eda01785b65e4eb14f18723da426635628 is still `in_progress` at `Unity Editor 2021.3.45f2 Android import and compile` step62. Water has passed only via explicit experimental limitation and is not authentic FFT/GPU-ready. No new game Release or installable APK/OBB/XAPK proven from this run. T1–T4 sources and workflows are not touched.

For next signed delivery acceptance, audit known real previous [Raft Android early-test APK86 Release](https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1) via authoritative public GitHub Release and [native CI41812889049](https://github.com/alwansan/raf/actions/runs/41812889049) metadata: both pin source `d181ee7152580f49ee0b41dfd05fa2bfdacfafe5`, workflow terminal success. Release contains APK loose 672894330 bytes, OBB original logical 2301202061 bytes and multipart XAPK logical 2974097643 bytes. Source-only public asset metadata size/digest and body full logical hash claims can be checked; **no downloaded APK bytes or actual signature** can be validated by this metadata-only test.

## Planned
Create a fail-closed independent source-only verifier for matching release tag native run id, run/source SHA, declared logical whole files sizes and published multipart sizes/digests. Tests should prove missing/extra/stale part or SHA, source identity or reverse order fail; digest and byte/signature/device verified flags remain false. Do not duplicate package content reassembly tests; use official published metadata only. Isolated GitHub CI then capture work/experiment/event and explicit limitations.

## Next
Build fixture and validator, execute tests, inspect actual GitHub CI, checkpoint independently. Continue to monitor immutable native Unity step only; no other full native build.
