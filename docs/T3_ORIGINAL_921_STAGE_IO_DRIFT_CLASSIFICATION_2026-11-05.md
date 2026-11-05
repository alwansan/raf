# T3 — authenticated original 921-use Shader48 SPIR-V I/O drift, inputs versus outputs

**Date:** 5 November 2026. **Owner:** T3, origin=chat, session `20261105T1542Z-T3-chat-io-drift-integration-a6d9`. **Issue:** RENDER-002 remains **OPEN**. This is a source-private CPU shader translation/reflection classification, **not a Unity ShaderLab patch, Android GPU acceptance, or an owner-confirmed graphics repair**.

## Why this was a distinct test

[Prior authentic CI42052605123](https://github.com/alwansan/raf/actions/runs/42052605123) proved one true DXBC vertex/fragment program pair from each of four original Passes of the original Shader48 referenced by **921 scene Renderer Material slots** could translate to Vulkan1.1-valid SPIR-V, derive HLSL and recompile valid roundtrip SPIR-V. All eight stage numeric resource binding dictionaries matched; original source and roundtrip vertex/fragment interfaces were each internally compatible in all four Passes. However, **0/8 per-stage I/O location/type arrays were byte-for-byte structurally equal**. That comparison alone did not identify why.

Scheduled T3 session `20261105T1526Z-T3-scheduled-iosem-6c42` created `scripts/t3_stage_io_drift.py` and `tests/test_t3_stage_io_drift.py` with privacy-safe set/multiset-based classifier. This chat **reused** the classifier instead of making a duplicate, adding a guarded opt-in `--classify-io-drift` to `scripts/t3_original_top_shader_fourpass_translation.py`. The opt-in validates **all 8 actual original-vs-roundtrip stage reflection pairs** before declaring success and publishes only safe numeric totals. It rejects arbitrary keys, booleans disguised as integer counters, malformed reflection, and partial classification. Default legacy mode/status remains unchanged.

Source lineage: original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, six SHA-pinned original scene files, four original Shader/Material serialized owners with exact byte/SHA checks (269,007,288 owner bytes), and genuine source graph `Renderer→Material→Shader48`. The selected highest-use 921-original-slot Shader has one source SubShader and four normal Passes; exactly one genuine original matched DXBC V/F permutation pair per Pass is sampled (four pairs/eight stages). The other **29** matched source pairs of the **33** total original pairs and **eight unpaired original vertex records** remain unprocessed here. Neither the source Shader author name nor any Unity Shader GUID or original compiled program bytes are published.

## Verified actual source result

[GitHub Actions CI42058881426](https://github.com/alwansan/raf/actions/runs/42058881426) **SUCCESS**, original-source job `classify-real-source-SPIRV-roundtrip-io`. The source-free guard passed **71 tests**: five scheduled T3 classifier controls, twenty integrated T3 translator controls, twelve prior original Shader48 linkage controls, twelve original Renderer graph controls and twenty-two inherited B03 controls. The true source test then compiled the eight stages through real `vkd3d-compiler` → `spirv-val` → `spirv-cross --hlsl` → `glslangValidator` → `spirv-val`, and used the real SPIR-V reflections. Numeric-only artifact `t3-authentic-original-921-stage-IO-drift-42058881426`, artifact id `13429604578`; original D3D11, SPIR-V, generated HLSL, stage paths, original Shader names, GUIDs and per-program hashes were not uploaded.

| Source-vs-roundtrip real I/O category | Stage inputs | Stage outputs |
|---|---:|---:|
| Stage reflection comparisons performed | 8 | 8 |
| Stages with identical location/type lists | **0** | **4** |
| Total original interface locations, summed across stages | **34** | **29** |
| Total roundtrip interface locations, summed across stages | **34** | **29** |
| Original locations no longer present at the same stage and side | **8** | **4** |
| New locations in the roundtrip at that stage and side | **8** | **4** |
| Original-vs-roundtrip type **multiset** equal, ignoring locations | **8/8** | **8/8** |
| Stages with relocation candidate (lists different, same type multiset) | **8/8** | **4/8** |
| Differences of type at still-shared numeric locations (aggregate) | **3** | **5** |

All **eight** stage translations still produced valid Vulkan1.1 SPIR-V and derivative HLSL roundtrip. All four vertex/fragment source pairs remained structurally compatible, as did all four roundtrip pairs. All **eight** original↔roundtrip numeric resource binding slot dictionaries matched. The I/O classifier's total `same_location_type_changes` counts above are consistent with **values being reallocated to different numeric locations**: they do **not** contradict 8/8 full type-multiset equality. The checker does not prove which original semantic maps to which new location.

**Evidence-supported interpretation:** the entire counted discrepancy is **compatible with numeric location relocation/reordering while preserving type multiplicities and total declared slot count**. Input location remapping candidates occur for **8/8** source stages; output remapping candidates for **4/8**. This is narrower than a generic "all I/O broken" conclusion. But it is not sufficient to conclude an unchanged vertex attribute binding, semantic correspondence, interpolation, builtin treatment, matrices, normal vectors, textures, actual ABI or pixels. Full original-program execution or image equivalence remains **unknown**.

The earlier temporary synthetic [CI42058541334](https://github.com/alwansan/raf/actions/runs/42058541334) failed solely because its fixture expected four added slots where a location move counts one addition *and* one removal across Vertex/Fragment. [CI42058710660](https://github.com/alwansan/raf/actions/runs/42058710660) **SUCCESS** after the synthetic expected-count correction; source original run CI42058881426 then passed. The final heavy original workflow `.github/workflows/raft-t3-original-921-io-drift-classification.yml` was made **manual-only** after successful verification to prevent repetitive ZIP2/source-stage runs.

## Required next engineering check before any Unity shader installation

Investigate mapping of real original DXBC input/output signature semantics to roundtrip SPIR-V builtin/Location decorations **within the disposable private source runner**. Unlike type-set equality, that check must verify semantic names/indices, location and component mapping, interpolation qualifiers, matrix/input packing and vertex attributes without releasing program identifiers. Separately verify per-Pass original render states, all material keywords, original constant buffer offsets, texture/sampler binding semantics and eight unmatched Vertex permutations. Only then stage an authenticated ShaderLab solution under original exported Shader GUID and test with actual Unity 2021 Vulkan/Android and on-device graphics. Do not patch ShaderLab with dummy fallback, declare full original HLSL recovered, or interpret SPIR-V validator success as Android fidelity.

**Unchanged:** no game shaders, textures, scenes, prefabs, `.meta`, GUID, `.rgd`, audio, Settings or touch files edited. Existing separate T1 FFT, T2 Foam, T4 world/save and T5 native build workflows were not modified or canceled. T5 full native [CI42052375742](https://github.com/alwansan/raf/actions/runs/42052375742) ended **failure** separately and is not repaired by this source-only evidence. **RENDER-002 OPEN / NOT_READY 0/3**.
