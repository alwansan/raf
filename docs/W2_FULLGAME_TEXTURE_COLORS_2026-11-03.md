# W2 full-game per-owner texture color-space-split inventory — 3 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Fifth non-overlapping micro-lane:
the per-Texture2D `m_ColorSpace` × `m_TextureFormat` aggregate extended from
the two CI-pinned payload owners to the **entire original serialized game**
(82 owners). Fully non-overlapping with W3 (material→shader inventory,
shaders' serializedproperty schemas, per-material keyword usage), W1
(programs/rasterization) and A12 (vendor names); W3's statement scopes the
formats lane as W2's.

## Identity chain of custody (fail-closed)

Every one of the 82 owners was hashed locally and cross-checked against its
registered Git identity before parsing:

| Kind | Count |
|---|---:|
| LFS pointer oid match (resources.assets, sharedassets0.assets, sharedassets36.assets) | 3 |
| Tracked regular blob content match (`git show HEAD:path`) | 79 |

Any mismatch — or a missing pointer — aborts with no aggregates. The full
per-owner manifest of SHA256 digests and byte counts is in the companion JSON
(all digests are of tracked public objects; no payload is published).

## Aggregate result (local authenticated run; CI pending → recorded when green)

| Metric | Value |
|---|---:|
| Serialized owners scanned | 82 |
| Skipped (no typetrees) | `*.resS` stream companions and FMOD `.bank` files |
| Texture-bearing owners | 37 (45 owners contain zero Texture2D) |
| Original Texture2D objects, full game | **4,050** |
| sRGB-labelled (`m_ColorSpace` Gamma=0) | **1,173** (28.96 %) |
| Linear (`m_ColorSpace` Linear=1) | **2,877** (71.03 %) |

Top owners (texture-bearing): `sharedassets0.assets` 1,123 (265 G/858 L),
`sharedassets1.assets` 416 (67/349), `resources.assets` 408 (153/255),
`sharedassets35.assets` 383 (114/269), `sharedassets30.assets` 356
(109/247), `sharedassets36.assets` 287 (82/205), `sharedassets34.assets` 254
(82/172), `sharedassets24.assets` 227 (78/149), `sharedassets29.assets` 199
(62/137), `sharedassets25.assets` 192 (64/128), `sharedassets6.assets` 87
(25/62), `sharedassets8.assets` 38 (15/23). Per-owner full split table and
top pairs are in the companion JSON.

## Engineering significance (bounded)

- Game-wide closure of the color chain: the mix extends beyond the earlier
  two-owner subset — the full original game stores **4,050**
  texture objects, of which 28.96 % are sRGB-labelled and 71.03 % linear. A
  faithful port must reproduce the per-texture split everywhere, not only in
  the first two owners; any `levels`/scene-side texture (in `levelN` scene
  owners, keeping the same chain) must stay divided accordingly.
- Proven: the scheme extends uniformly to scene owners, so a port's global
  Linear color space (earlier lane finding) plus per-texture flags remains
  coherent game-wide.
- Not proven / out of scope: which texture each material consumes at
  per-material level is only aggregate here (W3's material inventory channel),
  on-device sampling math, shader programs, any build.

## Reproduction and fail-closed controls

`scripts/probe_w2_fullgame_texture_colors.py` (lazy UnityPy import,
identity-kind cross-check — LFS pointer oid or tracked regular blob —
forbidden-key rejection, aggregate-only), 8/8 synthetic fail-closed tests in
`tests/test_w2_fullgame_texture_colors.py` (unsafe owner names, out-of-enum
color space, non-int format, pointer mismatch, pointer match, unverified-local
manifest, aggregate-only output), and
`.github/workflows/raft-w2-fullgame-texture-colors.yml` (unique W2 concurrency
group, `cancel-in-progress: false`, tests-first without serializer, reuse of
the two-owner W1 LFS cache + hydration of the third LFS owner
`sharedassets36.assets`, repo-identity gate inside the probe itself,
aggregate-only artifact, ≤30 min).

## Boundaries

- Aggregate-only publication; no object names, path IDs, keyword strings,
  image bytes or per-texture identities.
- Original payloads read-only; no `.meta`/GUID/source modification; no
  Unity/APK/OBB/XAPK/Release, native request, scheduled task, CL write or
  protected-branch mutation.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3.
