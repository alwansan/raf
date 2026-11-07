# T2 — bounded IL metadata index hardening

- session_id: 20261107T0923Z-T2-scheduled-il-index-bounds-k7p2
- origin: scheduled
- base_sha: 3b95730f006c816b70c2dcd96c90eddf7c9f2442
- resumed_from_sessions: 20261107T0824Z-T2-scheduled-arg-type-consistency-d6e2; 20261107T2227Z-T2-chat-blit-texture-role-6c52
- owner feedback: docs/DEVICE_FEEDBACK_42058825739_AR.md; phone artifact 42058825739 world entry/save/re-entry confirmed, packaging publish failed; water pass and FFT errors remain.
- work: prompt/coordination/work/WATER-001/20261107T0923Z-T2-scheduled-il-index-bounds-k7p2.json; scope recorded in commit 93063edf5ab150bdca0da958386a74e92c9bab29 before editing.
- hypothesis: synthetic bounded IL provenance allowed argument/local indices above CLI 16-bit metadata limit, potentially constructing unsupported origins and accepting invalid synthetic provenance.
- source fix: scripts/t2_pass1_stack_provenance.py, commit 45ca3870635fde3fa40d5ebd8f4cad5819b4d9a4. Reject indices above 65535 for ldarg/stloc/ldloc, retain 65535 boundary.
- tests added: tests/test_t2_pass1_stack_provenance.py, commit 2737a2f3432759c0b1961ed7531108b75443c240. Positive max-index and negative over-limit cases.
- validation: static review only. Exact repository test suite NOT executed; no CI triggered or dispatched, no claim of passing tests. New code is a synthetic guard, not a Mono.Cecil/original-game parser.
- actions snapshot: T3 42333961072 success; T2 original 42308583977 success; T2 evidence summary 42308935364 failure. No equivalent native run duplicated.
- integration limits: no ShaderLab/game assets/.meta/GUID/.rgd/audio/Settings/touch changed; no Android/Unity rendering proof. WATER-001 OPEN.
- next_step: execute exact repository unittest suite and inspect any failure; then attach bounded provenance to authenticated Mono.Cecil pass1 producer evidence with fail-closed ambiguity, coordinate T1/T3 for FFT and particle FX.
