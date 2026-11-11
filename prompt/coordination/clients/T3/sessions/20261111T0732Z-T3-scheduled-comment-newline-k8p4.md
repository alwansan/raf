# T3 checkpoint — 20261111T0732Z-T3-scheduled-comment-newline-k8p4
origin=scheduled
base_sha=607a4b77c9b7252cdfd5ceffa41a27b5859bc2c0
resumed_from_sessions=20261111T0633Z-T3-scheduled-block-sequence-w7m2;20261111T0533Z-T3-scheduled-block-indent-n4q8
issue_id=RENDER-002
work=prompt/coordination/work/RENDER-002/T3-20261111T0732Z-T3-scheduled-comment-newline-k8p4.md

## Verified finding
Read owner feedback docs/DEVICE_FEEDBACK_42058825739_AR.md: phone success for world entry/save/re-entry on run 42058825739; white materials and square smoke remain open. Read AGENTS.md, CURRENT_OWNER_REQUIREMENTS, STATUS, CHAT_AND_SCHEDULE, PROMPT, OPERATING_MODEL. HEAD initially 607a4b77c9b7252cdfd5ceffa41a27b5859bc2c0. Latest T2 Actions run 42979397381 completed success (source-only).

Inspected actual scripts/t3_particle_material_chain_audit.py. The three Python comment lines immediately before material_indent contained literal backslash-n sequences rather than physical line breaks. This put material_indent and tail initialization inside a comment, so a block-style m_Materials list reaches an undefined material_indent and fails at runtime. The existing block-style tests already exercise this path but were not executed in prior cycles.

## Changes
- Scope commit 0264e2208edf932e01d8de7a8ee204dd7656053a
- Fix commit 7f7f3b53c4a08f8facc179006fad458863b1c1a5: turn escaped comment newline sequences into actual physical newlines, restoring material_indent assignment.
- Test commit c990bcf318cab55aec8a17e1e27d58275c9f63e6: explicit block-list runtime regression.
- No Unity/ZIP2/CL asset modified; no game build dispatched.
- Validation: inspected exact source replacement and new test via GitHub connector. Full Python unittest suite NOT executed in this environment (container cannot resolve github.com). This is a source fix, not a device rendering fix.

## Next
Run python -m unittest scripts.tests.test_t3_particle_material_chain_audit in a CI runner or connected checkout, then run read-only census on verified ZIP2 and exported Unity YAML; correlate emitter material hash with shader/texture binding, blend/alpha and phone screenshots. Keep RENDER-002 OPEN / NOT_READY; preserve T4 mouse and T5 resolution scopes.
