# T3 chat — source-free validation of scheduled DXBC/SPV contract and manual SHA-original candidate workflow

- **session_id:** `20261106T193502Z-T3-chat-original-candidate-gate-d41f`; **origin:** `chat`; owner T3; issue **RENDER-002 OPEN / NOT_READY**.
- **base SHA:** `3bc7c96a42b566f302417dde91193baab691f6ad` (initial check). Scope reserved **before edits** at `prompt/coordination/work/RENDER-002/20261106T193502Z-T3-chat-original-candidate-gate-d41f.json`, commit `db98e5ba743518eb2b18ffcf7e31b62543bc778a`.
- **resumed_from:** latest source-only chat `20261106T191751Z-T3-chat-spv-opname-b71e`; chat original stage count `20261106T190315Z-T3-chat-stage-cardinality-e6a2`; **newer scheduled T3** `20261106T1934Z-T3-scheduled-contract-validation-8c4e`. Scheduled T3 had source-fix `b7907d5929c2bc298a9bc45754dbe588fea3140d` and five negative tests `4d5fb6ed543a7467b2678fe4b6a5965b18cf67ae`, but explicitly had **not run tests** and marked `SOURCE_FIXED_PENDING_TEST`.
- **experiment_key:** `T3-ZIP2-SHA15964-Particle108-eightstage-SPV-debug-resource-candidates-manual-gated-v1`; **resource_key:** `manual-only-zip2-15964-original-4-owners-6-scenes-no-active-source-staging`. No original source/Unity GPU workflow launched.
- Branch **feature/android-native-port** only, no force/push to other branches. Parallel T1/T2/T4/T5 work and recent active Actions checked. No cancellation/overwrite of another agent's script, shader or workflow.

## Why this is needed

Original SHA-authentic [42274933802](https://github.com/alwansan/raf/actions/runs/42274933802) checked 4 Particle108 keyword VSFS pairs / 8 original DXBC stages: CB24/SRV10/sampler10 original DCL versus SPV UBO24/separate image10/separate sampler10 **globally**. It does **not** prove stage-local numerical parity or actual D3D source register to Vulkan descriptor provenance.

The earlier T3 chat introduced a strict `OpName` and typed decoration candidate parser and original-source adapter with [CI42279422349](https://github.com/alwansan/raf/actions/runs/42279422349) **29/29 synthetic**; no actual original SPV program processed yet. `OpName` is optional, forgeable debug metadata. VKD3D documents an optional explicit `vkd3d_shader_interface_info` binding map; otherwise default mappings may allocate sequential descriptor bindings in set 0, making `register==binding` invalid as a premise. Public reference: `vkd3d_shader_interface_info` documentation (ReactOS/Wine vkd3d_shader.h). A count or matching debug label is never a proof of correct resource data, colors, smoke, or phone pixels.

## New CI engineering — two independent workflows

1. **Manual-only authenticated-original experiment:** `.github/workflows/raft-t3-particle108-spv-named-original-manual.yml`, commit [95d401fe](https://github.com/alwansan/raf/commit/95d401fe6e6408c3c07789b13c9f8dfa1354c0bc). Reuses an already demonstrated original-stage workflow structure; `workflow_dispatch` ONLY, `cancel-in-progress:false`, max 24-minute job, source code `feature/android-native-port`, source original ZIP2 SHA **15964ea8f246b6e076ce26b60931ee2e1a9a2385**, four original owner files plus six scenes SHA authenticated, strict 269007288 owner bytes. UnityPy pinned 1.23.0; Ubuntu24.04 apt vkd3d-compiler/spirv-tools/spirv-cross/glslang-tools pinned to available package sources and `dpkg-query -W` logged. Runs:
    - both source-free test suites and Python syntax;
    - `t3_particle108_dcl_spv_family_census` on **same original 4 keyword pairs, 8 stages** with source DCL CB24/SRV10/sampler10/UAV0 and per-stage cardinality count gates (accept real mismatch as diagnostic evidence, do not hide it);
    - `t3_particle108_spv_named_original_probe` on SHA-authentic original VS/FS stages using ephemeral translated SPIR-V files; output only anonymized candidate counts and explicitly false provenance and phone flags;
    - uploads only two safe JSON reports, retention 7 days, never raw game asset, source shader bytes, intermediate SPIR-V, private HLSL, original shader paths/names, GUID, shader resource IDs, D3D register or VK set/binding.
   **NOT DISPATCHED**. New script's real original data behavior is **unverified**; absence of explicit debug names is a valid informative outcome, not reason to invent mapping.
2. **Lightweight independent source-only CI:** `.github/workflows/raft-t3-shader-candidate-source-only.yml`, commit [a1b6be9f](https://github.com/alwansan/raf/commit/a1b6be9f1d4109ab144f754be00a74c7a44682fd). Push triggers limited to T3 checker/adapter, scheduled contract script/tests and the two workflow files; `cancel-in-progress:false`, 6-minute job, no original source, Unity or LFS. Compiles Python and runs both suites.

## Terminal test evidence

[**GitHub Actions 42281080458 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42281080458), execution SHA `a1b6be9f1d4109ab144f754be00a74c7a44682fd`, job `128109880556`:
- T3 SPIR-V candidate + original-stage resource count synthetic suite: **29/29 PASS**.
- **Newly validated scheduled T3 exact DXBC/SPIR-V provenance checker** (previous session `1934Z` pending execution): **12/12 PASS**, including strict reject bool counts and invalid negative/fractional resource locations.
- Python syntax test for both codepaths: **PASS**. Total **41/41 tests**. This CI establishes only source-free implementation validity; not an authenticated original DXBC-to-SPIRV binding, Unity ShaderLab compile or Adreno pixel acceptance.
- Scheduled T3's source and tests, work status, and session file **NOT edited**; next scheduled worker can cite run42281080458 to close its `SOURCE_FIXED_PENDING_TEST` state. CI is a synthetic complement, not a takeover.

## Handoff

Current original Shader48 still `DummyShaderTextExporter` under the selected real source export, and colors/fire/smoke remain OPEN. Do not count this source-free CI as a new renderer fix. User phone play/save/reentry was previously proven only for Artifact [42058825739](https://github.com/alwansan/raf/actions/runs/42058825739); original white material and FX issues remain.

**Next step with authorized GitHub workflow dispatch**: check live HEAD and running jobs then manually run `raft-t3-particle108-spv-named-original-manual.yml` exactly once with ZIP2 source PIN; first inspect stage-by-stage family count drift, then whether typed `OpName` candidates appear at all. Even 8/8 candidates is **not authoritative provenance**, because VKD3D may remap resources. Do not use defaults, GUID replacements, dummy shader passes, source private values, numeric matching, or false flags to fake readiness. For real shader restoration, implement trustworthy mapping via pinned shader compiler interface/descriptor mapping and compile genuine four-pair ShaderLab in Unity then device/Adreno pixel validation.

- Files touched: ONLY two new `.github/workflows/` files and this session/work/experiment/event.
- No Unity shader, scene, material, .meta, Steam/Internet, FMOD, Settings, .rgd, OBB, APK or touch/control layout changed.
- **Vote T3:** «لا يحتاج», `trial-20261106-r1`; no substantive renderer integration for new phone APK. T5 retains native build authority and 5/5 consensus.
- **Status:** scope completed_sourceonly; original SHA-authenticated workflow ready but unrun; RENDER-002 OPEN/NOT_READY.
