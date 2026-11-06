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

## Verified evidence — completed

- First source-free test run [42211872487](https://github.com/alwansan/raf/actions/runs/42211872487) @ `bba9abcc`: FAIL **before original data recovery** because three synthetic bitcarrier test fixtures reused `%b` as an OpBitcast writer and an OpImageFetch result. The SPIR-V verifier properly rejected duplicate result IDs; no original numerical result from this run. Fixed only fixture IDs in test commit `08483339e19514681fe81be9c8c0babaa3f7c574`.
- Exact corrected run [42212055131](https://github.com/alwansan/raf/actions/runs/42212055131) @ `a9fe62d73adbb90555599dd50120dc6cc3dd1fd8`: **SUCCESS**, job `127872831426`, 13/13 new tests PASS, original ZIP2 source recovery / SPIR-V private slot0 audit / same-Vulkan roundtrip / cleanup all PASSED.
- **Source-authentic original butterfly site1 coordinate Y**: two bounded may-reaching component writer candidates, `sint32_bits_to_float32` and `float32_constant`, one each. This is a **signed 32-bit integer bit-pattern interpreted as float**, not a numeric int→float conversion, on the bitcarrier writer. The other candidate is a float constant. All X sites still originate from one whole-vector writer each.
- **Butterfly site2 Y**: one `float32_constant` same-component may-reaching writer. Source site0 X/Y: one whole-vector may-reaching writer each. Source pin: `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385`, authenticated in original private recovery, no original game bytes/SSA IDs or bit patterns published.
- **Crucial limits:** the two butterfly site1 Y writers remain *may* reach, not selected per actual invocation. Whether Unity/SPIRV-Cross/glslang preserves the bit pattern through translation, authored FindKernel identity, Vulkan↔Unity pixel parity and Android Adreno water are **not proven**. `original_integer_coordinate_semantics_proven=false`. WATER-001 OPEN.
- Evidence JSON: `prompt/coordination/experiments/T1/20261106T113707Z-T1-chat-bitcarrier-producer-c8f1.json`. Canonical event: `prompt/coordination/B_TEAM/events/T1/20261106T113707Z-T1-chat-bitcarrier-producer-c8f1.json`. Only T1 script, new test and isolated T1 workflow changed; no shader/game assets, audio, Settings, touch, T2–T5 files, native Android Actions or other agents altered.

## Status and next engineering step

- origin: chat
- status: completed (scoped typed bitcarrier provenance)
- run_urls: https://github.com/alwansan/raf/actions/runs/42211872487 ; https://github.com/alwansan/raf/actions/runs/42212055131
- next_step: Analyze **original butterfly site1 Y branch/loop predicate** distinguishing the signed-int bitcarrier write from the float-constant write; isolate actual private dispatch input choice without publishing literal values. Then perform a controlled same-input paired original Vulkan↔Unity test of translated coordinate addressing; only patch shader lowering if evidence demonstrates a specific failure, followed by Adreno/phone validation. Preserve previous positive source and negative numeric CI separately.
