# W2 full-game material scalar-property usage baseline — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Ninth non-overlapping
micro-lane: serialized **scalar property usage** (`m_SavedProperties.
m_Floats` / `m_Ints`) across every serialized owner — the last unmeasured
material aggregation. Only name-keyed usage counters are published; the
float/int values themselves are structurally unpublishable (leak guard
rejects any decimal literal). Identity handling identical to the
full-game lanes (committed-object verification via `git show HEAD:<path>`).

## Aggregate result (local authenticated run 82/82 owners verified)

**1,556 serialized materials in 18 material-bearing owners**, carrying
**33,899 float property entries across 486 distinct property names**;
**19 materials have zero scalar properties**:

| aggregate | value |
|---|---|
| whole-build `m_Ints` | **zero entries in the entire game** — every scalar property is a float |
| render-mode group | `_Mode`/`_SrcBlend`/`_DstBlend`/`_ZWrite` = **1,438 pairs each** |
| surface constants | `_Metallic` 1,491 · `_Glossiness` 1,487 · `_BumpScale` 1,438 · `_OcclusionStrength` 1,437 · `_Parallax` 1,437 · `_UVSec` 1,437 · `_DetailNormalMapScale` 1,437 |
| transparency | **`_Cutoff` 1,457** (alpha-cut) |
| inf sentinels | none in the scalar floats (unlike the tint ring) |

## Engineering significance (bounded)

- The render-mode quad (`_Mode`/`_SrcBlend`/`_DstBlend`/`_ZWrite`, present
  on 1,438 materials) is the legacy Standard-shader blend configuration:
  if a rebuilt exporter drops it, transparent/water surfaces lose their
  blend state and render opaque/pale even with the color chain intact.
- `_Cutoff` on 1,457 materials is the alpha-cut path — a second,
  independent transparency mechanism whose loss is a distinct defect class.
- The whole-build **zero `m_Ints`** result is a trivial fail-closed port
  invariant: any rebuilt material document carrying `m_Ints` entries
  deviates from the original serialization.
- Direct verification baseline for W1's material-document export lane and
  W4's instrumented build (scalar property-name coverage).

## Reproduction and fail-closed controls

`scripts/probe_w2_material_scalar_properties.py` (identity verification
reused from the full-game probe; 82-owner enumeration rule), 9/9 synthetic
fail-closed tests in `tests/test_w2_material_scalar_properties.py`
(usage counters incl. zero-scalar materials, `m_Ints`-separate table,
entry-shape enforcement, NaN hard-fail, inf counted, decimal-literal leak
guard `assert_no_float_literals`), workflow
`.github/workflows/raft-w2-material-scalar-properties.yml` (same LFS
rehydration strategy as the binding lane; unique W2 concurrency group;
`cancel-in-progress: false`; ≤30 min).

## Boundaries

- Aggregate-only: name-keyed counters; no property values, object names,
  path IDs, or payload bytes.
- No Unity/APK/OBB/XAPK/Release, no native request file, no `.meta`/GUID
  change, CL read-only; W4's running trial build (41812889049) observed
  passively only.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3.
