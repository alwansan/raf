# T1 session 20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e
origin: scheduled
resumed_from_session: 20261109T2315Z-T1-scheduled-ci-gate-7c2f
baseline_sha: 7e3736012430e781cd383db89e3c4512a820c9cf
scope_commit: 12c6f11e59a9d35603403e36ee07004843484a6d
scope: clients/T1/work/20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e.md
issue: WATER-001 OPEN / NOT_READY 0/3

## Verified delta
Previous T1 session documented failures 42715257589 (source parity) and 42715257606 (offline source recovery), with full build 42696228231 failing before Unity.
T5 changed scripts/verify_android_offline_candidate.py at fb0bfea9846437bdd74ae55ba38a5e39bd5b993a ("stage original T1 FFT dispatch trace in managed parity manifest").
The newer offline integration run 42723946943 at that SHA is completed/success; job offline successful. Managed compile parity 42723947211 at same SHA is completed/success; preflight job successful. These supersede the previous CI-gate status for this source candidate; do not claim the original full native build now passes. HEAD at start 7e3736012430e781cd383db89e3c4512a820c9cf (T5 documentation).
Other latest T4 mouse capture / immersive checks 42723947226 and 42723947160 completed success at fb0bfea9; no T1 ownership change.

## Device and FFT interpretation
Owner 5 Nov run 42058825739 artifact: world entered, saved, exited, reentered. Packaging publication failed. CL 220911-559: 23,884 water pass errors and 3,850 FFT kernel errors; CL 230108-327: 39,132 water pass errors and 6,026 kernel errors. Never sum epochs or infer GPU time from HUD.
Original shader asset GUID -> original FindKernel callsite -> actual kernel index -> dispatch resources / thread-group -> GPU readback is not yet established. CI preflight success is not Unity or phone GPU execution. No first divergent numerical Vulkan/Unity pass verified this cycle.

## Decision and next
No redundant CI or Unity/native build requested. T5 staging parity issue appears resolved for the checked source-only candidate, but native APK packaging and actual FFT GPU binding remain unverified.
Next: inspect T1 original FFT dispatch trace manifest in reconstructed candidate, correlate with original shader GUID and FindKernel; capture same-session per-pass GPU buffers and compare Vulkan/Unity numerically, then request device test only through shared lab policy. Preserve T4 physical mouse three buttons and T5 Resolution work.
status: completed_ci_gate_audit; WATER-001 OPEN NOT_READY.
