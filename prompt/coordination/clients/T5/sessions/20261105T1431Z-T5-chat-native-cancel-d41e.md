# T5 chat — native run cancellation versus game-build failure integration

- session_id: `20261105T1431Z-T5-chat-native-cancel-d41e`
- origin: `chat`
- status: `completed`
- base_sha: `9f604d89e5673be50628f215500a47dca0bba992`
- resumed_from_sessions: `20261105T1404Z-T5-chat-native-diagnostic-3c8e`; `20261105T1407Z-T5-chat-profile-reader-window-c8a1`; scheduled `20261105T1348Z-T5-scheduled-7c91`
- issue_id: INTEGRATION-001
- experiment_key: t5-github-native-run-42042902522-cancel-vs-codefailure-vs-release-proof-v1
- resource_key: t5-cpu-only-native-run-result-audit
- work: `prompt/coordination/work/INTEGRATION-001/T5-20261105T1431Z-T5-chat-native-cancel-d41e-native-run-verdict.json`
- intended_files: standalone `scripts/t5_audit_native_run_verdict.py`, independent tests, narrow CPU workflow, new T5 session/experiment/event.

## Verified native attempt evidence
One T5 native diagnostic request `753802d75196210d721cca0f4fdec6ce7800bf0d` produced [run42042902522](https://github.com/alwansan/raf/actions/runs/42042902522), now **completed CANCELLED**; do NOT conflate with build-source failure. GitHub jobs native-request-gate SUCCESS, unity-license-preflight SUCCESS, reconstruct CANCELLED, delivery-result FAILURE (its input NATIVE_RESULT=cancelled; explicit `test "$NATIVE_RESULT" = "success"` fails), publish-early-test SKIPPED; no generated artifacts. Reconstruct logs show original mesh position audit processed up to public step `sharedassets24.assets` then `##[error]The operation was canceled.` There was no Unity import, IL2CPP, APK/OBB/XAPK, signing or release. No mesh integrity exception or test failure observed before cancellation. Who/what initiated cancellation **unknown**. Existing workflow has `cancel-in-progress:false` on global and native-engine concurrency, and reconstruct timeout 240m; this is not evidence of automatic superseding or timeout.

Current branch HEAD advanced past request; a later branch SHA cannot be substituted into the immutable run. T1 source-free Unity Mesa/Vulkan [42045389521](https://github.com/alwansan/raf/actions/runs/42045389521) was active when starting; do NOT launch a second Unity/native job or cancel teammate work. T4 exact original shipped `Data.rgd` generic Load<T> managed CI42043768798 passes but no user-save Android game; T3 source comparison still cannot claim authentic shader programs on phone. Last real game candidate APK86, NOT_READY 0/3.

## Independent verification plan
Implement a privacy-safe metadata-only Python classifier of official GitHub run+jobs+artifacts snapshot with exact source SHA/run id checks, terminal/nonterminal, reconstruct cancellation/failure, downstream fail-gate propagation, no release claim from job results alone. Add negative controls for failed genuine Unity stage, nonterminal run, mismatched SHA, missing artifact record, contradictory result, and "success" without independently verified signed release. Run bounded source-only CI with no Unity/LFS/request changes. Store actual run evidence/category and limits in experiment, event, this session, and work.

## Pending
No production code changes or native retry requested. Next checkpoint requires real CI tests and exact final status/limits.


## Result checkpoint — 2026-11-05 14:39 UTC

**Status: completed (T5 native cancellation forensic classification / isolated tool).** Original native game build remains cancelled and produced no new candidate. This cycle **did not** launch another native/Unity build.

### Immutable failed attempt and source boundary
- Original one-shot native request `753802d75196210d721cca0f4fdec6ce7800bf0d`, [run42042902522](https://github.com/alwansan/raf/actions/runs/42042902522) completed `cancelled`.
- [Exact jobs](https://github.com/alwansan/raf/actions/runs/42042902522): native-request-gate SUCCESS; unity-license-preflight SUCCESS; reconstruct CANCELLED at step `Restore every pinned external Mesh buffer while retaining original serialized identities`; delivery-result FAILURE because its own `NATIVE_RESULT=cancelled` gate rejected non-success; publish-early-test SKIPPED; 0 workflow artifacts. In reconstruct job127298291857 the last visible successful progress was mesh position audit through `sharedassets24.assets`; next event `The operation was canceled`. No actual Mesh exception or Unity compiler error established. No Unity Editor import, APK/OBB/XAPK, release or phone success occurred. Who requested the cancellation **unknown**; source workflow has `cancel-in-progress: false` and 240m reconstruct timeout, so do not invent actor or reason.
- T1's Unity software-Vulkan image discriminators and T3's Renderer/Shader join are active/independent; no T1–T4 job or full native attempt cancelled by this T5 cycle.

### Actual new integrated test
- Source `scripts/t5_audit_native_run_verdict.py` [commit be75a56e](https://github.com/alwansan/raf/commit/be75a56e4822c81ecb5b1fbb8a4dc7ab4d52a1fa).
- Public official GitHub REST run/jobs/artifacts metadata (whitelisted safe fields, NO original game bytes or secrets) preserved in `tests/fixtures/t5_native_run_42042902522.json` [commit602d918d](https://github.com/alwansan/raf/commit/602d918d2364fc09d246f65cfe722eb7f3bd39a4). This fixture is filtered metadata, NOT full raw log and cannot establish cancellation provenance.
- New independent `tests/test_t5_native_run_verdict.py` and bounded 6m `.github/workflows/raft-t5-native-run-verdict.yml` workflow at [commit0186107e](https://github.com/alwansan/raf/commit/0186107e2d79622fc934d2430ad94d51e194043e). CI [**42046665995**](https://github.com/alwansan/raf/actions/runs/42046665995), job127311357157, **SUCCESS 16/16** `Ran 16 tests in 0.027s / OK`.
- The real run snapshot classifies `native_job_cancelled_no_source_failure_established`, `native_stage=original_mesh_restoration`, `downstream_failure_follows_cancelled_native=true`, `artifact_records=0`, `cancellation_initiator=unknown`. Strong negative controls distinguish actual reconstruct failure/timeout, nonterminal states, wrong immutable id/SHA, duplicate job, missing evidence, unexpected stage and contradictory success. A successful `publish-early-test` job or lone artifact record **never** establishes signed-release hashes, full original content or Android install.
- Work `prompt/coordination/work/INTEGRATION-001/T5-20261105T1431Z-T5-chat-native-cancel-d41e-native-run-verdict.json` completed; experiment `prompt/coordination/experiments/T5/T5-20261105T1431Z-T5-chat-native-cancel-d41e-native-verdict.json`; event `prompt/coordination/B_TEAM/events/T5/20261105T1438Z-native-cancel-verdict.json`. T5 `state.json` and `MEMORY.md` remain historical helper pointers and were not overwritten while other T5 sessions may exist.
- **No production original/game/Unity changes; no new signed APK/OBB/XAPK; WATER-001, RENDER-002, LOCAL-005 OPEN and game NOT_READY 0/3.** Owner-working audio/Settings preserved; touch remains deferred.

### Next resumable step
Read HEAD and all nonterminal Actions before any resource allocation. Confirm cancellation provenance before re-requesting a huge native import when possible; do not assert a Mesh source bug from the canceled step. Choose single immutable current source candidate only after coordinating T1 graphics and T3 real material program-quality gaps plus T4 source/game save markers. If native attempt fails with a genuine step exception, fix that exact gate and rerun separately. Do not mix newer HEAD with the canceled immutable source.
