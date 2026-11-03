# W2 original texture color-space/token format aggregates — 3 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Third non-overlapping micro-lane:
direct per-Texture2D `m_ColorSpace` × `m_TextureFormat` aggregates across the
two SHA-pinned original payload owners, completing the color-loss chain that
started with the external-pointer verification and the Linear project color
space.

## Inputs re-authenticated

Same two owners as all W2 probes (full SHA256 verified before parsing):
`resources.assets` (`87493249…8595c`, 111,533,516 B) and `sharedassets0.assets`
(`0498f738…8a3c3`, 115,978,112 B). Unity `ColorSpace` engine enum: Gamma=0,
Linear=1 — fail-closed outside {0,1}.

## Aggregate result (local authenticated run; CI pending → recorded when green)

### resources.assets — 408 textures, 4 distinct formats

| colorSpace label | Textures | share |
|---|---:|---:|
| Gamma (= sRGB-labelled data) | 153 | 37.5 % |
| Linear (data textures) | 255 | 62.5 % |

Dominant pairs: format 12 Linear 151; format 10 Linear 98; format 1 Gamma 66;
format 12 Gamma 63; format 10 Gamma 17; format 4 Gamma 7.

### sharedassets0.assets — 1,123 textures, 5 distinct formats

| colorSpace label | Textures | share |
|---|---:|---:|
| Gamma | 265 | 23.6 % |
| Linear | 858 | 76.4 % |

Dominant pairs: format 12 Linear 466; format 10 Linear 259; format 12 Gamma
243; format 4 Linear 133; format 1 Gamma 12; format 4 Gamma 5.

Format integer values are published as packaging metadata only; their engine
names are not proprietary but are deliberately not asserted here where the
type tree does not print them — the counts are the evidence.

## Engineering significance for pale-surface color symptoms (bounded)

- Proven: the original pipeline stores **both** sRGB-labelled textures and
  linear data textures per owner (37.5 % / 62.5 % in `resources.assets`;
  23.6 % / 76.4 % in `sharedassets0.assets`). A faithful port must reproduce
  this split: sampling sRGB-labelled albedo textures **as-if-linear** (or vice
  versa) washes out or darkens surfaces — the same class of symptom as a
  wrong global color space, but per-texture.
- Coherence: the Linear project color space (`probe_w2_color_space_settings`)
  with a large linear-labelled texture share is internally consistent — the
  Android port must keep the global color space Linear **and** the per-texture
  sRGB flags as in the original.
- Not proven / out of scope: which per-texture flag each individual material
  consumes (aggregate only), actual on-device sampling math, shader programs
  (W1 lane), or any build.

## Reproduction and fail-closed controls

`scripts/probe_w2_texture_color_formats.py` (lazy UnityPy import, verified two
owner parse, aggregate-only JSON with forbidden-key rejection), 6/6 synthetic
fail-closed tests in `tests/test_w2_texture_color_formats.py` (out-of-enum
color space, non-int format, name-leak check, probe gate on unverified
sources), workflow `.github/workflows/raft-w2-texture-color-formats.yml`
(unique W2 concurrency group, `cancel-in-progress: false`, two-owner LFS
rehydration with full SHA verification, aggregate-only artifact, ≤15 min).

## Boundaries

- Aggregate-only publication: no object names, path IDs, image bytes or
  per-texture identities are published.
- Original payloads read-only; no `.meta`/GUID/source modification; no
  Unity/APK/OBB/XAPK/Release, native request, scheduled task, CL write, or
  protected-branch mutation.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3. W3's 82-owner material→shader
  inventory and W1's reconstruction lane untouched and not duplicated.
