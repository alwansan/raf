# T1 20261105T002257Z-T1-fft-unity-contract

- Started: 2026-11-05T00:22:57.688Z
- Identity: T1; resumed_from_session: 20261104T235355Z-T1-9fca (PAUSED as of 2026-11-05T00:19:00Z); no active same-identity session observed on re-read.
- Baseline HEAD at review: 1219f24fbd8d1194e0c913403dd171d70cf03a3b (revalidate before shared writes).
- Issue: WATER-001 remains OPEN. Original B48 source selector → 20 compiled candidates is proven, Unity runtime kernel mapping and authored .compute are NOT proven.
- Verified predecessor: T1 CPU Vulkan bank0 6 executions CI https://github.com/alwansan/raf/actions/runs/41939314440 ; bank1 negatives https://github.com/alwansan/raf/actions/runs/41938536760 and https://github.com/alwansan/raf/actions/runs/41939082498.
- Today reviewed T_TEAM/PROMPT_AR.md, README.md, OPERATING_MODEL_AR.md, RESTORE_AR.md, LEGACY_HANDOFF.md, MIGRATION_2026-11-05.md, SOURCES_AND_ACTIONS_AR.md, TEMPLATES.md, SUMMARY.md, previous T1 state/MEMORY/session/work and B48/B30 findings; inspected HEAD, commits, branch Actions (T3 active 41940350604), release APK86 and CL SHA5394407; no Actions cancelled.
- Scope: build a strictly isolated authored-.compute Unity 2021 Editor runtime selection probe (no game runtime substitution, no fake indices) and reproducible bounded staging preflight; do not touch shared native workflow or other agents.
- Hypothesis: a private signed/sha-constrained staged source + explicit B48 candidate contract + actual Unity FindKernel/HasKernel/GetKernelThreadGroupSizes can observe Unity runtime index allocation, separating it from original compiled slot position. Any source-only stage remains unproven until Unity runs.
- State: started; work plan file follows. Updated evidence and next step to be appended after tested result.

### Checkpoint: 2026-11-05T00:32:25.064Z
Source-only authored FFT Unity runtime probe scaffold and SHA/selector gates added: scripts/t1_stage_unity_fft_kernel_probe.py, android-port/Editor/T1FftKernelRuntimeProbe.cs, tests/test_t1_stage_unity_fft_kernel_probe.py, workflow raft-t1-fft-unity-kernel-probe.yml. CI41941690194 and CI41941716641 SUCCESS (7 synthetic suites); original owner not supplied to CI, no authored original .compute, Unity/Adreno/device or genuine kernel mapping proof. Report docs/T1_UNITY_FFT_RUNTIME_PROBE_2026-11-05.md and experiment 20261105T0031Z-T1-authored-unity-kernel-stage. Work PAUSED rather than claiming restoration; WATER-001 OPEN. Next authenticate authored source + private manifest, actual Unity execution, coordinate T5.
