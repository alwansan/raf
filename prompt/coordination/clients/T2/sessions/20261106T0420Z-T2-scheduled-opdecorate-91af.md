# T2 scheduled — truncated OpDecorate fail-closed guard

- session_id: `20261106T0420Z-T2-scheduled-opdecorate-91af`; origin: `scheduled`; issue: WATER-001; scope: synthetic SPIR-V parser hardening only.
- owner phone baseline: docs/DEVICE_FEEDBACK_42058825739_AR.md, run 42058825739; local-world save/reopen confirmed by owner; water/FFT failures remain. CL pinned 520c4cf409aa20a4db54ff80ed87d8807d9cba57; no new device evidence.
- initial HEAD: `97052b8fcaea32074f9945a1acc7788dc2c285f0`; work plan commit `d5fafe4591dcb4bf5a1f67558e9038fde24c5279`.
- resumed: T2 chat selective descriptor proof 20261106T024715Z and scheduled CB0 checkpoint 20261106T0316Z; original CI 42153150468 passed 71 tests, 4 type collisions eliminated, 2 CB0 extent mismatches remain. No repeat of original CI.
- new finding: scan_binary_decorations previously ignored SPIR-V OpDecorate instructions whose word count was 1 or 2 (valid instruction boundaries but invalid decoration arity). Fail closed before reading decoration type, rather than silently skipping them. This does not change valid SPIR-V semantics.
- source commit: `6579cc33ea6187d6443945a95f5c1bc87b54feae`; test commit: `9a14e9634316cf31dbfaef3f3ef39ea2bd9b5e61`. New source-free regression covers word counts 1 and 2. **Test not executed yet**; neither CI nor Unity/device validation claimed.
- no shader, GUID, .meta, scenes, FMOD, Settings, input or packaging edits. T3 retains effects; T4 physical mouse; T5 Resolution and three buttons.
- next: run `python -m unittest tests.test_t2_foam_private_descriptor_set_remap` in a checkout at or after test commit; then independently inspect original private CB0 member offset/type/upload proof before integrating Foam ShaderLab. WATER-001 OPEN; NOT_READY.
