# T3 scope 20261111T1230Z-T3-scheduled-shader-owner-p6x8
origin=scheduled
Issue: RENDER-002; source evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md (white raft/hand, square smoke).
Scope: scripts/t3_material_shader_binding_audit.py and independent synthetic tests only. No T4 mouse, T5 resolution, T1/T2 water, Unity or APK.
Hypothesis: unique GUID match against arbitrary .meta currently incorrectly counts a texture or material GUID as a valid Shader binding; distinguish wrong owner extension and ambiguous owner without disclosing paths/GUIDs.
Experiment: T3-SHADER-OWNER-TYPE-20261111. Resource: CPU-only, no shared CI. Baseline script blob faea2f7cb0d0dcbd00c858dbf104c6d64f16533a.
Evidence pending; follow-up: compare authentic ZIP2 material bindings against export, then device visuals. Do not infer pixels from static check.
