# T2 scheduled scope — strict probe marker boundaries
session_id: 20261109T0124Z-T2-scheduled-m5q8
origin: scheduled
base_head: 6df332417716557cddb644bf6239f4a59923c204
issue: WATER-001 OPEN
resumed_from: prompt/coordination/clients/T2/sessions/20261109T0020Z-T2-scheduled-7c4d.md
owner_baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md (world/save/reload device-confirmed; water unresolved)
experiment_key: T2-GLES-MARKER-EXACT-20261109
files: scripts/t2_gles_device_jsonl_gate.py; tests/test_t2_gles_device_jsonl_gate.py; unique session/work files only
hypothesis: substring marker `tolerance=2` wrongly accepts `tolerance=20`; CASE03 substring `0x8cd7` accepts `0x8cd70`. Fail closed on complete numeric tokens, preserve real CL text syntax.
shared_resource: none; no Unity/mini build; no T3/T4/T5 source overlap. Test source via independent synthetic records, do not claim device water.
status: scoped
