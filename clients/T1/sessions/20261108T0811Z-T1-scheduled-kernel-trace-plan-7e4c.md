# T1 WATER-001 — 20261108T0811Z-T1-scheduled-kernel-trace-plan-7e4c
origin: scheduled
baseline_sha: 86c0b442920c7ec6face2f9b71de38f889203a39
status: investigating_original_kernel_trace
experiment_key: T1-FFT-KERNEL6-TRACE-20261108
shared_resource: none; no Unity/GPU build requested
files: clients/T1/sessions/20261108T0811Z-T1-scheduled-kernel-trace-plan-7e4c.md; prompt/coordination/T_TEAM/work/T1/20261108T0811Z-T1-scheduled-kernel-trace-plan-7e4c.md (if available)
hypothesis: Android log kernel index 6 cannot identify a Unity ComputeShader without shader GUID + named FindKernel trace + dispatch callsite. Source-only dispatch validation cannot establish original FFT parity.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57; sessions 220911-559 (23884 pass errors, 3850 kernel), 230108-327 (39132 pass errors, 6026 kernel). Artifact world enter/save/reenter succeeded; publication failed.
latest source-only test: 42457914824 SUCCESS on a29329608e1ec4e5378f222ce427a25e8a5fe742; not GPU parity.
next experiment: capture per-dispatch shader GUID, FindKernel(name)->index, GetKernelThreadGroupSizes, SetTexture/SetBuffer bindings, dispatch dimensions and pass ordinal from same frame; record matching original program/resource fingerprints separately. Compare paired Vulkan/Unity RGBA32F captures using existing t1_fft_first_divergence.py at first mismatch. Do not assume index 6 maps to FFT.
constraints: do not publish raw game shader assets or logs with secrets; preserve meta/GUID, no duplicate CI, no T4/T5 scope edits, NOT_READY 0/3.
