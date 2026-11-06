# T3 scheduled — 20261106T2133Z-T3-scheduled-contract-schema-9a2f

- origin: scheduled; issue: RENDER-002 OPEN / NOT_READY; Stay in Chat.
- resumed_from_sessions: 20261106T2035Z-T3-scheduled-local-contract-test-f4b2; 20261106T1934Z-T3-scheduled-contract-validation-8c4e.
- base_sha: a1737bd736e276d53df808442cfae3b1eea0d488; scoped reservation commit: 09e6effd201339d269a7701b8d86a83eb8b53de3.
- owner device evidence: docs/DEVICE_FEEDBACK_42058825739_AR.md reviewed; owner-confirmed world/save/re-entry only for Artifact 42058825739, original source e9c358ed. White raft/hand, square smoke and lighting remain open; CL snapshot 520c4cf... contains images and LF logs. The 220911-559 session records 23,884 water pass errors and 3,850 FFT errors, not proof of a Shader48 root cause.
- trial policy and votes reviewed: T3 remains 'لا يحتاج' because no authentic game shader fix was integrated; owner-direct native builds are separate.
- live Actions at initial checkpoint: native build 42296450023 in_progress on a1737bd; do not cancel or duplicate. This cycle did not dispatch CI or Unity.
- hypothesis: DXBC/SPIR-V contract join accepted missing required keys until a KeyError escaped, so corrupt or partial reflection could crash diagnostics rather than fail closed.
- changed scripts/t3_dxbc_spirv_contract_join.py in commit 827f17ee62ac05343ba19dbbe4adb88aa7742647: strict stage-specific required field sets and mapping types, returning invalid_schema before key extraction.
- changed tests/test_t3_dxbc_spirv_contract_join.py in commit 084a3d9d32a5703100d4e2a2ac36bba38b218bce: four new regression cases for missing DX register, missing SPIR-V binding, missing provenance set, and non-dict input.
- validation boundary: source and test cases published, **test execution not yet verified**. Expected suite size 16; requires exact-commit Python unittest / cheap CI. No original Shader48 DXBC, source material, Unity render, Android GPU pixels or device test were run.
- next: execute python3 -m unittest -v tests.test_t3_dxbc_spirv_contract_join on immutable SHA 084a3d9d; inspect Actions without rerunning equivalent jobs. Then use authenticated original Shader48 provenance to compare DXBC RDEF with SPIR-V descriptors, especially two incompatible V/F pairs, before modifying a game shader. Keep T4 physical mouse and T5 resolution/buttons separate.
- status: SOURCE_FIXED_PENDING_TEST; RENDER-002 OPEN; NOT_READY. No .meta/GUID/.rgd, audio, Settings, native request, raw assets or shared memory modified.
