# T2 original Foam Material: typed Unity Graphics route (source-only)

**Owner:** T2 · **Issue:** WATER-001 · **Session:** 20261106T2203Z-T2-chat-graphics-path-7d3e · **UTC checkpoint:** 2026-11-06T22:09:47.960Z

## Source and reproducibility

Pinned source: `alwansan/raf:zip2` immutable `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. Existing private workflow validates original Unity Shader owner (`sharedassets0.assets`, 115,978,112 bytes) and original managed `Assembly-CSharp.dll` (3,211,776 bytes) against manifest/SHA; reads one exact original Foam Shader name privately, compiles typed Mono.Cecil scanner, runs original IL scan, validates strict aggregate JSON, purges private source. No original strings, GUIDs, private identifiers, IL or game bytes are published.

- Code: [3bbb7b040b7a626e61f68e5572d402ee49a93a4d](https://github.com/alwansan/raf/commit/3bbb7b040b7a626e61f68e5572d402ee49a93a4d)
- [SHA-original Actions **42302222142**](https://github.com/alwansan/raf/actions/runs/42302222142): SUCCESS, job `128182594125`, source SHA identical to code commit.
- Synthetic controls: 56/56 safe-report tests, 6/6 original-name tests, Mono.Cecil synthetic selftest PASS. The new public-family partition is exclusive and validated; typed Material parameter identity is required (name similarity alone cannot count).
- Safe 1249-byte artifact id `13545245167`, digest `sha256:2e77b9a496468746a77183a9a88e39daca248862af5433ad2b8d724acc1e637b`; retention through 2026-11-13 UTC.

## Verified bounded result

| Source-original typed IL property | Aggregate |
|---|---:|
| Exact original Material field load sites | 13 |
| Following straight-line IL instructions inspected | 98 |
| Sites using exact Material/Object instance receiver | 9 |
| Sites passing exact original Material as typed Graphics parameter | 2 |
| Graphics.Blit public API family | **2** |
| Graphics.DrawMesh | 0 |
| Other Graphics API families | 0 |
| Mixed Graphics API families within one material-field source site | 0 |
| CommandBuffer and Renderer typed Material parameters | 0 |
| Ambiguous/budget sites | 0 |

**Interpretation:** Both proven *typed original Graphics material-consuming calls* use the public Unity `Graphics.Blit` method family, not `Graphics.DrawMesh`. The original Foam Material is therefore consumed by a Blit/render-texture-related codepath at these two verified field-read sites. This is a useful source-level narrowing of the water Foam restoration target, not a runtime or full-callgraph proof; further calls beyond the bounded 32-IL straight-line window may exist.

## Strict unknowns

- Actual `Graphics.Blit` overload and its source Texture/destination RenderTexture/value and optional pass index: **NOT YET CLASSIFIED**.
- Whether that IL runs during Android world rendering, the original texture/sampler/CB0/vector upload and Unity 2021 ShaderLab importer: **UNKNOWN**.
- Whether both original passes are selected as intended or pixels appear on the Adreno: **NOT VERIFIED**.
- Prior [original CB0 source CI42300107157](https://github.com/alwansan/raf/actions/runs/42300107157) still reports genuine VS/FS reflected array-length mismatch in both passes; no guessed padding, alias or dummy shader allowed.
- Existing native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) was still in `Unity Editor 2021.3.45f2 Android import and compile` at last check on older immutable SHA `a1737bd736e276d53df808442cfae3b1eea0d488`; it **does not contain** this new source-only scanner commit, and was not cancelled or duplicated.

**Next engineering:** inspect exact public `Graphics.Blit` method overload signature on the same original typed field value; classify input `Texture`, output `RenderTexture`, optional explicit pass int and material alias, with source-only synthetic negatives; then join original RenderTexture ownership/producer to water pipeline and coordinate with T5 on an authorised actual Unity export/pixel test. WATER-001 OPEN; game NOT_READY.
