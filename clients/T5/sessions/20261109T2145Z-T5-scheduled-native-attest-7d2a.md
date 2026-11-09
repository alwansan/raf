# T5 scheduled checkpoint — 20261109T2145Z-T5-scheduled-native-attest-7d2a
session_id: 20261109T2145Z-T5-scheduled-native-attest-7d2a
origin: scheduled
work: work/T5/20261109T2145Z-T5-scheduled-native-attest-7d2a.md
baseline_sha: 1cccb086c30ee9a8e9f36af9a7a5880ff05985e9
scope_commit: 61cfda374968f16c1622b9cb39fbecd50fcdd9fa
resumed_from: clients/T5/sessions/20261109T2049Z-T5-scheduled-native-watch-b72e.md and 20261109T2045Z-T5-chat-native-owner-rerun-5f28.md
owner_device: docs/DEVICE_FEEDBACK_42058825739_AR.md confirms world entry/save/reload ONLY on older run 42058825739.
verified_current: https://github.com/alwansan/raf/actions/runs/42696228231 ended FAILURE at 2026-11-09T21:15:36Z; job 129428944191 reconstruct failed on "T5 attest final native Android runtime source bytes (read-only)" AFTER original graphics restore, mesh staging and 40-scene export, BEFORE Unity Editor invocation. native gate and license preflight PASS. delivery-result FAIL is downstream; publish-early-test SKIPPED.
source_contract: scripts/t5_validate_runtime_staging_parity.py compares exact staged .cs names and bytes in unity-candidate/Assets/RaftAndroid/Platform to android-port/Runtime/Platform, requires LocalProfileStore.cs and rejects symlinks/oversize. Workflow calls this with --project. Exact failure stderr not accessible through connected GitHub fetch; logs endpoint rejected, so do not assert which check failed.
other_ci: T4 mouse same-epoch source run 42704198957 SUCCESS; CI runner guard 42704199229 SUCCESS; T2 canonical evidence 42697151936 FAILURE separate; no new full native run initiated.
deliverable: published isolated work file and precise failure classification, without altering runtime or shared workflow; prevented incorrect release-only diagnosis and duplicate Unity request.
unverified: signed APK/OBB/XAPK from this run do not exist; no hash/version pairing, Resolution device test, or GPU measurements. CL Mini v0.2.17 test and old v91 OBB SAF hash cannot be attributed to this failed build.
next: inspect exact failed step log job 129428944191; reproduce byte-parity with synthetic final candidate and fix staging only if proved. Preserve Settings, GUID, .rgd and T4 input scope; coordinate a single later Unity run.
readiness: NOT_READY
