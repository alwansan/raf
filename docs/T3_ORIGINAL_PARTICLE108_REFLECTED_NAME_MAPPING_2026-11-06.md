# T3 — Original Particle108: SPIR-V names all change during HLSL roundtrip; name-only automatic location patch is unsafe

**Verified result:** With the unique 108-use original ParticleShader48 selected from SHA-authenticated PC Raft, every located compiler-reflected stage interface variable was renamed during the SPIRV-Cross HLSL→glslang SPIR-V roundtrip. **0/26** accumulated input variable names and **0/20** output names match between original Vulkan1.1 SPIR-V and roundtrip SPIR-V. The **2/4** mismatching roundtrip Vertex/Fragment permutation pairs therefore cannot be repaired safely by original/roundtrip **reflected names alone**. RENDER-002 remains **OPEN / NOT_READY**; no Android or Unity shader replacement.

## Real immutable-source CI

- [Actions 42144978122](https://github.com/alwansan/raf/actions/runs/42144978122) **COMPLETED SUCCESS** at workflow/source commit `0998c6d82115b0f9753ede85d49ab2a9b7fc26ec`, **141/141** Python source-free tests PASS (23+13+9+12+5+7+7+7+9+11+5+11+22).
- Six original scene serialized files, four original Shader/Material owner files SHA-verified from ZIP2 pinned commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; original shader selected only by private six-scene ParticleSystemRenderer→Material21→Shader48 graph, using **108** particle material slots and **54** Renderer instances, not any public/private shader name. One original `.resS` provider independently full SHA verified and three original Texture2D source spans read. No original game binaries or Shader code in public artifacts.
- Original normal Pass and platform4 D3D11 stage linkage verified again: 16 program records, four genuine keyword-matched Vertex/Fragment pairs and eight source DXBC stages. `vkd3d-compiler`→Vulkan1.1 SPIR-V, `spirv-cross`→HLSL and `glslang`→SPIR-V roundtrip: **8/8** valid for both original and roundtrip; full stage reflection **8/8** each.
- Compiler-reflected I/O names are not authenticated original DXBC semantics and do not by themselves prove Unity ShaderLab or Android pixel parity; no semantic assumption used.

## Public-safe results from real private reflections

| Count | Real observed result |
|---|---:|
| Source SPIR-V and roundtrip SPIR-V stages compared | **8/8** |
| Original→roundtrip named stage interface comparisons | **8/8** |
| Source/roundtrip located inputs, each | **26/26** |
| Source/roundtrip located outputs, each | **20/20** |
| Input entries without a reflected name | **0/26 each** |
| Output entries without a reflected name | **0/20 each** |
| Located input name+type matches across source→roundtrip | **0/26** |
| Located output name+type matches across source→roundtrip | **0/20** |
| Inputs with original-only / roundtrip-only reflected names | **26 / 26** |
| Outputs with original-only / roundtrip-only reflected names | **20 / 20** |
| Stages with full located name+type preservation | **0/8** |
| Stages that qualify for safe automated name-only location patch | **0/8** |
| Original source vertex/fragment interface compatible | **4/4** |
| HLSL roundtrip vertex/fragment interface compatible | **2/4** |
| Source-compatible and roundtrip-incompatible pairs with complete reflected name bridge | **0/2** |
| Original D3D signature semantics and interpolation parity proven | **NO** |
| Actual Android fire/smoke GPU pixel/Unity shader import proven | **NO** |

Original and roundtrip stage input/output type multisets remained equal **8/8** in previous [CI42141506120](https://github.com/alwansan/raf/actions/runs/42141506120), with candidate location-only remaps. However **the compiler-derived names are completely disjoint**. Types may repeat and builtin semantics/vertex interpolation may require independent treatment. This finding explicitly rules out an unambiguous original→roundtrip location bridge **by reflected names alone**: it does not rule out recovery via *authentic original DXBC semantic signatures* combined with private HLSL semantic declarations and SPIR-V stage I/O metadata.

## Files and safety

- New `scripts/t3_particle108_reflected_name_bridge.py` reuses exact SHA-original four keyword pairs and the established `t3_spirv_interface_name_drift.py` reflected-name classifier. For each of eight original stages, compares strict sanitized SPIR-V interfaces to full PRIVATE `spirv-cross --reflect` name records and sums only allowlisted nonnegative numeric fields, never printing variable names, locations per stage, shader code, hashes, GUIDs or source IDs.
- `tests/test_t3_particle108_reflected_name_bridge.py` adds seven synthetic guards for names preserved but pair incompatible, names renamed, unlocated builtins treated as unproven, malicious arbitrary classifier keys/booleans, disagreement between raw and sanitized reflection, invalid compiler output and malformed original pairs. Isolated existing `.github/workflows/raft-t3-original-renderer-shader-impact.yml` additionally reran the scheduled T3 reflection order canonicalization test; it passed. The scheduled T3-owned source/fixture files were not modified by this chat scope.
- T3 isolated runner set `concurrency.cancel-in-progress=false`. No full Unity Android build, game `.shader`, `.meta`, Material, Texture, prefab, scene, OBB, APK, save, sound, settings, water/FFT or touch changes. No other worker CI cancelled.

## Next action (distinct falsifiable question)

Use original DXBC input/output semantic records (`ISGN`/`OSGN`/extended signatures), shader linkage metadata and the actual recovered HLSL `SV_*` / `TEXCOORD*` semantic declarations to construct a *private* exact semantic/location bridge for all four keyword pairs. Require deterministic one-to-one correspondence, no duplicated ambiguous semantic index/type/interpolation, preserve all 10 source-authentic Material TexEnv pointers and original ColorMask RGB/alpha Blend/ZWrite Off. If mapping cannot be proven, mark BLOCKED rather than guessing shader locations. Only then attempt a disposable SPIR-V patch and `spirv-val`/four-pair interface comparison, followed by real T5 post-vendor source-GUID tracing and Android smoke/fire screenshot acceptance.

**Gate: RENDER-002 OPEN / NOT_READY.**
