# T5 chat — native run cancellation versus game-build failure integration

- session_id: `20261105T1431Z-T5-chat-native-cancel-d41e`
- origin: `chat`
- status: `active`
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
