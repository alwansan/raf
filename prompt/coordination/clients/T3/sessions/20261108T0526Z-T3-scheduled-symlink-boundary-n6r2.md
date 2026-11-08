# 20261108T0526Z-T3-scheduled-symlink-boundary-n6r2
origin: scheduled
identity: T3
issue: RENDER-002 OPEN / NOT_READY
resumed_from_sessions: 20261108T0427Z-T3-scheduled-duplicate-shader-guid-q8m4.md; 20261108T0326Z-T3-scheduled-fixture-6b2d.md
owner_feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md (phone world/save/reentry success limited to artifact 42058825739; white raft/hand, lighting and square smoke remain open)

## Scoped change
Prevent the aggregate Material→Shader audit from reading symlinked .mat and .shader.meta files pointing outside its scanned root. Previous code rejected symlink shader source, but still read symlinked Material/meta files. Count skipped inputs separately; preserve original seen counts. Added a synthetic outside-root symlink regression test. No real game assets, .meta, GUID, .rgd, Unity, CI or build requests changed.

Scope record: prompt/coordination/work/RENDER-002/20261108T0526Z-T3-scheduled-symlink-boundary-n6r2.md
Scope commit: b68aa10c8ee82a8f4763058538eef3ef8bd796bb
Code commit: 1d9e16904dcc1e6b6b7c334597d151f5df6f59e3
Test commit: 8bc3d8eaabbdedab51bd6aa65f47bafd0ca2530c
Fixture newline correction: 017190599cd21e2108e3fb315c36963a22689303

## Validation and limits
Static source/test review only. Local git clone fails DNS resolution (Could not resolve host github.com); exact published suite not executed. Do not treat this as material/shader restoration or device pixel evidence. No CI dispatch because no equivalent source validation status was established and no heavy resource was needed.
Next: run python3 -m unittest tests.test_t3_material_shader_link_audit on exact branch source, then run audit against a complete verified export; trace white hand/raft and square smoke Renderer→Material→Shader/texture/blend with actual original and Android evidence.
