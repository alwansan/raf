# T1 scheduled session — 20261109T0931Z-T1-scheduled-trace-provenance-a6f2
origin=scheduled
status=source_fixed_tests_pending
baseline_sha=b66b28121d8394800e87609d251dce648e9c27b1
scope_file=clients/T1/work/20261109T0931Z-T1-scheduled-trace-provenance-a6f2.md

## Device and latest evidence
Owner's 42058825739 Artifact: world entry, save, exit and re-entry confirmed; publish/packaging failed. CL fixed snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57: water-pass and FFT-kernel error floods. This does not prove water rendering or kernel binding. Later unified mini lab direction (2026-11-08) supersedes five mini APKs.

## Change
- Scope commit cb56c63d94e6e016da4eaa346a7aa5577f02e7bd.
- Code commit 2f6f64c1dab0556b68beade835555bee918d7afa: optional session_id/build_sha/shader_guid/resource_guid must match between before and returned events, including key presence. Prevents false pairing when logs from different builds/sessions are combined. Does not require these fields on legacy traces and retains runtime_kernel_identity_proven=false, gpu_execution_proven=false.
- Test commit 05130df7f0b60c0185ead8422af9a5f564f48571: five synthetic regressions for matching provenance, cross-session, cross-build, missing GUID and legacy non-proof.
- Latest observed HEAD before session commit: 05130df7f0b60c0185ead8422af9a5f564f48571.

## Validation / limits
Tests authored but not executed in this environment: container GitHub DNS resolution failed. No Unity build, no phone execution, no numeric Vulkan/Unity pass comparison, no readiness change. No T4/T5 files changed; physical mouse/buttons and Resolution remain their scoped work.

## Next
Run python3 -m unittest discover -s tests -p 'test_t1_fft_pair_provenance_a6f2.py' -v on a working runner. Inspect actual device JSONL field names and ensure producer emits stable session/build/GUID metadata on both sides; then correlate first FFT pass divergence to authentic Unity FindKernel/Dispatch and Vulkan input buffers. WATER-001 OPEN; NOT_READY 0/3.
