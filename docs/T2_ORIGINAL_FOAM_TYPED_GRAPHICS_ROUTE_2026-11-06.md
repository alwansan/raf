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

## Original explicit Blit overload verification (2026-11-06T22:15:52.203Z)

Follow-up [source-only CI42303074180](https://github.com/alwansan/raf/actions/runs/42303074180) on [201e14ca](https://github.com/alwansan/raf/commit/201e14caf01c4cbc47a798055830235eebbcbdb8) independently authenticates original managed source and categorizes the **same two** exact Material-consuming Blit sites:

- **2/2**: public static `Graphics.Blit(UnityEngine.Texture, UnityEngine.RenderTexture, UnityEngine.Material, System.Int32)` (explicit `pass` parameter).
- **0**: implicit/default-pass three-argument overload; **0**: other or mixed typed signatures.
- 58/58 strict Python report tests + 6/6 synthetic original-name controls + C# Mono.Cecil selftest PASS. Safe aggregate artifact id `13545620124`, 1295 bytes, SHA256 `52a035aae3e2a170ca70bd08fe32b7f83b4fd17095d1f246f5a69d755330cf94`.

This establishes the *public method signature*, **not** the value of either original `int pass`, actual source/destination RenderTexture identities, live Unity ShaderLab selection, or Android water pixels. Next: trace the precise integer operands of the two original calls, refuse dynamic/unknown without guessing and test whether the original two-pass paths are actually distinguished.

## Exact public Blit pass-literal source evidence (2026-11-06T22:20:53.935Z)

The independent [CI42303756960](https://github.com/alwansan/raf/actions/runs/42303756960) on code SHA [a36bf27c](https://github.com/alwansan/raf/commit/a36bf27c60959abf1e4128abb31c21b31b2bd133) executed the same pinned original Shader owner + managed DLL SHA checks and source-only typed Cecil analysis. It validates the direct top-of-IL-stack literal producer to the `Graphics.Blit(Texture, RenderTexture, Material, int pass)` public **last int pass argument** (maximum four intervening NOP instructions; computed/unknown producers explicitly remain unknown).

**Source-authentic 2/2 exact Material-consuming Blit sites:** `pass literal 0` = **1**; `pass literal 1` = **1**; other literal = 0, dynamic/indirect = 0, mixed within same field-read source site = 0. This is an exact static-IL distinction of the two original pass selections, not a guessed HLSL rewrite. 61/61 safe-report Python controls, 6/6 name controls and Cecil synthetic IL selftest PASS. Source-safe artifact `13544799516` (1,334B), sha256 `9526055bb841044323b458c270d0f927115cd7c5f46e17b28d4822b7e57ed34d`.

**Implication for a future authentic Unity import:** retain both original Foam ShaderLab passes and do not rewrite either source `Blit` pass selector or map both to one dummy pass. Verify original private ShaderLab two-pass completeness, actual exported Shader identity/GUID and runtime material/RenderTexture/CB0 binding before claiming water restoration. The original VS/FS CB0 reflected length mismatch and phone pixels remain unresolved. This evidence cannot be attributed to native [42296450023](https://github.com/alwansan/raf/actions/runs/42296450023) (older source, still Unity importing at last T2 check). WATER-001 OPEN, NOT_READY.
