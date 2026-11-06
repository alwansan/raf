# T3 scheduled — 20261106T2035Z-T3-scheduled-local-contract-test-f4b2

- origin: scheduled; identity: T3; issue: RENDER-002 OPEN / NOT_READY.
- work scope: [isolated test record](../../../work/RENDER-002/20261106T2035Z-T3-scheduled-local-contract-test-f4b2.json), commit `42e4fe3c15b4d3ba6e9af4a43cb30d732c50e1e3`.
- resume: [previous scheduled validation](20261106T1934Z-T3-scheduled-contract-validation-8c4e.md), source commits `b7907d59` and `4d5fb6ed`.
- inputs: fetched `scripts/t3_dxbc_spirv_contract_join.py` and `tests/test_t3_dxbc_spirv_contract_join.py` from `feature/android-native-port` on 2026-11-06; copied verbatim in logic to isolated local Python test files. No game source, ZIP2, original DXBC or private data downloaded.
- command: `cd /tmp/t3test && python3 -m unittest -v tests.test_t3_dxbc_spirv_contract_join`.
- observed: **12 tests PASS**, `Ran 12 tests in 0.001s / OK`. Tests include nonidentity remap, missing provenance, array spans, stage mismatch, duplicate target, invalid bool/negative/fractional indices. This is local CPython reproduction, **not** GitHub Actions, Unity, native shader translation, original Shader48, or device acceptance.
- owner device report: `docs/DEVICE_FEEDBACK_42058825739_AR.md` read. Artifact 42058825739 had owner-confirmed world/save/reopen; white hand/raft, square smoke, missing lighting remain unresolved. Device logs show 23,884 water pass and 3,850 FFT kernel errors in 220911-559; these are not proof of a particular shader cause.
- trial build: read trial policy and readiness. Owner-direct native run `42281310905` exists at source `d692400115c36c4839fa4f4954e5f6ed1c60d413` per team checkpoint; **live run completion not independently checked in this local test**. Do not launch duplicate build. T3 vote remains `لا يحتاج`; no material/ShaderLab change.
- next: verify latest branch Actions and test job on exact immutable SHA; apply contract join only with explicit original Shader48 DXBC↔SPIR-V provenance, investigate the two incompatible vertex/fragment pairs and material renderer identity before any visual patch. Coordinate with T1/T2 and do not alter T4 mouse or T5 resolution/buttons.
- state: local source regression PASS, original shader fidelity UNKNOWN, RENDER-002 OPEN, full NOT_READY. No original assets, `.meta`, GUID, `.rgd`, Settings, audio or CI workflows changed. Stay in Chat.
