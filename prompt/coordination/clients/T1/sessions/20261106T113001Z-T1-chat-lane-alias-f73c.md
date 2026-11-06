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

## Verified original FFT result — 2026-11-06

- [GitHub Actions 42211108743](https://github.com/alwansan/raf/actions/runs/42211108743) **completed SUCCESS** from exact workflow SHA `3737326672b2168028970c17443ce08c511df408`, job `127869673627`, all original ZIP2 acquisition/private Vulkan analysis and cleanup steps passed. New synthetic `tests/test_t1_fft_spirv_lane_alias_effect.py` **15/15 PASS** on checked-out source.
- Input owner: pinned `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Raw game binaries, original shader bytecode, constant offsets, individual SSA IDs and pixel values remain in private runner only.
- Original slot0 **source**: X physical x → one full-vector may-reaching `OpVectorShuffle` writer; Y physical y → one full-vector writer.
- Original slot0 **butterfly site1**: X physical x → one full-vector may-reaching `OpVectorShuffle` writer; **coordinate Y comes from a different physical vector lane beyond x/y**, with **two** same-lane may-reaching writers (value producer opcode categories `OpBitcast` and `OpConstant`). This refines the prior assertion treating coordinate Y as physical Function-vector lane 1.
- Original slot0 **butterfly site2**: X physical x → one full-vector may-reaching `OpVectorShuffle` writer; Y physical y → one same-lane `OpConstant` writer.
- In this bounded model on all six lanes: `static_unknown_alias_writers=0`, `uninitialized_possible=false`, `unknown_write_possible=false`, `pointer_escape_possible=false`. This is **not** a proof of complete original shader value semantics; the analyzer covers exact Function-vector single scalar constant-index OpAccessChain plus direct stores, and tracks branch joins/loops conservatively.
- Important limits: `original_integer_origin_proven=false`, `full_value_proven=false`, Vulkan-vs-Unity numeric parity unverified, authored Unity FindKernel/runtime resource identity unverified and no Adreno/device water acceptance. Original water remains broken per owner device evidence.
- Experiment: `prompt/coordination/experiments/T1/20261106T113001Z-T1-chat-lane-alias-f73c.json`. Canonical result event: `prompt/coordination/B_TEAM/events/T1/20261106T113001Z-T1-chat-lane-alias-f73c.json`. No shader, game, audio, Settings, touch or T2–T5 files modified; full native CI belongs to other agents.

## Status and handoff

- origin: chat
- status: completed (scoped original FFT component-aware source investigation)
- run_urls: https://github.com/alwansan/raf/actions/runs/42211108743
- next_step: isolate butterfly site1 coordinate Y's two may-reaching **same physical component** writers, specifically the candidate whose immediate value opcode is `OpBitcast`. Trace that source's signed-integer carrier SSA lineage vs the alternative `OpConstant` and use private, strict branch-aware analysis. Do not rewrite coordinate operands based solely on producer opcode or static may-reach counts. Then validate true same-input Vulkan↔Unity numerical parity and Android Adreno after authored binding confirmation.
