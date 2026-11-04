# B04 RENDER-002 — read-only Android quality state evidence (2026-11-04)

## Source basis and question

Raft original source uses Unity 2021.3.45f2. Original `Raft_Data/globalgamemanagers` is 1,914,356 bytes, SHA256
`6d1288cd08b91d8c321ed2526503404b64b978819985b9b7fa5a9a146c29a8f5`
[pinned and authenticated by W2](W2_COLOR_SPACE_SETTINGS_2026-11-03.md).
Original `m_ActiveColorSpace=1` (Linear) and five QualitySettings tiers:
`textureQuality=[3,2,0,0,0]`, `pixelLightCount=[0,0,2,3,3]`,
`antiAliasing=[0,0,0,0,0]`. This is **original packaging metadata**,
not current Android quality state or a proof that tier indices align.

B04's earlier [original Linear PlayerSettings fix](B04_ORIGINAL_COLOR_SPACE_PARITY_2026-11-04.md)
is source-integrated, but real exported settings/phone colors remain untested.
B12's existing bounded Android `scene_shader_snapshot` already counts
unsupported/zero-pass shaders, renderer and Mesh assets, color space, fog,
and ambient mode. It did **not** expose the active runtime quality tier and
texture/light/shadow quality. Those values can help falsify a global
quality/lighting mismatch separately from missing ShaderLab programs.

## Implementation

- Add one `OriginalQualityStateSnapshot()` getter-only function to the
  existing `android-port/Runtime/Platform/AndroidTestDiagnostics.cs`.
  A single call is appended to the *same delayed, bounded, scene-specific*
  renderer snapshot, after a three-second delay and loaded-scene check.
- Its stable aggregate fields: `quality_level_index`,
  `quality_tier_count`, `pixel_light_count`,
  `master_texture_limit`, `anti_aliasing`, `shadow_mode`,
  `shadow_distance`; no proprietary quality names, scene asset bytes,
  renderer paths or shader sources. `QualitySettings.names` is used ONLY
  for its array length.
- A separate try/catch returns `quality_snapshot_error_type` if a
  quality getter fails, ensuring B12 renderer/shader logs are retained.
- NO `QualitySettings.SetQualityLevel`, mutation of any runtime quality
  property, Settings UI, resolution, audio, touch, ShaderLab, texture or
  .meta/GUID. Does not add a per-frame capture.
- Code source [84b604f](https://github.com/alwansan/raf/commit/84b604f5117c83402c33be03e71630a234eff845),
  invocation rebase on B12's newly bounded traversal
  [bc63f59](https://github.com/alwansan/raf/commit/bc63f59de0875bee6fdff71f21f5a9dd991f5045).
  B12's root/transform/pending/renderer/material ceilings and
  partial-sample reason are preserved.

## Tests and concurrency lesson

- The initial original-managed offline integration on source 84b604f
  [41928222177](https://github.com/alwansan/raf/actions/runs/41928222177)
  **SUCCESS** (actual adapted original gameplay compile, *not Unity Editor*).
- Concurrent B12 [2c15dfb](https://github.com/alwansan/raf/commit/2c15dfbf8ccc)
  replaced the renderer traversal. It preserved the new quality helper but
  omitted its invocation. B04 fail-closed tests exposed the orphaned
  helper. B04 did **not** roll back B12's bounded traversal; it restored
  only the expression linking the two functions at bc63f59.
- Initial B04 isolated [41928410376](https://github.com/alwansan/raf/actions/runs/41928410376)
  **FAILED**: real code lacked invocation; one test assertion order was
  also misleading. Rebased run
  [41928576465](https://github.com/alwansan/raf/actions/runs/41928576465)
  **FAILED** one synthetic expectation (`quality_snapshot_error_type`
  field check ran before the more specific error-fallback check). Fixture
  assertions, **not runtime gameplay**, were repaired.
- Final [B04 isolated CI41928607504](https://github.com/alwansan/raf/actions/runs/41928607504)
  **SUCCESS, 9/9** synthetic source-safety tests on source
  [6b9390a](https://github.com/alwansan/raf/commit/6b9390a0a47cb24b58b25790b73750fc18cc1603).
  Checks include read-only getters, exact one append, B12 existing
  renderer/mesh fields, no per-frame capture, missing/injected setter,
  duplicate output, missing delay and missing fallback.
- **Rebased original-managed compile SUCCESS:**
  [41928576383](https://github.com/alwansan/raf/actions/runs/41928576383)
  built source bc63f59 after the quality invocation was reconnected to
  B12's new traversal; original-adapted gameplay validation, RPC harness
  and CSharp compile steps all passed. This is still NOT Unity/IL2CPP
  nor on-device ShaderLab/pixel proof.
- No Unity Editor/IL2CPP Android device execution, no actual new phone
  logs, no current quality/lighting evidence yet. Last real phone report
  belongs to APK86/run41812889049 and predates these changes.
  **RENDER-002 stays OPEN; readiness NOT_READY, 0/3.**

## Falsifiable follow-up

On the next justified native test APK, read the one-time
`scene_shader_snapshot` event alongside reported
`color_space`, `quality_level_index`, `quality_tier_count`,
`pixel_light_count`, `master_texture_limit`,
`anti_aliasing`, `shadow_mode` and `shadow_distance`.
Compare against authenticated W2 five-tier source metadata, taking
into account Android default quality selection. If the exported
quality tiers or on-device selected tier are actually wrong,
repair ONLY with source- and runtime-proven semantics; do not
silently force the quality level to hide missing original shader passes.
Keep water FFT, Material PPtr parity, GPU/pixels and world .rgd as
separate acceptance gates.

No new full game build, native request, release or schedule was started by B04.
