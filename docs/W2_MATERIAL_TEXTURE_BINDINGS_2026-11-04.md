# W2 full-game material texture-binding survival baseline — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Eighth non-overlapping
micro-lane, and the first ring explicitly about the **material→texture
wiring**: `m_SavedProperties.m_TexEnvs` → `m_Texture` PPtr per serialized
material, over every serialized owner (identity handling identical to the
full-game lanes; committed-object verification via `git show HEAD:<path>`).

## Aggregate result (local authenticated run 82/82 owners verified)

**1,556 serialized materials in 18 material-bearing owners** (coherent
with the known 1,544-selected / 1,536-exported material scale of the
document lanes), carrying **4,583 actual texture bindings** (vs 5,663 null
slot declarations):

| aggregate | value |
|---|---|
| slot usage (bound) | `_MainTex` 864 · `_BumpMap` 714 · `_MetallicGlossMap` 623 · `_Diffuse` 604 · `_Normal` 569 · `_Smoothness` 234 · `_MetallicRSmoothnessA` 180 · `_Metallic` 158 · `_MetallicRPaintMaskGSmoothnessA` 87 · `_EmissionMap` 84 |
| PPtr `m_FileID` of bound entries | self-file (0) = **4,166**; external = **417** across 11 distinct external-file indices (2:159, 5:189, 6:24, 7:9, 13:10, 12:3, 9:4, 14:4, 10:2, 11:1, 4:12) |
| fully-unbound materials | 2 owners carry materials with **zero** bound slots |

Only slot *names* (engine packaging metadata) and integer counters are
published — never the reference identity of a texture or any path ID.

## Engineering significance (bounded)

- The external-reference structure matters as much as the binding itself:
  417 bindings point through `m_FileID` external indices, so a rebuilt
  material→texture graph must reproduce *both* the binding count and the
  external-file mapping (the proven 1-based `external_id = m_FileID - 1`
  deref from lane 1 applies). Getting either wrong silently yields flat
  pale surfaces even with correct color space, tints and sampler settings.
- Direct verification baseline for W1's material-document export (1,556
  serialized materials ⇒ per-document binding survival check) and for W4's
  instrumented build (texture graph integrity before Unity import).
- The 2 fully-unbound-material owners give a bounded negative fixture:
  unbound materials are legitimate originals and must not be "fixed" by an
  exporter.

## Reproduction and fail-closed controls

`scripts/probe_w2_material_texture_bindings.py` (identity verification
reused from the full-game probe; 82-owner enumeration rule), 10/10
synthetic fail-closed tests in `tests/test_w2_material_texture_bindings.py`
(bound/null classification incl. `m_FileID`-only external refs, malformed
entry/PPtr shapes, negative PPtr components, non-Material objects, leak
guards: `m_PathID`/`m_FileID`/`m_Scale`/`m_Offset` and numeric IDs never
published), workflow `.github/workflows/raft-w2-material-texture-bindings.yml`
(same LFS rehydration strategy; unique W2 concurrency group;
`cancel-in-progress: false`; ≤30 min).

## Boundaries

- Aggregate-only: no object names, no target path IDs, no external-file
  paths, no float values, no payload bytes.
- No Unity/APK/OBB/XAPK/Release, no native request file, no `.meta`/GUID
  change, CL read-only; W4's running build (41812889049, water gate passed,
  Unity import) is observed passively only.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3.
