# T3 chat — SHA-original Particle108 SPIR-V OpName/debug-binding candidates

- **session_id:** `20261106T191751Z-T3-chat-spv-opname-b71e`
- **origin:** `chat`; **owner:** T3; **issue:** `RENDER-002` **OPEN / NOT_READY**.
- **base_sha:** `ce2c1ae43b50d6994605a14e11f5bf78492b0b11`; first scope reservation `prompt/coordination/work/RENDER-002/20261106T191751Z-T3-chat-spv-opname-b71e.json` published in commit `7ade75774368548d68a9b3d0ae0e18cc4ef1f1a4`.
- **resumed_from:** `20261106T190315Z-T3-chat-stage-cardinality-e6a2`, `20261106T185041Z-T3-chat-dcl-spv-family-census-a91d`, and independent `20261106T1828Z-T3-scheduled-contract-fixture-b6e1`. Scheduled T3's `t3_dxbc_spirv_contract_join.py` untouched.
- **experiment_key:** `T3-PARTICLE108-SPIRV-VKD3D-OpName-DXBC-source-DCL-debug-candidate-contract-v1`; **shared_resource:** synthetic-SPIRV only, no original ZIP2/Unity CI dispatched.

## Evidence-based question

Earlier SHA-pinned original run [CI42274933802](https://github.com/alwansan/raf/actions/runs/42274933802) confirmed 4 original keyword VS/FS pairs, 8 stages, original DCL CB24/SRV10/Sampler10 against VKD3D-translated SPIR-V UBO24/separate_image10/separate_sampler10 **in aggregate**. Earlier follow-up added **per-stage** cardinality counters with [CI42276510557](https://github.com/alwansan/raf/actions/runs/42276510557) source-only 14/14, but original run for those new counters is still pending. Source-original Shader48 remains exported as **DummyShaderTextExporter**. Equal counts alone cannot prove which D3D register corresponds to which Vulkan descriptor set/binding.

Vulkan SPIR-V may contain debug `OpName` labels such as `cb2`, `t3`, `s1`, associated with resource variables and `DescriptorSet` / `Binding` decorations. Such labels are **untrusted, optional, forgeable and often stripped**. Their presence could yield **only candidate correspondences**; even a perfectly matching label set is **not** proof of actual DXBC-source-to-SPIR-V-Vulkan binding semantics, shader numeric equivalence or device pixels. No numeric identity / guesses used to infer mappings.

## Implemented engineering

- New `scripts/t3_particle108_spirv_opname_candidates.py` [e836f3ed](https://github.com/alwansan/raf/commit/e836f3ed10855110ca53a78160879f00d0424aa8), bounded binary SPIR-V 1.0–1.6 parser (8 MiB cap), exact `OpEntryPoint` stage, `OpName`, `OpDecorate` `DescriptorSet`/ `Binding`, `OpTypePointer`, `OpVariable`, struct/image/sampler/storage categories. Strict var storage/pointee family validation. Incomplete or conflicting/duplicate typed debug-name candidates never pass all-coverage boolean. Unsupported descriptor arrays/combined image-samplers are not interpreted as individual original register mappings. Public result contains **only counts and false proof flags**; no original resource names/numbers, Vulkan descriptor sets/bindings, SPV IDs, bytecode, or per-stage identifiers.
- Header version parser initially read SPIR-V minor version from bits 0–15 instead of bits 8–15, producing `T3_SPIRV_HEADER` on valid 1.3 synthetic modules. Corrected [2506049d](https://github.com/alwansan/raf/commit/2506049d07ff351eb6a83d0e24bfd122ab82fa24), with explicit valid 1.3 / reject unknown 1.7 regression in test commit [d00887f1](https://github.com/alwansan/raf/commit/d00887f1f03f964ec7bf9c19bbabdc1f48c27bc3).
- New `scripts/t3_particle108_spv_named_original_probe.py` [427844c5](https://github.com/alwansan/raf/commit/427844c59cb2de4e05edf6742638c73ced7e970a): private runner uses the pre-existing genuine-source six scene/four original shader owner SHA pins; selects the unique original 108 particle Renderer Material-slot Shader48 and original four keyword VS/FS DXBC pairs, uses VKD3D compilation + `spirv-val` and checked stage SPV `original.spv` from each of 8 disposable temporary directories. Calls debug-name candidate parser privately; emits only summary counts and **never claims descriptor provenance or ShaderLab/Android pixels**. The authentic-source `probe` itself has **NOT** been run this cycle.
- Added 15 synthetic regressions to `tests/test_t3_particle108_dcl_spv_family_census.py` across [5aecd7c7](https://github.com/alwansan/raf/commit/5aecd7c71f9044cfeb1577d4df919d974e10dd4d), [d00887f1](https://github.com/alwansan/raf/commit/d00887f1f03f964ec7bf9c19bbabdc1f48c27bc3), and [c37e07a5](https://github.com/alwansan/raf/commit/c37e07a5566a4eebe3767115eb37bd7cac893f57): source-free 14 old + 12 SPV binary name/type/decoration checks + 3 adapter VSFS stage/keyword checks. Cases include missing/forged debug labels, stage mismatch, unsupported pointer types or arrays, duplicate binding targets and decorations, truncated instruction, fake `provenance_proven=true` adapter result, exact four-stage pair count. **No original game bytes present in public fixtures.**

## Terminal CI evidence

- [CI42278854388 FAILED](https://github.com/alwansan/raf/actions/runs/42278854388), job `128102205248`: first new parser read SPIR-V minor from wrong bits; test implementation error, not original Raft SPV.
- [CI42279006117 SUCCESS](https://github.com/alwansan/raf/actions/runs/42279006117), job `128102726757`: **26/26** source-free tests after correcting header.
- [**CI42279422349 SUCCESS**](https://github.com/alwansan/raf/actions/runs/42279422349), job `128104185298`: **29/29** source-free tests including original source adapter synthetic 8-stage and false-provenance controls. Python synthetic tests, not genuine original-shader runs.

## Boundaries and next step

**Original source/shader-recovery outcome: UNVERIFIED.** This cycle did not dispatch original ZIP2 stage compiler/translator job; no original resource names were seen or inspected, and no actual D3D register↔Vulkan set/binding provenance has been established. `OpName` candidate coverage even if found may never be treated as authoritative. T3 source-authenticated previous stage-family global counts remain [42274933802](https://github.com/alwansan/raf/actions/runs/42274933802), and original stage-by-stage counts remain unrun. Existing original workflow is manual-only, and previous attempt to arm it was blocked; no bypass, fresh original export, or duplicate heavy Unity native job.

For next T3 chat/scheduled cycle, recheck live HEAD, work leases, pending Actions, then **if an authorized original-only workflow dispatch is available** first execute updated original source per-stage cardinality check. If no stage count loss, run this new private debug-name candidate script on a single SHA-authentic original source stage to see whether VKD3D even preserves useful `OpName`; never log names, register/set/binding numbers or intermediate shader bytes. Any apparent match needs independent verified compiler provenance (or authoritative descriptor mapping), not numeric equality. Only then integrate non-dummy original four-pair Shader48 into properly referenced ShaderLab and require Unity shader compile plus owner Adreno pixel tests. Preserve all scene/.meta/GUID/.rgd, audio, Settings, touch deferral, and other workers' CI. No APK/OBB/XAPK request and no material game assets changed.

- **RENDER-002:** OPEN / NOT_READY.
- **T3 trial-20261106-r1:** `لا يحتاج` — this is source-only diagnostic engineering, not a new integrated phone-testable render fix.
- **work:** `prompt/coordination/work/RENDER-002/20261106T191751Z-T3-chat-spv-opname-b71e.json`
- **experiment:** `prompt/coordination/experiments/T3/20261106T191751Z-T3-chat-spv-opname-b71e.json`
- **event:** `prompt/coordination/B_TEAM/events/T3/20261106T191751Z-T3-chat-spv-opname-b71e.json`
