# W2 original material color-tint aggregates — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Sixth non-overlapping micro-lane —
the ring W3's audit explicitly left to W2 ("no material property values
(W2's lane)"): serialized **color-tint usage** counters from
`m_SavedProperties.m_Colors` on the two SHA-pinned owners. No color values
are published — only per-property-name counters and per-material boolean
class counts; names are engine packaging metadata.

## Aggregate result (local authenticated run; CI pending → recorded when green)

### Class split (out of 163 + 351 = 514 materials)

| Owner | materials | non-default tint | only identity tint | no color props |
|---|---:|---:|---:|---:|
| resources.assets | 163 | **151** | 10 | 2 |
| sharedassets0.assets | 351 | **343** | 7 | 1 |
| **Total** | **514** | **494** (96.1 %) | 17 | 3 |

### Highest-deviation tint properties (aggregate counters only)

| property | owner | using | identity | non-identity | alpha<1 | outside [0,1] |
|---|---|---:|---:|---:|---:|---:|
| `_EmissionColor` | resources | 105 | 2 | 103 | 0 | 2 |
| `_SSS_Color` | resources | 51 | 0 | 51 | 51 | 0 |
| `_Color_Multiply` | resources | 50 | 0 | 50 | 50 | 0 |
| `_SSS_color` | resources | 50 | 0 | 50 | 0 | 0 |
| `_HueVariationColor` | resources | 41 | 0 | 41 | 41 | 0 |
| `_ShimmerColor` | resources | 16 | 0 | 16 | 14 | 0 |
| `_EmissionColor` | sharedassets0 | 327 | 6 | 321 | 1 | 9 |
| `_Side2_Base` / `_Side2_Pattern` | sharedassets0 | 89/89 | 0 | 89/89 | 86/83 | 0 |
| `_BuildingEmission` | sharedassets0 | 88 | 0 | 88 | 87 | 0 |
| `_Side1_Base` / `_Side1_Pattern` | sharedassets0 | 89/89 | 2 | 87/87 | 85/84 | 0 |

Full per-name tables (32 names in resources.assets, 77 in
sharedassets0.assets) and the inf-sentinel counters (e.g. clip-rect style
non-finite components) are in the aggregate artifact; NaN still fails closed.

## Engineering significance (bounded)

- Proven: **96.1 % of all original materials carry at least one non-identity
  color tint**, and a large share of the tints are blended (`alpha<1`) or
  emission/HDR-class properties. Any port that normalizes tint properties to
  the identity `(1,1,1,1)` (the classic failure when a rebuilt exporter
  writes fresh material documents) produces washed-out, pale surfaces even
  after the color space and per-texture flags are correct.
- Direct use for the active export lanes: W1's decompiled-export/material
  document work and W4's instrumented full-build can verify their exported
  material documents **statistically** against this baseline — e.g. every
  exported/cloned material should keep its non-identity tint distribution;
  per-property-name counters give a bounded reference (no values, only
  class counts).
- Coherence: completes the sixth ring of the W2 pale-surface chain:
  no broken references → Linear global space → per-texture sRGB split →
  queue/keyword/instancing shape → game-wide split (4,050) → **tints must
  survive export**.
- Not proven / out of scope: per-material identity mapping, on-device
  rasterization, shader programs (W1), keyword configs (W3), any build.

## Reproduction and fail-closed controls

`scripts/probe_w2_material_tint_stats.py` (lazy UnityPy import, verified
two-owner parse, aggregate-only JSON, forbidden-key + float-literal-leak
guards), 8/8 synthetic fail-closed tests in
`tests/test_w2_material_tint_stats.py` (identity/non-identity + alpha,
out-of-unit and inf counters, NaN hard-fail, entry-shape enforcement,
missing colors, value leak), workflow
`.github/workflows/raft-w2-material-tint-stats.yml` (unique W2 concurrency
group, `cancel-in-progress: false`, two-owner LFS rehydration + full SHA
gate, aggregate-only artifact, ≤15 min).

## Boundaries

- Aggregate-only publication: no color float values, no material names,
  no path IDs, and no keyword strings (property names only).
- Original payloads read-only; no `.meta`/GUID/source modification; no
  Unity/APK/OBB/XAPK/Release, native request, scheduled task, CL write or
  protected-branch mutation; W4's running full build [41808015938] is not
  engaged by this lane.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3.
