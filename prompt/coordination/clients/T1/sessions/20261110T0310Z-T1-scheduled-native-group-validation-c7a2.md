# T1 — 20261110T0310Z-T1-scheduled-native-group-validation-c7a2
origin: scheduled
issue: WATER-001
resumed_from: 20261110T0209Z-T1-scheduled-fft-first-mismatch-6c4e; 20261109T2115Z-T1-chat-direct-fft-thrown-hook-2b6e
baseline_sha: 443da13323a40b83fc358b355ea1f4fdd97051f1
work: prompt/coordination/work/WATER-001/T1-20261110T0310Z-scheduled-native-group-validation-c7a2.md
source_commit: 4c50a7bbc2724d9303ab84e8f8c2f048365b67c7
test_commit: 7a1c7bd4743b883a9c1864cfbfeefaf65dd3f3bf

## Read and coordination
Read owner device report first, AGENTS, requirements, STATUS, T_TEAM live protocol, previous scheduled session and T1 chat state/MEMORY. Original artifact 42058825739 world load/save/re-entry confirmed, but FFT kernel and water-pass errors remain, no proof of original GPU FFT. T4 physical mouse and T5 Resolution/three controls and packaging not edited. Original FFT direct synchronous thrown hook preserved.

## Concrete fix
The native JSONL parser accepted `group_xyz=1,0,1` or negative Y for a before-dispatch event, even though a valid Unity Dispatch must have positive group counts. It could then count a matching returned event as an admissible trace pair. Tightened native before validation to require X=1, Z=1, Y>0. New four regression cases cover positive Y, zero Y, negative Y and nonunit X/Z. Legacy synthetic traces unchanged. A valid pair still explicitly has runtime_kernel_identity_proven=false and gpu_execution_proven=false. This is a provenance/trace integrity fix, not a GPU FFT fix.

## CI and limits
At checkpoint 2026-11-10 03:10 UTC, run https://github.com/alwansan/raf/actions/runs/42747722414 was in_progress on the source commit; new test commit followed. No manual CI rerun, no Unity/APK build or phone execution. Source-only test result for new cases pending. No raw game material published.

## Next
Check the CI result and run four new tests, verify no existing native trace expected Y=0; use actual original same-build Unity `Dx11FFT` hook on next approved installed artifact to correlate source numeric6, bank/size, `before/returned/threw`, first water error and shader instance. Capture original GPU readback for Vulkan/Unity first mismatch. WATER-001 OPEN, NOT_READY 0/3.
