# T1 WATER-001 — 20261108T1006Z-T1-scheduled-kernel-alias-6f3d
origin: scheduled
baseline_sha: c44f84b4333b0779022b36bc59dc5c1f82c04dd1
status: source_fix_published_validation_pending
experiment_key: T1-FFT-KERNEL-ALIAS-20261108
scope: prompt/coordination/T_TEAM/work/T1/20261108T1006Z-T1-scheduled-kernel-alias-6f3d.md
owner baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Owner's artifact entered/saved/reentered world; release publishing failed. Logs 220911-559: 23884 water-pass errors, 3850 kernel; 230108-327: 39132 pass errors, 6026 kernel. Counts do not identify kernel 6.
live HEAD before scope: c44f84b4333b0779022b36bc59dc5c1f82c04dd1. Most recent Actions checked: 42468530415 T4 regression success; no new T1 native request.
previous T1 trace work: 988ccbfd91ff559a9d7f5811cb719737cf2e44c5, cd2bfef660ee919a227ab49ad211f90ffceaf1ff, 1aacc01d72f9d2fd84ba9ba87ecc6895dd9739e7.
fix: scripts/t1_fft_trace_consistency.py now rejects a single (session, normalized GUID, index) associated with different kernel names. Original checker only rejected a single (session, GUID, name) associated with different indices. Reverse map preserves distinct shader/session scopes. Commit 70cf9dd9d1f0769809fbd8e4315f08b124df7c3d.
tests: scripts/test_t1_fft_trace_index_alias.py contains six cases: alias rejection, different session/GUID acceptance, distinct index acceptance, existing drift rejection, GUID case normalization. Commit a3e019dac945412f1afa344df1bd8ad043d81961.
verification: source inspected via GitHub connector; execution NOT performed (container git DNS resolution failed). No Unity GPU, Vulkan/Unity paired capture, or device validation. Source-only structural check; original identity unproven. No native CI duplicated; T4/T5 scope unchanged.
next: run python -m unittest scripts.test_t1_fft_trace_index_alias and existing trace tests in CI or connected checkout; inspect first failure. Capture authentic same-frame GUID/name/index/SetTexture/Dispatch and original resource fingerprints; compare paired Vulkan/Unity first divergent pass. Keep WATER-001 OPEN, NOT_READY 0/3.
