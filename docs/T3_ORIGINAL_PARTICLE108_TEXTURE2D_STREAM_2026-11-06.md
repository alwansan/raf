# T3 — authenticated original 108-use Particle Shader48 Texture2D28 and streamed-image source

**RENDER-002 OPEN / NOT_READY. Source-only typed Texture and .resS provider evidence; no Android pixel acceptance.**

## Authenticated real original input

[GitHub Actions 42120918486](https://github.com/alwansan/raf/actions/runs/42120918486) **SUCCESS** on code source `87ca7a76309ef68e69dcb65b1dff9c822482694c`. **23+13+7+7+5+11+22 = 88/88 Python tests PASS** and six original source scenes plus four Material/Shader owners SHA-verified. Original ZIP2 source is `15964ea8f246b6e076ce26b60931ee2e1a9a2385`; 269,007,288 owner bytes staged, no LFS. No native AssetRipper/Unity build ran.

Earlier [source TexEnv run 42119098398](https://github.com/alwansan/raf/actions/runs/42119098398) proved that the unique source ParticleShader48 with 108 Renderer Material slots, 54 distinct Renderers, one original Pass, ColorMask RGB and Alpha Blend uses five distinct original Material21 objects. Their 10 original TexEnv texture pointer slots are all nonnull, local (fileID=0), with complete UV fields and three distinct original Texture PPtr targets.

## New source Texture2D and streamed provider proof

| Fact in authenticated original source | Count |
|---|---:|
| Original Material21 Texture PPtr uses | 10 |
| Distinct original local Texture target pointers | 3 |
| Source objects confirmed as actual Unity Texture2D class28 | **3** |
| Texture2D with valid dimensions, format and image size metadata | **3** |
| Texture2D with non-empty external m_StreamData | **3** |
| Declared extents within pinned ZIP2 manifest resource provider lengths | **3** |
| Distinct .resS/.resource provider names required | **1** |
| Texture2D whose actual external payload was staged and SHA-verified in this bounded test | **0** |
| Texture2D depending on provider that was not staged in this bounded test | **3** |
| Proven original image payloads and Android device pixels | **0** |

The three referenced objects are authentic Texture2D class28, not guessed assets. Their resource offsets and byte lengths are within **one** original external provider declared by the immutable ZIP2 manifest. That provider's external bytes were **not** copied or hash-verified in this narrow experiment; this does not establish its absence from the full native build, APK, OBB or XAPK.

The source-only evidence does not yet identify full-native exported Texture GUIDs, TextureImporter settings, decoded image payload fidelity, shader sampler/alpha behavior, real Particle emitters or the user's square fire/smoke screenshot.

## Code, test and privacy

- `scripts/t3_original_particle_material_texenv.py` supports private in-memory local Texture target outparam, leaving original owner+PathID identities out of public results.
- `scripts/t3_original_particle_texture_targets.py` resolves original owner/pathID only inside SHA-pinned source, validates actual Texture2D type and m_StreamData declared bounds, checks the private provider name against the ZIP2 manifest, and verifies staged provider bytes against manifest SHA only if a provider was staged. Never logs shader/material/texture IDs, names, raw bytes or private paths.
- Seven independent synthetic tests validate missing or wrong Texture2D class, bad metadata/stream path/extent, absent manifest, bad staged SHA, target-multiplicity and private result integrity. Legacy W1/B25/source original suites also pass.
- CI uses the existing dedicated 22-minute original 6scene/4owner ZIP2 source-only workflow; only safe numeric summaries uploaded.

## Next engineering gate

Use same-instance private W1 Material21 plus B02 Texture2D28 export trace to map all FIVE original Materials and THREE original Texture2D objects to actual Unity GUIDs. Verify those actual exported Material TexEnv bindings and that the full native/Android packaging has authentic data for the shared streaming provider. Match device fire/smoke emitter Material/Shader/Texture before changing real ShaderLab or claiming the square-effects rendering fixed.

**No Unity .shader or .meta, game assets, source texture payload, audio, Settings, controller input, water/FFT, world/save or native APK was modified.** No other workers' jobs cancelled.
