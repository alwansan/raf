# T1 — actual licensed Unity2021 ten-category FFT float-carrier GPU discriminator

- **session_id:** `20261106T190131Z-T1-chat-carrier-real-gpu-3c8f`
- **origin:** `chat`
- **base_sha:** `4085da0987f754fdf5de1cebde40406358c640ad`
- **resumed_from_sessions:** `20261106T1850Z-T1-chat-gpu-input-join-b71c`, `20261106T181000Z-T1-chat-carrier-report-gate-4c7d`, `20261106T1808Z-T1-scheduled-unity-carrier-gate-m4k8`.
- **scope status:** `completed` after actual licensed Unity GPU result; **WATER-001 OPEN**, game readiness **NOT_READY 0/3**.
- **work:** `prompt/coordination/work/WATER-001/20261106T190131Z-T1-chat-carrier-real-gpu-3c8f.json`
- **experiment:** `prompt/coordination/experiments/T1/20261106T190131Z-T1-chat-carrier-real-gpu-3c8f.json`
- **result event:** `prompt/coordination/B_TEAM/events/T1/20261106T190131Z-T1-chat-carrier-real-gpu-3c8f.json`
- **source ZIP2:** `15964ea8f246b6e076ce26b60931ee2e1a9a2385` not acquired in this **sourcefree synthetic** experiment.
- **trial vote round:** `trial-20261106-r1`, T1 = `لا يحتاج` unchanged; no large integrated original-game shader fix.

## Restored state and coordination

Read T_TEAM RESTORE_AR, CHAT_AND_SCHEDULE_AR, TRIAL_BUILD_POLICY_AR, TRIAL_BUILD_READINESS.md, prior T1 chat 1850Z and scheduled 1808Z, C#/.compute fixture, strict private NUnit report gate, and existing licensed Unity GameCI workflow pattern. Live initial HEAD `b23f452c8ce034e064cd6166d94bd05d80a16dff`; no running or queued Actions initially. All T2–T5 votes and their files remained untouched. Independent work scope and intended files registered before changes: [3229089](https://github.com/alwansan/raf/commit/322908960532923deb0f16c359885fc9c423bdb2).

