# T1 — original FFT vs HLSL-roundtrip X coordinate lane depth budget

- session_id: 20261106T125300Z-T1-chat-hlsl-deep-lane-8e4c
- origin: chat
- status: waiting_ci
- issue_id: WATER-001
- base_sha: fb17194e8658ac3b2f3fa2fdfdffd991bd730484
- resumed_from_sessions: 20261106T124531Z-T1-chat-butterflyx-vector-writer-a6f3; 20261106T1215Z-T1-scheduled-coordinate-overflow-r6q2; 20261106T123411Z-T1-chat-y-inequal-branch-f52a
- work: prompt/coordination/work/WATER-001/T1-20261106T125300Z-T1-chat-hlsl-deep-lane-8e4c.json
- scope_commit: 2e876f7ca1921e064858b622c358f2f6e6cce791
- workflow_commit: 327c1b6431ad75de2a215c338e91c359e2f0a8f7
- run_urls: https://github.com/alwansan/raf/actions/runs/42221101286

## Verified baseline

Original-private [42220554705](https://github.com/alwansan/raf/actions/runs/42220554705) PASS with X signed-integer Input vector source passed through OpVectorShuffle → OpBitcast(sint32_bits_to_float32) → OpVectorShuffle → full local Function store. The same source-authenticated workflow's HLSL glslang compiled candidate SPIR-V `t1_fft_spirv_read_provenance` recorded coordinate X `depth_limit` with default depth 4. The parser supports max --coordinate-depth 12 and prior source SSA analysis used 12; use this legal upper bound before claiming an actual source type/bitcast loss. Scheduled T1 session `20261106T1215Z` separately tightened capture parser overflow/limits with source tests never run on GitHub.

## New bounded experiment

Own work scope reserved after checking no T1 private-source Actions in progress/queued. Changed only the existing T1 isolated no-Unity workflow to execute `tests/test_t1_fft_coordinate_probe_compare.py` at checkout and to invoke HLSL roundtrip `scripts.t1_fft_spirv_read_provenance --coordinates --coordinate-depth 12` instead of default depth 4. It still SHA-verifies ZIP2 original input, performs no Unity or Android build, does not publish SPIR-V or original shader source, and uses existing 20-minute timeout/concurrency. This is not a numerical replay; it resolves (or preserves) the structural provenance ambiguity and validates comparison parser safety.

## CI checkpoint

Run `42221101286` triggered by commit `327c1b6`, queued at checkpoint. Read new tests first and only bounded `RAFT_T1_PASS0_SPIRV_PROVENANCE` marker after `RAFT_T1_COORDINATE_PROFILE hlsl_roundtrip_slot0`; record X lane boundary and typed bitcasts. If synthetic parser tests fail, repair only actual confirmed defect, with fresh SHA expected value. Do not infer Android water readiness from a source-only test. WATER-001 remains OPEN.
