# T1 | 20261106T113001Z-T1-chat-lane-alias-f73c

- session_id: 20261106T113001Z-T1-chat-lane-alias-f73c
- origin: chat
- status: waiting_ci
- resumed_from_sessions: 20261106T112050Z-T1-chat-alias-origins-b62f; 20261106T110543Z-T1-chat-cfgreach-f4d9; 20261106T110837Z-T1-scheduled-fft-first-divergence
- base_sha: 0f1df68c33d614ea497c1bc0d790b9f849839c1f
- issue_id: WATER-001
- work_id: prompt/coordination/work/WATER-001/T1-20261106T113001Z-T1-chat-lane-alias-f73c.json
- plan_commit: e0c87187786c01439fdd21e3ce52f5a9aafd03be
- source_commit: db1d4886531b11f1a3060eb3a44f10ab555fc768
- test_commit: 047899363c3ba957ef4d69f46990160f7e4320c3
- workflow_commit: 3737326672b2168028970c17443ce08c511df408
- run_urls: https://github.com/alwansan/raf/actions/runs/42211108743
- experiment_key: water001-original-slot0-fft-constant-index-vector-lane-alias-effect-v1-originalzip2pin-15964ea8-fft0
- resource_key: t1-fft-vulkan-roundtrip-isolation-ubuntu24-only

## Restored evidence and hypothesis

The source-authentic private slot0 FFT run 42209856944 succeeded and identified `indexed_access_static` aliases: four for source/site1 and eight for site2. Prior CFG audit 42208932160 reduced direct store candidates to one per site and physical X/Y, but kept `alias_store` unknown. This session addresses whether a constant-index write can be proven to affect a *different* physical load lane and should be excluded from that lane's may-reaching writers. It does not assume original authored Unity kernel mapping, numeric parity, or device water.

## Registration and changes

Before edits, verified live branch HEAD and no T1 roundtrip Actions queued/in-progress. The existing Android offline adapter and T2 ledger activities are independent; no cancellation or file ownership changes. Scope recorded in work file at `e0c8718`.

Added `scripts/t1_fft_spirv_lane_alias_effect.py` and `tests/test_t1_fft_spirv_lane_alias_effect.py` only, then added a source-authentic original slot0 private script call plus source-free adversarial tests to existing isolated `.github/workflows/raft-t1-fft-vulkan-roundtrip-isolation.yml`. The implementation tracks `OpVectorShuffle`/composite physical lanes, limits SPIR-V Function vector aliases to exact vector pointers and single constant-index `OpAccessChain`, and reports static/may-reaching same/other-lane writes. Dynamic index, pointer escape, unsupported storage, branch joins and loops fail closed. Public output does not include private source data, SSA IDs, literal offsets, or pixel contents.

## Evidence status

Run 42211108743 triggered by the workflow update and was in progress at checkpoint. No local exact-source test result claimed; use GitHub Actions job step and source-authentic marker. No Unity Editor, full Android build, phone test, or shader source rewrite started in this T1 scope.

## Next step

Read Actions test step; if any fixture/implementation fails, fix exactly and rerun a distinct validated commit. If successful, inspect only `RAFT_T1_FFT_VECTOR_LANE_EFFECT` bounded labels for site1 X and site2 X/Y. Record result, limitations, experimental metadata, canonical result event and update own work file to completed or blocked. WATER-001 remains open.
