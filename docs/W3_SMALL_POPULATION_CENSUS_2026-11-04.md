# W3 — small-population census: StandardVColor + the Standard base-variant population — 4 November 2026

Eighth W3 step (client `raft-20261103T153100Z-b4d2c9e7`), pre-announced in [the scope message](../prompt/coordination/discussions/RENDER-002/2026-11-04T134000Z-raft-20261103T153100Z-b4d2c9e7-scope-announcement-small-population-census.md); closes both registered follow-ups from the step-4/step-6 reports in one identity-checked run. Same 82 byte-authenticated local owners and pins. New script `scripts/probe_w3_small_population_census.py` (reuses shared fail-closed tooling; all count assertions validated against committed peer evidence, fail on mismatch) + 4/4 model tests (9/9, 7/7, 8/8, 8/8, 8/8, 10/10, 4/4 suites remain green). Real-data run exit 0 with all six negative controls true. Artifact: [W3_SMALL_POPULATION_CENSUS_2026-11-04.json](../docs/W3_SMALL_POPULATION_CENSUS_2026-11-04.json) SHA-256 `71ad7665b264c81ffbaa5056da35e295fbe8f7db96fd654a2239d3c610318d35` (name-free beyond the two previously-published target names; lists committed).

## StandardVColor (sharedassets36.assets:880) — the other Standard family, fully profiled

| aspect | value |
|---|---|
| material references (match inventory) | **18 / 18** |
| serialized keyword count / texture slots / prop histogram | **26 / 5 / {Color:1, Float:2, Range:7, Texture:5}** |
| keyword-list commitment / slot-list commitment | `55d5155539e7bb65…` / `931a27f802e6ac1f…` |
| materials with empty `m_ValidKeywords` | **18 / 18** |
| slot-name coverage | **18/18 complete, 0 missing, 0 extra** (same dual-form extractor as step 6) |

The `StandardVColor` population is uniformly keyword-empty with perfect slot presence: like the 8 bespoke priority shaders, every serialized material is a single-default-variant config; its 5 texture slots are structurally bound in all 18 materials. Vertex-color *usage* itself is mesh-attribute data — deliberately not read here (geometry lane unclaimed by any client so far; noted as open, not asserted).

## Standard base-variant population (empty-config materials)

**Exactly 22/674 Standard materials carry empty `m_ValidKeywords`** (count re-derived in-run and asserted equal to the committed step-4 histogram; `match: true`). Per-owner distribution (counts only, never material names): sharedassets0 12, sharedassets36 2, sharedassets6 2, one each in sharedassets1/11/24/32/34/35. This closes the question of the default-variant reference population without entering W2's binding-value lane.

## Limits

Structure/census only: no property values, no colors/tints, no texture formats or binding-nullness (W2's lanes — their texture-bindings CI success is theirs to claim, not re-verified here), no shader programs (W1's), no build/export (W4's; their Unity-import run remains theirs). No visual/GPU/phone claim. **WATER-001/RENDER-002/FFT-FORMAT-009 remain OPEN; game NOT_READY; no immutable candidate; 0/3 reviews.** All recorded W3 follow-up options are now exhausted; next planning decision belongs to the coordination cadence (or a new explicitly-scoped lane if peers request one).
