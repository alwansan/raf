# T4 isolated LOCAL-005 — FileManager declaration-shape classification

- identity: T4; status: paused_identity_conflict; session_id: 20261105T0635Z-T4-filemanager-signature-classification
- resumed_from_session: 20261105T0543Z-T4-automation-native-candidate-gate
- baseline_sha: 07f74328bb13e361a8b2fe530e36e61cf7202e56
- taken_over_from: T4 20261104T2357Z-T4-lw01, independent 20261105T0024Z-T4-filemanager-restore01; B07/B14/B19/B24/B37/B50 evidence remains attributed to its authors.
- safety: state.json still active for 20261104T2357Z-T4-lw01; no state/MEMORY changes, no old session overwritten.

## Live checkpoint and plan before work
Read T_TEAM PROMPT/README/RESTORE, AGENTS, owner requirements, prompt README/CONTINUE/STATUS, T_TEAM operating model, legacy handoff, sources, migration, templates, current T4 state, latest isolated session, FileManager report, parser and controls. GitHub branch HEAD at baseline. Latest true Raft release remains APK86 from 41812889049, not LogRaft releases. Latest returned Actions runs are completed; T1 private FFT Unity boundary failed 41978496060, runner guard passed 41978496046. No native device evidence.

## Distinct engineering hypothesis
Existing `scripts/t4_original_rgd_load_contract.py::METHOD` recognizes a single-line block-bodied method with a restricted return type and optional simple `where` constraint. `scripts/t4_original_filemanager_contract.py` uses it to infer FileManager target existence, but original CI41942655373 found exactly one call-like token and no parsed target. A safe next step is to classify *declaration-shape candidates* separately from call sites, without assuming a candidate is callable or changing production adapter. Implement an isolated privacy-safe classifier with synthetic adversarial controls; only authenticated original CI can determine which category applies to actual FileManager.

## Guardrails
Do not publish original source/names; do not patch runtime FileManager, .rgd schema, Steam guards, .meta, sound, Settings or touch. No heavy Unity job or other Actions cancellation. Keep source SHA gates. Result remains NOT_READY 0/3 until integrated Unity/phone create/save/relaunch/reopen.

## Implemented checkpoint
- Added isolated source-only diagnostic `scripts/t4_filemanager_declaration_shapes.py` at commit `c3919ed499d17452184ac57ef97a6ab3546b9c0d`; it distinguishes candidate block/expression declarations, unresolved declarations and call-like tokens, with no original source printed. It deliberately does **not** resolve the actual private original method, nor prove runtime callability.
- Added eight synthetic tests `tests/test_t4_filemanager_declaration_shapes.py` at commit `b133e4d424f491d43ec12c87af93fa9742bb6ea3`. Tests have **not** been executed in this run; no CI or phone claim. The diagnostic needs authenticated original SHA-pinned FileManager input in private staging and validation against real decompiler syntax before any production integration.
- Existing `METHOD` regex was independently checked on local synthetic cases: block one-line recognized, expression-bodied and newline-before-name and nested-generic-return not recognized. This establishes a parser coverage limitation, **not** which shape original FileManager uses. No runtime files modified.
- Next: run synthetic tests, correct any false positives, then integrate read-only classifier into bounded original SHA-pinned workflow; only after private original evidence consider a save-path runtime change. Avoid duplicate Unity build with T5. LOCAL-005 OPEN / NOT_READY 0/3.
