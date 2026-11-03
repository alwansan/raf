# W3 — per-material serialized keyword-usage audit for the priority original Shaders — 3 November 2026

Fourth W3 engineering step in this cycle, pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-03T174000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-per-material-keywords.md) and deliberately non-overlapping with W1 (programs/ShaderLab/raster/compile) and W2 (pointer corroboration, texture formats/sRGB/color-space, material colors). It directly consumes the committed inventory (priority set identity) and the step-3 schema (per-shader serialized `m_KeywordNames` sets) — no other client's evidence duplicated.

Inputs: the same 82 byte-authenticated local PC owners (identical owner set and pin verification as the committed inventory); keyword state read from every original Material (`m_ValidKeywords`, `m_InvalidKeywords`, `disabledShaderPasses`), joined to its Shader by the same fail-closed external-pointer resolution as the inventory. Names never enter the repo or artifacts (`--print-names-local` echo is local-only); keyword/pass lists are published as SHA-256 sorted-list commitments only.

## Headline result — the original game uses a tiny fraction of the serialized keyword budget

- **1,282 non-engine materials reference the 11 priority targets** (exact match to the inventory's per-shader reference counts; the 16 engine transports pass by unchanged, fail-closed).
- **ZERO keyword-set violations game-wide**: every material's `m_ValidKeywords` set is a subset of its Shader's serialized `m_KeywordNames` set (all 1,282 checked, 0 violations). The step-3 keyword budget is therefore authoritative for every existing material — any ShaderLab reconstruction carrying the exact serialized keyword set admits every serialized material keyword-config.
- **`Standard` (674 materials — 674/674 references from the inventory): only 7 distinct `m_ValidKeywords` strings are used, out of the 37 serialized.** Histogram of sized sets: 22×empty, 21×1, **498×2**, 118×3, 15×4 — i.e. the game population concentrates on two-keyword variant configs; the empty set among them means 22 Standard materials render with the base keyword config.
- **`Nature/SpeedTree8` (50): 7 distinct strings, all materials configured (set sizes 3–6; 34×4 dominant) — no empty configs among them.**
- `ParticleShader` (48): exactly **one** distinct used keyword string (42 empty / 6 configured, 1 keyword each).

| pathID | Shader | materials | used distinct | keyword-set histogram | violations |
|---:|---|---:|---:|---|---:|
| 2398 | `Standard` | 674 | 7 | 22×0, 21×1, 498×2, 118×3, 15×4 | 0 |
| 2416 | `Skin_Amplify` | 208 | 0 | 208×0 | 0 |
| 2445 | `Shimmer` | 96 | 0 | 96×0 | 0 |
| 2424 | ` BlockPaint` | 87 | 0 | 87×0 | 0 |
| 2405 | `Nature/SpeedTree8` | 50 | 7 | 6×3, 34×4, 9×5, 1×6 | 0 |
| 2426 | `ParticleShader` | 48 | 1 | 42×0, 6×1 | 0 |
| 2414 | `Tri-Planar` | 30 | 0 | 30×0 | 0 |
| 2439 | `Vegetation` | 29 | 0 | 29×0 | 0 |
| 2417 | `ParticleShader_Additive` | 26 | 0 | 26×0 | 0 |
| 2451 | `AnimalDissolve` | 23 | 0 | 23×0 | 0 |
| 2440 | `FireParticles_Amplify` | 11 | 0 | 11×0 | 0 |

Engineering reading (aggregate only): the bespoke appearance shaders (`Skin_Amplify`, `Shimmer`, `' BlockPaint'`, `Tri-Planar`, `Vegetation`, both particle shaders, fire, dissolve) carry **empty keyword configs in all of their serialized materials** — their appearance variation is entirely in properties/colors/textures, not keyword variants. For those targets a single-default-variant reconstruction covers every serialized material; only `Standard`, `Nature/SpeedTree8`, and `ParticleShader` add real variant-enumeration load. `disabledShaderPasses` slots: 0 across all 11 targets' materials (none disabled). `m_InvalidKeywords` non-empty materials total **317** (published only as counts; legacy stale keyword strings are common — a defunct-keyword cleanup avenue, never material colors, which stay W2's lane).

## Evidence and controls

- Script: `scripts/probe_w3_per_material_keywords.py` (82-owner byte-auth + pins, same one-pass structure as the inventory, fail-closed negative/out-of-range FileID, engine transports counted-never-resolved, empty-string names never committed).
- Model tests: `scripts/w3_test_per_material_keywords.py` — **8/8 OK** (empty/nonempty counting, histogram invariant, consistency gating, deterministic sorted commitments, empty-string commitment rejection, priority table identity, engine-transport set parity with the inventory). Previous 9/9, 7/7, 8/8 suites remain green.
- Real-data run exit 0, all four negative controls true. One superseded probe run (pre-fix `commit_names` semantics for empty strings) ran exit 0 with identical headline numbers; it was replaced by the corrected run before publication — the corrected artifact is the only durable one.
- Aggregate artifact: `docs/W3_PER_MATERIAL_KEYWORD_USAGE_2026-11-03.json`, SHA-256 `3e1ebc22169c23b107bf3a9a1751972b23b671a246fab3eb4762a92a52a8906d` (verified: zero name strings inside).

## Limits

Keyword-config evidence only: no material property values/colors (W2's lane), no pass/program bodies (W1's lane), no texture payloads/formats (W2's lane), no Unity compile nor CPU/GPU representation claim, no phone visual claim. WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; the game stays NOT_READY with no immutable candidate and 0/3 independent readiness reviews. **The 22 empty-config Standard materials and the `StandardVColor` (sharedassets36:880) vertex-color path are flagged as future W3 options**, as are `m_FallbackName`/`m_CustomEditorName` enumeration and the `m_NonModifiableTextures` resource-binding map.
