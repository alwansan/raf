# T2 WATER-001 — Original Foam authored Shader texture property and direct Material TexEnv boundaries

## SHA-authenticated result (2026-11-05)

[Real GitHub Actions **42017542487**](https://github.com/alwansan/raf/actions/runs/42017542487) **SUCCESS** on immutable ZIP2 owner `Raft_Data/sharedassets0.assets` exactly **115,978,112 bytes**, SHA256 `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`, original Shader pathID **2420**, raw object SHA256 `67bd7a7fadd7934c9b2b4925945c2df2a489e14b34692ce3c721aeffd63166b1`. **21/21 synthetic tests** passed before original source scan. Test and actual data use source-only `scripts/t2_foam_material_property_bridge.py`, `tests/test_t2_foam_material_property_bridge.py` and an isolated `.github/workflows/raft-t2-foam-material-property-bridge.yml` (source validation SHA pins, no Unity build, no LFS).

Original `m_ParsedForm.m_PropInfo.m_Props` contains **2 authored Shader properties, exactly 1 Texture property** (the other is a non-texture numeric property). Source `m_NameIndices` resolves the real four-stage `m_TextureParams` private names; exact string comparisons performed only inside CI memory and no original private names/IDs were emitted. Of **six original sampled texture rows** (five in pass0 fragment, one in pass1 fragment), **2** source texture-name occurrences match the *one authored Texture property* — one each fragment pass; **4** pass0 fragment source texture names have **no authored Texture property**. Thus it would be incorrect to fabricate six `Properties { 2D }` authored Material entries merely because six actual t/s registers are used. The remaining four source-bound resource strings may refer to global/command-buffer/dynamic/non-property textures, **but their upload source is NOT proven by the absence of authored Shader properties**.

| SHA-authentic scoped source fact | Observation |
|---|---:|
| Authored Shader properties | 2 |
| Authored Texture properties | 1 |
| Original source texture rows across four stages | 6 |
| Source texture rows matching authored Texture property string | 2 (pass0 fragment 1, pass1 fragment 1) |
| Original source texture rows without authored Texture property | 4 (pass0 fragment) |
| Original Material objects in **the same owner** | 351 |
| Same-owner original Materials with direct `m_Shader` local PPtr `(fileID=0, pathID=2420)` | **0** |
| Verified actual same-owner Material TexEnvs for Foam | **0** |

This **does not imply zero game-wide Foam Materials**: other asset providers with local or external Shader PPtrs were not staged. Nor does it imply absent runtime-created Materials or global textures. The original static Shader property declaration has one texture used in two passes; actual Material runtime uploads and per-frame texture allocation/binding remain unknown. Source name matching 2/6 is not sampler filter/wrap, UV mapping, texture object content, Unity Material shader GUID, ShaderLab compile or Android-pixel proof.

### Method and provenance

- Exact source-checkout `zip2@15964ea8f246b6e076ce26b60931ee2e1a9a2385` and unchanged owner SHA. B25 original shader name registry + CB/pass identity, T2 texture register helpers and source string identity, W3 original `m_PropInfo.m_Props` typed authored property mapping (`m_Type==4` Texture), B05 strict `normalize_texenvs` PPtr/UV parsing. Reuses historical authorship; no replacement/shadow decoder.
- Original single-owner local `Material.m_Shader` PPtr must be **exact** fileID0/pathID2420; unrelated or external refs are not accepted as local. Only exact saved TexEnv property-name equality would establish a static source-side join. A nonzero local texture PPtr must resolve to typed Texture2D/Cubemap/RenderTexture in this file, while an external target remains unknown; null pointer separately classified. No Material matched in the authenticated owner.
- Published only bounded aggregate numeric report in artifact **13409313191**, ZIP digest `07bf2ec8be15eee1a89e63e363c9b33ece3300ab2436bbd072299e69d8cfbd9d`, [Actions link](https://github.com/alwansan/raf/actions/runs/42017542487). No private source Shader/Material/texture names, source object identifiers, private values/UVs, original bytes or HLSL/SPIR-V uploaded. All source staging removed even on failure.
- Earlier original [CI42013590671](https://github.com/alwansan/raf/actions/runs/42013590671) proves per-pass exact six native DXBC t/s registers→translated SPIR-V active sampler descriptor variable IDs and 21 SAMPLE uses, **not** material property source. This new source-prop evidence narrows that remaining gap. T1 FFT and T3 source Texture2D parity developments are independent and preserved.

**Next:** identify the original runtime provider of the four pass0 fragment non-property texture names via an exact-name/managed-IL static match (when source-authenticated) or another original asset provider; do not infer `Shader.SetGlobalTexture`/Material upload without actual opcode or exact binding evidence. If original Unity Material exists in a different SHA-pinned asset provider, resolve its source Shader pointer across external table and match exact original private property/TexEnv strings. Then establish sampler/filter/UV/CB upload, private authentic two-pass ShaderLab import and actual GPU/Adreno. WATER-001 **OPEN**, project **NOT_READY0/3**, no newer on-phone Foam test than APK86.
