# W2 original material property aggregates — 3 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Fourth non-overlapping micro-lane:
serialized **Material property statistics** across the two SHA-pinned owners —
custom render-queue overrides, lightmap flags, instancing and double-sided-GI
toggles, keyword/disabled-pass entry counts and saved-property entry counts.

## Inputs re-authenticated

`resources.assets` (`87493249…8595c`) and `sharedassets0.assets`
(`0498f738…8a3c3`), full SHA256 verified before parsing. Fail-closed on any
non-int/missing required field; output rejects names, Shader PPtrs, keyword
strings and property names.

## Aggregate result (local authenticated run; CI pending → recorded when green)

### resources.assets — 163 Materials

| Aggregate | Value |
|---|---|
| custom render queue | `−1` (default) 153; **`2450` 7; `3000` 2; `5000` 1** (4 distinct) |
| lightmap flags | 4→140; 0→13; 1→6; 5→4 |
| instancing enabled | 141 |
| double-sided GI | 36 |
| valid keywords per material | 0→89; 2→20; 3→8; 4→34; 5→6 |
| disabled passes per material | 0 for all 163 |
| texEnv entries top | 4→55; 6→50; 9→29; 1→14 |

### sharedassets0.assets — 351 Materials

| Aggregate | Value |
|---|---|
| custom render queue | `−1` 324; **`2450` 22; `3000` 3; `2000` 2** (4 distinct) |
| lightmap flags | 4→210; 0→113; 1→19; 5→8 |
| instancing enabled | 266 |
| double-sided GI | 9 |
| valid keywords per material | 0→242; 1→10; 2→63; 3→29; 4→7 |
| disabled passes per material | 0→350; 1→1 |
| texEnv entries top | 9→126; 6→110; 2→45; 4→33 |

Corroboration: 163 + 351 = **514 Materials**, matching A13's and W3's owner
split exactly (another independent count agreement).

## Engineering significance for pale-surface symptoms (bounded)

- Proven: 35 materials (7+2+1 in `resources.assets`; 22+3+2 in
  `sharedassets0.assets`) deliberately override the render queue, including
  the 2450 / 3000 transparent-geometry queues and one 5000 overlay. A port
  that collapses queue assignment loses transparency ordering — a plausible
  second-order contributor to washed-out/over-blended surfaces.
- Proven: instancing is used heavily (141/163, 266/351) and lightmap-flag 4 is
  the dominant mode; a port missing these toggles changes lighting
  accumulation.
- Proven: keyword counts differ per owner in a clear shape (0-keyword
  majority), consistent with per-material feature variants; a rebuilt shader
  must preserve the keyword variant shape (count distribution) or variant
  selection changes appearance.
- Coherence with the rest of the W2 color chain: no broken references →
  Linear global space → per-texture sRGB split → these queue/keyword
  aggregates; the Android port must reproduce all four to preserve color.
- Not proven / out of scope: per-material identity mapping (aggregate only),
  actual device rasterization, shader programs (W1 lane), any build.

## Reproduction and fail-closed controls

`scripts/probe_w2_material_property_stats.py` (lazy UnityPy import, verified
two-owner parse, aggregate-only JSON, forbidden-key rejection), 8/8 synthetic
fail-closed tests in `tests/test_w2_material_property_stats.py`, workflow
`.github/workflows/raft-w2-material-property-stats.yml` (unique W2 concurrency
group, `cancel-in-progress: false`, two-owner LFS rehydration + full SHA
gate, aggregate-only artifact, ≤15 min).

## Boundaries

- Aggregate-only publication: no material names, shader names, path IDs,
  keyword strings, property names, colors or payload bytes.
- Original payloads read-only; no `.meta`/GUID/source modification; no
  Unity/APK/OBB/XAPK/Release, native request, scheduled task, CL write or
  protected-branch mutation.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3. W3's 82-owner inventory, W1's
  reconstruction lane and A12's vendor lane untouched.
