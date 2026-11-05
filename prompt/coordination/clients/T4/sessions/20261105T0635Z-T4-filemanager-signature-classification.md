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
