# T3 — SHA-authenticated original particle image stream bytes

**Status: source payload verified. RENDER-002 remains OPEN / NOT_READY. Android pixels/export binding have NOT been verified.**

## Immutable originals and real CI

- Original ZIP2 Git provider: `15964ea8f246b6e076ce26b60931ee2e1a9a2385`. SHA-verified six PC Raft scenes plus four Material/Shader owners, comprising 269,007,288 assembled owner bytes. The exact external source provider was selected PRIVATELY from original serialized `m_StreamData` records for the single top-108 ParticleSystemRenderer Shader48.
- [GitHub Actions 42125608932](https://github.com/alwansan/raf/actions/runs/42125608932), source commit `276aad3df4b76067e9061b267caf3c12c1616cb3`: **COMPLETED SUCCESS**. Source-free tests **23+13+7+7+9+9+5+11+22 = 106/106 PASS**. No AssetRipper full export, Unity compile, Vulkan runtime or APK was invoked.
- First test-only CI [42125435490](https://github.com/alwansan/raf/actions/runs/42125435490) failed before original staging: one bool-as-schema-version guard was too permissive, and one synthetic test incorrectly demanded a substring in a status constant. Tightened the source plan version check to integer-only and revised the test, then reran and passed. Do not represent the failed run as an original-data failure.

## Actual original chain and source payload evidence

| Exact pinned-original source fact | Verified result |
|---|---:|
| ParticleSystemRenderer Material slot uses of unique source Shader48 | 108 |
| Distinct source Renderer objects using that shader as particle | 54 |
| Distinct original Material21 source objects on that shader | 5 |
| Non-null local Material TexEnv PPtrs | 10 |
| Distinct genuine original Texture2D class28 target objects | 3 |
| Manifest-listed external .resS/.resource source providers required | **1** |
| Original external provider reconstructed from exact immutable ZIP2 and FULL byte-size + SHA256 verified | **1/1** |
| Original Texture2D m_StreamData ranges read via seek from full-SHA-verified provider | **3/3** |
| Total authentic source-range bytes read | **983,052** |
| Original source ranges containing nonzero data | **3/3** |
| Distinct in-memory SHA256 source-range fingerprints (digests not published) | **3/3** |
| Duplicated source byte ranges | **0** |
| Partially overlapping source byte ranges | **0** |

**New conclusion:** the authentic source `.resS` bytes are present in ZIP2 and obtainable; the previous source-only six-scene/four-owner test omitted staging them only because its input subset intentionally excluded external payloads. This run resolved that original-source acquisition gap. It cannot demonstrate those source bytes were imported into the full Unity Android build, retained in OBB, decoded into valid original RGBA, or actually sampled by the game's particle material/fragment program.

The original Shader48's fixed-function source render state was separately verified in [42116530618](https://github.com/alwansan/raf/actions/runs/42116530618): `ColorMask RGB`, Alpha-dependent color+alpha Blend, ZWrite OFF, Cull OFF; an exact Unity2021 ColorWriteMask-bit opt-in translator exists but no original executable Unity Shader was changed. Neither a source stream hash nor a successful `UnityPy` typetree read certifies the user's fire/smoke squares have been corrected.

## Confidentiality and test integrity

- `scripts/t3_original_particle_texture_targets.py` gained an optional caller-owned PRIVATE stream plan. It is emitted to runner temp only when explicitly requested, permission mode 0600, never to GitHub Actions artifact or console.
- `scripts/t3_original_particle_stream_provider.py` requires exactly one validated manifest provider, three source ranges, genuine immutable `zip2` Git SHA, positive bounded size, exact manifest digest, no symlink escape, sufficient disk, and exact SHA-verified full provider bytes. It dynamically sparse-checks out ONLY this selected provider (no broader original game folder). It verifies all three byte extents using the scheduled T3 strict overlap guard and reads/fingerprints their source byte ranges privately. The only published output is safe numeric counters, not source file names, PathIDs, property labels, GUIDs, texture bytes, paths or SHA digests.
- Nine new synthetic invalid-plan/manifest/extent/byte-reading tests and nine inherited scheduled T3 range-guard tests passed with the inherited 88-source checks. Real original payload is not included in artifacts.
- Source code fixes and integration: `49131f6cab23067e390bd1301f9778c764a8a1cb` (private source plan), `6b63f836711de38274db64b2a7e6d1f246015d61` (exact-provider SHA stage), `da4c76e4985da45ec242a781188df6598f1a8c6b` (tests), `69cc8448194fa273114d994062413c19b93b56dd` (schema guard), `387041ab10c33d694685b2ad17881bdd2b978901` (test correction), `276aad3df4b76067e9061b267caf3c12c1616cb3` (terminal CI workflow).

## Next gate and T5 handoff

Use a **same-instance** full-native W1 Shader48/Material21 + B02 Texture2D28 source→export GUID trace to prove the precise five original Material source IDs and three Texture2D objects reach their actual Unity `.mat` / TextureImporter with non-null sampler textures. Check whether the actual signed APK/OBB/XAPK contains/imports the now-byte-verified provider/pixels. Then identify the real source ParticleSystemRenderer emitter and its material in device logs/screenshots before changing ShaderLab or claiming fire/smoke pixel correctness. Any new source→export helper should consume this source-gated chain, not re-run blanket source census.

**No game assets, .meta/GUID, shader source, OBB/APK, audio, Settings, input, water/FFT, saved world or team CI were modified or cancelled.**
