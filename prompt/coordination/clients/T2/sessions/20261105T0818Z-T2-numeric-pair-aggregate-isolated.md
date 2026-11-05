# T2 isolated engineering session 20261105T0818Z-T2-numeric-pair-aggregate-isolated

- Identity: T2; status: paused_identity_conflict (shared state/MEMORY not overwritten).
- resumed_from_session: 20261105T0523Z-T2-stage-scope-isolated (previous conversation checkpoint, not independently verified in repository).
- baseline_sha: 9b744fd289ed856bce5ae3fc02d9aeed083c9b78 (branch read at 2026-11-05 08:18Z).
- taken_over_from: B20 Foam CB evidence, B45 Blur staging, B17 Spectrum; attribution retained.
- hypothesis: current Foam source descriptor audit loses numeric (m_Index,m_SamplerIndex) values after validating them, preventing a safe original-pair ambiguity census; duplicate source pairs must not be mistaken for source→SPIR-V identity.
- change: scripts/t2_foam_texture_identity.py now privately retains source numeric pairs and reports only complete/distinct pair counts and SHA256 digest; explicit numeric_pair_identity_to_spirv_verified=false. No private names/values in report. Commit 20fff14ea0f2e95b528c262c8af99e31247d316f.
- evidence level: source edit only; original private ZIP2, Unity compile, GPU and device NOT run. Existing authenticated source evidence CI41941354379 and CI41958159556 are historical, not rerun.
- rejected hypothesis: equal counts and literal symbol names imply numeric texture→sampler linkage. Neither is proven.
- next_step: add adversarial unit tests for duplicate pairs/missing fields, run original SHA-pinned audit with no raw disclosure; then investigate DXBC t/s→SPIR-V set/binding translation semantics. WATER-001 OPEN, NOT_READY 0/3. No touch, audio, Settings or .meta changes.
