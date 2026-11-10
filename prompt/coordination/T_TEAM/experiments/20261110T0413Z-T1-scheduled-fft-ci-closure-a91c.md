# T1 FFT native-group CI evidence boundary — 2026-11-10

Experiment key: t1-native-dispatch-positive-y-regression-4c50a7b-ci-42747722414
Owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; original device success limited to entering, saving and re-entering the world from run 42058825739 artifact.

## Verified
- Branch HEAD at review: 8e8e7a46fda9008197210701ad0585d73eab502e (03:52:39Z).
- GitHub Actions run 42747722414 completed SUCCESS, started 2026-11-10T03:10:49Z, head_sha 4c50a7bbc2724d9303ab84e8f8c2f048365b67c7.
- The four new regression tests were committed later at 7a1c7bd4743b883a9c1864cfbfeefaf65dd3f3bf. The successful run's head SHA predates this commit; do NOT claim that run executed the four new tests. The workflow watches tests/test_t1_fft_dispatch_pair_native_jsonl.py; a fresh run on test commit was not visible among latest branch workflow runs at review.
- Current source auditor checks native group_xyz with X=1, Z=1 and Y>0. The audit explicitly returns runtime_kernel_identity_proven=false and gpu_execution_proven=false.
- The original hook still asserts original_findkernel_callsite_present=false, original_runtime_mapping=unverified and gpu_result=unverified. A positive pair is therefore not a GPU result.

## Decision and next experiment
No redundant CI dispatched. First verify the four tests against current HEAD (local unittest or distinct CI on a source SHA containing 7a1c7bd); then extract authenticated FFT asset GUID and runtime FindKernel/Dispatch mapping. Capture paired GPU readbacks per pass from the SAME build/session to compare Vulkan and Unity and identify first numerical mismatch. The 220911-559 water pass/kernel error counts (23884/3850) and 230108-327 counts (39132/6026) remain separate device-session observations; no inferred causal one-to-one pairing.

## Boundaries
SOURCE_ONLY; not original GPU proof, not water restoration, not Unity compile, not device validation. No modification to T4 mouse or T5 Resolution/controls.
