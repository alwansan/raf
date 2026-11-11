# T3 scheduled checkpoint — 2026-11-11 19:30 UTC

- session_id: 20261111T1930Z-T3-scheduled-shader-orphan-g7q2
- origin: scheduled
- issue_id: RENDER-002
- resumed_from_sessions: 20261111T1731Z-T3-scheduled-texenv-parser-r6m2; 20261111T1626Z-T3-scheduled-orphan-texture-meta-n6p4; 20261108T2013Z-T3-chat-cl-pixelcopy-surface-f2n8
- baseline source: scripts/t3_material_shader_binding_audit.py blob 5e596f5ec53ec4396671a11fffcb271e775abb97
- work: prompt/coordination/work/RENDER-002/20261111T1930Z-T3-scheduled-shader-orphan-g7q2.json
- experiment_key: shader-meta-owner-asset-existence-synthetic-20261111

## Verified observation
Prior shader audit counted a unique matching `.shader.meta` as `shader_guid_unique_in_supplied_tree` without checking whether the corresponding `.shader` file existed. This is a structural false-positive risk. Texture audit already distinguishes orphan .meta; shader audit did not.

## Implementation
- [0791230955](https://github.com/alwansan/raf/commit/0791230955bc94fe5e86cd8b44b99d01348470f2): add `shader_guid_orphan_meta_without_asset` for matching GUID with absent/unsafe shader asset. Preserve duplicate and nonshader categories.
- [4f747d12](https://github.com/alwansan/raf/commit/4f747d124981b78de1b9dadc008c0ba219cf9460): isolated synthetic regression fixture.
- [97348fbc](https://github.com/alwansan/raf/commit/97348fbc28cb85f33a8c077f3d13593dee936ee6): correct fixture newline escapes.

## Evidence boundary
Not executed in CI or on device in this session. No ZIP2 original asset comparison, no Unity import, shader variant, particle alpha/blend or Android pixel proof. Source/export parity from CI 41939404454 (41 materials, 227 UV, 89 internal textures, 25 external unresolved) remains scoped. Owner's run 42058825739 confirms world/save/reentry but not graphics repair. No game assets, .meta, .rgd, audio, Settings, mouse, or touch modified. T4 owns mouse, T5 resolution/delivery.

## Next
Run `python -m unittest discover -s tests -p 'test_t3_shader_orphan_meta.py'` (source-free) in existing T3 test workflow if not already running; inspect result before repeating. Then apply shader/texture audits to authenticated same-scope original/export and inspect the 25 external dependencies, particle material alpha/keywords and ShaderLab variants. Do not claim white/square smoke root cause from structural audit.
