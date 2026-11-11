# T3 session 20261111T1731Z-T3-scheduled-texenv-parser-r6m2
origin: scheduled
baseline_sha: c7f042d490fd713f23d1c6b22ce08b472c1e6516
scope_commit: 55ca3232c02c4e5f0683a025252cf4c9ab0d2e6d
status: evidence_reviewed; no asset fix claimed

## Device evidence
Owner report docs/DEVICE_FEEDBACK_42058825739_AR.md: artifact 42058825739 enters/saves/reopens world on device; screenshots show white hand/raft and square smoke. CL 520c4cf409aa20a4db54ff80ed87d8807d9cba57, 220911-559: 23884 water pass errors, 3850 FFT kernel errors, 1333 cursor RGBA32 warnings; these are not by themselves proof of material root cause. Preserve working save, sound, Settings.

## Live code observations
The current tree contains scripts/t3_material_texture_binding_audit.py and tests/test_t3_material_texture_binding_audit.py. Existing tests cover null, absent GUID, nontexture GUID, ambiguous .asset and orphan .meta. Current scanner is static partial-tree only, cannot establish shader variants, alpha, lighting or actual pixels. No original ZIP2/export tree staged in this run; no root-cause proof. Avoid another synthetic patch without original comparison.

## Next decisive experiment
Acquire pinned ZIP2 source and actual same-export material manifest using existing staged artifacts. Run existing scripts/t3_material_texture_binding_audit.py, t3_material_shader_binding_audit.py, t3_particle_material_chain_audit.py on identical source/export boundaries; join renderer -> material GUID -> shader GUID -> texture GUID; emit aggregate counts and hashed IDs only. Compare suspect smoke renderer blend/ZWrite/alpha/keyword states with image evidence. Verify missing external refs against full package tree, not partial root. Run existing unit workflow only if no equivalent active run; no Unity build initiated.

## Coordination
T4 owns physical mouse, T5 Resolution/buttons/build; T1/T2 water. No shared source or CI modified. Work scope: work/T3-20261111T1731Z-T3-scheduled-texenv-parser-r6m2.md. No new readiness claims. No old sessions overwritten.
