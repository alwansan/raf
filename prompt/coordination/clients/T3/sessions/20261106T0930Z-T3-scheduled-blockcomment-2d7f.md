# T3 scheduled — block-comment Shader declaration false positive
session_id: 20261106T0930Z-T3-scheduled-blockcomment-2d7f
origin: scheduled
issue: RENDER-002
baseline_sha: 991a51b7fc26eeaabd083386be51d3b99bfecf96
scope_plan_commit: 35d187dfcac98ac4c3409d92db3741e6c43118d5
code_commits: 5fd5b19bc60e95fdc5187466da7fc2b418c33ed3; 66a6e0084eee257f49d0783e01e7d071947b021e
test_commits: 979a6714a1710d050c9be4741ab7757e5ecb70fc; dc74dc71af7178129e524071200249bb2324d271
resumed_from: 20261106T0825Z-T3-scheduled-empty-shader-gate-7c2a and T3 earlier Shader48 sessions.
owner_evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md, phone world/save/reentry confirmed only on artifact 42058825739.
finding: previous structural gate's Shader declaration regex could match a Shader line inside /* ... */ block comment. New comment-aware masking preserves quoted strings and newlines, and treats unterminated block comments as comments. It does not prove shader program authenticity.
validation: six isolated Python regex behavior assertions PASS (block comment, valid declaration after comment, unterminated comment, quoted comment markers, line comment, multiline declaration). Full repository unittest and CI NOT RUN; no Unity build. Three new unittest fixtures committed but execution pending.
next: execute python -m unittest discover -s scripts -p 'test_t3_shader_identity_gate_syntax.py' on checked-out HEAD; apply structural gate to same-instance SHA-pinned post-restoration Shader48 and linked materials; compare authentic DXBC shader identity and V/F semantics independently before any visual repair claim.
status: SOURCE_FIXED_PENDING_TEST; RENDER-002 OPEN; NOT_READY.
non_scope: no .meta, GUID, .rgd, resources, mouse, resolution, audio, Settings or touch edits; no Actions canceled.
