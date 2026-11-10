# T2 scheduled checkpoint — 20261110T0921Z-T2-scheduled-operand-evidence-k8p4

- origin: scheduled
- date_utc: 2026-11-10T09:21Z
- branch: feature/android-native-port only
- resumed_from: prompt/coordination/clients/T2/state.json (last indexed 20261108T1956Z-T2-chat-pass1-source-kind-4d6a); latest prior scheduled strict-gate commit 4fc93a3 and tests aa658ea.
- device anchor: docs/DEVICE_FEEDBACK_42058825739_AR.md, source e9c358eda01785b65e4eb14f18723da426635628, owner world save/reopen succeeded from artifact; packaging release failed. 2026-11-08 owner report confirms click/wheel failure, water and effects still broken.
- baseline files read: AGENTS.md, docs/CURRENT_OWNER_REQUIREMENTS.md, prompt/STATUS.md, T_TEAM/CHAT_AND_SCHEDULE_AR.md, PROMPT_AR.md, OPERATING_MODEL_AR.md, T2 state/MEMORY, scripts/t2_foam_rhs_origin_guard.py.
- work: prompt/coordination/work/WATER-001/T2-20261110T0921Z-T2-scheduled-operand-evidence-k8p4.json; commit 6e05d1576a1cf3acd36ede8a8a8eab24aeeaa8d8.
- hypothesis: OpCode.Name for bare ldloc/ldarg and .s forms does not contain its operand. The pre-existing strict classifier could label an unverified load even when complete_slice=True.
- source-only fix: scripts/t2_foam_original_operand_gate.py, commit 56cbc4a67c708707ac4abaf3b04d720893c43a1d.
- regression tests: tests/test_t2_foam_original_operand_gate.py, commit f7e02736e387879db637f5957cdee38124d1f8a2.
- verification: source files committed and reviewed; no actual Python suite or Mono.Cecil original input run this cycle. No Unity/CI or device test; no shader or shared assets touched.
- limitation: operand_verified is caller-supplied and MUST come from resolved original Mono.Cecil VariableDefinition/ParameterDefinition. It is not proof of object identity. The existing strict gate remains unchanged; new wrapper is opt-in until integrated with original CIL producer.
- next: run `python -m unittest discover -s tests -p 'test_t2_foam_original_operand_gate.py' -v` on immutable SHA; add Mono.Cecil original operand resolution and CFG proof; compare pass1 Texture source with pass0 and actual render-target instance binding; no ShaderLab merge before authentic resource/CB/sampler/state proof.
- coordination: T3 fire/material, T4 physical mouse, T5 resolution/packaging and unified mini-lab remain outside this scoped edit. WATER-001 OPEN; NOT_READY 0/3.
