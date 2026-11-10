# T1 session 20261110T0112Z-T1-scheduled-device-proof-boundary-c6a2
origin: scheduled
resumed_from_session: 20261110T0011Z-T1-scheduled-runtime-gate-recheck-c91e
baseline_sha: e6a3fbd8395f09aad0fefef88b783de052e0951d
scope_commit: 7527f869baf2e76256050c02e7d8a5c94e2cb96c
scope: clients/T1/work/20261110T0112Z-T1-scheduled-device-proof-boundary-c6a2.md
status: evidence_boundary_confirmed; WATER-001 OPEN / NOT_READY 0/3

## Evidence and finding
Read 5 November device report before triage. Owner on POCO F5 Pro entered/saved/exited/reentered world from 42058825739 Artifact. Build publish/delivery failed. CL 220911-559 23884 water pass and 3850 FFT kernel errors; 230108-327 39132 water pass and 6026 kernel errors. Counts are per-session, not cumulative; HUD FPS is not GPU time.

Read live shared mini readiness: T1-05 has **actual owner-device Android15 Adreno730** synthetic 512-local SSBO FFT result: 1024 floats, maxabs 2.3841858E-7 <= 3E-5, GL0, unmap true. CL pinned https://github.com/alwansan/CL/tree/1dc0bf53303c1486afdb5a812d8597d682292589/test/shared-20261109-225506-552476830 . CI42690809051 source tests success. This closes the synthetic device compute probe, **not** original Raft Unity FFT or original FindKernel/Dispatch. Do not request another Mini build without changed driver. The original shader GUID -> original FindKernel callsite -> kernel index -> Dispatch resource/thread group -> actual GPU readback remains unverified; numeric Vulkan/Unity first divergent pass unknown.

Current branch HEAD at scope start e6a3fbd8395f09aad0fefef88b783de052e0951d. Recent CI 42728727179 and 42728726420 success (T3 provenance and runner guard); T2 CI42727990721 success; T5 source offline 42723946943 and managed preflight 42723947211 success at fb0bfea9. No evidence that latest full native XAPK or original FFT has passed. No CI canceled/repeated. T4 physical mouse and T5 Resolution ownership preserved.

## Next actionable proof
Extract verified ZIP2 original FFT shader identity and .meta GUID and managed original FindKernel callsite, record kernel names/index and resource/CB layout; instrument original Unity runtime before/after Dispatch with per-pass GPU readback from same source SHA/session; run deterministic Vulkan vs Unity comparison, stop at first mismatch and report input hashes, tolerance and GPU driver. Do not conflate this with the synthetic probe. Preserve owner world-success baseline, sound/Settings, .rgd and all source assets.
