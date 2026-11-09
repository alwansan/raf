# T3 — strict smoke per-pass metadata gate (scheduled)

- session_id: 20261109T1225Z-T3-scheduled-smoke-pass-v2-n4r7
- origin: scheduled
- resumed_from_session: 20261109T1131Z-T3-scheduled-smoke-evidence-gap-p9v4
- initial HEAD: cb7ade4e2aba6211e20e6a7dc98656867a5f48bf
- work registration: 9fdad9701a5930f7351da232368d468d97816fdf
- code commit: 19ad6e140fe3a6d3fa6f67d449dae7ca12894ffb
- test commit: c95058637ebca1f33489d06bda0dde3ff2d997f2
- issue: RENDER-002, OPEN, NOT_READY

## Read / observations
Read AGENTS, owner requirements, STATUS, T_TEAM prompt/operating/chat protocol, original device feedback, T3 state and MEMORY, previous 11:31Z session. Phone artifact 42058825739 has owner-confirmed local world/save/re-entry, **not** rendering restoration. CL 5 Nov shows white hand/raft, square smoke; smoke-linked Shader48 17 named renderers/34 material slots is not fire 108-use shader. Recent Actions 42607763178 and 42607763273 completed success but are not smoke device proof. No equivalent smoke-pass CI run observed in latest run listing.

## Actual change
New independent `scripts/t3_smoke_pass_state_gate_v2.py` (does not change v1) rejects missing per-pass Blend Src/Dst/Op, ZWrite, Cull, ColorMask, alpha clip and program-present metadata. Compares pass count/order and exact values, checks 17/34 smoke graph identity and SHA256 source provenance. New 8 synthetic unittest cases cover pass order, factor mismatch, absent fields, invalid alpha, wrong shader and source. No raw game assets published; no actual original/export pass metadata extracted.

## Limits / verification
Code and test source published via GitHub connector; tests were **not executed** in this run, and the gate has not been fed original Shader48 metadata. A match cannot prove texture alpha, authentic GPU program or phone pixels. No Unity/Android APK build, no game resources, no CL writes, no shared workflows or others' files changed.

## Next
Execute `PYTHONPATH=scripts python -m unittest discover -s tests -p test_t3_smoke_pass_state_gate_v2.py`; correct failures. Then use SHA-authenticated ZIP2 source in isolated private original/export workflow to emit metadata-only per-pass JSON for the exact smoke shader and run this comparator. Only then decide a targeted material/shader repair. Avoid conflating 108-use dummy evidence with 34-use smoke.