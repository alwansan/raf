# T3 — 25 real cross-owner Texture2D references verified in one export (2026-11-05)

## Question and source provenance
Previous T3 [Material/UV original-vs-real-export comparison](T3_AUTHENTIC_MATERIAL_EXPORT_PARITY_2026-11-05.md) established 41 selected original Materials, 227 TexEnv/UV slots, 89 same-owner texture reference occurrences with exact export identity and 113 original null texture slots. It left **25 external-source Texture pointers unproven**, not necessarily damaged. This continuation targets those 25 and does not repeat the already successful color/UV export checks.

Original immutable ZIP2 commit `15964ea8f246b6e076ce26b60931ee2e1a9a2385` and manifest authenticated. Relevant owner byte sizes / SHA256: `sharedassets6.assets` 6,607,272B `0476792cfeffac19d16e920011ed8d2fb2da62973c2f09a8689bc59e1ac4b632`; `sharedassets0.assets` 115,978,112B `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3`; `sharedassets1.assets` 34,888,388B `c6bdf49f7d38ab060872fcb298770bc7113959f85ea2fd1a42dc663323d7660a`.

[Source-only exact original dependency table test 41941882103](https://github.com/alwansan/raf/actions/runs/41941882103) **SUCCESS**: the 25 `m_FileID` values resolve by one-based index into `sharedassets6.assets` original serialized `externals` table: exactly **22 targets declared in sharedassets0.assets and 3 in sharedassets1.assets**. Every target provider exists uniquely in the ZIP2 manifest; no object ID/class/export identity was inferred at this stage. Source-only tests included 9 fileID/duplicate/alias/negative controls.

## Genuine original→same-instance AssetRipper verification
[Real 11-provider ZIP2 actual original/export run 41942377246](https://github.com/alwansan/raf/actions/runs/41942377246) **SUCCESS** at source [6191b472](https://github.com/alwansan/raf/commit/6191b4721ba7b9e37a198a763d41df2ae52cd6ca). Pinned public AssetRipperCLI source `036098ab525a3f9f693dc101edeb21faad4d32d8` compiled with W1 Material21/Shader48 and B02 Texture2D28 private trace capture in one exporter invocation (same 32-hex export_instance). Original 11 providers staged from pinned ZIP2 using exact bytes/SHA before reading. No raw game assets/traces were published; only aggregate report. Results:

| Original-scope property | Real observed |
|---|---:|
| Original selected Materials | 41 |
| Original external Texture slot occurrences | 25 |
| SHA-pinned original external owner files | 2 |
| Actual referenced original target objects typed as `Texture2D` | 25 |
| Exact source-owner+PathID→same-export GUID+fileID+type matches | **25/25** |
| Original-to-export target changed or lost | 0 |
| Source external targets not typed / absent | 0 |
| Export Texture2D trace missing targets | 0 |
| Export Material slot dropped or changed to null | 0 |

The combined selected-original result is **89 prior verified internal + 25 newly verified external = 114 non-null texture-slot occurrences with preserved object identity**, plus 113 genuinely null texture slots and 227/227 original UVs, all within just the 41 original Material records. This does **NOT** establish pixels, current game project integration, texture content, sampler/sRGB/import defaults, original shader variants/programs, or every game Material.

New reproducible exact dependency-table helper: `scripts/t3_external_texture_lineage.py` and 9 regression controls `tests/test_t3_external_texture_lineage.py`. Same-export type/identity validator `scripts/t3_external_texture_export.py` and 12 controls `tests/test_t3_external_texture_export.py`. Independent no-LFS workflows `.github/workflows/raft-t3-original-external-owner.yml`, `.github/workflows/raft-t3-external-texenv-export.yml`, both use `cancel-in-progress:false`.

At resume, another T3 B43 keyword/pass CI `41941363661` was active; this external-focused session did not change that workflow, duplicate its experiment, cancel any Actions or edit shared `clients/T3/state.json`/MEMORY.md due possible T3 identity overlap. Original B05/B02/B15 and B43 attribution preserved.

## Next separate unresolved fidelity question
T3 [TextureImporter sampler experiment](../.github/workflows/raft-t3-texture-sampler-sameexport.yml) targets only the **distinct Texture2D assets referred to by these 114 source slots**, using B15's prior original sampler + actual importer metadata checker. `sharedassets1.assets` SHA/size was added to its exact owner allowlist after genuine original provenance; it does not change original resource assets, Unity .meta or render flags. The importer comparer treats `-1` enum overrides and `-100` mip-bias as UNKNOWN rather than equal or drift. No Android or game-pixel fix can be inferred from source-only or AssetRipper metadata comparisons.

Issue `RENDER-002` remains **OPEN**. User's currently installed game evidence remains APK86; full Unity/Adreno visual acceptance and water/FFT and local world work remain separate priorities.
