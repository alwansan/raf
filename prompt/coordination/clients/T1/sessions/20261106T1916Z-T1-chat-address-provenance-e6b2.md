# T1 — Unity2021 same-dispatch FFT computed-address provenance vs buffered carrier

- **session_id:** `20261106T1916Z-T1-chat-address-provenance-e6b2`
- **origin:** `chat`
- **base_sha:** `e718c98ff98c6f3f31de589b082aab52360972a2`
- **resumed_from_sessions:** `20261106T190131Z-T1-chat-carrier-real-gpu-3c8f`, `20261106T1907Z-T1-scheduled-report-shape-n8v2`, `20261106T175623Z-T1-chat-float-carrier-context-b82c`
- **status:** scoped test **completed**; WATER-001 remains **OPEN**; game readiness **NOT_READY 0/3**.
- **work:** `prompt/coordination/work/WATER-001/20261106T1916Z-T1-chat-address-provenance-e6b2.json`
- **experiment:** `prompt/coordination/experiments/T1/20261106T1916Z-T1-chat-address-provenance-e6b2.json`
- **event:** `prompt/coordination/B_TEAM/events/T1/20261106T1916Z-T1-chat-address-provenance-e6b2.json`
- **original source ZIP2 pin:** `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original game bytes **not acquired this cycle**.
- **trial-20261106-r1:** T1 vote **لا يحتاج** unchanged; no full-game APK or significant water shader edit to phone-test.

## Restored live evidence and collaboration

Read live T_TEAM RESTORE_AR/CHAT_AND_SCHEDULE_AR/PROMPT_AR, team vote, previous T1 scheduled report-shape 1907Z (distinct file and source-only format gate) and chat Unity canary 190131Z. Initial HEAD `c282212bce7aa5f915860928c163fd32ebd46f12`, pre-scope HEAD `e718c98ff98c6f3f31de589b082aab52360972a2`; no queued Actions, other T5/local CI in progress on unrelated files. Work scope registered **before source edits** [3aa3d053](https://github.com/alwansan/raf/commit/3aa3d0533bb858eac3e5bc2730f2f76b2eda55d2). No collision with scheduled T1 `scripts/t1_fft_carrier_report_shape.py`; did not touch existing Unity sourcefree canaries or any T2–T5 work and did not cancel workflows.

Prior actual sourcefree Unity backend evidence:
- [42129683073](https://github.com/alwansan/raf/actions/runs/42129683073) marker `RAFT_T1_DISPATCH_ADDRESS_CONTROL {integer:0, bitcast_only:63, subnormal_multiply:63, normal_multiply:0}`. Uses `((x<<2)+x+Offset)&63`, `precise float`, static dispatch global; sourcefree, not original Raft.
- [42276235955](https://github.com/alwansan/raf/actions/runs/42276235955) real Unity2021 OpenGLCore one-dispatch 10-category structured-buffer address carrier had **0/640 errors**; origin of address differs.
- Original-derived actual Raft FFT private Unity [42198180194](https://github.com/alwansan/raf/actions/runs/42198180194) previously differed on Butterfly coordinate reads against original Mesa Vulkan; [42254539826](https://github.com/alwansan/raf/actions/runs/42254539826) SHA-original vs translated candidate on same Vulkan backend matched 384 invocation-keyed reads. No original authored runtime FindKernel/binding proof from these alone.

## New independent code

Created these new files on writable branch `feature/android-native-port` only:
- `android-port/Experiments/T1/T1FftAddressProvenance.compute` [b2fbbdb3](https://github.com/alwansan/raf/commit/b2fbbdb3a4343b459c61a38f58d003e1fac04937): one 64-thread Dispatch; computed uint address `((i<<2)+i+11)&63` versus independent `StructuredBuffer<uint>` value `(5*i+11)&63`; **same 64 expected address values**. Compares raw bitcast, plain float multiply by one, precise float multiply by one, Texture2D.Load from raw and from precise carrier for both sources. Six positive controls: both integer values, direct Texture2D.Load both origins, static dispatch global buffer read, normal precise float. 16 `uint` output words/invocation.
- `android-port/Experiments/T1/T1FftAddressProvenanceTests.cs` [44aa6d97](https://github.com/alwansan/raf/commit/44aa6d972d99415f2fa8fa175799a255983617b5): real licensed Unity2021.3.45f2 OpenGLCore GPU test with `ComputeShader.FindKernel`, exact 64x1x1 group, bindings, `Dispatch(1,1,1)`, `ComputeBuffer.GetData`. Checks 6 positive controls = 0, writes ten diagnostic mismatches as bounded 16 decimal lines, no original data/addresses/values public.
- `scripts/t1_fft_address_provenance_gate.py` [b23ef853](https://github.com/alwansan/raf/commit/b23ef8532f79e9275de40e87189beaa85f9a0be6): exact one NUnit test, Unity exit status 0, strict no-unsafe-XML, exactly 16 bounded ASCII 0..64 counters and controls; computed vs staged paired mismatch arrays and privacy-safe classification. Allows diagnostic nonzero counts but never invalid control.
- `tests/test_t1_fft_address_provenance_gate.py` [d70db302](https://github.com/alwansan/raf/commit/d70db30248c7bc4f86c95f17e1921632f48e1a73): 11 adversarial source-only tests/source contracts; synthetic pass, computed-only, buffered-only, mixed, 6 control failures, malformed/out-of-bounds, duplicate/wrong NUnit, unsafe XML, links/oversize, redacted CLI.
- `.github/workflows/raft-t1-fft-unity-address-provenance.yml` [aba2bcac](https://github.com/alwansan/raf/commit/aba2bcacd253ea91f225d768d802e5359018f008): isolated `ubuntu-24.04` licensed Unity `2021.3.45f2` with shared `raft-native-engine` mutex, `cancel-in-progress:false`, 25m job, SHA-pinned GameCI CLI `v0.1.72`, no raw logs/artifacts; private cleanup always. No ZIP2, LFS or original gameplay code.

## Actual evidence: REAL UNITY GPU success with nonzero discriminatory counts

[GitHub Actions **42278153683**](https://github.com/alwansan/raf/actions/runs/42278153683) at `aba2bcacd253ea91f225d768d802e5359018f008`, job `128099796286`: **COMPLETED SUCCESS**. Source-only Python gates **11/11 and 4/4 passed**, CLI SHA authenticated, actual Unity2021 OpenGLCore GPU NUnit exactly one case passed, cleanup step SUCCESS. Decoded job marker:

```json
{
  "classification": "computed_only_context_difference",
  "synthetic_gpu_invocations_expected": 64,
  "synthetic_gpu_words_expected": 1024,
  "synthetic_category_mismatch_counts":
    [0,0,63,0,63,0,63,0,0,0,63,0,63,0,0,0],
  "computed_address_category_mismatches": [63,63,63,63,63],
  "buffered_address_category_mismatches": [0,0,0,0,0],
  "positive_controls_passed": true,
  "sourcefree_unity_nunit_exact_case_passed": true,
  "original_raft_shader_compiled_or_compared": false,
  "float32_FTZ_cause_proven": false,
  "android_adreno_water_proven": false
}
```

**Key experimental outcome:** computed and staged uint address *values* matched (the integer controls are both zero mismatch) inside one dispatch, but computed-address-derived bitcast/plain/precise/Texture2D.Load all had **63 mismatches in 64 threads** while independently staged-buffer-derived carriers were **0/64** in every paired path. Six integer, direct texture, global and normal-float positive controls all zero. This is substantially stronger than assuming the 63/64 and 0/640 separate runs use equivalent lowering. It isolates the **provenance/compiler-context sensitivity** of the synthetic Unity OpenGLCore float carrier, not the exact float output bits (only bounded counts observed) nor formal cause/FTZ semantics. `precise` alone does not explain the difference because both computed plain/precise fail and staged plain/precise pass.

## Trust boundary and next action

No original game FFT shader executed, no private original SPIR-V side-by-side with Unity in this cycle, no reproduced game runtime FindKernel/SetTexture bindings or Android Adreno water pixels. **Do not patch water shaders or claim original water fixed** based on synthetic-only evidence; no new trial APK warranted. Preserve game build source + owner device result [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739) (world entry/save/reentry worked but water/colors/shaders still impaired).

Next T1 chat/scheduled worker: first read HEAD/new sessions/running actions and last work. Highest-value follow-up is a trusted/private SHA-original direct SPIR-V keyed `OpImageFetch` trace versus Unity2021 original-derived candidate **with matched physical source/butterfly bytes** and pinned shader/dispatch metadata via `scripts.t1_fft_private_unity_input_join`. Compare Butterfly coordinate producer SSA, exact in-shader computed-vs-staged value origin; only after original-vs-translated numeric and binding proof, make smallest semantics-preserving HLSL fix and retest before requesting device build. A potential *separate* low-cost follow-up is a sourcefree 1-parameter test capturing zero-collapse **counts only** among the 63 computed-carrier mismatches, but that would still not alone prove original FFT FTZ or water.

Scoped source files, experiment and CI are complete; release resource key, no continuing heavy build. T1 trial vote remains `لا يحتاج`, no peer files edited.
