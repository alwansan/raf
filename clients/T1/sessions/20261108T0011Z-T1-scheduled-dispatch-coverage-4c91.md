# T1 scheduled session 20261108T0011Z-T1-scheduled-dispatch-coverage-4c91
origin: scheduled
baseline_sha: 28e369b343015bd86cd7084dace640f7a5bf5b21
final_verified_head_before_session: 615833cd56fc987046c35cf8da3731c949cbc126
scope: WATER-001; FFT FindKernel/Dispatch geometry, isolated from T2/T4/T5
owner_phone: docs/DEVICE_FEEDBACK_42058825739_AR.md; 42058825739 artifact world enter/save/reenter success, publish failure. CL pinned 520c4cf: 220911-559 23884 water-pass / 3850 kernel; 230108-327 39132 / 6026.
work: prompt/coordination/work/T1/20261108T0011Z-T1-scheduled-dispatch-coverage-4c91.md
new code: scripts/t1_fft_dispatch_coverage.py; scripts/test_t1_fft_dispatch_coverage.py
commits: plan 9dfc96f3a3dcef209f0f186647b417009c89e0b6; validator 226464a2c52a34f8cc0f8891d7c2057eb3f55b87; regression 615833cd56fc987046c35cf8da3731c949cbc126.
finding: strict conservative structural gate checks ComputeShader GUID, kernel name, FindKernel==Dispatch index, numthreads and exact ceil dispatch group coverage, without exposing game bytes. This is an evidence-quality check, not a demonstration that any original Unity FFT dispatch passes; legitimate padded overdispatch with explicit bounds checks would require a separate justified policy.
tests: six unittest cases published but NOT executed in this runtime; local github.com DNS resolution failed, GitHub connector read/write succeeded. No native/Unity/GPU/device test. No new FFT capture data.
actions: at final check 0 in_progress for branch; no equivalent CI dispatched.
next: execute python3 -m unittest scripts.test_t1_fft_dispatch_coverage on exact commit, then collect authentic GUID, kernel names, GetKernelThreadGroupSizes, FindKernel, Dispatch, logical extent and shader resource fingerprints. Match original Vulkan and Unity pass captures to identify first numeric divergence. Do not assume kernel index 6 is FFT.
readiness: WATER-001 OPEN; NOT_READY 0/3; trial vote unchanged. T4 physical mouse and T5 buttons/Resolution remain their separate scopes.
