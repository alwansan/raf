# T1 WATER-001 — 20261108T1006Z-T1-scheduled-kernel-alias-6f3d
origin: scheduled
baseline_sha: c44f84b4333b0779022b36bc59dc5c1f82c04dd1
status: active
experiment_key: T1-FFT-KERNEL-ALIAS-20261108
shared_resource: none; source-only Python, no Unity/GPU/CI dispatch
files: scripts/t1_fft_trace_consistency.py; scripts/test_t1_fft_trace_index_alias.py; clients/T1/sessions/20261108T1006Z-T1-scheduled-kernel-alias-6f3d.md; this work file
hypothesis: same session and ComputeShader GUID cannot map a single kernel index to two different FindKernel names. Existing consistency checker catches name-to-index drift but misses index-to-name alias, allowing misleading kernel-6 attribution.
owner evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57; 220911-559 and 230108-327. Owner confirmed world save/reenter from 42058825739 artifact; packaging publication failed. Historical APK86 does not supersede.
previous T1: 988ccbfd (trace consistency); cd2bfef6 (five tests); 1aacc01d (session).
plan: add reverse index mapping check scoped by session+GUID, regression for alias rejection and distinct shaders/sessions acceptance, execute tests locally. This is structural only, not original kernel identity or GPU parity.
next: original shader GUID/program fingerprints and same-frame FindKernel/Dispatch/SetTexture trace; paired Vulkan/Unity first mismatch.
