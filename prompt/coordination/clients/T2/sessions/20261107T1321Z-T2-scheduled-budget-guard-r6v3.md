# T2 scheduled — IL budget guard
session_id: 20261107T1321Z-T2-scheduled-budget-guard-r6v3
origin: scheduled
started_at: 2026-11-07T13:21Z
resumed_from_sessions: 20261107T1120Z-T2-scheduled-reconstructed-suite-r9k4; 20261107T1016Z-T2-scheduled-il-operand-type-f8c2
base_sha: eca2cda7f651b5f4f8d29f4af03a9c8be85698ee
issue_id: WATER-001
work: prompt/coordination/work/WATER-001/20261107T1321Z-T2-scheduled-budget-guard-r6v3.md

## Owner/device priority
Read docs/DEVICE_FEEDBACK_42058825739_AR.md: phone world entry/save/re-entry succeeded on artifact; publish failed; water pass/FFT errors remain. T3 owns colors/fire/candles/smoke; T4 physical mouse, T5 three buttons/Resolution. No overlap.

## Changes and evidence
- Registered work before editing, commit a70c97e1ea4e8c6e3c652d4e00f3ce1f5e67f539.
- Fixed synthetic trace allowing caller-supplied max_steps >128 to bypass hard intended budget, commit 6592fa91464a7bcf0694754480bdf056bde137a4.
- Added boundary and bypass regression tests, commit ac08fff3afbc3d702c9e162f99acd52af6230fb0.
- Original previous-turn patch was prepared but not committed; applied minimal equivalent change to live GitHub source.
- Tests have NOT been executed against checked-out original repository bytes this run; no claim of PASS.

## Boundaries / next steps
This is only synthetic IL provenance guard, not Mono.Cecil integration or ShaderLab/CB0. Pass 1 Foam resources remain unresolved. No Unity/device run, no original shader assets published, no duplicate CI. Next: run tests/test_t2_pass1_stack_provenance.py from immutable repository checkout, then connect real Mono.Cecil producer tracing, avoiding overlap with T2 chat. WATER-001 remains OPEN and trial build not requested.
