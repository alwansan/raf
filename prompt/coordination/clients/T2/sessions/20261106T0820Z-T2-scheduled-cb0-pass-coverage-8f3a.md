# T2 — scheduled CB0 authenticated pass coverage

- session_id: `20261106T0820Z-T2-scheduled-cb0-pass-coverage-8f3a`; origin: `scheduled`; issue: WATER-001 OPEN.
- resumed_from_sessions: `20261106T0720Z-T2-scheduled-cb0-extent-gate-d4e2`, `20261106T0620Z-T2-scheduled-selective-id-coordinate-4e8b`.
- base_sha: `6f8c3d970756d931056d52a103db52e8407d7c04`; work registration commit `bfe9f58b0c370943a6de088b24e388555921dfb5`.
- Owner phone evidence: `docs/DEVICE_FEEDBACK_42058825739_AR.md`; run 42058825739 artifact world entry/save/reentry confirmed by owner, delivery publication failed. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; 23,884 / 39,132 water pass errors in two sessions. No inference of device water recovery.
- Original Foam selective remap experiment: https://github.com/alwansan/raf/actions/runs/42153150468 (four descriptor class conflicts removed, two CB0 extent mismatches remain).
- Scope: `prompt/coordination/work/WATER-001/20261106T0820Z-T2-scheduled-cb0-pass-coverage-8f3a.json`; experiment key `foam-cb0-pass-coverage-source-gate-v1`.
- New source patch: `415335c109f7079e8966130cb8c8e3683babacaa` adds optional strict bounded expected_pass_count to source-only CB0 gate. Without this, a single authenticated link could produce a positive verdict despite two required original Foam passes. Incomplete evidence now returns blocked_CB0_pass_coverage_mismatch.
- Regression patch: `80baf1c563a069b8fc9a32c1d4f7a273be2dfbed` adds two methods: incomplete vs complete synthetic two-pass evidence, invalid bool/float/out-of-bounds counts. Existing callers unchanged when argument omitted.
- Validation: tests committed, **not executed** in this cycle. No Unity, original shader, GPU, phone, package or new CI evidence. This does not resolve the two CB0 byte mismatches or prove member ABI/upload. No touch, Settings, mouse, resolution, audio, .meta, GUID or .rgd files changed.
- Next: run `python -m unittest tests.test_t2_foam_cb0_extent_gate` on current HEAD; pass independently authenticated original two-pass count to the actual integration caller only when one exists; prove CB0 member offsets and Unity upload, then test ShaderLab. Coordinate T1 FFT and T3 fire/candle/smoke. WATER-001 OPEN.
