# T1 chat — first real opt-in original ZIP2 FFT vs Unity private GPU replay

- session_id: `20261106T2031Z-T1-chat-real-unity-pair-6d9a`
- origin: `chat`
- base_sha: `3d6ed8f1a42a3a05d7feb8e8365820703ba92df4`
- resumed_from_sessions: `20261106T2017Z-T1-chat-private-producer-gate-8f31`, `20261106T2015Z-T1-scheduled-native-fft-gate-x4q9`, `20261106T195959Z-T1-chat-ci-log-pin-7b42`.
- issue WATER-001 OPEN / NOT_READY 0/3; T1 trial vote remains «لا يحتاج».
- work: `prompt/coordination/work/WATER-001/20261106T2031Z-T1-chat-real-unity-pair-6d9a.json` (waiting_ci).
- experiment: `prompt/coordination/experiments/T1/20261106T2031Z-T1-chat-real-unity-pair-6d9a.json`.
- canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T2031Z-T1-chat-real-unity-pair-6d9a.json`.
- source: current branch HEAD checked before launch; original ZIP2 immutable SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`.

## Intent and non-overlap

Read latest live T_TEAM RESTORE, CHAT_AND_SCHEDULE, PROMPT, vote and prior scheduled 20:15/chat 20:17 handoffs, checked active Actions, T5's open independent Editor ABI preflight source-only work. No queued/in-progress Unity/native job at scope reservation (20:30 UTC), no native build or T2–T5 source touched. Scoped original ZIP2 SPI-V versus real Unity 2021 OpenGLCore first FFT candidate 1024x32 seed19 3-site invocation trace. Shared resource `raft-native-engine-feature/android-native-port` is protected by job concurrency with `cancel-in-progress:false`; no other job canceled. Work reserved first [4452059](https://github.com/alwansan/raf/commit/445205918116906be71eca04fb21a047659639cb).

## Actual attempts (not a successful original FFT comparison yet)

1. Triggered existing opt-in, T1-owned `.github/workflows/raft-t1-fft-unity-input-identity.yml` by a one-shot comment and safe `[t1-paired-replay]` commit [225e131](https://github.com/alwansan/raf/commit/225e131dd039e24e1d74caa4b1d975391506bd4b). This is NOT a native XAPK request.
2. [CI 42289104961](https://github.com/alwansan/raf/actions/runs/42289104961), job `128137544591` FAILED **before original ZIP2 or Unity** in source-only test validation. Four `OptInOriginalUnityWorkflowContract` cases failed with `FileNotFoundError`: the workflow's sparse checkout had `scripts`, `tests`, `android-port/Experiments/T1` but did not include `.github/workflows/raft-t1-fft-unity-input-identity.yml` that the four tests read. Not a shader/kernel/Android failure.
3. Fixed **real CI preflight bug** by including that exact workflow file in sparse-checkout [177a573](https://github.com/alwansan/raf/commit/177a57342dc6197e2f5dceee940c9bb0bec34c6f), preserving license/mutex/ZIP2 source, private path restrictions and all other gates.
4. Corrected opt-in retry [CI 42289238865](https://github.com/alwansan/raf/actions/runs/42289238865), job `128138000484`: at 20:33Z **IN_PROGRESS**, passed license/disk, checkout, all source-only tests and exact GameCI CLI download/checksum. At checkpoint it was running **source-free Unity ComputeShader test before original ZIP2 acquisition**. No claim of actual original/Unity GPU parity or successful completion. Standard paired diagnostic/runner compat workflows are separate; do not confuse green results with original test.

## Next session/scheduled handoff

**First action:** check [run 42289238865](https://github.com/alwansan/raf/actions/runs/42289238865) / job `128138000484` fresh status/steps; while running, keep work `waiting_ci` with this run, do NOT trigger duplicate. If failed, inspect first failed stage, decode only fixed safe public status/CI contracts, avoid raw private shaders/pixels/IDs. If successful, extract `RAFT_T1_PRIVATE_ORIGINAL_UNITY_JOIN`, producer stage and private trace shape, actual original-vs-Unity invocation/ULP site profile and evidence SHA, then choose smallest proven candidate correction; don't confuse generated HLSL compiled slot with authored in-game kernel or Android Adreno water acceptance. If license/resource delayed, preserve wait checkpoint and do a different scoped T1 source task. T5 handles native build and Editor ABI; current T1 vote remains «لا يحتاج».

## Final completed retry — real GPU numeric result, 20:36Z

[Run 42289238865](https://github.com/alwansan/raf/actions/runs/42289238865) job 128138000484 **COMPLETED FAILURE at last numerical parity gate as intended**. Sourcefree GameCI success; real ZIP2 SHA pinned; 20 original DXBC compute programs privately staged; direct original SPIR-V Vulkan ImageFetch keyed recorder ran and preserved output against uninstrumented original; original Vulkan 2-pass success. Real Unity 2021.3.45f2 OpenGLCore imported original-derived HLSL first two slots, ran 2-pass GPU, NUnit wrote `complete`. Private SHA/source-candidate/trace and exact same physical 1024x32 seed19 inputs verified. Unity GPU CopyInput mismatches source=0/32768, butterfly=0/32768. Keyed reads reference/unity coverage = [64,256,64], no missing/extra reads. **Actual cross-backend coordinate mismatch**: site0=63/64 (x zero-collapse63); site1=252/256 (x zero-collapse252); site2=64/64 (x zero-collapse63, y zero-collapse64). Instrumented Unity output matches uninstrumented Unity output (64/64). Original-vs-Unity pixel mismatch pass0=63/64, pass1=31/32. This is **authentic executed numeric divergence**, not float32 FTZ causal proof; authored in-game FindKernel and Android Adreno water unverified. No proprietary contents published; cleanup succeeded. **Do not rerun baseline**; next experiment changes ONLY private translated candidate with `integer_source` using unchanged original reference. WATER-001 OPEN, trial vote unchanged.
