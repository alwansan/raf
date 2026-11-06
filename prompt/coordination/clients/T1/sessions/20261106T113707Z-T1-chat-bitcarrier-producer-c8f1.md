# T1 | 20261106T113707Z-T1-chat-bitcarrier-producer-c8f1

- session_id: 20261106T113707Z-T1-chat-bitcarrier-producer-c8f1
- origin: chat
- issue_id: WATER-001
- status: waiting_ci
- resumed_from_sessions: 20261106T113001Z-T1-chat-lane-alias-f73c; 20261106T112050Z-T1-chat-alias-origins-b62f; 20261106T110837Z-T1-scheduled-fft-first-divergence
- base_sha: 2d69ccfcc0b36e7cf6490848899f00955d61bffa
- work_id: prompt/coordination/work/WATER-001/T1-20261106T113707Z-T1-chat-bitcarrier-producer-c8f1.json
- scope_commit: 243b755d2a45223f253bdc7b82f955919efe3d2e
- tool_commit: d525a2773c19bb5a80db08d73e9bff13f6ed8f59
- test_commit: 64d38a85efc4d93b6bb17f36ba5cff1c4e82d3da
- workflow_commit: bba9abcc6d524fa6fe41eec19de14c43fc498862
- experiment_key: water001-original-slot0-butterfly1-y-samecomponent-opbitcast-intcarrier-v1-pin15964ea8
- resource_key: t1-fft-vulkan-roundtrip-isolation-ubuntu24-no-unity

## Restored original evidence

Original SHA-authenticated FFT slot0 private Vulkan CI 42211108743 completed SUCCESS with 15/15 source-level adversarial tests. The Butterfly1 coordinate Y comes from a physical Function-vector lane beyond X/Y, with two CFG may-reaching same-component writers whose opcode families were OpBitcast and OpConstant. This is not numeric parity or a proven original signed-int carrier. Nearby scheduled T1 session 20261106T110837Z wrote a separate coordinate-keyed comparator, no overlap.

## Pre-registered distinct work and changes

Work scope reserved before writes. New source-private typed producer audit `scripts/t1_fft_spirv_scalar_writer_carrier.py` classifies scalar OpBitcast source/destination *types* (signed/unsigned 32-bit bits reused as float versus actual numeric conversion) and constants for only CFG may-reaching component writers. New `tests/test_t1_fft_spirv_scalar_writer_carrier.py` includes source-free adversarial controls; existing isolated `.github/workflows/raft-t1-fft-vulkan-roundtrip-isolation.yml` updated to run tests and analyze SHA-verified original slot0 privately. No original bytes, SPIR-V IDs, numeric constants or pixels may be exposed; only aggregate type categories.

## Evidence and checkpoint

GitHub Actions source workflow update `bba9abcc6d524fa6fe41eec19de14c43fc498862` committed; run reference will be recorded after it appears. No exact-source test outcome asserted before CI. No Unity Editor, native Android full build, original shader rewrite, audio/Settings/touch changes or T2–T5 file changes.

## Next step

Check branch runs for the exact workflow SHA, inspect synthetic test step (13 new controls expected) and original private marker `RAFT_T1_FFT_SCALAR_WRITER_CARRIERS`. If tests fail, repair the minimal fail-closed issue and rerun once after changed input. If success, record source-backed type of Butterfly1 Y OpBitcast immediate source, preserve alternate constant/branch semantics, and hand off numeric parity follow-up. WATER-001 remains OPEN / NOT_READY.
