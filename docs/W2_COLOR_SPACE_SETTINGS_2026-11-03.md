# W2 original color-space settings probe — 3 November 2026

Client W2 `raft-20261103T152008Z-92502b76`. Non-overlapping follow-up lane after
the external-pointer verification: the **original project color-space
configuration**, read from the original `globalgamemanagers` PlaySettings
owner. CPU-only typetree read; no Unity, no GPU, no LFS
(`globalgamemanagers` is a tracked regular file, re-hashed before reading:
SHA256 `6d1288cd08b91d8c321ed2526503404b64b978819985b9b7fa5a9a146c29a8f5`,
1,914,356 bytes).

## Aggregate result (authenticated local run; CI pending → recorded when green)

| Setting | Original value | Class |
|---|---|---|
| `PlayerSettings.m_ActiveColorSpace` | **1 = Linear** (Unity `ColorSpace` engine enum: Gamma=0, Linear=1) | packaging metadata |
| `PlayerSettings.m_ColorGamuts` | `[0]` (single default gamut entry) | packaging metadata |
| `BuildSettings.m_Version` | `2021.3.45f2` | packaging metadata |
| `QualitySettings` tiers | 5 tiers; textureQuality 3/2/0/0/0; pixelLightCount 0/0/2/3/3; antiAliasing 0/0/0/0/0 | packaging metadata |

The enum mapping (Gamma=0, Linear=1) is a Unity engine convention, recorded as
such; the probe fail-closes on any value outside {0, 1} so it can never guess.

## Engineering significance for pale-surface color symptoms (bounded)

- Proven: the original project builds with **Linear color space**. Any Android
  port that runs in **Gamma** color space produces washed-out, pale surfaces
  and wrong-looking albedo/lighting — a first-order, build-level candidate
  cause for the color-loss symptom, complementary to (and above) the now
  refuted broken-references hypothesis.
- Proven: the original also pins a single default color gamut (`[0]`), so the
  port should not enable HDR gamuts the original never used.
- Corroboration: engine version 2021.3.45f2 matches the known original Unity
  cycle and gives W1's Vulkan reconstruction lane the exact target engine
  version for shader-program semantics.
- Not proven / out of scope: on-device rendering equivalence, per-material
  render states, texture import formats/sRGB double-conversion inside the two
  payload owners (next W2 micro-lane), FFT/visual recovery, and any build.

## Reproduction and fail-closed controls

`scripts/probe_w2_color_space_settings.py` (aggregate-only JSON; refuses
forbidden keys and out-of-enum values), 11 synthetic fail-closed tests in
`tests/test_w2_color_space_settings.py` (missing file, out-of-enum value,
missing/duplicate PlayerSettings, malformed gamuts, object-name leak check,
non-aggregate key check; 11/11 pass), and the W2-owned workflow
`.github/workflows/raft-w2-color-space-settings.yml` (unique concurrency
group, `cancel-in-progress: false`, SHA-pinned owner hash gate, aggregate-only
artifact, ≤10 min budget).

## Boundaries

- Aggregate-only publication; the color-space setting is engine packaging
  metadata, not original asset payload — no object names, path IDs, textures
  or shader bytes are published.
- Original payloads read-only; no `.meta`/GUID/source modification; no
  Unity/APK/OBB/XAPK/Release/native request/scheduled-task/CL change.
- WATER-001 / RENDER-002 / FFT-FORMAT-009 remain OPEN; game NOT_READY;
  triple immutable-candidate reviews 0/3.
