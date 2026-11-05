# T3 — authentic original 921-use Shader48 SPIRV-Cross reflected interface names across HLSL roundtrip

**5 November 2026; worker T3; origin=chat; session `20261105T1607Z-T3-chat-spv-name-location-7c2d`; RENDER-002 OPEN.**

## Distinct question and source

A prior SHA-pinned original Raft six-scene/four-owner run [CI42058881426](https://github.com/alwansan/raf/actions/runs/42058881426) selected the Shader48 used by **921 original Renderer material slots** and proved that **8/8** genuinely linked original D3D11 Vertex/Fragment stage samples produce valid SPIR-V → derivative HLSL → valid roundtrip SPIR-V. Each of 8 source/roundtrip stage **type multisets and interface slot cardinalities** match, yet source/roundtrip I/O lists are equal at their exact numeric locations for **0/8** stages. Eight input stages and four output stages were candidates for numeric Location redistribution. That did not prove DXBC source Semantic identity or GPU/pixel parity.

This session tested a *different hypothesis*: whether each interface's exact **SPIRV-Cross reflected name and type** still identifies it when numeric Location changes. The names are compiler-generated or compiler-preserved metadata, **not** authentic source D3D11 input/output signature semantics. Therefore even complete name retention would remain only a diagnostic, never proof of the original material/mesh attributes, interpolation or color parity.

The new strict private parser `scripts/t3_spirv_interface_name_drift.py` re-reads each original and roundtrip `spirv-cross --reflect` JSON in memory on the disposable runner. It rejects missing/wrong schema, ambiguous names or locations, dangerous names, oversized inputs and disagreement with the existing safe location/type baseline; it counts unnamed and unlocated records explicitly. The owner T3 source translator `scripts/t3_original_top_shader_fourpass_translation.py` exposes `--classify-reflected-names`, an **opt-in** that automatically keeps the prior `--classify-io-drift` numeric baseline and requires all eight original/roundtrip stage reflection pairs. It refuses extra/private result fields and invalid numeric counters. The historical default mode and status are unchanged.

Original proprietary DXBC, Unity Shader serialized bytes, SPIR-V, derived HLSL, raw names, semantic strings, per-object IDs, GUIDs, SHA hashes and private paths **never appear in output or artifact**. The workflow uses original ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, with exact source owner/scene SHA checks, including the same four original Shader/Material providers and six level scenes. It samples one true matched original DXBC V/F pair from each original Pass: four pairs/eight stages. The other 29 matched pairs and eight unpaired Vertex variants are out of scope.

## Verified actual result

[CI42062573338](https://github.com/alwansan/raf/actions/runs/42062573338) **SUCCESS** — 86 source-free unit controls passed (5 previous T3 stage I/O drift, 10 new name classifier, 5 new integration, 20 prior four-Pass translator, 12 original DXBC linkage, 12 original Renderer graph, 22 inherited B03), then original SHA-verified source translation and private reflection succeeded. The safe numeric artifact `t3-authentic-original-921-SPIRV-private-name-drift-42062573338`, ID **13432423131**, was uploaded without private shader data. Earlier lightweight [CI42062415122](https://github.com/alwansan/raf/actions/runs/42062415122) **SUCCESS**: 40 source-free tests for the new and integrated tools.

| Property summed across eight stage input/output reflections | Inputs | Outputs |
|---|---:|---:|
| Source SPIR-V located interfaces | **34** | **29** |
| Roundtrip SPIR-V located interfaces | **34** | **29** |
| Original and roundtrip interfaces with private names | **34 / 34** | **29 / 29** |
| Exact names shared between original and derived SPIR-V | **0** | **0** |
| Name + type identical interface entries | **0** | **0** |
| Source-only names / derived-only names | **34 / 34** | **29 / 29** |
| Per-stage type **multiset** unchanged (previous numeric classifier reconfirmed) | **8/8** | **8/8** |
| Exact location/type list unchanged on both sides of same stage | — | **0 of 8 complete stage comparisons** |

No stage had an unnameable located entry, so this is not a missing-name parsing artifact. The raw reflected names are present on both sides and disjoint across the same input/output stage populations. It is **consistent with a full compiler naming-convention change during SPIRV-Cross HLSL derivation / glslang compilation**. It does **not** prove that vertex attributes or interpolators disappeared, that original D3D11 semantic names were lost by the game, or that rendered colors differ. Indeed, all numerical slot types/cardinalities and paired V/F interface compatibility remained validated. At no point is the reflected-name equality used as a surrogate for DXBC source Semantic equivalence.

**Key rejected inference:** “Source SPIRV-Cross name labels identify the same original vertex/fragment semantics after HLSL roundtrip.” In this sample they do **not** match at all (0/34 input, 0/29 output). Renaming is not semantic destruction.

## Why it matters and follow-up

The next discriminator must read **authenticated original DXBC input/output signature entries** (`ISGN`, `OSGN`, and 5.x variants `ISG1`, `OSG1`, `OSG5`, as supported). Each entry carries original semantic name/index, system-value flag, component type, source register, four-component mask and read/write mask. They must be parsed bounds-safely and kept private; later relate verified original semantics to SPIR-V `Location`, `Component`, `BuiltIn`, interpolation and HLSL roundtrip signature mapping. Parser source reference: [LLVM DirectX Container format](https://llvm.org/docs/DirectX/DXContainer.html). Merely matching type multisets or synthetic names is insufficient. No undocumented offset assumptions or fabricated original semantics are allowed. The next experiment must separately verify the genuine DXBC signature container format before comparing semantic mappings.

Also outstanding: full original 33 matched variants (only four sampled), eight unpaired original Vertex permutations, per-Pass original raster/depth/blend state, texture/sampler/constant-buffer and matrices, Unity ShaderLab binding, ARM64/Vulkan compile and Adreno device framebuffer proof.

**No game shader, texture, scene, prefab, .meta/GUID, save .rgd, FMOD, Settings or touch files edited. No T1–T5 native/FFT workflows canceled or changed. RENDER-002 remains OPEN / NOT_READY 0/3.** The heavy original workflow `.github/workflows/raft-t3-original-921-spv-name-drift.yml` is manual-only after this successful verification.
