# T1 WATER-001 — evidence-gated first mismatch
session_id: 20261110T0209Z-T1-scheduled-fft-first-mismatch-6c4e
origin: scheduled
issue_id: WATER-001
status: active
intended_files: isolated work record; no Unity/game sources
experiment_key: t1-original-fft-binding-vs-synthetic-t105-42058825739
resource_key: none (no shared GPU/Unity/CI)

## Device baseline (read first)
- docs/DEVICE_FEEDBACK_42058825739_AR.md: 42058825739 source e9c358eda01785b65e4eb14f18723da426635628; world enter/save/exit/re-enter succeeded from artifact, publishing failed.
- 220911-559: 23,884 water pass errors, 3,850 FFT kernel errors, 1 OBB GUID warning, 1,333 cursor RGBA32 warnings.
- 230108-327: 39,132 pass errors, 6,026 kernel errors, 2 OBB GUID warnings. These are different log windows; counts must not be summed as unique failures.
- CL snapshot 520c4cf409aa20a4db54ff80ed87d8807d9cba57.

## New discriminator
- scripts/t1_fft_dispatch_pair_audit.py explicitly requires original_findkernel_callsite_present=false, original_runtime_mapping=unverified, gpu_result=unverified for native before events. A positive pair cannot establish authentic kernel binding or GPU readback.
- scripts/t1_shared_fft_device_evidence.py explicitly requires original_raft_compute_executed=false for synthetic T1-05. Its successful numeric result is a control only.
- Therefore next decisive experiment must log an original shader GUID, FindKernel name/result, dispatch groups, buffer bindings and post-dispatch GPU readback for a *single* FFT pass on the *same* immutable build/session; compare against pinned Vulkan reference with dimensions, normalization, orientation and epsilon recorded. First divergent pass wins; no aggregate-only claims.
- Distinguish managed Dispatch return from GPU execution; correlate exception timestamps with water pass errors within the same session. Do not claim causal mapping from aggregate counts alone.

## Existing CI
- 42723946943 offline success; 42723947211 preflight success (not a Unity build).
- 42696228231 reconstruct failed at T5 runtime source-byte attestation; do not reuse as device FFT proof.

## Boundary
No new CI, no original runtime binding claim, no changes to T4 mouse or T5 Resolution/UI. Stay NOT_READY until original on-device evidence.
