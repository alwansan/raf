# T1 scheduled session 20261108T0206Z-T1-scheduled-capture-path-regression-b6e4
origin: scheduled
baseline_sha: 04eb8cfa34bfa143ecb1e4d11f6561943d00691d
scope: WATER-001 private FFT comparator capture path regression, no overlap with T4/T5
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; artifact 42058825739 entered/saved/reentered world; Actions publishing failed. CL pinned 520c4cf; 220911-559 23884 water-pass and 3850 kernel errors; 230108-327 39132 and 6026. This supersedes historical APK86.
work: prompt/coordination/work/T1/20261108T0206Z-T1-scheduled-capture-path-regression-b6e4.md
source_change: scripts/test_t1_fft_capture_budget.py; added 3 independent regressions: parent traversal rejected, symlink capture rejected, valid nested regular capture accepted.
plan_commit: a34698bcf768bd5b5405fc38ff7bdd297e3454d1
test_commit: 388c53ad7d841bb89864a6a321e7bb3e1064f432
final_head_checked: 388c53ad7d841bb89864a6a321e7bb3e1064f432
tests: NOT EXECUTED. Local git fetch fails DNS; no new relevant Actions run visible at final check. Test publication is not a passing test.
limits: No original Unity FFT capture or Vulkan-vs-Unity numeric parity, no proven mapping of Kernel Index 6 to Unity FindKernel/Dispatch or original ComputeShader GUID. No Unity, native, GPU, or phone run; no trial-build vote.
next: run python3 -m unittest scripts.test_t1_fft_capture_budget against test_commit; obtain original Unity ComputeShader GUID/kernel names/GetKernelThreadGroupSizes and FindKernel/Dispatch traces; compare original matched Vulkan/Unity pass captures to first divergence. Preserve T4 physical mouse and T5 Resolution/buttons scopes.
readiness: WATER-001 OPEN; NOT_READY 0/3.
