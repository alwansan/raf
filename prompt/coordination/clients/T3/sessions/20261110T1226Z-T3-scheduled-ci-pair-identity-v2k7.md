# T3 — 20261110T1226Z-T3-scheduled-ci-pair-identity-v2k7
origin=scheduled
issue_id=RENDER-002
base_sha=c03c24a94b282d673d1fc63fb2077658692dc579
resumed_from_sessions=20261110T1132Z-T3-scheduled-ci-head-audit-q7m2;20261110T1030Z-T3-scheduled-render-type-parity-f3k9
work=prompt/coordination/clients/T3/work/20261110T1226Z-T3-scheduled-ci-pair-identity-v2k7.md

## Evidence and new result
Read owner phone feedback, AGENTS, CURRENT_OWNER_REQUIREMENTS, STATUS, T_TEAM operating/protocol, latest T3 sessions, comparator, Actions and team work index. Phone artifact 42058825739 at e9c358e confirmed world/save/reentry; white hand/raft, smoke square and lighting still unresolved. CL source pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57. Mouse T4, resolution T5; no overlap.
CI run https://github.com/alwansan/raf/actions/runs/42799750403 is completed SUCCESS on ef457271, validating the previous 3 bool/int regressions (prior waiting_ci can close). No equivalent current build or active run seen in latest 20 Actions at review.
Discovered pair integrity gap: the prior t3_render_state_pair_diff.py accepts two independently formatted state summaries without asserting they refer to the SAME material, shader and pass. Added scripts/t3_render_state_pair_identity.py to require exact matching material_guid, shader_guid and pass_index, strict lower-case 32-char GUID and 64-char source digest formats, reject unknown envelope keys, and preserve compare's MISMATCH/INCONCLUSIVE semantics. No assets exposed.
New source commit 30cbf7e10d9178ccd7b3fa6d59b7bede26ac8dd3; tests commit e1bfd7750635aed3e1e3064547464b7ce3d5d4c5. Locally 8/8 tests passed using an interface-compatible copy of comparator; repository test file includes one additional shader-identity regression, NOT yet executed as repository CI. Work completion commit 29ac1999afb8638641fe652565ba9e21c36b8fbe.

## Limits and continuation
This checks identity syntax and equality, NOT that GUIDs truly came from authenticated original/export sources. The source_sha256 is format-only, not a digest of bytes verified by this tool. Does not extract original DXBC, restore ShaderLab, test Unity, or establish phone pixels; no fix to white/smoke/lighting claimed. RENDER-002 OPEN / NOT_READY 0/3. No APK or Unity/Actions dispatched. Preserve .meta/GUID/.rgd and all team resources.
Next: execute the 9 tests against checked-out current repo in CI or local, then obtain two independently authenticated original/export render-state summaries for the SAME material/shader/pass from pinned ZIP2 and actual exporter; run identity gate then state comparator, and report only safe mismatches. Coordinate original source acquisition with T5/T2. No duplicate build.
