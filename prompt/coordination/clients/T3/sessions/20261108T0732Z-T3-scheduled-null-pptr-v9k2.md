# T3 session 20261108T0732Z-T3-scheduled-null-pptr-v9k2
origin: scheduled
issue_id: RENDER-002
base_sha: 20c2c33dcf76a1dac7deb35470d2b49169e95416 (scope commit; branch may advance concurrently)
resumed_from_sessions: 20261108T0630Z-T3-scheduled-parser-boundary-f4c9; 20261108T0526Z-T3-scheduled-symlink-boundary-n6r2
work: prompt/coordination/work/RENDER-002/20261108T0732Z-T3-scheduled-null-pptr-v9k2.md

## Source finding and fix
Read owner phone report docs/DEVICE_FEEDBACK_42058825739_AR.md and AGENTS.md, current owner requirements, STATUS, T_TEAM chat/schedule, prompt and operating model. Owner-confirmed world/save/reopen only on source e9c358eda01785b65e4eb14f18723da426635628, artifact run 42058825739; white raft/hand, lighting and square smoke still unresolved. T4 physical mouse and T5 resolution/UI are separate scopes.

In scripts/t3_material_shader_link_audit.py a material m_Shader PPtr with fileID=0 and a nonzero stale GUID was incorrectly reported shader_guid_resolved_in_scan if that GUID matched a Shader.meta. Unity PPtr with fileID=0 is null; the audit must not promote it to authentic shader restoration. Fix commit 90ae61fb762ea6454911067d82d91f37da5adf84 classifies fileID zero first as shader_pointer_null regardless of GUID, preserving nonzero fileID/zero GUID builtin category. Regression added 416159688ebcd5be78d48573680a2a345642c0df; fixture newline correction 14802c0c886dc5688df30f9067dafe171b59971b.

## Verification and limits
Source inspection confirms conditional ordering and test assertions. Local GitHub DNS unavailable (git ls-remote: Could not resolve host github.com), so repository tests were NOT executed. No original ZIP2 tree, actual CL image pixels, or full Unity Material->Shader->Texture chains were inspected this run. No Unity build, new Actions dispatch, or phone validation. The fix prevents a false positive in a diagnostic, not a demonstrated cause or repair of the device graphics. No asset, GUID, .meta, .rgd or shared files changed.

## Next
Run python -m unittest tests.test_t3_material_shader_link_audit on the exact committed source; use pinned complete original export and apply audit with evidence for actual hand/raft/smoke material identities and ShaderLab/texture/alpha variants. Check active team scope and HEAD before touching shared resources. RENDER-002 OPEN; NOT_READY.
