# T1 WATER-001 isolated work
session_id: 20261108T2006Z-T1-scheduled-firstpass-json-4a7d
origin: scheduled
baseline_sha: 20766ed850c16bc18bfab37ed5c6913c64c9d3f0
scope: scripts/t1_fft_first_divergence.py and isolated regression test only; no Unity, no T4/T5, no CL writes.
experiment_key: t1-private-firstpass-duplicate-key-gate-20261108
hypothesis: duplicate JSON object keys in private pass manifest silently replace reference/observed and can make first divergence select a different capture; reject duplicate keys before any private pixel read.
shared_resource: none; no CI launch.
owner_baseline: 42058825739 phone world save/reentry succeeded from Artifact; water/kernel failures persist; publication failed.
prior: T1 axis identity fix a12076184214b348eaa8d1435730cde0f46a33da; 42513642491 success.
status: planned

## Outcome
source_fix_commit: 3ee2e1ac5727f29485d14db28b846540576058bf
test_commit: a9e5b9bd9efd2862bd28f515824c4f665b984aab
observed_head_before_close: 09eada01575a640d1e0cabf6bdaa23e3d82e90f7
status: source_fixed_test_pending
validation: source review only; local runner cannot resolve raw.githubusercontent.com; no new CI launched. Existing test workflow may run on push; verify live Actions next cycle.
limits: prevents ambiguous JSON capture references; not evidence of actual Unity FindKernel/Dispatch or Vulkan numeric parity.
next: execute python -m unittest scripts.test_t1_fft_firstpass_manifest_duplicate_keys; then obtain original resource GUID/kernel/dispatch and paired GPU captures.
