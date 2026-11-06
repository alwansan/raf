# T3 — Original Particle108: four genuine D3D11 keyword pairs translate to valid Vulkan SPIR-V, but HLSL roundtrip changes stage locations

**Finding:** All **8/8** original Vertex/Fragment D3D11 stage variants (four exact keyword pairs) for the SHA-authenticated original highest-use one-Pass Particle Shader48 translate to valid Vulkan 1.1 SPIR-V, and all **8/8** yield HLSL and valid SPIR-V after HLSL roundtrip. However, original source-stage Vertex→Fragment interfaces are compatible **4/4**, whereas roundtrip pair interfaces are compatible only **2/4**. Source versus HLSL-roundtrip per-stage input+output interfaces are exactly identical **0/8**; the preserved IO type multisets and changed location decorations point to a *candidate location/semantic remap*, not an established authored shader equivalence or Android fix.

## Reproducible real PC source + isolated GitHub CI

- [First real translation run 42141030091](https://github.com/alwansan/raf/actions/runs/42141030091) **COMPLETED SUCCESS**, code SHA `3e01555d67514697b1895813782000f8a15f5aa4`, 126/126 source-free tests; first measured the 8/8 SPIR-V+HLSL feasibility and 2/4 roundtrip stage interface compatibility.
- [Detailed eight-stage location/type diagnostic 42141506120](https://github.com/alwansan/raf/actions/runs/42141506120) **COMPLETED SUCCESS**, exact workflow/source SHA `9ab1c1ca2dcca4006d28be6ae416118cebc1fe25`, **133/133** tests. Eight real stages were classified using the previously tested strict `t3_stage_io_drift.classify_stage_io`; private SPIR-V reflection names, types, locations and real shader source remained runner-private.
- Original PC inputs pinned to ZIP2 SHA `15964ea8f246b6e076ce26b60931ee2e1a9a2385`: all six original scenes + four original Shader/Material owner serialized files SHA verified. A single original image `.resS` provider was independently reconstructed, full manifest SHA checked, and three Texture2D28 original byte ranges read. UnityPy `1.23.0`. No LFS source replacement, no source image substitution.
- Genuine original private Renderer→Material21→Shader48 graph identifies the unique **108 ParticleSystemRenderer material-slot source** used by **54 distinct particle renderers**, with one original normal Pass and exact 4 Vertex/Fragment keyword pairs; 16 D3D11 program table records. Original fixed-function state retains `ColorMask RGB`, alpha-dependent Blend, ZWrite Off. All 10 original source Material TexEnv Texture PPtrs were previously verified against one actual bounded AssetRipper export in CI42134436841, including the intentionally nonexportable one.
- Ubuntu `24.04`; `vkd3d-compiler 1.2-15build1`, `spirv-tools 2025.1~rc1-1~ubuntu0.24.04.2`, `spirv-cross 2021.01.15+1.3.239.0-1build1`, `glslang-tools 15.1.0-2~ubuntu0.24.04.2`. Translation is private original **DXBC→SPIR-V→HLSL→SPIR-V**, each SPIR-V validated with `spirv-val --target-env vulkan1.1`. `spirv-cross --reflect` was used only for safe anonymous counts and interface comparisons.

## Verified counts (original private D3D11 source, not shipped Android artifacts)

| Verified measure | Real result |
|---|---:|
| Original exact shader stage pairs attempted | **4/4** |
| Original private D3D11 stage programs attempted | **8/8** |
| Source DXBC→Vulkan 1.1 SPIR-V validated | **8/8** |
| SPIR-V→HLSL generated | **8/8** |
| HLSL→Vulkan SPIR-V roundtrip validated | **8/8** |
| Original and roundtrip stage reflections independently parsed | **8/8 each** |
| Original 4 Vertex/Fragment SPIR-V pair interfaces compatible | **4/4** |
| After HLSL roundtrip 4 Vertex/Fragment SPIR-V pair interfaces compatible | **2/4** |
| Original/roundtrip *exact* per-stage input/output interface equality | **0/8** |
| Original/roundtrip exact SPIR-V resource slot shape equality | **6/8** |
| Total original and roundtrip input slots | **26/26** |
| Total original and roundtrip output slots | **20/20** |
| Stages with unchanged input interface | **4/8** |
| Stages with unchanged output interface | **4/8** |
| Stages with candidate input-only location remap | **4/8** |
| Stages with candidate output-only location remap | **4/8** |
| All eight stages retain input type multiset | **8/8** |
| All eight stages retain output type multiset | **8/8** |
| Total added/removed input locations across stages | **4 added, 4 removed** |
| Total added/removed output locations across stages | **4 added, 4 removed** |
| Same-location output type assignments changed | **4** |
| Android APK shader text/Unity import/emitter pixels tested | **NO** |

**Interpretation:** The IO type *multisets* and total slot counts survive translation, but SPIRV-Cross HLSL→glslang's roundtrip relocates some interface locations; collisions or swapped types at the same old locations can make two of four vertex/fragment pairs incompatible even though each stage's SPIR-V validates independently. The `location_only_remap_candidate` classification is explicitly **candidate**, not permission to blindly reorder duplicate type instances: source reflected semantic identity, builtin `SV_POSITION` and user locations still need a private exact mapping. The two original/roundtrip resource slot shape differences also need checking before claiming sampler/texture preservation. Do not drop original shader keywords or force placeholder textures.

## Code, tests and audit controls

- New `scripts/t3_original_particle108_spirv_translation.py`: exact authenticated original shader selection, four full keyword+player-bucket variant pairs using original `m_BlobIndex` and proper DXBC shader-stage version, eight private CPU translations, strict fail-closed source/roundtrip SPIR-V reflection schema, anonymous interface compatibility and location-vs-type drift totals. Private compiler outputs, original shader bytes, names, `m_PathID`, export GUIDs, sampled IO types and per-program hashes are never uploaded or included in public report/error text.
- New source-free `tests/test_t3_original_particle108_spirv_translation.py`: eleven synthetic controls for complete source variant permutation matching, partial translation not mislabelled successful, mismatched/duplicate keyword buckets, wrong-stage DXBC, synthetic output reflection drift, ambiguous/stale resource metadata, private hashed output suppression and classifier malicious or negative numeric inputs. Existing five `test_t3_stage_io_drift.py` controls added to workflow.
- Scope-specific `.github/workflows/raft-t3-original-renderer-shader-impact.yml` installs pinned Ubuntu package versions at runtime, reruns the inherited six-scene SHA source pipeline and nine original DXBC linkage controls, uploads **numeric aggregate JSON only**. Its `concurrency.cancel-in-progress=false` preserves other work.
- [Initial synthetic-only failing run 42140918323](https://github.com/alwansan/raf/actions/runs/42140918323) was due to incorrectly rejecting standard `pathlib.PosixPath` temporary runner directories by requiring exact type `Path`. Corrected with `isinstance(temporary,Path)` before any source ZIP2 staging/translation. The two subsequent genuine source runs above passed. No real original shader defect was inferred from the initial fixture bug.

## What to do next

**Next source-safe engineering step:** link the original SPIR-V vertex outputs to fragment inputs and the recovered HLSL semantics *within each of the four exact keyword permutations*. Distinguish candidate location-only remaps from ambiguous duplicate-type mappings, built-in position semantics and sampler/UBO resource binding drift; validate a full 4/4 stage-interface fix with `spirv-val` and actual exact source semantic correspondence, not just a 4/4 integer count. Only then consider producing an isolated ShaderLab prototype preserving ColorMask RGB, alpha Blend, ZWrite Off, all four original keyword variants and ten source-authentic Material Texture bindings.

**Still not verified:** exact source Shader48 post-T5 vendor restorer `.shader` GUID in production Unity, Android ARM64 Unity compiler/Vulkan GPU, complete original DXBC code semantic parity, full texture/image alpha sampling or whether this 108-use source shader is the particular user's square fire/smoke emitter. No `.shader`, `.meta`, Material, prefab, texture, scene, OBB/APK or game runtime system was modified. `RENDER-002` remains **OPEN / NOT_READY**.
