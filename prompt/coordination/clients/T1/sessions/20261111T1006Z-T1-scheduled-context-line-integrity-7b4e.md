# T1 session 20261111T1006Z-T1-scheduled-context-line-integrity-7b4e
origin: scheduled
UTC: 2026-11-11T10:06Z
branch: feature/android-native-port
baseline: c9547601324338cdd833fbc98f10ebc1eec5ac98
observed_head_before_session: ea17a0c099188e42f36d0e83d1e14f2b29e515ca

## Owner evidence first
Device 42058825739 source e9c358eda01785b65e4eb14f18723da426635628: owner entered world, saved and reopened from artifact; packaging publication failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57, sessions 220911-559 (23884 water pass errors, 3850 FFT) and 230108-327 (39132, 6026). These are event totals, not GPU time or proof of cause. T4 physical mouse click/scroll and T5 resolution/right-side buttons own independent scopes; 8 Nov unified mini-lab supersedes five separate APKs.

## Scope and change
Work: prompt/coordination/work/WATER-001/20261111T1006Z-T1-scheduled-context-line-integrity-7b4e.md
Found source t1_fft_pass_proximity.py accepts context row line=0 for a center line>0; invalid log provenance could become a nearest pass. Fixed line >=1 validation (commit 565847a21bd40186202276523273c677f6cde465). Added zero/negative context line regressions (commit ea17a0c099188e42f36d0e83d1e14f2b29e515ca). No game resources or source changed.

## Evidence/limits
Existing 5 tests inspect same-line, distance, direction, marker allowlist, errors-only. New tests added but not yet executed in Actions. Local Git network DNS failure, so no full repo checkout; GitHub connector wrote source directly. No CL raw scan performed this cycle, no Unity or GPU execution, no original FFT binding proven. No duplicate Actions triggered. Latest observed T5 right panel regression 42998052750 SUCCESS; predecessor 42997954913 failed; neither is GPU proof.

## Next
Run python3 -m unittest discover -s scripts -p 'test_t1_fft_pass_proximity.py'; if green, apply scanner --errors-only to authenticated CL log sessions and record pass marker proximity, then correlate original ComputeShader GUID and exact FindKernel/Dispatch trace for one same-build device run. Do not infer causality from proximity. WATER-001 OPEN / NOT_READY 0/3.
