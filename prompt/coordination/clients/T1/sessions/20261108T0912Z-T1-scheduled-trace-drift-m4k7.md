# T1 scheduled session 20261108T0912Z-T1-scheduled-trace-drift-m4k7
origin=scheduled
issue=WATER-001
branch=feature/android-native-port

## Baseline and owner evidence
Read docs/DEVICE_FEEDBACK_42058825739_AR.md first. Owner confirmed entering, saving, leaving and reopening world from artifact on source e9c358eda01785b65e4eb14f18723da426635628. Release publication failed; do not regress to historical APK86 interpretation. CL 220911-559: 23,884 water-pass errors and 3,850 FFT kernel errors; CL 230108-327: 39,132 and 6,026. Counts do not establish kernel identity. Physical mouse belongs T4; three controls and Resolution belong T5. No touch-layout work.

Read AGENTS, owner requirements, STATUS, T_TEAM CHAT_AND_SCHEDULE, PROMPT, OPERATING_MODEL, T1 state/MEMORY, trial vote ledger and current FFT validator. Previous source-only FFT test success run 42457914824 at a2932960 does not prove Android water or original runtime kernel identities.

## Scope
Work: prompt/coordination/work/WATER-001/T1-20261108T0912Z-T1-scheduled-trace-drift-m4k7.json
Experiment key fft-trace-index-drift-m4k7; shared resource none. New files only: scripts/t1_fft_trace_consistency.py and tests/test_t1_fft_trace_consistency.py. Avoid concurrent T1 file overlap and T4/T5 files. No native build or duplicate CI dispatch.

## Result
Created work record commit a79d37f46fc134556c6808598d09c8d428ae856e.
Created trace validator commit 988ccbfd91ff559a9d7f5811cb719737cf2e44c5.
Created five synthetic regression cases commit cd2bfef660ee919a227ab49ad211f90ffceaf1ff.
Locally exercised four equivalent synthetic controls (single, duplicate, drift rejection, separate-session acceptance) using a reduced local validator stub; full repository unittest has NOT been executed. The new checker reuses scripts.t1_fft_dispatch_coverage.validate for strict per-observation geometry and rejects within-session GUID+name kernel-index drift, while explicitly reporting no proof of original identity/GPU execution.

## Boundaries and next
Cannot identify kernel index 6 from index alone. Need SHA-pinned original Unity ComputeShader GUID, name and FindKernel/Dispatch trace, matched Vulkan/Unity RGBA32F private pass captures. Execute python -m unittest tests.test_t1_fft_trace_consistency against current branch; inspect latest Actions before running any new CI. Compare first divergent pass only after authentic paired inputs. WATER-001 OPEN, NOT_READY 0/3. No Unity/Android run or release claimed.