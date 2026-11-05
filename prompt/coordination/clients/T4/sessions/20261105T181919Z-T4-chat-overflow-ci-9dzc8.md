# T4 chat — source-free overflow regression added to CI and verified

- session_id: 20261105T181919Z-T4-chat-overflow-ci-9dzc8
- origin: chat
- status: completed (CI wiring scope only)
- resumed_from_sessions: 20261105T1737Z-T4-scheduled-h6v2; 20261105T1736Z-T4-chat-rgd-return-local-stores-r6n8
- base_sha: b855f3b921411deb66d138bf795ff29bb77bda0f
- work_id: prompt/coordination/work/LOCAL-005/T4-20261105T181919Z-T4-chat-overflow-ci-9dzc8-overflow-ci-wiring.json
- experiment_key: T4-jsonl-queue-overflow-global-failclosed-05631bd-15plus2-sourcefree-CI-wiring-v1
- resource_key: none
- CI: https://github.com/alwansan/raf/actions/runs/42083434118

## Coordination and prior evidence
T4 scheduled 1737Z implemented strict queue-overflow fail-closed guards at commits 6b2ffec and 05631bd and left execution pending. T4 previous chat 1736Z authenticated the original derived RGD local direct constructor with source-only [CI42076494669](https://github.com/alwansan/raf/actions/runs/42076494669), 67/67 synthetic controls. T5 native Android [run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) was still in_progress with package delivery step pending at last 18:20 UTC inspection; not cancelled or restarted. Current session reserved work before workflow change in commit d00af305e157a4d49f2815afac75cb201ebdc2db, no shared parser/test modifications.

## Actual improvement + checked execution
Original workflow sparse checkout included only scripts/t4_verify_device_world_save_log.py and tests/test_t4_verify_device_world_save_log.py; it never fetched or ran the already published scripts/test_t4_overflow_gate.py. Updated solely .github/workflows/raft-t4-world-save-log-evidence.yml at commit [e8c0d05261529ce5f4a8240a610601db85b52563](https://github.com/alwansan/raf/commit/e8c0d05261529ce5f4a8240a610601db85b52563): path trigger, sparse checkout, Python compile, targeted two overflow unit tests, and truthful 17 controls label (15 existing + 2 new). No workflow concurrency changes and no native build dispatch.
[GitHub Actions 42083434118](https://github.com/alwansan/raf/actions/runs/42083434118) completed **SUCCESS** for source commit e8c0d05261529ce5f4a8240a610601db85b52563. The decoded job log for job 127442170698 shows Python py_compile pass, 15/15 original parser tests OK, plus 2/2 new overflow controls OK:
- Without overflow, cross-session Save/Load nonzero can yield **hints only**.
- With recorded global queue overflow, both positive cross-session hints are suppressed; no device confirmation.
No source-free test published private phone/user log, game asset or RGD.

## Limits
The successful tests are source-free synthetic evidence-checker regression validation, not the Android gameplay/world issue fix, not original SaveWorld execution or actual RGD persistence, not Unity/IL2CPP/device acceptance. They do not establish that all dropped logger events are detectable. Original .meta/GUID/save format, B50 Steam guards, local host, audio, Settings untouched; touch deferred. LOCAL-005 remains OPEN and overall NOT_READY 0/3.

## Next
Scheduled T4 should consume matching source SHA CI42083434118 instead of re-running the same checks. T5 native run42058825739 is independent. When signed fresh APK/OBB/XAPK exists, obtain authentic owner phone evidence for offline playable world, SaveWorld/SaveUser and nonzero real .rgd, full exit then same-world reopen and callback/caught-exception sequence; do not assert from source-only CI.

## Addendum: T5 native publish failure, scoped read-only diagnostic

Registered separate INTEGRATION-001 read-only work `prompt/coordination/work/INTEGRATION-001/T4-20261105T181919Z-T4-chat-overflow-ci-9dzc8-native-publish403-readonly.json` before diagnostic handoff; no T5 native script or workflow edits.

At 2026-11-05T18:22Z [T5 native run42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) changed to **completed failure**. Jobs native-request-gate and unity-license-preflight SUCCESS; **reconstruct SUCCESS**; publish-early-test FAILURE, delivery-result FAILURE. Published-delivery job 127441439836 successfully downloaded artifact `raft-android-test-delivery`, verified its compressed download digest against expected `29d967c5f1868a10aa0f8f3b9f0306e828c1d32ef3cda2909f7482b5d111eef6`, then `gh release create` returned **HTTP 403 Resource not accessible by integration** at 18:21:48Z. This is an authorization failure at Release creation, NOT a proved Unity/source/packaging failure, and DOES NOT independently validate signatures or Android use.

Saved GitHub Actions artifact metadata from run42058825739: delivery ID `13441227298` size `5948243524` compressed bytes, expires `2026-11-06T18:19:05Z`; signed-output checkpoint ID `13441766832` size `2974110506`, expires `2026-11-07T18:18:17Z`. Retention deadlines are GitHub API metadata, not new Releases. T5 handoff `prompt/coordination/discussions/INTEGRATION-001/20261105T1825Z-T4-publish-403-artifact-handoff-to-T5.md`; avoid duplicating heavy native run. T5 should inspect workflow permissions/appropriate owner-authorized publication identity and reuse authenticated artifacts/checkpoint with staged size/SHA verification before expiration. Never disclose tokens, weaken auth, assert published Release, nor substitute source-only success for device result. Original LOCAL-005 remains OPEN NOT_READY 0/3.
