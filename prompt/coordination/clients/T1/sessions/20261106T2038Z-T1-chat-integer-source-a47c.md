# T1 — controlled original FFT vs Unity integer_source private GPU counterfactual

- session_id: `20261106T2038Z-T1-chat-integer-source-a47c`; origin: `chat`.
- resumed_from_sessions: `20261106T2031Z-T1-chat-real-unity-pair-6d9a`, `20261106T2017Z-T1-chat-private-producer-gate-8f31`.
- base_sha: `deb46f69187bc7491f97b9aef555980bb66de46d`.
- scope: `prompt/coordination/work/WATER-001/20261106T2038Z-T1-chat-integer-source-a47c.json`; experiment `prompt/coordination/experiments/T1/20261106T2038Z-T1-chat-integer-source-a47c.json`; result event `prompt/coordination/B_TEAM/events/T1/20261106T2038Z-T1-chat-integer-source-a47c.json`.
- status: **waiting_ci** [run 42290211798](https://github.com/alwansan/raf/actions/runs/42290211798), job `128141366121`. No native XAPK request, no replacement of game shaders or T2–T5 files, no cancellation.
- WATER-001 **OPEN/NOT_READY 0/3**. T1 trial vote still **لا يحتاج**. Original ZIP2 pin `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

## Proven baseline [42289238865](https://github.com/alwansan/raf/actions/runs/42289238865)

Genuine exact original ZIP2 direct SPIR-V Vulkan vs original-derived HLSL Unity2021 OpenGLCore keyed GPU buffers on verified same 1024x32 seed19 input. Both source and butterfly Unity CopyInput 0 mismatches per 32,768 texels. Original reference direct ImageFetch site counts 64/256/64, candidate site0 63/64 X-zero-collapse, site1 252/256 X-zero-collapse, site2 64/64 changed (X-zero63 and Y-zero64). Original-vs-Unity mismatches pass0 63/64 and pass1 31/32 pixels. Unity traced vs untraced shader output matched, all private input/role/candidate source SHA verified, authored runtime kernel and Android unproven. Run marked failure because numeric parity mismatched; this is useful real GPU divergence.

## Distinct controlled change

The current opt-in T1 workflow already supports `T1_INTEGER_SOURCE`. After direct original Vulkan trace, it keeps reference untouched, runs `spirv-opt` SSA local access elimination on private slot0 SPIR-V, then `scripts.t1_fft_source_integer_coordinates` rewrites **only its source ImageFetch signed int2 coordinate** to derive integer bit lanes without intermediate float carrier, translates private variant using SPIRV-Cross and updates only ephemeral slot0 SHA. The source-only test proves one designated source ImageFetch changed, not all sites. The Unity import/trace and exact SHA/CopyInput/numeric guard run afterward. No new ad-hoc ShaderLab or game change.

- Reserved disjoint scope [e2b8d1a](https://github.com/alwansan/raf/commit/e2b8d1aba320453feef46dd2967a094f043521b0) after checking no native/Unity in progress.
- Triggered exactly one counterfactual [commit 18ed8e3](https://github.com/alwansan/raf/commit/18ed8e3a8db0e29e955bf8dfcb7a4b3f019cd26e) with `[t1-paired-replay] [t1-integer-source]` on T1-owned workflow path. Shared `raft-native-engine` mutex; `cancel-in-progress:false`.
- Latest observation: run started, license/disk/checkout/source-only tests and GameCI binary checksum success; sourcefree Unity test in progress. **Do not guess variant outcome yet.**

## First next step for scheduled T1 or continuation

Re-read actual [run 42290211798](https://github.com/alwansan/raf/actions/runs/42290211798) and job `128141366121`. If reaching private FFT comparison, extract only safe markers `RAFT_T1_SLOT0_VARIANT`, `RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN`, `RAFT_T1_FFT_PRIVATE_UNITY_PRODUCER`, `RAFT_T1_INPUT_IDENTITY`, `RAFT_T1_FFT_TRACE_COMPARE`, and first-pass aggregate parity; compare 63/252/64 to variant site counts. Non-uniform change in source-only site0 isolates integer carrier translator path; do not assume FTZ. If stage failed beforehand, record first failing step and no numeric conclusion; no blind replay. Cleanup private original assets. T5 native import independent. No signed Unity compiler-binary attestation or Android water proof.
