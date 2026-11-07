# T2 — fail-closed duplicate JSON keys in Foam role gate

- session_id: 20261107T2023Z-T2-scheduled-role-json-duplicate-8d31
- origin: scheduled
- issue_id: WATER-001; status: completed (scoped report hardening only)
- baseline HEAD: 2ef5b6213802ba7c48ffd973fc3357e6fece3d88
- owner device: docs/DEVICE_FEEDBACK_42058825739_AR.md (world entered/saved/re-entered from 42058825739 artifact; water pass/FFT errors remain)
- scope registration commit: fdca95afc5324ef5ec64662055e2afab552dab2e
- implementation commit: da7ac14e0e5ad59a7149e782f37ee6b2f15e70c4
- regression commit: c4c59046b7495415a26aaf7a24eda025183251a4
- touched: scripts/t2_foam_pass_role_gate.py and tests/test_t2_foam_pass_role_duplicate_json.py; no original IL, ShaderLab, native request, T3, T4 or T5 source touched.
- hypothesis/result: JSON decoder default silently keeps the last duplicate field, permitting misleading source/pass evidence. CLI now calls json.load(..., object_pairs_hook=unique_keys), rejects duplicate members at every nesting level before validate. Four source-free tests added for valid pass roles, duplicated source, duplicated pass, duplicated top-level sites.
- tests: NOT EXECUTED in this run; no claim of passing tests or source/Unity/device acceptance.
- coordination: T2 chat original Foam producer report remains separate; its authenticated per-site evidence supersedes older synthetic global aggregate. Avoid touching its C# parser and workflow.
- evidence limits: this protects one CLI entry point only. Python direct validate(dict) cannot detect duplicate keys already discarded by a caller. WATER-001 remains OPEN; CB0/ShaderLab/runtime water not proved.
- next_step: run python -m unittest tests.test_t2_foam_pass_role_duplicate_json from exact Git checkout, then ensure every consumer of the role gate invokes strict JSON parsing. Continue original pass1 producer analysis privately and coordinate with T3 fire/smoke; no redundant native build.
