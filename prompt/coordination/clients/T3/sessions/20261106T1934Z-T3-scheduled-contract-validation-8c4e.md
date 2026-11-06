# T3 scheduled — 20261106T1934Z-T3-scheduled-contract-validation-8c4e

- origin: scheduled; owner: T3; issue: RENDER-002 OPEN / NOT_READY.
- baseline HEAD: cba461ecd1aebeb3a2e1bb67547ffa573c40d505.
- scope: prompt/coordination/work/RENDER-002/20261106T1934Z-T3-scheduled-contract-validation-8c4e.json; scope commit df33ab85e7e115289b0ac3874ecd4984d524489a.
- source fix: b7907d5929c2bc298a9bc45754dbe588fea3140d; regression fixtures: 4d5fb6ed543a7467b2678fe4b6a5965b18cf67ae.
- resumed from scheduled 20261106T1828Z-T3-scheduled-contract-fixture-b6e1; chat 20261106T191751Z-T3-chat-spv-opname-b71e (different files).

## Owner device evidence

Read docs/DEVICE_FEEDBACK_42058825739_AR.md: original 42058825739 phone world entry/save/reentry success, release upload failure. Menu/raft/hand white, square smoke, missing light/FX remain OPEN. No new phone test. T4 mouse and T5 Resolution/buttons are independent. Existing Shader48 remains Dummy and material identity does not establish particle-smoke causality.

## Concrete defect and change

The source-free DXBC/SPIR-V contract checker accepted Python bool as int for resource array spans, and allowed negative, boolean or fractional register/set/binding coordinates. Thus an invalid synthetic provenance row could produce no validation error or misleading downstream error. Added strict nonnegative integer checks (excluding bool) for resource coordinates and strictly positive integer spans; five regressions cover invalid DX register, SPV binding, provenance set/register and boolean array count. No original shader assets, raw bytes, .meta, GUID, .rgd, Settings or FMOD changed.

## Verification and limitations

Published source and tests to feature/android-native-port. **Tests have not been executed**: Python local runtime lacks repository checkout/network; no equivalent CI dispatch initiated. Next: run `python3 -m unittest tests.test_t3_dxbc_spirv_contract_join` in a checked-out CI environment and check expected 12/12; only then advance to SHA-pinned original Shader48 per-stage DXBC↔SPIR-V resource provenance, where missing mapping must remain unproven. This fix is a source validation guard, not recovered ShaderLab, smoke, water, white surfaces, or a device-ready render fix. No new trial APK vote; T3 remains «لا يحتاج» in trial-20261106-r1.

## Status

SOURCE_FIXED_PENDING_TEST; RENDER-002 OPEN; NOT_READY. No native build, no Action cancellation or duplicate. Stay in Chat respected.