Recovery clue: prior [42129683073](https://github.com/alwansan/raf/actions/runs/42129683073) was genuine Unity OpenGLCore sourcefree dispatch canary with `integer=0, bitcast_only=63, subnormal_multiply=63, normal_multiply=0` mismatches. Its generated shader uses a computed `((x << 2) + x + AddressOffset) & 63u` address, static global dispatch ID, and `precise float` subnormal. Later [42261467757](https://github.com/alwansan/raf/actions/runs/42261467757) and [42264618337](https://github.com/alwansan/raf/actions/runs/42264618337) showed 320/320 exact sampled-image paths and simple Phi/loop synthetic paths, respectively. Previous original-derived Unity OpenGLCore FFT [42198180194](https://github.com/alwansan/raf/actions/runs/42198180194) still differs from original Mesa Vulkan in butterfly coordinates; true source/origin and kernel binding not proven for full Raft water.

## Concrete new engineering execution

The existing committed synthetic fixture `android-port/Experiments/T1/T1FftCarrierContext.compute` + `T1FftCarrierContextTests.cs` (source already established in session 175623Z), and the existing strict `scripts/t1_fft_carrier_context_result_gate.py` (14 adversarial gate unit tests from session 181000Z), were previously blocked from actual GPU execution due to workflow publication. This cycle successfully published **new isolated** `.github/workflows/raft-t1-fft-unity-carrier-context.yml` at [4928f866](https://github.com/alwansan/raf/commit/4928f866d0f035797e776ee004cc9e476aa1d49d) without altering the previous Phi/bitcarrier workflows. It:
- Uses `ubuntu-24.04`, `UNITY_LICENSE` environment, pinned GameCI CLI v0.1.72 release SHA256 `1de550a620ee92e05e920b6db7d431621440b60b2577f04b4a997dc92a58cb0a`, Unity Editor **2021.3.45f2**, explicit **OpenGLCore** NUnit assertion, and existing `raft-native-engine` shared mutex, `cancel-in-progress:false`.
- Stages **only sourcefree authored** `T1FftCarrierContext` ComputeShader and NUnit test in temporary Unity project. No ZIP2, native Android game, LFS, original shader, release, or APK/OBB/XAPK.
- Requires 3 fixture + 14 private-gate adversarial + 4 sourcefree Unity fixture Python tests before Unity.
- Compiles/executes one licensed GPU NUnit test, 64 invocations × 10 sourcefree paths (raw carrier, scale-by-one, normal float, five sampled-image contexts, static thread carrier). Three positive controls must pass, other seven are diagnostics and are **not suppressed if nonzero**.
- Parses exact bounded private NUnit XML plus ten canonical 0..64 decimal counts through `scripts.t1_fft_carrier_context_result_gate`. Only public redacted counts; private XML, shader project, logs and CLI removed under `if: always()`.

## Actual result (not merely synthetic Python static inspection)

[Actions 42276235955](https://github.com/alwansan/raf/actions/runs/42276235955), SHA `4928f866d0f035797e776ee004cc9e476aa1d49d`, job `128093156740`, status **COMPLETED SUCCESS**. Inspected live job step statuses: licensed Unity GPU step **success**, cleanup **success**. Job output included:
```
RAFT_T1_CARRIER_CONTEXT_GATE {"classification":"no_synthetic_context_difference",
 "positive_controls_passed":true,
 "sourcefree_unity_nunit_exact_case_passed":true,
 "synthetic_gpu_invocations_expected":64,
 "synthetic_gpu_words_expected":640,
 "synthetic_category_mismatch_counts":[0,0,0,0,0,0,0,0,0,0],
 "original_raft_shader_compiled_or_compared":false,
 "android_adreno_water_proven":false}
```
**640/640 synthetic GPU outputs matched** for this exact 64-thread fixture; all ten categories had zero mismatches. Source gate checks 3/3 + 14/14 + 4/4 pass. Original-game shader / original water pixels / Unity runtime kernel identity / Adreno device were NOT tested. A positive synthetic result rules out only the particular sourcefree direct-structured-buffer coordinate/bitcarrier/Texture2D contexts as a reproducible FTZ failure on this Unity OpenGLCore driver. It does not invalidate previous 63/64 computed-address/precise sourcefree canary or original-derived Unity FFT mismatches.

## Discriminating next experiment (avoid blind rerun)

The previous sourcefree dispatch canary `scripts/t1_sourcefree_dispatch_fixture.py` contains a **different address provenance** (`((x << 2) + x + AddressOffset) & 63u`), `precise float` qualifier, `static uint3 DispatchId`, and six-word output structure; today's sourcefree 10-path test uses coordinates read from `StructuredBuffer<uint2>`, different arithmetic/SSA and five Texture2D.Load paths. Exact arithmetic/precision/optimizer provenance may explain the differing synthetic results, but **no causal attribution yet**.

Next T1 independently test *same GPU dispatch/input* old computed shift-add-mask address versus new direct buffer coordinate/bitcarrier (one variable at a time), preserving original fixtures and published positive/negative canaries. Alternatively higher-priority execute actual SHA-original SPIR-V versus Unity2021 matched-input keyed trace with strict private `scripts/t1_fft_private_unity_input_join.py`; capture genuine per-kernel FindKernel/texture binding and source identity before game shader edits. If an authentic real shader fix is later merged, reassess T1's single vote `لا يحتاج`. No native game build request yet.

No peer files, source assets, audio, Settings, touch, Android request, or other running Actions modified. T1 sourcefree project and private test outputs erased by successful cleanup. This chat session's scoped files are released.
