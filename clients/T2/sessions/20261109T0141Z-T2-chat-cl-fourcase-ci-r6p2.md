# T2 chat — SHA-pinned original CL/test four-case JSONL validation, CI SUCCESS

- session_id: `20261109T0141Z-T2-chat-cl-fourcase-ci-r6p2`
- origin: `chat`
- branch (only writable): `feature/android-native-port`
- created_utc: 2026-11-09T01:41Z
- base_sha: `6fe95344909bd919dc8bc08cc245bda640e1155e`
- current coordination note: other worker T4 later advanced branch to `acedf8264c608c438a062b5cb1745860670172c1`; no force/reset, no shared file modification.
- resumed_from:
  - `clients/T2/sessions/20261108T2320Z-T2-scheduled-pixel-consistency-k4v9.md`
  - `clients/T2/sessions/20261108T2120Z-T2-scheduled-gles-evidence-q6m2.md`
  - `clients/T2/sessions/20261108T1956Z-T2-chat-pass1-source-kind-4d6a.md`
- issue_id: `WATER-001` overall OPEN; this narrow evidence verification is COMPLETED.
- experiment_key: `T2-CL-f401b7ffe3b6-SHARED-230157-CASE01-04-REAL-JSONL-GATE-v1`
- work: `work/experiments/20261109T0141Z-T2-chat-cl-fourcase-ci-r6p2.md`
- ownership: **T2-only** CI workflow; CL/test READ ONLY; no shared APK, pack, T1/T3/T4/T5 driver or game source changes.

## Hypothesis and preconditions

Prior T2 scheduled session published a strict source-free Python JSONL gate with numeric CASE02 pixel comparison (<=2 tolerance) and adversarial tests, but neither full unittest nor authentic owner CL/test exports had been run because its prior runtime couldn't resolve GitHub. Before committing this cycle, checked live Actions: no queued/in_progress/waiting jobs. T2 evidence already shows the owner's r2 Android15 Adreno730 **synthetic** T2-01..04 PASS for session `shared-20261108-230157-466487336`; authenticity of Raft original water is a distinct unproven question. Existing T5 shared Mini r3 built and no new T2 compiled driver change, so **NO_BUILD** vote unchanged.

## Work executed and reproducibility

1. Registered narrow scope on live head with work commit `3a43f7b3df617d39e85dc5e70343ba070d94ec6c`.
2. Added isolated <8 min GitHub Actions workflow `.github/workflows/raft-t2-gles-cl-evidence-gate.yml` on source commit `edf1cd6a0ba1cdc6a791f8c43763942a0ad1c428`, with independent concurrency `cancel-in-progress: false`, read-only permission, sparse checkout, no compiled game/Unity, no artifacts and scratch cleanup.
3. CI fetches four owner per-case JSONL **at fixed CL commit** `f401b7ffe3b6ead9038f3b35273599dcf8286e68`, directory `test/shared-20261108-230157-466487336`. It verifies exact Git blob identity before using each:
   - CASE01 `t2-gles-20261108-230235-466525434.jsonl` git blob `9019ac477d1cec28c0d237224bfaed9f868b14b1`.
   - CASE02 `t2-gles-20261108-230235-466525675.jsonl` git blob `0f01e5ce66299f94868b37e81990ad338bf29eb8`.
   - CASE03 `t2-gles-20261108-230235-466525949.jsonl` git blob `b271f1c5419927524393118a1406c4ccb420f909`.
   - CASE04 `t2-gles-20261108-230236-466526243.jsonl` git blob `11c44c8700ab661efa8129b98cf4ce8731172959`.
4. **Real CI result:** [run 42547038822](https://github.com/alwansan/raf/actions/runs/42547038822), commit `edf1cd6a0ba1cdc6a791f8c43763942a0ad1c428`, completed SUCCESS at 2026-11-09 01:43 UTC. Job `128934156208` all steps passed. **15/15 Python adversarial tests PASS**; 4/4 Git blobs match; actual CASE01, CASE02, CASE03, CASE04 all returned exactly `synthetic_gles_log_consistent=true` and `original_raft_water_verified=false`. No raw original owner logs copied into Git/Action artifacts; CI output only bounded boolean/category records.
5. T4 worked concurrently and advanced HEAD without conflict; no other team's work or running job was cancelled or overwritten.

## Proof boundary

This closes the **source-free CL device-export integrity / syntactic and numeric self-consistency verification** gap left by the prior scheduled session. It DOES NOT prove raw GPU pixel buffer authenticity independently of the exporting app, does not establish the original PC shader or CB0/sampler/RenderTexture binding, does not execute Unity water rendering or a new Raft APK on device. The phone PASS pertains only to the earlier shared Mini r2, **not** this CI. Actual original pass1 `Texture` returned from original managed callee with conditional/throw flow; crosspass instance equality and proper ShaderLab binding unproven; `WATER-001` OPEN and full game NOT_READY.

## Handoff to scheduled T2

- Keep shared Mini vote **NO_BUILD** without a genuine compiled T2 driver change; T5 owns Mini build. No full game XAPK request from this cycle.
- Continue **original-source Foam pass1 CFG/return-join and RenderTexture instance producer/receiver proof** in the existing separate CIL workflow, preserving Unity original bytes and private source. Then verify original CB0 matrix/vector/sampler coupling before authoring live ShaderLab and running Unity/Adreno pixels.
- Do NOT repeat these four CL exports or this 15-test CI without changed code/source evidence. This new workflow is reusable for later changes in the T2 source-free gate.
- To rerun only when justified: `python3 -m unittest discover -s tests -p 'test_t2_gles_device_jsonl_gate.py' -v`; four original per-case `python3 -m scripts.t2_gles_device_jsonl_gate CASE0X file.jsonl` after Git object identity verification.
- Work record contains scope and closure. Latest canonical project status should retain WATER-001 OPEN; no percentage of game completion asserted.

## Canonical summary refresh blocker — separated from successful experiment

The event `prompt/coordination/B_TEAM/events/T2/20261109T0143Z-T2-chat-cl-fourcase-gate-result.json` was published (commit `687d181d63c48cc2811e38948942a93d06a0a385`). Automatic T2 summary refresh was triggered at [CI 42547293865](https://github.com/alwansan/raf/actions/runs/42547293865) but FAILED in `scripts/refresh_b_team.py::read_records` on **pre-existing T3** event `prompt/coordination/B_TEAM/events/T3/20261106T2007Z-T3-chat-explicit-original-d52e.json`: `ValueError: Missing record identity`. The T3 event lacks both `id` and `event_id`; this is independent of the 15/15 + four owner evidence gate SUCCESS. No silent records skipped and no cross-owner file edit. Owning T3 was informed at `prompt/coordination/T_TEAM/T2_TO_T3_20261109T0147Z-summary-identity-blocker.md` (commit `92d50c0197e27f9b1dc75112748edeb4f54ea75f`). When T3 fixes the stable unique identity, rerun the normal deterministic summary workflow; keep WATER-001 OPEN.
