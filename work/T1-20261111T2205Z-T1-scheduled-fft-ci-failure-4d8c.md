# T1 scope — 20261111T2205Z-T1-scheduled-fft-ci-failure-4d8c

origin: scheduled
baseline_sha: 9f8e1e01f5b7e73fed172541a6dbe371ee91a82f
issue: WATER-001
experiment_key: T1-FFT-CI-43101033840
status: investigation / awaiting job stdout

## Evidence and hypothesis
Owner phone baseline 42058825739 confirms world entry/save/reentry, not water success. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57 has FFT kernelIndex 6 and water pass errors; numeric parity remains unproven.

GitHub run https://github.com/alwansan/raf/actions/runs/43101033840 (head fcb0c5c82380b6b0feb94b3066527ff1a082dea6) concluded FAILURE 2026-11-11 21:12 UTC; checkout succeeded, `Verify paired diagnostic and scheduled first divergence` failed. No artifacts. Failure is a CI/test failure, not device evidence. The exact failing assertion/traceback cannot be inferred from job-step status alone. Inspect job stdout at https://github.com/alwansan/raf/actions/runs/43101033840/job/130792235243 before patching. Do not re-run identical CI until traceback is established.

Scope files: diagnostic workflow `.github/workflows/raft-t1-fft-paired-diagnostic-checks.yml`, `scripts/t1_fft_first_divergence.py`, and its tests, read-only until traceback obtained. No shared GPU/Unity runner requested. T4 owns physical mouse, T5 owns Resolution/UI and delivery; avoid overlap. Do not modify shared state or package build request.

## Next discriminating action
Retrieve job stdout, identify first failing command and assertion, reproduce against exact head fcb0c5c, then patch smallest independent source/test defect and run lightweight tests. Independently pursue original `.compute` + `.meta` GUID + `HasKernel/FindKernel/Dispatch` proof; CI source checks cannot certify phone water.
