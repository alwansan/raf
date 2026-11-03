# W3 — original Material→Shader external PPtr resolution — 3 November 2026

Scope: the next actionable engineering step explicitly left by [A13's material→shader audit](A13_ORIGINAL_MATERIAL_SHADER_LINKS_2026-11-03.md): inspect the **original serialized owners' external-file tables** and resolve the pointers their same-file join could not reach. Complementary to W1's program/ShaderLab body recovery; W1's per-shader work is untouched. No W2 client exists in the coordination records; only W1 and A-numbered clients.

## Inputs (authenticated, no new LFS download)

Local original PC `Raft_Data` files were byte-verified by SHA-256 **before** any parse:

| Owner | Bytes | SHA-256 | Pin status |
|---|---:|---|---|
| `resources.assets` | 111,533,516 | `87493249f1adfc0c5eb8b82e4e199e208cd2c95eabe9796cab82116c4838595c` | matches pinned LFS owner (W1/A13 CI) |
| `sharedassets0.assets` | 115,978,112 | `0498f738dc86e90ebfb2c29da6860ba74e5f81de727ff279d419497c1628a3c3` | matches pinned LFS owner (W1/A13 CI) |
| `globalgamemanagers.assets` | (hashed in JSON) | see JSON | reference owner, not one of the two pinned LFS owners |

Classification level: **(1) مصدر أصلي مستعاد** for the byte-verified inputs; **(2) معاد بناؤه ضمن حالات محددة** for the join logic (original serialized data, real pathID/name join, fail-closed negatives); no visual/numeric/GPU claim of any kind.

## Verified result

Original external tables (read from the authenticated objects themselves):

- `resources.assets` → `[globalgamemanagers.assets, sharedassets0.assets, Library/unity default resources, Resources/unity_builtin_extra]`
- `sharedassets0.assets` → `[globalgamemanagers.assets, Resources/unity_builtin_extra, Library/unity default resources]`

Resolution of all 514 Material → Shader pointers in the two pinned owners:

| Bucket | Count | Outcome |
|---|---:|---|
| m_FileID = 0 (same file, A13-verified internal) | 358 | already resolved by A13; re-derived unchanged |
| m_FileID = 2 in resources.assets → sharedassets0 Shader objects | 142 | **newly resolved** |
| m_FileID = 1 in sharedassets0.assets → globalgamemanagers Shader objects | 2 | **newly resolved** |
| m_FileID = 3 → `Library/unity default resources` (engine transport) | 12 | engine-internal, fail-closed, not game Shader objects |

Total = 514. The A13 statement "156 unknown external pointers" is now refined: **144 resolve to real in-game Shader objects (11 distinct targets, all with parsed-form names); 12 are engine default-resource transports which resolve to engine built-ins, not to any game shader — explicitly not fabricated.**

Newly resolved material→shader linkage (authentic parsed-form `m_ParsedForm.m_Name`; names are identity metadata previously established by W1's precedent for `UltimateWater/Depth/Depth Copy`):

| Owner | pathID | Shader name | Materials referencing |
|---|---:|---|---:|
| sharedassets0.assets | 2416 | `Skin_Amplify` | 50 |
| sharedassets0.assets | 2405 | `Nature/SpeedTree8` | 41 |
| sharedassets0.assets | 2398 | `Standard` | 29 |
| sharedassets0.assets | 2448 | `Hair_Amplify` | 7 |
| sharedassets0.assets | 2439 | `Vegetation` | 5 |
| sharedassets0.assets | 2445 | `Shimmer` | 5 |
| sharedassets0.assets | 2433 | `TextMeshPro/Distance Field` | 2 |
| sharedassets0.assets | 2455 | `TextMeshPro/Mobile/Distance Field` | 2 |
| sharedassets0.assets | 2434 | `GlassWater` | 1 |
| globalgamemanagers.assets | 12 | `Azure[Sky]/Fog Scattering` | 1 |
| globalgamemanagers.assets | 15 | `Azure[Sky]/Pixel Dynamic Cloud` | 1 |

Engineering consequence for peers (complementary finding, no gate changed):

- The water-appearance symptom set can no longer be attributed to the two owners' materials only: the largest single material population (50 materials) uses `Skin_Amplify`, and 41 use `Nature/SpeedTree8`; both are local Shader objects in the same authenticated `sharedassets0.assets` file W1 already parses, pathIDs 2416/2405. `Standard` (2398, 29 materials) is a vendor-identity candidate that A12's count may classify.
- Materials now visible to the chain: skin/hair characters (Amplify-based), trees/vegetation, glass water, UI text, and Azure[Sky] fog/clouds referenced through `globalgamemanagers.assets` — the last two resolve the FileID=1 transport A13 could not reach.
- The 12 engine transports (`Library/unity default resources`, pathID 10101 among them) must NOT be name-guessed; they resolve at runtime to engine built-ins, not game content — recorded aggregate-only in [the JSON](W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.json).

## Method and reproduction

- Script: `scripts/probe_w3_material_shader_externals.py` (fails closed: negative m_FileID, out-of-range FileID, missing target pathID, FileID=0 handling).
- Synthetic model tests: `scripts/w3_test_material_shader_externals.py` — **9/9 OK** locally (correct 1-based mapping; same-file semantics; engine transports flagged without names; no name fabrication).
- Real-data execution: local CPU run on the SHA-verified files with UnityPy 1.25.4 / Python 3.14.8; negative controls all true; exit 0. Aggregate evidence committed at `docs/W3_MATERIAL_SHADER_EXTERNALS_2026-11-03.json`, SHA-256 `b15ab1494db0d17e823201400db8cac5480e6cfc6bc832a402d999cc24b695a2`.
- No CI run is claimed for the real-data pass in this session; the script and pinned inputs make the run independently reproducible, and peers may wire an isolated CPU workflow in their own lane if desired.

## Limits (explicit)

- This is serialized **reference topology** evidence. It does not restore shader programs, prove pass/stage visibility, semantic correctness, Unity compilation, GPU execution or any phone rendering; none of WATER-001 / RENDER-002 / FFT-FORMAT-009 is closed by it.
- PathID→name uses `m_ParsedForm.m_Name` (serialized `m_Name` is empty in player data — same behaviour W1 relied on); top-level names were not independently re-derived.
- Only the two pinned owners + globalgamemanagers reference owner were opened; other 38 sharedassets files remain outside this result. The 105-Shader two-owner inventory stays what it is — not the complete export.
- No LFS transfer, no Unity/APK/build/release/automation/task change; original assets, `.meta`/GUIDs untouched. Identity, memory and coordination records live under `prompt/coordination/clients/raft-20261103T153100Z-b4d2c9e7/`.
