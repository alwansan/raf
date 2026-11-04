# B24 — independent Raft Android engineering memory

Session: `20261104T2126Z-B24-6f19` (2026-11-04T21:27:28.998Z); generation B-2026-11-04. No prior B24 state found; new identity. Writing only `feature/android-native-port`. Current reviewed initial branch head `6bd9026e63b0147f3bb995188a1aa79d956533b3` (live branch may move). ZIP2 source pin: `15964ea8f246b6e076ce26b60931ee2e1a9a2385` (not downloaded in this scope).

## Read and verified

B team PROMPT_AR, README, OPERATING_MODEL_AR, SOURCES_AND_ACTIONS_AR, TEMPLATES, REVIEW, SUMMARY; AGENTS, current owner requirements, prompt README/CONTINUE/STATUS, ZIP2 provider and RESTORE. Read live branch, Actions, Releases, CL index, WATER-001/RENDER-002/LOCAL-005 issues, local world adapter/instrumentation code, B07 original callback probe and CI, main offline CI and native workflow.

Latest published real Raft APK86: run https://github.com/alwansan/raf/actions/runs/41812889049; newer LogRaft release tags are not game releases. CL original APK86 logs/summary linked by REVIEW_2026-11-04 demonstrate SteamUserStats.StoreStats DllNotFoundException after WorldHasBeenLoaded, plus invalid water passes/kernelCount0. Owner reports FMOD audio and Settings working, touch/layout deferred.

## Chosen gap and plan

Work `B24-20261104T2126Z-B24-6f19-world-callback-compile-parity` / issue LOCAL-005. Main native workflow calls `instrument_android_runtime_operations --apply` with trace manifest including `GameManager.OnWorldRecieved`; cheap `verify_android_offline_candidate.prepare()` selects only `adapt_android_offline_startup.PINS`, which excludes `GameManager`. B07 confirms source SHA and standalone wrapper lexical correctness, but that does not exercise full managed compilation of instrumented original GameManager. Correct preflight/actual-native parity, not game behavior. Need add SHA authenticated trace-only source selection and candidate write in fail-closed stage, synthetic negative controls, then inspect real CI. No Unity build or touch/audio changes. Do not claim WorldHasBeenRecieved or .rgd/device fixed.

## Followup/checkpoints

Read concurrent HEAD before writes; do not overwrite others. At finish record actual commit and CI URL/status, limitations and next move. Identity belongs only to B24.

## Verified checkpoint 2026-11-04T21:32:10.807Z

- Integration commit: https://github.com/alwansan/raf/commit/5cfd0544af9808dbd0326a7394a99283846d7ed4. Modified only `scripts/verify_android_offline_candidate.py`; new B24 synthetic tests and isolated workflow. The original `GameManager` SHA `8eb76bcf22028ace2394afe96051ae1e3e59e44f8243c2a68d6b163d80802306` is pinned by `config/runtime-operation-traces.json` and matched by the B07 authentic-original source proof. Late write gate authenticates trace-only sources using that SHA (no PINS bypass).
- B24 CI https://github.com/alwansan/raf/actions/runs/41916497807 **SUCCESS**, 6/6 targeted synthetic (missing, duplicate, changed post-selection, unregistered and SDK homonym controls plus preserve meta).
- Existing full real-original managed CI https://github.com/alwansan/raf/actions/runs/41916497902 **SUCCESS** on the exact integration source; original ILSpy recovery, adapted local RPC harness, original managed C# compilation passed. Native Unity Editor, ARM64, pixels and phone **NOT TESTED**. No claimed fix for Steam loaded-world failure or .rgd roundtrip. Audio and Settings untouched; touch deferred. Latest published Raft APK86 predates this.
- Work completed for callback compilation parity only. Next: move to distinct P0 blocker; recheck live HEAD, current teammates' work before writing.

## Foam checkpoint: original private four-stage Vulkan CI (2026-11-04T21:56:24.790Z)

- Final source and tests revision [a43ba5b8](https://github.com/alwansan/raf/commit/a43ba5b8cf337ea053581102aa45c2efaefe3537), green [https://github.com/alwansan/raf/actions/runs/41920166966](https://github.com/alwansan/raf/actions/runs/41920166966) 9/9 source-only negative/positive synthetic and authentic original 4-stage private DXBC→Vulkan1.1 SPIR-V→HLSL→Vulkan SPIR-V (all green). Earlier positive [https://github.com/alwansan/raf/actions/runs/41919758958](https://github.com/alwansan/raf/actions/runs/41919758958) confirms authentic source and stage translation before hardening.
- Source pin ZIP2 15964ea8, sharedassets0 115,978,112 bytes sha0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3; original Foam object PathID2420 SHA67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1 now separately hard-pinned.
- Exact original CB0 partial serialized vector member difference: pass0 both vertex/fragment 2; pass1 both vertex/fragment 1. Rejected assumption that both passes have 2. Two genuine passes, 4 original stages translated. Vertex 3 partial CB slots, fragment 1; original nonzero-size parameter envelopes 112B vertex, 52B fragment. Do NOT treat empty numeric records as empty CB and discard resource binding.
- Remaining: regenerate/authenticate real two-pass Foam ShaderLab with per-pass runtime CB/resource/texture bindings and GUID identity, then Unity/Android GPU proof. Do NOT update WATER gate/dummy flags/acceptance. No APK created; owner confirms Audio/Settings work, touch deferred. Water and LOCAL-005 remain OPEN; B24 state paused until explicit next session, not running in background.
- Full evidence: [Foam report](https://github.com/alwansan/raf/blob/feature/android-native-port/docs/B24_ORIGINAL_FOAM_PROGRAM_TRANSLATION_2026-11-04.md), resources B24-foam-original-stage-translation, experiment B24-20261104T2135Z-original-foam-stages. Both scoped B24 work records completed, but project not ready.
