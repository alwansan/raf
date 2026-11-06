# T1 — actual prior Unity float-carrier anomaly and new targeted source fixture

- session_id: 20261106T175623Z-T1-chat-float-carrier-context-b82c
- origin: chat
- status: blocked_ci_workflow_publication (source-only source contract checks verified; NOT Unity GPU executed)
- issue: WATER-001 OPEN / NOT_READY 0/3
- base_sha: 6af6fba382e5f7dc050070c4620abf140f1e6820
- resumed_from_sessions: 20261106T174500Z-T1-chat-phimerge-opengl-g6k2; 20261106T172258Z-T1-chat-bitcarrier-textureload-c4e9; 20261106T1714Z-T1-scheduled-vulkan-unity-gap-q8n4
- T1 trial vote: لا يحتاج, round trial-20261106-r1, persisted earlier at d5330515a091e4503187040361cad226a01fb35b (not changed)
- owner trial policy: prompt/coordination/T_TEAM/TRIAL_BUILD_POLICY_AR.md
- work: prompt/coordination/work/WATER-001/20261106T175623Z-T1-chat-float-carrier-context-b82c.json
- experiment: prompt/coordination/experiments/T1/20261106T175623Z-T1-chat-float-carrier-context-b82c.json
- event: prompt/coordination/B_TEAM/events/T1/20261106T175623Z-T1-chat-float-carrier-context-b82c.json
- source pin: zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385 NOT accessed this cycle.

## New actual-source-backed evidence

Recovered previously executed [Unity 2021 OpenGLCore dispatch canary 42129683073](https://github.com/alwansan/raf/actions/runs/42129683073), job marker:
`RAFT_T1_DISPATCH_ADDRESS_CONTROL {"integer":0,"bitcast_only":63,"subnormal_multiply":63,"normal_multiply":0}`.
This is a genuine **actual synthetic** 64-lane Unity GPU result with 63/64 mismatches for subnormal float bit-carrier preservation and 0 for pure integer/normal-float controls, not an original FFT proof.

The later distinct synthetic sourcefree [42261467757](https://github.com/alwansan/raf/actions/runs/42261467757) showed 320/320 zero mismatches in sampled-image paths using bitcast, and [42264618337](https://github.com/alwansan/raf/actions/runs/42264618337) showed 320/320 zero for branch/nested/loop float Phi carriers. Those are not contradictory as GPU compiler may optimize direct bitcast-to-Load path differently from materializing asuint(asfloat(...)) or applying float arithmetic. Actual SHA-original derived Unity OpenGLCore FFT [42198180194](https://github.com/alwansan/raf/actions/runs/42198180194) has 252/256 butterfly1 X and 63/64 butterfly2 X mismatches, both classified constant-observed under one fixture; original derived same-Mesa Vulkan vs translated candidate [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) matches all 384 keyed reads. Do not conclude 63/64 raw float-carrier error is necessarily the actual FFT root cause without a discriminating same-dispatch test.

## New code committed on branch (isolated, no original game asset)
- `android-port/Experiments/T1/T1FftCarrierContext.compute` commit `278cd350e30ba8cd0ba3e1463f666262d28e6c02`: one actual GPU dispatch with 10 context-specific uint32 outputs per lane including integer baseline, float raw bitcast, float arithmetic, normal-float control, five Texture2D.Load variants and private-static thread carrier. Public synthetic only.
- `android-port/Experiments/T1/T1FftCarrierContextTests.cs` commit `dfc4855b123d67601f066903c9529647e5b3b1f4`: real Unity 2021 OpenGLCore EditMode GPU readback code, 64 threads × 10 categories = 640 words, strict direct integer, normal-float, direct-image positive controls, other category mismatch counts retained as diagnostic, not forced to match.
- `tests/test_t1_fft_carrier_context_fixture.py` commit `ea1f1ef4565ff1e995db9474c1b042129fcfaace`: 3 Python source-only fixture tests.
- Independently fetched all three committed files and checked 10 out buffer writes, 5 image paths, static carrier, 3 NUnit positive controls, OpenGLCore, ComputeShader Dispatch/GetData, and 3 Python test declarations. **10/10 JS source-contract assertions passed; this is not execution of the Python/Unity tests.**

## Blocker at workflow publication

Attempted to publish new scoped workflow `.github/workflows/raft-t1-fft-unity-carrier-context.yml` using connected GitHub app on `feature/android-native-port`, with private Unity license environment and the shared `raft-native-engine` mutex. The publish action was **blocked by the tool's security check** (not a GitHub Actions test failure). A second smaller safe-scoped workflow creation attempt was also blocked. Checked by fetch: workflow file does not exist (404). No CI was triggered, no Unity GPU run of the new fixture, no new APK or Android device test. Do not claim 640 GPU words validated, nor rerun previous test as a substitute.

## Next actual engineering action

When authorized workflow publication is available, independently recheck live HEAD, work and CI, then stage only this sourcefree fixture using existing licensed pinned Unity2021 GameCI pattern and require exact NUnit success and bounded 10-class counts. Test result can distinguish raw bitcast/subnormal materialization from sampled-image coordinate-lowering context. If all categories pass, float context hypothesis remains unproven; if raw/materialized paths fail while direct sampling controls pass, narrow converter backend semantics; still need source-authentic original Unity keyed trace before patch. No new native trial APK justified: T1 vote remains لا يحتاج. If workflow publication remains blocked, another T1 cycle may focus on source-private original FFT evidence or collaborator scopes rather than blindly retry.

Other T1 sessions and other T2–T5 files/votes were not changed.
