# T1 independent scope — 20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e
session_id: 20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e
origin: scheduled
updated_at: 2026-11-10T00:11:00Z
baseline_sha: 7e3736012430e781cd383db89e3c4512a820c9cf
issue_id: WATER-001
status: completed_source_gate_audit
intended_files: clients/T1/work/20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e.md; clients/T1/sessions/20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e.md
experiment_key: t1-original-fft-gate-recheck-fb0bfea9-42723946943
resource_key: none (read-only CI audit; no shared Unity/GPU build)
hypothesis: The new T5 managed parity manifest staging correction resolves the earlier pre-Unity source recovery gate, but still cannot prove authentic FFT FindKernel/Dispatch or numerical GPU parity.
resumed_from_session: clients/T1/sessions/20261109T2315Z-T1-scheduled-ci-gate-7c2f.md
owner_baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md; 5 Nov artifact world enter/save/reenter; FFT 3850 and 6026 errors in distinct CL sessions, pass errors 23884 and 39132 respectively.
scope_boundary: no changes to T5 staging or T4 physical mouse / T5 Resolution, no full build, no duplicated CI.
result: 42723946943 offline success and 42723947211 preflight success at fb0bfea9; previous gate failures superseded only for source-only checks. No Unity/device proof.
next: inspect original compute shader GUID and FindKernel/Dispatch binding; compare first numerical Vulkan/Unity mismatch with same-session GPU readback.
