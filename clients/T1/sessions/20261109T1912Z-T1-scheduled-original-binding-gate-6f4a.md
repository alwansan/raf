# T1 scheduled session — 2026-11-09 19:12 UTC
session_id: 20261109T1912Z-T1-scheduled-original-binding-gate-6f4a
origin: scheduled
resumed_from_sessions: 20261109T1610Z-T1-scheduled-duplicate-pair-8f31; 20261109T1806Z-T1-scheduled-provenance-presence-q5n8 (prior reported checkpoint)
base_sha: ddc14f24ef4cd173547ecfe8bf8d25ab712dbcae
scope: clients/T1/work/20261109T1912Z-T1-scheduled-original-binding-gate-6f4a.md
experiment: work/experiments/20261109T1912Z-T1-scheduled-original-binding-gate-6f4a.md

Reviewed live owner 5 Nov and 8 Nov reports, current requirements, team operating/cooperation rules, T1 trace source and GitHub branch/Actions. Source-level finding: the current original FFT passive hook explicitly asserts original_findkernel_callsite_present=false, original_runtime_mapping=unverified, gpu_result=unverified. A syntactically paired Dispatch log is not evidence of authentic original shader/FindKernel binding or numeric parity. Detailed proof obligations and bounded follow-up in experiment.

Owner success entering/saving/re-entering world remains limited to 42058825739 Artifact. WATER-001 remains OPEN/NOT_READY. No shared code, Unity runner, build, or CL write touched. No new numerical or device claim.

Next: acquire authentic program/kernel/resource mapping from verified ZIP2/reference and run deterministic first-pass Vulkan-vs-Unity numerical comparison, then instrument FindKernel/Dispatch with GPU readback. Coordinate shared mini-lab with T5. Existing regression tests require actual execution; do not repeat bookkeeping changes.
