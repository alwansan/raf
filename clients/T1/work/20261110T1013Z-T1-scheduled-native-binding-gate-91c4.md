# T1 WATER-001 — native binding evidence gate

session_id: 20261110T1013Z-T1-scheduled-native-binding-gate-91c4
origin: scheduled
baseline_sha: 028957e91ec1624bdfd121e45b698d113ea3de50
status: BLOCKED_ON_AUTHENTIC_RUNTIME_CAPTURE
resource: FFT original compute binding (shared GPU/Unity; no build requested)
files: scripts/t1_fft_dispatch_pair_audit.py (read-only), tests/test_t1_fft_native_trace_contract.py (read-only); this work file only.
experiment_key: T1-FFT-ORIGINAL-FINDKERNEL-RESOURCE-BINDING-20261110

## Evidence and decision
- Owner's 2026-11-05 phone report documents world entry/save/reentry from artifact 42058825739, not FFT recovery. Original reconstruct succeeded; publishing and delivery gate failed.
- Log 220911-559: 23884 water-pass errors, 3850 FFT kernel errors. Log 230108-327: 39132 and 6026 respectively. They are separate sessions; counts alone cannot establish causal ordering.
- Current native trace source schema has `original_findkernel_callsite_present=false`, `original_runtime_mapping=unverified`, and `gpu_result=unverified`. It cannot satisfy original FindKernel/Dispatch GPU proof regardless of paired_count.
- Run 42788071163 succeeded on f7da4de (before tests commit 70e8cbd); do not claim coverage of later tests.

## Required decisive experiment
1. Identify authentic original FFT compute asset and .meta GUID, kernel names, and Unity callsite from verified ZIP2/Unity resource graph without publishing proprietary bytes.
2. Capture on one immutable build SHA: shader asset GUID, resolved kernel name/index via FindKernel, bound buffers/textures, dispatch XYZ, readback output digest and numeric per-pass comparison against pinned Vulkan reference. Record pass order and first divergent pass.
3. Match timestamp/session/build for the first kernel exception and first water-pass error in the same phone JSONL, not aggregated counters. Preserve no-proofs as unknown.
4. Use shared lab only if a GPU experiment can be run without pretending it is original Unity; coordinate any native build with T5 and avoid duplicate Actions.

No changes to T4 mouse, T5 Resolution/buttons, touch layout, .meta, scenes, or game data. No READY claim.
