# T3 scheduled — reject declaration-free shader false positives
session_id: 20261106T0825Z-T3-scheduled-empty-shader-gate-7c2a
origin: scheduled
issue: RENDER-002
base_sha: d3f4fdba1ba04c67b6c88b73b09c201170dade8f
resumed_from: 20261106T0732Z-T3-scheduled-gate-syntax-b91e; 20261106T0631Z-T3-scheduled-yamlpointer-4e8b; T3 chat 20261106T014652Z-T3-chat-particle108-authoredsem-1f83
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone world/save/reentry confirmed only on artifact 42058825739, graphics NOT confirmed.
scope_plan_commit: eea002660001ab81f8ff8adcaf7255c17bb8d2b7
code_commit: ba83733edbdaf0f2e8d81b2c95d654877ff74590
test_commit: b8297d15974fed888d8d9a06bbad32be43353ef5
finding: The structural Shader48 link gate accepted an empty .shader or a comment-only .shader as STRUCTURAL_LINK_ONLY when the GUID and Material pointer matched. A non-empty ShaderLab Shader declaration is now required, without treating the declaration as original shader provenance or Android pixel evidence.
checks: inspected fetched source and three new tests after commits; Python tests NOT EXECUTED in this run (container network unavailable and no redundant CI launched).
next: python -m unittest discover -s scripts -p 'test_t3_shader_identity_gate_syntax.py'; then run gate against SHA-pinned same-instance actual post-restoration Shader48/Material export; validate original shader identity and V/F interfaces independently. Do not claim square smoke/white materials repaired.
scope: scripts/t3_shader_identity_gate.py; scripts/test_t3_shader_identity_gate_syntax.py; own work/session only. No raw assets, Unity build, Actions cancellation, mouse/Resolution/touch modifications.
status: SOURCE_FIXED_PENDING_TEST; RENDER-002 OPEN; NOT_READY.
