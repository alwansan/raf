# T3 work scope — 20261111T1331Z-T3-scheduled-texref-h6m4
origin=scheduled
Baseline HEAD: 6485e86c802bb16b3a4f5b27554ace28b1267c62
Issue: RENDER-002 / white materials and square particles.
Files owned: scripts/t3_material_texture_binding_audit.py, tests/test_t3_material_texture_binding_audit.py, this work record and a new T3 session record only.
Hypothesis: a material's m_TexEnvs external texture GUID can be absent or resolve to a non-texture .meta even where Material->Shader GUID is present. Static classification is not device visual proof.
Experiment key: T3-TEXENV-GUID-STRUCTURE-20261111. No shared Unity build resource, no game assets, no .meta changes. Respect T4 mouse and T5 resolution scope.
Plan: create fail-closed aggregate-only read-only scanner, synthetic regressions, run Python tests when executable source available. Cross-check current HEAD before each write; never force update. Source-only, no CI dispatch.
Owner device baseline: run 42058825739 enters/saves/re-enters world; report says 23,884 water pass and 3,850 FFT kernel errors in session 220911-559. This scanner does not address those.
