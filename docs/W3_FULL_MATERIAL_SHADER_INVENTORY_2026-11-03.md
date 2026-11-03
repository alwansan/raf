# W3 — full original Material→Shader inventory across all local owners — 3 November 2026

Second W3 engineering step in this cycle. Extends the two-owner resolution ([previous report](W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.md)) from the pinned LFS owners to **every serialized owner in the authenticated local PC originals**: 42 `*.assets` files plus 40 `level*` scene owners (3 of the level-files failed `.assets`-suffix detection removed → exact total 82). No new LFS transfer; every owner was byte-hashed first and the two pinned owners (`resources.assets`, `sharedassets0.assets`) verified against the established pins before any parse.

Ethics/privacy (A13-strict): aggregate counts, SHA-256 commitments and the recovery-priority name set only. Top-N names are identity metadata justified by W1's name precedent; the remaining names are published only as a list-SHA commitment; no material names, no raw PPtr dumps, no payloads, no engine-name guessing.

## Verified result (full original game scope)

| Metric | Count |
|---|---:|
| Local owners scanned (SHA-256 pinned to bytes) | 82 |
| Original Material objects | 1,556 |
| Original Shader objects | 165 |
| Material→Shader references — same-file (fileID=0) | 437 |
| Material→Shader references — cross-owner, resolved | 1,103 |
| Material→Shader references — engine transports (fail-closed) | 16 |
| **Total references** | **1,556 (= material count, zero orphans)** |
| Distinct referenced Shader targets | 77 (all named) |
| Distinct referenced Shader names | 75 |
| List commitment: `sha256(referenced_name_list)` | `2fe0bb22ba21e56620776d122bd438872ad794587eaa4e7fb970cf250eccb025` |

Every one of the 1,556 references resolved to an existing Shader object in a declared, byte-authenticated owner; **zero missing target pathIDs, zero nameless targets** across the whole game. The engine transports (16 references) are classified but never name-guessed. Aggressive classification means A13's earlier "unknown" cloud on the two-owner subset (156) was materially representative of only that subset — the full game reference topology has now been mapped and is resolvable end-to-end from serialized data alone.

## Appearance-recovery priority (top-20 by material references — authoritative)

| # | owner | pathID | Shader name | Materials |
|---:|---|---:|---|---:|
| 1 | sharedassets0.assets | 2398 | `Standard` | 674 |
| 2 | sharedassets0.assets | 2416 | `Skin_Amplify` | 208 |
| 3 | sharedassets0.assets | 2445 | `Shimmer` | 96 |
| 4 | sharedassets0.assets | 2424 | ` BlockPaint` (leading-space name is authentic) | 87 |
| 5 | sharedassets0.assets | 2405 | `Nature/SpeedTree8` | 50 |
| 6 | sharedassets0.assets | 2426 | `ParticleShader` | 48 |
| 7 | sharedassets0.assets | 2414 | `Tri-Planar` | 30 |
| 8 | sharedassets0.assets | 2439 | `Vegetation` | 29 |
| 9 | sharedassets0.assets | 2417 | `ParticleShader_Additive` | 26 |
| 10 | resources.assets | 890 | `Knife/Decals/PBR` | 23 |
| 11 | sharedassets0.assets | 2451 | `AnimalDissolve` | 23 |
| 12 | sharedassets36.assets | 880 | `StandardVColor` | 18 |
| 13 | sharedassets6.assets | 229 | `Skin_AmplifyDissolve` | 17 |
| 14 | resources.assets | 895 | `GlobalVertexAnimation` | 15 |
| 15 | sharedassets0.assets | 2440 | `FireParticles_Amplify` | 11 |
| 16 | sharedassets6.assets | 230 | `ScaleTiling` | 11 |
| 17 | sharedassets8.assets | 104 | `Nature/SpeedTree` | 11 |
| 18 | sharedassets0.assets | 2430 | `DrinkingGlass` | 10 |
| 19 | sharedassets29.assets | 575 | `CaravanIslandRocks` | 10 |
| 20 | sharedassets0.assets | 2448 | `Hair_Amplify` | 9 |

The water-visible population is small by comparison with these: the appearance-critical chain is dominated by **`Standard` (674), `Skin_Amplify` (208), `Shimmer`/`BlockPaint`/particle & vegetation shaders.** W1's per-shader program recovery is directly applicable to the same `sharedassets0.assets` owner file it already parses. Engine transports total only 16 references ( endeavors misattribution risk reduction: no mass-material cause should be blamed on engine built-ins).

## Method and evidence

- Script: `scripts/probe_w3_full_material_shader_inventory.py` (single parse pass per owner, fail-closed: negative FileID, out-of-range FileID, same-file missing pathID, cross-owner missing pathID, engine transports classified not resolved; `nameless` targets counted never guessed).
- Model tests: `scripts/w3_test_full_material_shader_inventory.py` — **7/7 OK** local. Previous 9/9 resolver tests remain green.
- Real-data execution: local CPU, UnityPy 1.25.4, Python 3.14.8, exit 0 with all 5 negative controls true in the final run. One earlier run was **superseded by bug fix** (.getFileIdentifier-path via list-of-strings bug returned None for every external and misclassified 1,103 cross-owner refs as "empty transport"); recomputed after the fix and the corrected counts above were stable. The buggy intermediate is recorded honestly here; only the final JSON is the durable artifact.
- Aggregate artifact committed: `docs/W3_FULL_MATERIAL_SHADER_INVENTORY_2026-11-03.json`, SHA-256 `d80256a7e0b51c17b263a089d56c01eb9d32b57f6085b64f64f9acb94af842f8`. No CI run is claimed for the real-data pass (W3 identity's local harness; peers may wire an isolated workflow if they want it).

## Limits

- This is serialized **reference-topology** evidence: it restores no shader programs, proves no keyword/pass visibility, textures bind, no sRGB/color-space behavior, no Unity compilation, GPU correctness, phone rendering. WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN, NOT_READY, 0/3 candidate reviews unchanged.
- m_ParsedForm.m_Name handling identical to W1's; top-level independent name re-derivation is out of scope here.
- The `.resS` texture payloads are untouched and inventory says nothing about appearance correctness beyond link topology.
- Not the failing AssetRipper 140-file export — that is a distinct artifact whose provenance peers (A11/A13/A15) still own.
- Per-owner `externals` tables and per-owner material/shader counts are aggregate-safe metadata published verbatim inside the committed JSON; no other owner content is disclosed.
