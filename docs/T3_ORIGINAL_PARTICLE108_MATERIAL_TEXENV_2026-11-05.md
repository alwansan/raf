# T3 — Authentic 108-use Particle Shader48 source Material and TexEnv baseline

**Result:** Genuine ZIP2 original source Material21→Texture PPtr fidelity established for the single highest-use original ParticleSystemRenderer Shader48. **RENDER-002 remains OPEN**; Android material/texture binding not yet verified.

## Authenticated source and CI

- [GitHub Actions run 42119098398](https://github.com/alwansan/raf/actions/runs/42119098398) **COMPLETED SUCCESS** on source commit `775a18ec59a061783d46e7fbb77125c0929c8d34`. Tests **23 Renderer + 13 particle pass state + 7 Material TexEnv + 5 W1 ShaderLab + 11 B25 Foam + 22 B03 Renderer = 81/81 PASS**.
- Original ZIP2 immutable source commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385`, six scene SHA verification plus four exact original Material/Shader owner SHA verification (269,007,288 owner bytes; no LFS).
- Selected private original Shader48 through the actual six-scene `ParticleSystemRenderer → Material21 → Shader48` typed source pointers. Exactly one highest-use source ParticleShader48 covers **108 scene Renderer Material-slot references**, from **54 distinct ParticleSystemRenderer objects**. Prior same-source evidence found source fixed-function `ColorMask RGB`, both Blend groups Alpha-dependent, `ZWrite OFF`, `Cull OFF`.

## New original Material TexEnv proof

| Authenticated six-scene / four-owner original source scope | Real count |
|---|---:|
| Scene Particle Renderer Material-slot references to this source Shader48 | 108 |
| Distinct original Material21 objects bound to that Shader48 | **5** |
| Original Material `m_TexEnvs` slots across those 5 Materials | **10** |
| Non-null original texture pointer slots | **10** |
| Null original texture pointer slots | **0** |
| Original texture pointers local to Material owner (`m_FileID=0`) | **10** |
| External original texture pointers | **0** |
| Distinct source texture PPtr shapes across owning Materials | **3** |
| TexEnv entries with valid full UV scale + offset components | **10** |
| TexEnv entries with missing UV transforms | **0** |

This demonstrates the relevant original Materials **do contain non-null source Texture PPtr bindings**; it does **not** prove the targets' exact Texture2D object types, raw pixels, shader sampler use, alpha masks, their exported GUIDs, post-restorer ShaderLab, or a particular Android emitter. The three unique target PPtr shapes are counts only; original names/pathIDs were never published. `m_FileID=0` is a local owner reference, not an invented public asset GUID. A single Material may be referenced multiple times by distinct Renderers, so **108 source slots ≠ 108 Material objects**.

## Method and code

- [Private source in-memory Shader48→Material21 set join](https://github.com/alwansan/raf/commit/05d460d6853397ce6df765a435f21fbe4930435c) reuses the pinned six-scene/four-owner original source graph; no Material IDs leak to reports.
- [Exact five Material TexEnv original source analyzer](https://github.com/alwansan/raf/commit/02bdaba315805fe48684faafdeedf2a692725f16) `scripts/t3_original_particle_material_texenv.py` re-reads only SHA-authenticated owner objects, verifies their original `m_Shader` PPtr points back to the selected source Shader48, then uses the project's existing B05 `normalize_texenvs` to reject malformed pointer/UV records. It refuses external fileIDs outside actual serialized externals.
- [Seven synthetic TexEnv adversarial tests](https://github.com/alwansan/raf/commit/e812e6f1f6779d819c2c1511ea80917b5680d8d7) plus [two private Material outparam protections](https://github.com/alwansan/raf/commit/37c2e13eb28c548f3db5713147c9e8ee63bc57cf) guard duplicate labels, missing targets, fake owners, null/external mismatch, UV NaN/∞ and erroneous material count.
- [One bounded source-only CI integration](https://github.com/alwansan/raf/commit/775a18ec59a061783d46e7fbb77125c0929c8d34) in `.github/workflows/raft-t3-original-renderer-shader-impact.yml`, no full AssetRipper export, no Unity compilation, no APK/OBB and no private original data artifacts.

## Next

Use original Shader48→private same-instance W1 exporter Material21 and Texture2D28 trace to verify the exact five original Material source objects (108 ParticleSystemRenderer slots) and their ten bound local texture PPtrs survive the actual native export. Identify THREE source texture PPtr identities privately, verify owner/type28 and exported texture GUID/link without printing proprietary names or raw assets. Only afterwards correlate with actual phone square-fire/smoke emitter or change ShaderLab/Textures.

Keep `RENDER-002 OPEN / NOT_READY`; no game `.shader`, `.meta`, meshes/textures, water/FFT, sound, Settings, input, world/save files or native build request was changed. No other team's job was cancelled.
