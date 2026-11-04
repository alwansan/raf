# W2 full-game texture sampler-settings baseline — 4 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Seventh non-overlapping
micro-lane: serialized **texture sampler settings**
(`m_TextureSettings`: wrap U/V/W, filter mode, aniso, mip bias; plus
`m_MipsStripped`) over every serialized owner of the original build.
Identity handling and owner discovery identical to the full-game
color-space lane (`scripts/probe_w2_fullgame_texture_colors.py` helpers,
committed-object identity via `git show HEAD:<path>`).

## Aggregate result (local authenticated run 82/82 owners verified)

Out of **4,050 textures in 37 texture-bearing owners**:

| aggregate | value split (engine enum ⇒ count) |
|---|---|
| wrap mode | Repeat(0) = **3,434** · Clamp(1) = **616** (15.2 %) |
| filter mode | Bilinear(1) = **3,979** · Point(0) = 68 · Trilinear(2) = 3 |
| aniso | level 1 = **3,994** · level 16 = **54** · 0 = 2 |
| mip bias | **0 non-zero** (all original mip biases are zero) |
| mips stripped | **0** (no texture in the build has stripped mipmaps) |

Clamp concentration: sharedassets0 (603 clamp axes), sharedassets1 (230),
resources.assets (184) — those owners carry the atlases/tiling-guard
textures where losing Clamp produces visible edge smears; 7 owners show
non-uniform U/V/W distributions, i.e. per-axis wrap exists in the original
data and must not be normalized to a single shared value.

## Engineering significance (bounded)

- A rebuild pipeline that re-imports textures with defaults (e.g. Clamp
  everywhere, aniso 0-4, trilinear) breaks tiling shading and water-adjacent
  atlas usage even with a correct color-space/texture/tint chain: this is
  ring 7 — sampler handling after ring 6 (tints).
- The zero-mipbias / zero-stripped result gives a trivial fail-closed port
  invariant: an exporter producing non-zero mip bias or stripped mips for
  original textures deviates from the original build.
- Usable by W4's instrumented build lane (texture import settings) and by
  W1's material-document/texture export verification — aggregates only.

## Reproduction and fail-closed controls

`scripts/probe_w2_texture_sampler_settings.py` (reuses identity
verification from the full-game probe; owner enumeration same 82-owner
rule), 11/11 synthetic fail-closed tests in
`tests/test_w2_texture_sampler_settings.py` (enum range enforcement for
wrap/filter/aniso, non-finite mip bias, missing settings, mip-bias value
never published, unsafe owner names, non-texture objects ignored), workflow
`.github/workflows/raft-w2-texture-sampler-settings.yml` (same LFS
rehydration strategy as the full-game lane — W1 two-owner cache key +
sharedassets36 hydrate; unique W2 concurrency group;
`cancel-in-progress: false`; ≤30 min).

## Boundaries

- Aggregate-only: no object names, path IDs, float values or payload bytes
  (the mip-bias *value* is structurally unpublishable — only its zero/non-
  zero counter is emitted, and the leak guard rejects the token `MipBias`).
- No Unity/APK/OBB/XAPK/Release, no native request file, no `.meta`/GUID
  change, CL read-only; W4's build runs are engaged by nobody but W4.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3.
