# T5 chat — published Raft release public-metadata consistency

- session_id: `20261105T1713Z-T5-chat-release-metadata-83ac`
- origin: `chat`
- status: `completed`
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


## Verified final result — 2026-11-05 17:19 UTC

- Real Raft APK86 GitHub Release https://github.com/alwansan/raf/releases/tag/android-early-test-41812889049-1 and actual native CI https://github.com/alwansan/raf/actions/runs/41812889049 both pin immutable source d181ee7152580f49ee0b41dfd05fa2bfdacfafe5; native CI completed success. Published release has 12 official assets, 5 auxiliary, 1 whole APK, 3 OBB transfer chunks, 3 XAPK transfer chunks.
- Official release declared APK 672894330 bytes, logical OBB 2301202061 bytes, logical XAPK 2974097643 bytes; all public asset size sums and digest declaration syntax reconcile. Real byte SHA, signed APK, full assembled archive correctness, OBB mount and device behavior are NOT verified by metadata.
- Created scripts/t5_audit_published_raft_release.py, actual public safe fixture tests/fixtures/t5_raft_release_41812889049.json, 28 positive/negative tests tests/test_t5_audit_published_raft_release.py, and path-scoped CPU-only workflow .github/workflows/raft-t5-published-release-audit.yml.
- Official isolated CI https://github.com/alwansan/raf/actions/runs/42072829025 from f22e4e772461bd430ff5497a28c1d78956a7188d, job127405035641 COMPLETED SUCCESS: Ran 28 tests in 0.025s; OK. Controls reject run/target/tag mismatch, bad/duplicate/missing metadata, bad part indices, totals and direct APK digest claim drift. A syntactically valid altered multipart SHA cannot be independently caught without downloaded bytes; verified-content flag remains false.
- Work completed prompt/coordination/work/INTEGRATION-001/T5-20261105T1713Z-T5-chat-release-metadata-83ac-published-release-metadata.json; experiment prompt/coordination/experiments/T5/T5-20261105T1713Z-T5-chat-release-metadata-83ac-published-release-audit.json; event prompt/coordination/B_TEAM/events/T5/20261105T1718Z-release-metadata-audit.json.
- Current separate native CI https://github.com/alwansan/raf/actions/runs/42058825739 remains IN_PROGRESS at actual Unity Editor 2021.3.45f2 Android import/compile step62, source e9c358eda01785b65e4eb14f18723da426635628. Four small water/graphics diagnostics only. No new installable signed APK+OBB+XAPK, Raft Release, Adreno visuals or offline-world save/reopen acceptance. T1–T4 unaffected, no duplicate heavy build dispatched. NOT_READY 0/3.

Next: recheck same immutable native run and first terminal failure or package; if any new release appears, audit its metadata, then separately verify downloaded byte hashes, signature, XAPK/OBB and phone world. Preserve audio, Settings, original GUID/meta and RGD; touch deferred.
